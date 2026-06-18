# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/utils/CatchFunction.java

## Purpose
`CatchFunction` adapts synchronous exception recovery to `CompletableFuture` chains.

## Important APIs, Types, And Functions
It defines `R apply(R r, E e) throws IOException` and default `CompletableFuture<R> apply(CompletableFuture<R>, Class<E>)`.

## Control Flow
The default method calls `CompletableFuture.handle`. Normal completion returns the result. Exceptional completion is unwrapped and matched against the requested class. Matching exceptions invoke recovery; nonmatching exceptions are rewrapped and propagated.

## State, Persistence, And Dependencies
The interface has no state or persistence. It depends on `Async` exception helpers and Java futures.

## Integration Points
`AsyncUtil.asyncCatch` uses this interface for synchronous recovery logic. It is the parent of `AsyncCatchFunction`.

## Risks
Recovery only catches exceptions assignable to the specified class. A recovery `IOException` replaces the original failure. Non-IOException unchecked recovery failures propagate through future handling.

## Test Signals
Tests should cover normal pass-through, matching recovery, nonmatching propagation, checked recovery failure, and nested completion-exception unwrapping.
