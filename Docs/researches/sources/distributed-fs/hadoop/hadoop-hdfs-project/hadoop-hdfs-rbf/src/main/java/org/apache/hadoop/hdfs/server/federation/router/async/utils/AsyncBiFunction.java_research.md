# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/utils/AsyncBiFunction.java

## Purpose
`AsyncBiFunction` is the two-argument asynchronous function abstraction used by async foreach workflows.

## Important APIs, Types, And Functions
The functional method is `void applyAsync(T t, P p) throws IOException`. The default `async(T, P)` invokes it and returns the current thread-local future.

## Control Flow
Callers pass contextual state and one input element. Implementations start async work and set `CUR_COMPLETABLE_FUTURE`; the default method returns that future for chaining.

## State, Persistence, And Dependencies
No direct state or persistence exists. The interface depends on the `Async` thread-local future contract.

## Integration Points
`AsyncForEachRun` uses this interface to process each iterator element with access to the loop controller, enabling `breakNow()` from inside async callbacks.

## Risks
The same missing-current-future risk applies. Because it passes mutable loop state, implementations must avoid retaining and using the controller after the loop has progressed unexpectedly.

## Test Signals
Tests should cover normal two-argument composition, IOException propagation, and interaction with `AsyncForEachRun.breakNow`.
