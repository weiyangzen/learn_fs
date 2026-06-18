<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/checker/Checkable.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/checker/Checkable.java

## Purpose

`Checkable` is the generic interface for resources whose health can be probed. DataNode storage locations and volumes implement it so health-check orchestration can be shared.

## Important APIs, Types, And Functions

- `check(K context)` returns a result of type `V`.
- The context type is implementation-specific and may be null.
- The method may throw any `Exception`; an exception means the check failed.

## Control Flow

`AsyncChecker` implementations call `check` in executor threads, then convert returned results or thrown exceptions into futures and callbacks. Concrete checkables perform the actual disk, permission, or volume checks.

## State And Persistence

The interface owns no state. Implementations may inspect or mutate resource state, such as creating/checking directories or probing volumes.

## Dependencies And Integration Points

It is the common contract between `StorageLocation`, `FsVolumeSpi`, `ThrottledAsyncChecker`, `StorageLocationChecker`, and `DatasetVolumeChecker`.

## Risks And Edge Cases

The method may hang indefinitely depending on the target resource, so callers need asynchronous execution and timeouts. Broad `Exception` typing requires caller-side classification.

## Test Signals

Tests should verify concrete implementations return expected `VolumeCheckResult` values, throw on failed probes, and behave correctly when run asynchronously or timed out.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/checker/Checkable.java -->
