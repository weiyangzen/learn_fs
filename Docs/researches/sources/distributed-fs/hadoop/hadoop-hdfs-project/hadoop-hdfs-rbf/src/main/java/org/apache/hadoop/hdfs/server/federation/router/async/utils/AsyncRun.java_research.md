# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/utils/AsyncRun.java

## Purpose
`AsyncRun` is the zero-input async task abstraction used by `AsyncUtil.asyncTry` and custom async runners.

## Important APIs, Types, And Functions
It defines `void run() throws IOException` and default `CompletableFuture<R> async()`, which runs the task and returns the current thread-local future.

## Control Flow
Implementations run setup logic and must set `CUR_COMPLETABLE_FUTURE`. The default `async` method returns that future to callers for composition.

## State, Persistence, And Dependencies
No local state exists. It depends on the `Async` thread-local future contract.

## Integration Points
`AsyncUtil.asyncTry` calls `async()` and records the resulting future. `AsyncForEachRun` implements this interface to make foreach loops composable.

## Risks
The interface does not enforce future completion; incorrect implementations fail at runtime. The `run` name may be confused with synchronous `Runnable` behavior despite the future contract.

## Test Signals
Tests should cover successful future setup, IOException during run, missing future assertions, and chaining through `asyncTry`.
