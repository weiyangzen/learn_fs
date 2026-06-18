# sources/distributed-fs/ceph/src/rgw/rgw_cors_s3.cc

## Purpose
Implements S3 XML parsing and rendering for RGW CORS configuration, translating AWS-style XML elements into the shared `RGWCORSRule` model.

## Important APIs, types, and functions
`RGWCORSRule_S3::to_xml()` emits `CORSRule`, optional `ID`, method entries, origins, allowed headers, max age, and exposed headers. `RGWCORSRule_S3::xml_end()` validates and consumes child XML objects, enforcing allowed method names, id length <= 255, at least one origin, valid wildcard names, and numeric `MaxAgeSeconds`. `RGWCORSConfiguration_S3::xml_end()` requires at least one `CORSRule`. `RGWCORSXMLParser_S3::alloc_obj()` maps XML tags to parser objects.

## Control flow
The XML parser allocates typed objects per element. On close of a `CORSRule`, child element data is folded into the inherited rule fields. On close of `CORSConfiguration`, rule objects are copied into the configuration list. Rendering walks persisted rules and emits AWS XML.

## State and persistence
This file does not persist directly; it materializes the shared CORS state that `rgw_cors.h` encodes elsewhere.

## Dependencies and integration points
Uses `RGWXMLParser`, `XMLObj`, `XMLFormatter`, S3 XML namespace constants, and RGW debug prefix logging.

## Risks and test signals
Risks include case-insensitive method parsing differences, missing origin rejection, integer overflow mapping to invalid max-age sentinel, and static casts from base rules to S3-derived rules during XML output. Tests should include invalid methods, long IDs, malformed max age, wildcard names, multi-rule configs, and XML round trips.
