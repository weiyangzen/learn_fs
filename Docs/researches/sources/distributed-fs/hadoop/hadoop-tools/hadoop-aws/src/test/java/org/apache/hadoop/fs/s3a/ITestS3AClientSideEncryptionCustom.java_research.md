# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AClientSideEncryptionCustom.java

Purpose: concrete CSE test suite for custom keyring encryption.

Important APIs/types/functions: extends `ITestS3AClientSideEncryption`; `createConfiguration()` disables FS caching and sets `S3_ENCRYPTION_CSE_CUSTOM_KEYRING_CLASS_NAME` to `CustomKeyring`. `maybeSkipTest()` requires encryption tests enabled and `CSE_CUSTOM` configured. `assertEncrypted()` inspects xAttrs for crypto key-wrap algorithm `kms+context`.

Control flow: inherits all CSE tests and validates encryption by decoding `header.x-amz-cek-alg` style xAttrs through `HeaderProcessing`.

State and persistence: same as parent; uses custom KMS keyring for encrypted writes.

Dependencies and integration: `CustomKeyring`, S3A CSE custom keyring config, AWS encryption headers, and xAttr decoding.

Risks: requires KMS permissions and correct custom keyring configuration. Encryption assertion only checks key-wrap algorithm, not every header.

Test signals: inherited CSE integration coverage with custom keyring-specific header validation.
