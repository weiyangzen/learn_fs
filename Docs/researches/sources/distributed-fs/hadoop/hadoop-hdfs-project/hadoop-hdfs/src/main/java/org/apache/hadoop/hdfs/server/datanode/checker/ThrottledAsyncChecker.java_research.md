<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/checker/ThrottledAsyncChecker.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/checker/ThrottledAsyncChecker.java

## Purpose

`ThrottledAsyncChecker` is the main `AsyncChecker` implementation. It schedules `Checkable.check` calls on an executor, suppresses duplicate or too-frequent checks per target, optionally applies per-check timeouts, and caches recent results.

## Important APIs, Types, And Functions

- Constructor accepts a `Timer`, minimum milliseconds between checks, disk-check timeout, and executor.
- `schedule` rejects targets already in progress or checked too recently; otherwise it submits a callable and returns a `ListenableFuture`.
- Timeout support wraps the submitted future with `FluentFuture.withTimeout` using a scheduled executor.
- `addResultCachingCallback` removes in-progress entries and records success or failure completion time.
- `shutdownAndWait` interrupts scheduled and worker executors.

## Control Flow

Scheduling is synchronized. It first checks `checksInProgress`, then `completedChecks` and elapsed time since completion. A submitted task calls `target.check(context)`. Completion callbacks run in the direct executor and update the in-memory maps under lock.

## State And Persistence

State includes the timer, executor services, throttle interval, timeout, a map of in-progress futures, and a weak map of completed check results. Results are in-memory only and can disappear when target keys are garbage-collected.

## Dependencies And Integration Points

It is used by dataset and storage-location checkers. It depends on Hadoop `Timer`, Guava `ListenableFuture`/`FluentFuture`/callbacks, and Java executor services.

## Risks And Edge Cases

The map key type is raw `Checkable`, so equality semantics of targets control throttling. Timeout wrapping may leave underlying work running until interrupted by executor behavior. Empty optional means skipped, not healthy. Weak result caching can allow rechecks after target GC.

## Test Signals

Tests should cover duplicate suppression, minimum-gap suppression after success and failure, timeout behavior, callback cache updates, exception propagation, weak-cache behavior if relevant, and shutdown cancellation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/checker/ThrottledAsyncChecker.java -->
