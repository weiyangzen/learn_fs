# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AClientSideEncryptionKms.java

Purpose: concrete CSE test suite for KMS-backed client-side encryption.

Important APIs/types/functions: extends `ITestS3AClientSideEncryption`; `maybeSkipTest()` requires encryption tests enabled and `CSE_KMS` configured. `assertEncrypted()` reads xAttrs and verifies key-wrap algorithm `kms+context` plus materials-description content algorithm `AES/GCM/NoPadding` while ensuring the KMS key ID is not exposed in the materials description.

Control flow: inherits common CSE tests and applies KMS-specific header checks after writes/renames.

State and persistence: same as parent; encrypted objects use configured KMS key.

Dependencies and integration: S3A CSE-KMS configuration, `S3AUtils.getS3EncryptionKey`, AWS encryption headers, and xAttr decoding.

Risks: requires KMS permissions and correctly configured encryption key. Header expectations can change with encryption SDK versions.

Test signals: inherited CSE integration coverage with KMS-specific header/materials assertions.
