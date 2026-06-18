# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/utils/AsyncUtil.java

## Purpose
`AsyncUtil` is the static helper facade for building router async workflows around the current thread-local `CompletableFuture`.

## Important APIs, Types, And Functions
Important methods include `asyncReturn`, `syncReturn`, `asyncComplete`, `asyncCompleteWith`, `asyncThrowException`, `asyncApply`, `asyncApplyUseExecutor`, `asyncTry`, `asyncCatch`, `asyncFinally`, `asyncForEach`, `asyncCurrent`, and `getCompletableFuture`. `asyncReturn` supplies placeholder Java return values: false for booleans, -1 for integer/long, and null otherwise.

## Control Flow
Async router methods call one method to seed or update `CUR_COMPLETABLE_FUTURE`, then chain transformations and catches. `asyncCurrent` starts an async operation for every collection element, waits for all futures with `CompletableFuture.allOf`, and invokes a supplied aggregator over the future array.

## State, Persistence, And Dependencies
All state is the shared `Async.CUR_COMPLETABLE_FUTURE` thread-local. There is no persistence. Dependencies are Java futures, executors, the utility functional interfaces, and completion-exception wrapping.

## Integration Points
Every async router protocol method uses this class to bridge normal Java method signatures to asynchronous Hadoop IPC handling. `RouterAsyncRpcClient` also exposes the current future to aggregate downstream RPCs.

## Risks
The global thread-local design is fragile around executor boundaries. `asyncReturn` placeholders are intentionally not real results and must only be used where the IPC layer reads the future. `syncReturn` casts and rethrows `ExecutionException` causes as `Exception`, which can fail if the cause is an `Error`. `asyncCurrent` calls the aggregator even when `allOf` sees an exception, so aggregator code must inspect futures carefully.

## Test Signals
Tests should cover every helper in normal and exceptional cases, placeholder return values for primitive-compatible signatures, executor-based apply, foreach behavior, `asyncCurrent` partial failures, and thread-local isolation under reused router executors.
