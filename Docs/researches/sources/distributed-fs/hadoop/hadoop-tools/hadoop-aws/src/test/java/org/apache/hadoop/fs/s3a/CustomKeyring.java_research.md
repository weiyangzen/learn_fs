# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/CustomKeyring.java

Purpose: test-only AWS S3 encryption client `Keyring` implementation for custom client-side encryption tests.

Important APIs/types/functions: implements `software.amazon.encryption.s3.materials.Keyring`. Constructor builds a `KmsClient` using configured CSE KMS region and temporary AWS credentials, then builds a `KmsKeyring` with the S3 encryption key. `onEncrypt()` and `onDecrypt()` delegate to the wrapped KMS keyring.

Control flow: construction resolves bucket name from config, creates KMS client, creates KMS keyring, then all encrypt/decrypt calls are direct delegation.

State and persistence: holds `KmsClient`, `Configuration`, and `KmsKeyring` fields; no explicit close method.

Dependencies and integration: AWS encryption SDK S3 materials, AWS KMS SDK, S3A temporary credentials provider, and encryption-key configuration.

Risks: `KmsClient` lifecycle is not closed here. Tests require valid KMS permissions and region/key configuration.

Test signals: used by `ITestS3AClientSideEncryptionCustom` to validate custom keyring wiring.
