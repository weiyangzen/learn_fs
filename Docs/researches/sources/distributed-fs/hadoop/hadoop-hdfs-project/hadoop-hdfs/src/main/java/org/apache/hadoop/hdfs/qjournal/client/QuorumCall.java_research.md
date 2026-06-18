<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/client/QuorumCall.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/client/QuorumCall.java

Purpose: Tracks a set of asynchronous calls and waits until response, success, or failure thresholds are reached.

Important APIs/types/functions: `create`, `waitFor`, `cancelCalls`, `countResponses`, `countSuccesses`, `countExceptions`, `getResults`, `rethrowException`, `mapToString`, and internal pause detection via `StopWatch`/`Timer`.

Control flow: Factory registers direct-executor callbacks on every future; callbacks synchronize, store success or exception by key, and notify waiters. `waitFor` loops until response thresholds are met, periodically logs progress, detects possible process pauses and extends the deadline, and throws `TimeoutException` only after adjusted time expires.

State and persistence behavior: Keeps in-memory maps of successes and exceptions plus all futures for cancellation. Result maps are copied when returned, but the underlying call can still receive late completions.

Dependencies/integration: Used by `AsyncLoggerSet` and `QuorumJournalManager` for quorum RPCs. Exception messages include `RemoteException` assertion handling when Java assertions are enabled.

Risks: Direct callbacks execute on completing threads, so expensive callback work would be harmful; current callbacks are small. Timeout extension is heuristic and can mask long pauses. `maxExceptions` semantics return when count is greater than the threshold, matching majority-failure use but requiring care for callers.

Test signals: Tests should cover all wait exit conditions, late completion after return, cancellation, timeout logging thresholds, pause-based timeout increase with fake `Timer`, assertion-error rethrow, and `mapToString` protobuf formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/client/QuorumCall.java -->
