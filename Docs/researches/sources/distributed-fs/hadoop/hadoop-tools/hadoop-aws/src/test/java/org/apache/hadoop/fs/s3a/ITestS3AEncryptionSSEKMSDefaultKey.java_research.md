# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AEncryptionSSEKMSDefaultKey.java

Purpose: Tests SSE-KMS when S3/AWS uses the account/region default KMS key because no explicit key is provided.

Important APIs/types/functions: extends `AbstractTestS3AEncryption`, sets `Constants.S3_ENCRYPTION_KEY` to empty, returns `SSE_KMS`, uses `HeadObjectResponse`, `EncryptionTestUtils.AWS_KMS_SSE_ALGORITHM`, and `validateEncryptionFileAttributes()`.

Control flow: inherited encryption tests write/read encrypted objects. This class overrides `assertEncrypted()` to check server-side encryption is AWS KMS and that `ssekmsKeyId()` contains a KMS ARN rather than matching an exact configured key. The explicit file-attributes test writes data, verifies content, and validates encryption attributes with `Optional.empty()`.

State and persistence: writes S3 objects encrypted with the service/default key; no local state.

Dependencies and integration points: AWS default KMS behavior, S3 object metadata, and S3A file-attribute/xattr projection.

Risks: default key ARN format and availability are account/region dependent; exact key comparison is impossible by design; permissions to use default KMS key must exist.

Test signals: catches missing SSE-KMS headers and incorrect file-attribute reporting when no explicit KMS key is configured.
