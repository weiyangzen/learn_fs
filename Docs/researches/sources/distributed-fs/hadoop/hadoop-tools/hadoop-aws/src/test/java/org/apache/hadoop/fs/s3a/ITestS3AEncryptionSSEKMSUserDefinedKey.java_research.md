# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AEncryptionSSEKMSUserDefinedKey.java

Purpose: Concrete base encryption test for SSE-KMS with an explicit user-defined key.

Important APIs/types/functions: `S3AUtils.getS3EncryptionKey()`, `S3ATestUtils.getTestBucketName()`, `Constants.S3_ENCRYPTION_ALGORITHM`, `Constants.S3_ENCRYPTION_KEY`, and `S3AEncryptionMethods.SSE_KMS`.

Control flow: `createConfiguration()` reads the configured KMS key and verifies the base test configuration says `SSE_KMS`; otherwise it skips. It then delegates to the base configuration and writes `S3_ENCRYPTION_KEY`. `getSSEAlgorithm()` returns `SSE_KMS` so inherited base tests do the actual encrypted operations.

State and persistence: inherited tests create encrypted S3 objects; no extra state.

Dependencies and integration points: auth-keys KMS configuration, S3A encryption option propagation, KMS permissions, and inherited encryption contract.

Risks: environment-gated; wrong algorithm or blank key skips; KMS policy/region mismatch can fail during live writes.

Test signals: verifies explicit SSE-KMS key use in the common base encryption scenarios.
