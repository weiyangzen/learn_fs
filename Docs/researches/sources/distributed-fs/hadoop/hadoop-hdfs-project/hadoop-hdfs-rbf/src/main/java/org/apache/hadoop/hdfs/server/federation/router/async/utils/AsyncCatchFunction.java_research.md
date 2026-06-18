# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/utils/AsyncCatchFunction.java

## Purpose
`AsyncCatchFunction` is the asynchronous exception-handler counterpart to `CatchFunction`, allowing recovery logic to initiate new async work.

## Important APIs, Types, And Functions
It defines `void applyAsync(R r, E e) throws IOException`, synchronous `apply`, `async(R, E)`, and an override of `apply(CompletableFuture<R>, Class<E>)` that uses `handle` and `thenCompose` to flatten a recovery future.

## Control Flow
If the input future completes normally, the implementation returns the original future. If the unwrapped exception matches the requested class, it calls async recovery and composes its future. Nonmatching exceptions are rewrapped and propagated.

## State, Persistence, And Dependencies
The interface holds no state and relies on the thread-local future set by recovery implementations. It depends on completion-exception unwrapping/wrapping.

## Integration Points
`AsyncUtil.asyncCatch` accepts both sync and async catch functions. `RouterAsyncRpcClient.invoke` uses an async catch around reflected IPC calls so exception handling can continue through inherited async failover logic.

## Risks
Returning the original input future on normal completion means the generic handle stage temporarily has nested futures; the final `thenCompose` is critical. Recovery code must set the current future. Catch matching uses the unwrapped exception, but nonmatching propagation wraps the original wrapper, which can deepen nesting.

## Test Signals
Tests should cover matching and nonmatching exception types, async recovery success, async recovery failure, normal completion pass-through, and nested `CompletionException` unwrapping.
