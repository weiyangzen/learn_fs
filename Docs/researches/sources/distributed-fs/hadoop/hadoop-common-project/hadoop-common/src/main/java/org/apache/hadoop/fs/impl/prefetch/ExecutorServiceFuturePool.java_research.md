<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/ExecutorServiceFuturePool.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/ExecutorServiceFuturePool.java

## Purpose
Adapts a Java `ExecutorService` to the minimal future-pool API needed by the prefetch layer, avoiding a dependency on Twitter/Scala future pools.

## Important APIs, Types, And Functions
`executeFunction(Supplier<Void>)` submits supplier work, `executeRunnable(Runnable)` submits runnable work and casts the returned future, `shutdown(Logger, timeout, unit)` delegates to `HadoopExecutors.shutdown`, and `toString` exposes executor identity.

## Control Flow
Calls are direct pass-throughs to the wrapped executor. Supplier tasks run through `f::get`; runnable tasks run through `r::run`.

## State And Persistence
The only state is the wrapped `ExecutorService`. Task completion and cancellation semantics are those of the executor and returned `Future`.

## Dependencies And Integration Points
Used by `CachingBlockManager` for prefetch and cache-put tasks. Depends on Java concurrency APIs and Hadoop executor shutdown utilities.

## Risks
The class does not add cancellation beyond standard `Future.cancel`; comments note started work cannot really be cancelled by this abstraction. `executeRunnable` uses an unchecked cast from `Future<?>` to `Future<Void>`. Rejected execution and null task failures propagate from the underlying executor.

## Test Signals
Use direct executors or small thread pools to verify supplier/runnable execution, exception propagation through futures, shutdown timeout behavior, and rejected execution behavior after shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/impl/prefetch/ExecutorServiceFuturePool.java -->
