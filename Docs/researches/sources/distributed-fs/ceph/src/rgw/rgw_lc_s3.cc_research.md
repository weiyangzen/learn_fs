# sources/distributed-fs/ceph/src/rgw/rgw_lc_s3.cc

Purpose: Implements S3 XML parsing and rendering for RGW lifecycle configuration, converting between S3 XML elements and the internal lifecycle model in `rgw_lc.h`.

Important APIs and functions: `LCExpiration_S3::decode_xml()/dump_xml()`, `LCNoncurExpiration_S3`, `LCMPExpiration_S3`, `LCFilter_S3`, `LCTransition_S3`, `LCNoncurTransition_S3`, `LCRule_S3`, and `RGWLifecycleConfiguration_S3` provide S3-specific XML behavior. `check_date()` validates ISO-8601 lifecycle dates are day-aligned.

Control flow: `RGWLifecycleConfiguration_S3::decode_xml()` decodes all `Rule` entries, auto-generates a random lowercase id for missing ids, and enforces `rgw_lc_max_rules`. `LCRule_S3::decode_xml()` requires valid status, accepts either modern `Filter` or legacy top-level `Prefix`, parses expiration/noncurrent/multipart expiration and transitions, rejects rules with no action, and inserts transition actions by storage class. `rebuild()` revalidates parsed S3 rules into a generic `RGWLifecycleConfiguration`.

State and persistence: This file does not persist directly; it prepares lifecycle objects that later encode into bucket attrs. It preserves S3-specific details such as `ExpiredObjectDeleteMarker`, `NewerNoncurrentVersions`, `ObjectSizeGreaterThan`, `ObjectSizeLessThan`, and the Ceph extension `ArchiveZone`.

Dependencies and integration points: Depends on RGW XML decoder/formatter, S3 tag XML support, Ceph time parsing, random id generation from the Ceph context, and the lifecycle execution data model. Operation handlers use it when handling S3 lifecycle configuration APIs.

Risks: XML compatibility is delicate because old clients may omit `Filter` and use top-level `Prefix`. Size bounds are stored as strings and compared lexically in the current code path (`size_lt <= size_gt`), which is a risk for numeric correctness unless constrained elsewhere. `ExpiredObjectDeleteMarker` only accepts the literal string `"true"` as enabling.

Test signals: Tests should cover malformed dates, multiple expiration choices, missing status/storage class, empty filters, prefix/tag/size/ArchiveZone filters, legacy prefix compatibility, max rule enforcement, duplicate transition storage classes, dump/decode round trips, and S3 error mapping for invalid XML.
