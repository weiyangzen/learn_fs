<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/CSEV1CompatibleS3AFileSystemOperations.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/CSEV1CompatibleS3AFileSystemOperations.java

## Purpose

`CSEV1CompatibleS3AFileSystemOperations` extends modern CSE behavior with compatibility for objects written by older client-side encryption clients.

## Important APIs, Types, and Functions

It overrides `getObject()`, `getUnencryptedS3ClientFactory()`, and `getS3ObjectSize()`.

## Control Flow

Before a GET, it checks `CSEUtils.isObjectEncrypted()`. Encrypted objects use the encrypted client path inherited from `CSES3AFileSystemOperations`; unencrypted objects use `store.getOrCreateUnencryptedS3Client()`. Object length is delegated to `CSEUtils.getUnencryptedObjectLength()`. The unencrypted client factory is the configured/default S3 client factory.

## State and Persistence Behavior

The class is stateless. It introduces extra HEAD calls and may choose between two client instances per request.

## Dependencies and Integration Points

It integrates with `S3AStore`, configured S3 client factories, `CSEUtils`, AWS GET/HEAD models, and compatibility settings for CSE V1 data.

## Risks and Edge Cases

Per-read encryption detection adds latency. Misclassified metadata can route reads through the wrong client. The unencrypted client factory must be available when V1 compatibility is enabled.

## Test Signals

Tests should cover encrypted and unencrypted object reads, unencrypted factory selection, length derivation through CSEUtils, metadata lookup failures, and dual-client lifecycle behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/CSEV1CompatibleS3AFileSystemOperations.java -->
