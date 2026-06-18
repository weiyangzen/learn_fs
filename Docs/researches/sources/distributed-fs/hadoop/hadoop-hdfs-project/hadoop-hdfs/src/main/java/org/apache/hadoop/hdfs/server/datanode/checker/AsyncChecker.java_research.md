<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/checker/AsyncChecker.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/checker/AsyncChecker.java

## Purpose

`AsyncChecker` is the generic interface for scheduling asynchronous health checks against `Checkable` targets. It abstracts throttled disk/storage checks behind a `ListenableFuture` contract.

## Important APIs, Types, And Functions

- `schedule(Checkable<K,V> target, K context)` returns `Optional<ListenableFuture<V>>`; empty means the check was not scheduled.
- `shutdownAndWait(long, TimeUnit)` cancels executing checks and waits for termination.
- Generic type `K` is check context; `V` is result type.

## Control Flow

Implementations decide whether a check can be scheduled, often based on in-progress checks or minimum gap since the last check. Callers attach callbacks or wait on the future only when the optional is present.

## State And Persistence

The interface owns no state. Implementations such as `ThrottledAsyncChecker` maintain in-progress and completed-check caches plus executor services.

## Dependencies And Integration Points

It is used by `DatasetVolumeChecker` and `StorageLocationChecker` to decouple health-check orchestration from the specific resource being probed. It uses Guava-compatible `ListenableFuture` and Java executor shutdown semantics.

## Risks And Edge Cases

Callers must treat an empty optional as skipped rather than success or failure. Shutdown can interrupt checks that may be blocked in filesystem or disk operations.

## Test Signals

Tests should cover scheduling success, skipped scheduling, future completion, callback behavior, and shutdown interruption through concrete implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/checker/AsyncChecker.java -->
