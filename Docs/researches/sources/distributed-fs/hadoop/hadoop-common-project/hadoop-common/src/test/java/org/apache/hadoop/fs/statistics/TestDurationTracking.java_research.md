# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/statistics/TestDurationTracking.java

Purpose: Tests duration tracking in `IOStatisticsStore` and `IOStatisticsBinding` wrappers for try-with-resources, callables, functions, IOE-raising operations, Java functions, asynchronous evaluation, failures, unknown statistics, and stub tracker lifecycle.

Important APIs/types/functions: `IOStatisticsStore.trackDuration`, `DurationTracker`, `DurationStatisticSummary.fetchSuccessSummary/fetchDurationSummary`, `trackFunctionDuration`, `trackJavaFunctionDuration`, `trackDurationOfCallable`, `trackDurationOfInvocation`, `trackDuration`, `trackDurationOfOperation`, `FutureIO.eval/awaitFuture`, `STUB_DURATION_TRACKER_FACTORY`, helper `sleepf`, `assertSummaryValues`, and `assertSummaryMean`.

Control flow: `setup` builds a store with duration tracking for `requests`. Success tests track sleep operations and assert counters, min/max summaries, and mean sample counts. Failure tests wrap operations that throw arithmetic, runtime, IO, or file-not-found exceptions, intercept them, and verify success summaries mark missing success durations while failure summaries are updated. Unknown-stat tests verify safe no-op-like summaries. Stub tests verify a supplied tracker factory can be used and its returned tracker tolerates `failed` and repeated `close`.

State/persistence: Per-test `IOStatisticsStore` plus an `AtomicInteger` invocation counter. Sleep calls introduce time-dependent values but assertions use lower bounds. Teardown logs final stats.

Dependencies/integration: Integrates statistics store duration counters/min/max/mean, functional wrappers in `IOStatisticsBinding`, Hadoop `FutureIO`, and test exception interception.

Risks: Uses real `Thread.sleep`, so tests consume wall time and can be noisy on very slow systems; lower-bound assertions reduce flakiness. The summary assertions accept broad ranges and do not validate exact milliseconds.

Test signals: Counter values, success/failure duration summaries, mean samples, invocation count, propagated exception classes/messages, and stub tracker lifecycle tolerance.
