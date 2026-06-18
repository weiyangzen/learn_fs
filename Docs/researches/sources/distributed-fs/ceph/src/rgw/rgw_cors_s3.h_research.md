# sources/distributed-fs/ceph/src/rgw/rgw_cors_s3.h

## Purpose
Declares S3-specific XML adapters around the shared CORS model.

## Important APIs, types, and functions
`RGWCORSRule_S3` inherits `RGWCORSRule` and `XMLObj`, adding XML close-time parsing and `to_xml()`. `RGWCORSConfiguration_S3` inherits `RGWCORSConfiguration` and `XMLObj`, adding configuration-level XML parsing and stream output. `RGWCORSXMLParser_S3` subclasses `RGWXMLParser` and owns `DoutPrefixProvider`/`CephContext` pointers for logging and parser allocation.

## Control flow
Protocol code instantiates `RGWCORSXMLParser_S3`, parses request XML into `RGWCORSConfiguration_S3`, then stores the inherited common configuration. GET CORS paths call `to_xml()`.

## State and persistence
State is inherited from `RGWCORSRule` and `RGWCORSConfiguration`; the S3 classes add only logging/context pointers.

## Dependencies and integration points
This header binds `rgw_xml.h`, `common/XMLFormatter.h`, `common/dout.h`, and `rgw_cors.h`. It is the S3-facing bridge for bucket CORS handlers.

## Risks and test signals
The derived objects are copied into base-rule lists, so output paths assume stored rules can be safely treated as `RGWCORSRule_S3`. Tests should cover parser allocation for every supported tag and S3 output from parsed and persisted rules.
