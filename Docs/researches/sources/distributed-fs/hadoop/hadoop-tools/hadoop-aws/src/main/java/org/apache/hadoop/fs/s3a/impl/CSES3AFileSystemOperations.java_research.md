<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/CSES3AFileSystemOperations.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/CSES3AFileSystemOperations.java

## Purpose

`CSES3AFileSystemOperations` implements S3A filesystem operation hooks when AWS client-side encryption is enabled with the modern encryption client.

## Important APIs, Types, and Functions

It overrides object read, CSE gauge setting, encryption material lookup, S3 client factory selection, unencrypted factory selection, and S3 object size calculation.

## Control Flow

Reads use the encrypted S3 client returned by `store.getOrCreateS3Client()`. The CSE gauge is set to 1. Materials are delegated to `CSEUtils`. The encrypted client factory is `EncryptionS3ClientFactory`. `getS3ObjectSize()` subtracts the fixed CSE padding length when the result remains non-negative.

## State and Persistence Behavior

The class is stateless. External effects are client selection, reads, and metric gauge mutation.

## Dependencies and Integration Points

It integrates with `S3AStore`, `EncryptionS3ClientFactory`, `CSEUtils`, AWS SDK responses, and S3A IO statistics.

## Risks and Edge Cases

Padding subtraction is a simple compatibility rule and can be wrong for objects not produced by the expected encryption mode. Returning null unencrypted factory is correct for non-V1 compatibility but must be handled by callers.

## Test Signals

Verify encrypted client factory selection, gauge value 1, material lookup for KMS/custom methods, object read routing, and size handling below/equal/above the padding length.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/CSES3AFileSystemOperations.java -->
