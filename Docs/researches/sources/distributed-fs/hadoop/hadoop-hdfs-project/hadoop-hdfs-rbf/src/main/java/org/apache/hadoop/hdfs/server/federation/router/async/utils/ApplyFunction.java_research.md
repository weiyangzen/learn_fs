# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/utils/ApplyFunction.java

## Purpose
`ApplyFunction` adapts a synchronous, IOException-throwing transformation into a `CompletableFuture` continuation used by the router async DSL.

## Important APIs, Types, And Functions
The functional method is `R apply(T t) throws IOException`. Default overloads apply the function to a `CompletableFuture<T>` via `thenApply` or `thenApplyAsync` with an `Executor`, wrapping `IOException` with `Async.warpCompletionException`.

## Control Flow
When the input future completes normally, the supplied transformation runs and returns a new result. If it throws `IOException`, the future completes exceptionally with a `CompletionException`.

## State, Persistence, And Dependencies
The interface has no state. It depends on `CompletableFuture`, optional executors, and the shared exception wrapping helper.

## Integration Points
`AsyncUtil.asyncApply` and `asyncApplyUseExecutor` are the main callers. Async router modules use this interface for post-processing RPC results.

## Risks
Only `IOException` is explicitly caught; unchecked exceptions propagate through `CompletableFuture` naturally. Continuations without an executor run on the completing thread, so expensive transformations can delay IPC completion.

## Test Signals
Tests should cover normal mapping, checked exception wrapping, executor dispatch, and compatibility with `AsyncUtil.asyncReturn` chains.
