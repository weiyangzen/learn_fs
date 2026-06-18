<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ChecksumSupport.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ChecksumSupport.java

## Purpose

`ChecksumSupport` parses S3A checksum algorithm configuration and limits it to algorithms supported by the connector.

## Important APIs, Types, and Functions

Constants define configuration strings `NONE`, `CRC32C`, and `CRC64NVME`. `getChecksumAlgorithm(Configuration)` returns an AWS SDK `ChecksumAlgorithm` or null.

## Control Flow

The helper reads `fs.s3a.create.checksum.algorithm`, returns null for unset or `NONE`, converts the string to an AWS enum value, and rejects unsupported values with an argument check.

## State and Persistence Behavior

The class is stateless. The supported algorithm set is a static immutable set.

## Dependencies and Integration Points

It depends on Hadoop configuration, S3A constants, Guava immutable sets, AWS SDK checksum enums, and `Preconditions`.

## Risks and Edge Cases

String parsing is case-sensitive to AWS enum conversion. Unsupported algorithms fail early, which is preferable to creating requests S3A cannot reason about. Null return means no checksum selection.

## Test Signals

Test unset, `NONE`, supported CRC32C/CRC64NVME values, invalid enum strings, valid AWS enum values that are intentionally unsupported, and request-building integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/ChecksumSupport.java -->
