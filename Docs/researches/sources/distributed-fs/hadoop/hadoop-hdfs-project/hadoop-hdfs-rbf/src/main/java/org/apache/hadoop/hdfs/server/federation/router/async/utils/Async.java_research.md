# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/utils/Async.java

## Purpose
`Async` is the base interface for the router async utility DSL. It centralizes the thread-local current `CompletableFuture` and common completion-exception wrapping helpers.

## Important APIs, Types, And Functions
`CUR_COMPLETABLE_FUTURE` is a `ThreadLocal<CompletableFuture<Object>>`. Default methods include `setCurCompletableFuture`, `getCurCompletableFuture`, and blocking `result()`. Static helpers `unWarpCompletionException` and `warpCompletionException` normalize `CompletionException` wrapping.

## Control Flow
Implementations set the current future after starting async work. `result()` blocks on the thread-local future and unwraps `IOException` from `ExecutionException`, returning null on interruption.

## State, Persistence, And Dependencies
The sole state is thread-local, process-local future state. There is no external persistence. The interface depends on Java concurrency primitives and `IOException`.

## Integration Points
Every utility functional interface extends `Async`, and `AsyncUtil` manipulates the same thread-local. Router async RPC code relies on this implicit state to make Java method returns compatible with Hadoop IPC async responses.

## Risks
The misspelled `warp/unWarp` names are API details. Thread-local state can leak or be stale when reused threads do not overwrite it. `result()` returns null on interruption without restoring interrupt status. Assertions guard null futures, so production runs without assertions can fail later with null dereferences.

## Test Signals
Tests should verify future set/get isolation across threads, exception unwrapping, `IOException` propagation from `result()`, and cleanup/overwrite behavior on executor thread reuse.
