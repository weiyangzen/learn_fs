# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/utils/FinallyFunction.java

## Purpose
`FinallyFunction` provides cleanup/finalization behavior for async chains while preserving prior failures.

## Important APIs, Types, And Functions
It defines `R apply(R r) throws IOException` and a default `apply(CompletableFuture<R>)` that uses `handle`.

## Control Flow
The cleanup function runs for both normal and exceptional completion. If the original future had an exception, the default method rethrows that exception after cleanup. If cleanup itself throws `IOException`, that cleanup error becomes the completion exception.

## State, Persistence, And Dependencies
No state or persistence exists. The interface depends on `CompletableFuture` and `Async.warpCompletionException`.

## Integration Points
`AsyncUtil.asyncFinally` wraps this interface. `RouterAsyncRpcClient` uses it to release fairness permits and connection contexts.

## Risks
Cleanup exceptions can mask an original successful result and, depending on ordering, can also mask original failures. Cleanup receives null when the prior stage failed, so implementations must tolerate null inputs.

## Test Signals
Tests should verify cleanup on success, cleanup on failure, original exception preservation, cleanup exception behavior, and resource-release usage in RPC failure paths.
