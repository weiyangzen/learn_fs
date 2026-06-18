# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AEncryptionDSSEKMSUserDefinedKey.java

Purpose: Concrete `AbstractTestS3AEncryption` subclass for DSSE-KMS with a user-defined KMS key from test configuration.

Important APIs/types/functions: `S3AUtils.getS3EncryptionKey()`, `S3ATestUtils.skipIfEncryptionNotSet()`, `S3ATestUtils.getTestBucketName()`, `Constants.S3_ENCRYPTION_KEY`, and `S3AEncryptionMethods.DSSE_KMS`.

Control flow: `createConfiguration()` probes a fresh configuration for the bucket KMS key, skips/assumes if DSSE-KMS or key is unavailable, then delegates to the base configuration and injects the key. `getSSEAlgorithm()` selects `DSSE_KMS`; inherited base tests perform create/read/rename/encryption assertions.

State and persistence: inherited encryption tests write encrypted objects to S3. No extra local state.

Dependencies and integration points: live AWS KMS key, bucket auth-keys configuration, S3A encryption secrets, and base encryption test framework.

Risks: missing or wrong KMS key skips or fails; KMS permissions and bucket region matter; the class has little direct logic and depends on inherited test coverage.

Test signals: confirms configured DSSE-KMS writes and base encryption operations work with an explicit key.
