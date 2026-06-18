# sources/distributed-fs/ceph/src/rgw/rgw_tag_s3.h

## Purpose
`rgw_tag_s3.h` declares S3 XML wrappers for object tagging.

## Important APIs, Types, and Functions
`RGWObjTagEntry_S3` stores one key/value pair with XML decode/dump. `RGWObjTagSet_S3` derives from `RGWObjTags` and can dump/decode XML and rebuild a validated core tag set. `RGWObjTagging_S3` owns a tag set and exposes top-level XML decode plus rebuild.

## Control Flow
S3 operation handlers parse XML into `RGWObjTagging_S3`, call `rebuild()` to produce `RGWObjTags`, then persist those tags through normal object metadata paths.

## State and Persistence Behavior
These classes are transient XML request/response models. Persistence is delegated to `RGWObjTags`.

## Dependencies and Integration Points
Includes Formatter, expat, RGW XML helpers, and core tags. It is part of S3 REST tagging support.

## Risks
Inheritance exposes core tag mutation methods on the S3 set. The header does not itself enforce S3 tag limits until implementation rebuild.

## Test Signals
Compile coverage for XML decoder overloads, rebuild validation, and S3 operation integration with malformed XML.
