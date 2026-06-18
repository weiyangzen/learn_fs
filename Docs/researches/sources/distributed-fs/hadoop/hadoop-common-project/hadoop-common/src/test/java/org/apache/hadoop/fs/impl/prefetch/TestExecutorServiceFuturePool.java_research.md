# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/impl/prefetch/TestExecutorServiceFuturePool.java

## Purpose
Tests `ExecutorServiceFuturePool`, the prefetch package adapter that submits runnable and supplier-style work to a Java `ExecutorService` and returns `Future<Void>` handles. The file verifies both successful task execution and exception propagation through returned futures.

## Important APIs, Types, and Functions
The test class extends `AbstractHadoopTestBase` and uses JUnit 5 lifecycle methods. `setUp()` creates a fixed thread pool of size 3 with `Executors.newFixedThreadPool(3)`, and `tearDown()` always calls `shutdownNow()` to stop worker threads. Test methods instantiate `ExecutorServiceFuturePool` and exercise `executeRunnable(Runnable)` and `executeFunction(Supplier<T>)`. Success tests use an `AtomicBoolean` as the observable side effect and `Future.get(30, TimeUnit.SECONDS)` as the synchronization point. Failure tests use `LambdaTestUtils.interceptFuture` to assert that an `IllegalStateException` with message `deliberate` emerges from the asynchronous future.

## Control Flow
Each test builds a fresh pool wrapper over the shared executor. Success flows submit a closure, wait up to 30 seconds, then assert that the closure ran. Failure flows submit a closure that throws and then delegate to `interceptFuture`, which unwraps future completion failures and checks type/message. There is no retry or pooling logic in the test itself; it is focused on delegation semantics.

## State and Persistence
The only persistent-in-test state is `executorService`; it is recreated for every test and shut down after each test. `AtomicBoolean` instances are local and used only to detect task execution. No filesystem or external state is touched.

## Dependencies and Integration Points
The test integrates with Java concurrency primitives, JUnit 5, Hadoop test helpers, and the production `ExecutorServiceFuturePool`. It is a direct unit test of the prefetch executor abstraction used by asynchronous prefetch code.

## Risks and Edge Cases
The 30 second timeout prevents deadlocked futures from hanging the suite indefinitely. The tests cover both runnable and function entry points but do not validate cancellation, executor rejection, shutdown behavior, or thread naming. They also assume exception type/message are preserved through future wrapping.

## Test Signals
Passing tests signal that submitted work actually executes, returned futures complete, and failures remain inspectable to callers. They give regression coverage for asynchronous error propagation in prefetch infrastructure.
