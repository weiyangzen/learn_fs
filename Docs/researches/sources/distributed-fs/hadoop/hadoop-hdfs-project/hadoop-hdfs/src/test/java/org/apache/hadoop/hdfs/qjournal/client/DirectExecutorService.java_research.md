# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/client/DirectExecutorService.java

Purpose: Minimal test-only `ExecutorService` that runs submitted work synchronously in the caller thread. QJM tests use it to remove scheduler nondeterminism from `IPCLoggerChannel`.

Important APIs/types/functions: `DirectExecutorService`, nested `DirectFuture<V>`, `submit(Callable<T>)`, `execute(Runnable)`, `shutdown()`, `isShutdown()`, `isTerminated()`, and unsupported executor operations.

Control flow: `submit(Callable)` rejects after shutdown, invokes the callable immediately, captures result or exception in `DirectFuture`, and returns an already-done `Future`. `Future.get()` wraps captured exceptions in `ExecutionException`. `execute(Runnable)` runs inline.

State and persistence behavior: Only synchronized `isShutdown` state exists. There is no pool, queue, cancellation, timeout scheduler, or persistence.

Dependencies and integration points: Implements enough JDK `ExecutorService` behavior for QJM test logger factories. It is commonly injected into spy `IPCLoggerChannel` instances for deterministic call ordering.

Risks: Most `ExecutorService` methods throw `UnsupportedOperationException`, and `execute()` does not reject after shutdown. It should remain test-only.

Test signals: Indirectly stabilizes QJM client tests by making futures complete synchronously and ordered.
