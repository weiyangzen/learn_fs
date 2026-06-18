<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/BaseS3AFileSystemOperations.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/BaseS3AFileSystemOperations.java

## Purpose

`BaseS3AFileSystemOperations` implements `S3AFileSystemOperations` for normal, non-client-side-encrypted S3A filesystems.

## Important APIs, Types, and Functions

It implements `getObject()`, `setCSEGauge()`, `getClientSideEncryptionMaterials()`, `getS3ClientFactory()`, `getUnencryptedS3ClientFactory()`, and `getS3ObjectSize()`.

## Control Flow

Reads go through `store.getOrCreateS3Client().getObject(request)`. The CSE gauge is set to 0. Client factory selection reads `fs.s3a.s3.client.factory.impl` with the default factory fallback and instantiates it through `ReflectionUtils`. Object size is returned unchanged.

## State and Persistence Behavior

The class holds no state. All behavior is derived from method arguments and Hadoop configuration.

## Dependencies and Integration Points

It integrates with `S3AStore`, `RequestFactory`, AWS SDK `GetObjectRequest`, `HeadObjectResponse`, `S3ClientFactory`, and filesystem IO statistics gauges.

## Risks and Edge Cases

Returning null CSE materials and null unencrypted factory is part of the non-CSE contract; callers must branch on operation implementation rather than dereference blindly. Factory reflection can surface configuration class errors.

## Test Signals

Tests should verify plain client usage, gauge value 0, configured factory instantiation, null CSE materials, null unencrypted factory, and unchanged object length.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/BaseS3AFileSystemOperations.java -->
