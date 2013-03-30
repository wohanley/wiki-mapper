import argparse
import urllib2
from bs4 import BeautifulSoup
import re
import os
import sys
from pygeocoder import Geocoder
from pygeocoder import GeocoderError
from pykml.factory import KML_ElementMaker as kml
from lxml import etree
import unicodedata

parser = argparse.ArgumentParser(description="Generates a KML map file from a Wikipedia list article.")
parser.add_argument('source_url')
parser.add_argument('gm_api_key')
parser.add_argument('-t', '--title', default='My map')
parser.add_argument('-o', '--out', default='map.kml')
args = parser.parse_args()

# Ssshhhh, don't tell Wikipedia
req = urllib2.Request(args.source_url, headers={'User-Agent' : "Magic Browser"})
html = BeautifulSoup(urllib2.urlopen(req))

locations = []

for item in html.select('h3 span.mw-headline'):
    header = item.parent
    text = ''.join(header.next_sibling.next_sibling.find_all(text=True))
    text = re.sub(r'\[.*\]', '', text)
    text = os.linesep.join([s for s in text.splitlines() if s])
    locations.append((header.contents[2].string, text))

#maps = GoogleMaps(args.gm_api_key)

doc = kml.kml(
    kml.Document(
        kml.name(args.title),
        kml.Style(
            kml.IconStyle(
                kml.Icon(
                    kml.href("http://maps.google.com/mapfiles/kml/paddle/wht-circle.png")
                )
            )
        )
    )
)

for location in locations:
    try:
        #coordinates = Geocoder.geocode(unicodedata.normalize('NFKD', location[0]).encode('ascii','ignore'))
        coordinates = Geocoder.geocode(unicodedata.normalize('NFKD', location[0]).encode('ascii', 'ignore')).coordinates
        print(coordinates)
        doc.Document.append(kml.Placemark(
            kml.name(location[0]),
            kml.description(location[1]),
            kml.Point(
                kml.coordinates(','.join(format(x, "3.6f") for x in [coordinates[1], coordinates[0], 0]))
            )
        ))
    except GeocoderError as ge:
        sys.stderr.write(str(ge.message) + " on " + str(location[0].encode('ascii', 'replace')) + '\n')
    except TypeError as te:
        if location[0]:
            sys.stderr.write(str(te.message) + " on " + str(location[0].encode('ascii', 'replace')) + '\n')

out = open(args.out, 'w')
out.write("""<?xml version="1.0" encoding="UTF-8"?>""")
out.write(etree.tostring(doc, pretty_print=True))
