# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/async/utils/AsyncForEachRun.java

## Purpose
`AsyncForEachRun` implements sequential asynchronous iteration over an `Iterator`, with optional early break.

## Important APIs, Types, And Functions
Key methods are `run()`, private `doOnce(I)`, `breakNow()`, `forEach(Iterator<I>)`, and `asyncDo(AsyncBiFunction<AsyncForEachRun<I,R>, I, R>)`. It implements `AsyncRun<R>`.

## Control Flow
`run` completes immediately with null for an empty iterator. Otherwise it invokes `doOnce` on the first element and stores the returned future. `doOnce` calls the async function and then composes the next iteration after the current future completes, stopping when `breakNow` was called or the iterator is exhausted.

## State, Persistence, And Dependencies
The class stores the iterator, callback, and a boolean break flag. There is no persistence. It depends on `CompletableFuture` and the async utility interfaces.

## Integration Points
`AsyncUtil.asyncForEach` constructs this class. `RouterAsyncRpcClient` uses it for ordered NameNode failover and ordered remote-location invocation.

## Risks
Iteration is sequential, not parallel; naming can be misleading. The break flag is mutable and not synchronized, relying on callback ordering. Exceptions thrown while starting the first or later iteration are wrapped as completion exceptions.

## Test Signals
Tests should verify empty iterators, ordered execution, early break after a successful callback, exception propagation from first and later elements, and that later elements are not invoked after break.
