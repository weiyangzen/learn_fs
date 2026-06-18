<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/EncryptionS3ClientFactory.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/EncryptionS3ClientFactory.java

## Purpose

`EncryptionS3ClientFactory` creates AWS S3 encryption clients for S3A client-side encryption and wraps underlying standard sync/async clients.

## Important APIs, Types, and Functions

It extends `DefaultS3ClientFactory`. Overridden methods are `createS3Client()` and `createS3AsyncClient()`. Helpers include encryption-client availability checks, `createS3EncryptionClient()`, `createS3AsyncEncryptionClient()`, `createKmsKeyring()`, `getKeyringProvider()`, and `getCustomKeyringProviderClass()`.

## Control Flow

Creation first verifies the encryption client class is on the classpath. Sync client creation initializes both wrapped sync and async clients, then builds an `S3EncryptionClient` with legacy unauthenticated/rapping modes enabled. KMS materials build a KMS client using credential, KMS region, S3 region, or endpoint fallback. Custom materials reflectively instantiate a `Keyring` class. Async encryption client creation wraps the previously initialized async client.

## State and Persistence Behavior

The factory stores wrapped sync and async clients in fields during creation. The encryption-client availability flag is cached in a lazy atomic reference. No persistent state is written.

## Dependencies and Integration Points

It depends on AWS Encryption SDK S3 classes, AWS KMS, S3A `S3ClientCreationParameters`, `CSEMaterials`, Hadoop reflection, and instantiation IO errors.

## Risks and Edge Cases

Async encrypted client creation requires `s3AsyncClient` to have been initialized, making call order important. Missing encryption classes fail with `InstantiationIOException.unavailable()`. Custom keyring reflection supports a test-specific constructor fallback and can hide original errors inside RuntimeException/IOException.

## Test Signals

Cover missing encryption client class, KMS keyring region and endpoint fallback, custom keyring success/failure, sync-before-async creation order, legacy mode flags, credential propagation, and close lifecycle through `ClientManagerImpl`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/EncryptionS3ClientFactory.java -->
