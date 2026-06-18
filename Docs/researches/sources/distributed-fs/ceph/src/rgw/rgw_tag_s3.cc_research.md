# sources/distributed-fs/ceph/src/rgw/rgw_tag_s3.cc

## Purpose
`rgw_tag_s3.cc` adapts core `RGWObjTags` to S3 XML Tagging request/response formats.

## Important APIs, Types, and Functions
`RGWObjTagEntry_S3::decode_xml()` reads mandatory `Key` and `Value`. `dump_xml()` emits them and rejects empty values. `RGWObjTagSet_S3::decode_xml()` reads all `Tag` entries and inserts them. `rebuild()` validates and copies parsed tags into a destination `RGWObjTags`. `RGWObjTagging_S3::decode_xml()` reads mandatory `TagSet`.

## Control Flow
XML decode builds an S3 tag set first, then `rebuild()` applies core RGW tag validation. XML dump iterates the stored tag map and emits one `Tag` object per entry.

## State and Persistence Behavior
No external state is persisted here. Parsed XML is converted into the durable `RGWObjTags` representation by callers.

## Dependencies and Integration Points
Depends on RGW XML decoder/encoder helpers, Formatter, and `rgw_tag.h`. Used by S3 PutObjectTagging/GetObjectTagging and related operations.

## Risks
Decode inserts tags without validation until `rebuild()` is called, so callers must not skip rebuild. Dump rejects empty value even though core RGW tags allow it. Duplicate keys follow multimap behavior.

## Test Signals
Cover mandatory field failures, empty key/value dump rejection, too many tags via rebuild, duplicate tags, XML round trip, and TagSet omission.
