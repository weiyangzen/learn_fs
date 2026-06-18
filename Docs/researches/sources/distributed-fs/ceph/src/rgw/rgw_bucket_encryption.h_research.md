# sources/distributed-fs/ceph/src/rgw/rgw_bucket_encryption.h

Purpose: declares serialized S3 bucket default encryption configuration types.

Important APIs/types/functions: `ApplyServerSideEncryptionByDefault` stores `kmsMasterKeyID` and `sseAlgorithm`; `ServerSideEncryptionConfiguration` wraps default encryption and `bucketKeyEnabled`; `RGWBucketEncryptionConfig` wraps optional rule existence. Each exposes accessors, `encode()`, `decode()`, XML methods, and class encoders.

Control flow: `RGWBucketEncryptionConfig::encode()` persists `rule_exist` and conditionally persists `rule`; decode mirrors this. Nested classes encode/decode fields in fixed version-1 structures.

State/persistence: these are bucket-attribute payload types, serialized with Ceph buffer encoding and surfaced through XML/JSON.

Dependencies/integration: depends only on `include/types.h`, `include/encoding.h`, XML forward declaration, and formatter forward declaration. The low dependency surface makes it suitable as a metadata type.

Risks: no semantic validation in constructors or decode; invalid algorithm strings can be represented. `bucketKeyEnabled` defaults false, so omitted XML and explicit false are equivalent.

Test signals: buffer encode/decode of rule-present and no-rule cases, XML parsing for optional fields, API output for omitted KMS key and bucket key, and backward compatibility if future fields are added.
