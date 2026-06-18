# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/impl/TestFutureIO.java

## Purpose
`TestFutureIO` documents and validates which thread executes synchronous future-evaluation helpers compared with `CompletableFuture.supplyAsync()`.

## Important APIs, Types, And Functions
It uses a `ThreadLocal<AtomicInteger>` field, `setup()`, `testEvalInCurrentThread()`, `testEvalAsync()`, `getLocal()`, and `getLocalValue()`. The production API under test is `LambdaUtils.eval()`.

## Control Flow
`setup()` initializes the thread-local counter to 1. `testEvalInCurrentThread()` calls `LambdaUtils.eval()` with a completed future and a lambda that increments the thread-local; both local and returned values become 3, proving same-thread execution. `testEvalAsync()` uses `CompletableFuture.supplyAsync()`, leaving the caller thread local at 1 while the async task returns 3.

## State And Persistence
State is only per-test thread-local data. There is no persistent filesystem state.

## Dependencies And Integration Points
It depends on Java `CompletableFuture`, `AtomicInteger`, Hadoop `LambdaUtils`, and `HadoopTestBase`.

## Risks
Thread-affinity behavior matters for callers relying on thread-local context. If `LambdaUtils.eval()` becomes asynchronous, this test should fail.

## Test Signals
The signal is the contrast between caller-thread local value after `eval()` and after `supplyAsync()`.
