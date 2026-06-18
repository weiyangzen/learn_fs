# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/utils/AsyncApplyFunction.java

## Purpose
`AsyncApplyFunction` adapts an asynchronous transformation into a composable `CompletableFuture` continuation.

## Important APIs, Types, And Functions
The functional method is `void applyAsync(T t) throws IOException`; implementations must set the current future. `apply(T)` starts async work and blocks via `result()`. `async(T)` starts work and returns the current future. Future overloads use `thenCompose` or `thenComposeAsync`.

## Control Flow
When chained to a completed input future, `async(t)` is called and the returned current future is flattened into the parent chain. Checked setup errors are wrapped as completion exceptions.

## State, Persistence, And Dependencies
No direct state exists; the contract relies on `Async.CUR_COMPLETABLE_FUTURE`. There is no persistence.

## Integration Points
`RouterAsyncRpcClient.invokeMethod` uses this form when a continuation itself initiates an async RPC. `AsyncUtil.asyncApplyUseExecutor` can dispatch it onto namespace executors.

## Risks
Implementations that forget to set the current future will trip assertions or produce null chains. The synchronous `apply` method can block if used in the wrong context. Thread-local current future must be set on the same thread that calls `async`.

## Test Signals
Tests should cover flattening behavior, executor use, missing-current-future failures, checked exceptions during initiation, and non-blocking composition with nested RPC calls.
