# sources/distributed-fs/ceph/src/rgw/rgw_bucket_encryption.cc

Purpose: implements XML and JSON formatting for S3 bucket default encryption configuration.

Important APIs/types/functions: `ApplyServerSideEncryptionByDefault::decode_xml/dump_xml()`, `ServerSideEncryptionConfiguration::decode_xml/dump_xml()`, and `RGWBucketEncryptionConfig::decode_xml/dump_xml/dump()`.

Control flow: XML decode reads `KMSMasterKeyID`, `SSEAlgorithm`, `ApplyServerSideEncryptionByDefault`, `BucketKeyEnabled`, and optional `Rule`. XML dump emits only configured fields: KMS key only when non-empty, bucket key only when true, and rule only when present. JSON dump writes `rule_exist` and rule fields when present.

State/persistence: no storage I/O; it transforms XML/JSON around buffer-encoded structures declared in the header. Bucket encryption policies are persisted as bucket attrs elsewhere.

Dependencies/integration: uses `rgw_xml.h` decoders and Ceph JSON encoding. REST bucket encryption handlers use these methods to parse and return S3-compatible configuration.

Risks: this layer does not validate algorithm names or KMS key semantics. Optional XML elements are accepted without policy checks. Empty KMS key is omitted on output, which must match API behavior.

Test signals: XML decode/dump for SSE-S3 and SSE-KMS, bucket key enabled/disabled, absent `Rule`, malformed XML, JSON dump of configured/unconfigured cases, and buffer round-trip from the header.
