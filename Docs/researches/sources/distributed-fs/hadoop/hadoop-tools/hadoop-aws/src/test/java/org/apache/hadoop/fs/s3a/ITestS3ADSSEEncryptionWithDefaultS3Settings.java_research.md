# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3ADSSEEncryptionWithDefaultS3Settings.java

Purpose: Tests bucket-default DSSE-KMS encryption behavior where S3 bucket settings, not explicit S3A write settings, encrypt objects. It extends `AbstractTestS3AEncryption` but intentionally returns `S3AEncryptionMethods.NONE` to avoid overriding bucket defaults.

Important APIs/types/functions: `patchConfigurationEncryptionSettings()`, `assertEncrypted()`, `skipIfBucketNotKmsEncrypted()`, `EncryptionTestUtils.assertEncrypted()`, `EncryptionSecrets`, `ContractTestUtils.writeDataset()`, and `FileSystem.newInstance()` with `DSSE_KMS`.

Control flow: setup skips unless encryption is configured. The normal base-class propagation and direct encryption tests are disabled because the focus is existing bucket defaults. Rename tests first touch a probe object to confirm the bucket reports `aws:kms:dsse`; then files written under default settings are renamed through a DSSE-KMS-configured filesystem and verified for content and encryption metadata.

State and persistence: creates probe objects, data files, and target directories in S3, deleting probes in `finally`. Uses a second filesystem instance for rename behavior under explicit DSSE-KMS.

Dependencies and integration points: live bucket default encryption, configured KMS key in test configuration, S3 object metadata, S3A encryption-secret propagation, and copy/rename semantics.

Risks: highly environment-dependent; disabled inherited tests reduce generic signal; bucket default encryption must match the configured KMS key or assertions skip/fail; rename changes encryption via copy operation.

Test signals: verifies S3A can work with DSSE-KMS bucket defaults and that rename through an explicitly encrypted filesystem produces objects with the expected DSSE-KMS key.
