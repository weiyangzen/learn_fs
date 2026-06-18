# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AEncryptionSSEKMSWithEncryptionContext.java

Purpose: Tests KMS encryption with an S3/KMS encryption context for either SSE-KMS or DSSE-KMS. Since S3 HEAD does not reveal the encryption context, the test relies on KMS/IAM policy setup to make missing/wrong context observable.

Important APIs/types/functions: `S3AEncryption.getS3EncryptionContext()`, `S3AUtils.getEncryptionAlgorithm()`, `S3AUtils.getS3EncryptionKey()`, `Constants.S3_ENCRYPTION_CONTEXT`, `Constants.S3_ENCRYPTION_KEY`, and `ImmutableSet` of `SSE_KMS`/`DSSE_KMS`.

Control flow: configuration reads bucket-specific key, context, and algorithm; assumes the algorithm is KMS-based; skips if context is blank; removes overrides; sets key and context in the base configuration. `getSSEAlgorithm()` returns the discovered algorithm so inherited encryption tests execute with the selected KMS method.

State and persistence: inherited encrypted objects in S3; no local state. The `encryptionAlgorithm` field is set during configuration creation.

Dependencies and integration points: KMS encryption-context policy, S3A request header construction, bucket-specific encryption configuration, and base encryption tests.

Risks: correctness is only fully observable when external KMS policy denies decrypt without the expected context; otherwise it mainly verifies request construction does not fail. Field initialization depends on `createConfiguration()` running before `getSSEAlgorithm()` use.

Test signals: provides environment-gated coverage that encryption context is passed through for KMS-backed S3A writes and reads.
