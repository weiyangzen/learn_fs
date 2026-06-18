# sources/distributed-fs/ceph/src/rgw/rgw_public_access.cc

## Purpose
`rgw_public_access.cc` implements XML serialization, stream output, and union logic for S3 Public Access Block configuration.

## Important APIs, Types, And Functions
`PublicAccessBlockConfiguration::decode_xml()` reads `BlockPublicAcls`, `IgnorePublicAcls`, `BlockPublicPolicy`, and `RestrictPublicBuckets`. `dump_xml()` emits the same under `PublicAccessBlockConfiguration`. `operator<<` prints a human-readable boolalpha form. `config_union()` combines two configs by memberwise logical OR.

## Control Flow
The file is straightforward: decode from XML into bools, dump bools for response XML, or union account-level and bucket-level settings so any enabled restriction remains enabled.

## State And Persistence
The functions operate on the serializable configuration struct. Persistence is via the struct's buffer encoding in the header and bucket/account attrs handled elsewhere.

## Dependencies And Integration Points
It depends on `rgw_xml.h` and Ceph `Formatter`. `RGWPut/Get/DeleteBucketPublicAccessBlock` in `rgw_op.h` use this type, and public policy-status logic can combine account and bucket settings with `config_union()`.

## Risks And Test Signals
Risks include XML name mismatches with S3 clients, bool formatting expectations, and a minor stream-output formatting omission before two field values. Tests should cover XML decode/dump round trips, union truth table, buffer encode/decode from the header, and S3 API compatibility.
