<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/OffsetRange.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/OffsetRange.java

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/OffsetRange.java` models half-open byte offset ranges for NFS read/write coordination. The source was read as a complete 77-line file for this report.

## Important APIs, Types, and Functions

`OffsetRange` stores immutable `min` and `max`, validates `min >= 0`, `max >= 0`, and `min < max`, exposes package-private getters, overrides `hashCode`, `equals`, and `toString`, and provides `ReverseComparatorOnMin` ordering by descending min then descending max.

## Control Flow

Construction validates arguments with `Preconditions.checkArgument`. Comparisons and equality are deterministic value operations. Write-management classes use the comparator for pending-write range ordering.

## State and Persistence Behavior

Instances are immutable in-memory keys/ranges. Persistence of write data is handled elsewhere by `OpenFileCtx` and HDFS streams.

## Dependencies and Integration Points

It depends on Hadoop `Preconditions` and is used in write-path tests and pending write maps in the NFS gateway.

## Risks and Edge Cases

Single-point ranges such as `[5,5]` are rejected. The hash code is a simple cast of `min ^ max`, which is adequate for small maps but can collide. Package-private constructor/getters constrain use to the package.

## Test Signals

`TestOffsetRange`, `TestWrites`, and `TestOpenFileCtxCache` validate constructor guards, comparator ordering, equality, and use as pending-write keys.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/OffsetRange.java -->
