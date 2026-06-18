# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/utils/TestAsyncUtil.java

Purpose: parameterized tests for `AsyncUtil` semantics, comparing synchronous and asynchronous implementations of the same `BaseClass` operations.

Important APIs/types/functions: `ExecutionMode` parameter source, `BaseClass`, `SyncClass`, `AsyncClass`, `AsyncUtil.syncReturn`, `Async.CUR_COMPLETABLE_FUTURE`, `LambdaTestUtils`, `Time`, `Callable`, and JUnit assertions. `setUp(ExecutionMode)` selects the implementation, while `after()` clears async thread-local/current future state.

Control flow: tests cover basic `apply`, checked/runtime exception propagation, direct exception methods, chained apply, catch-then-apply recovery, catch/finally resource cleanup, async foreach, explicit foreach break, exception-driven foreach break, and concurrent/current aggregation. Helpers `checkResult` and `checkException` normalize sync versus async behavior by either using direct returns or `syncReturn` and exception interception.

State and persistence behavior: state is in thread-local async future context, worker threads, mutable resource lists, and simulated timing. No external persistence is used. Integration points are the async utility DSL and the paired reference/async implementations. Risks include timing-sensitive async completion, thread-local leakage between parameterized runs, and assertions tied to exact exception strings. Test signals are expected strings, expected exception classes/messages, cleared resources after finally, and false/non-null async future state after cleanup.
