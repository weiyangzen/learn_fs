<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFSNamesystemLock.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFSNamesystemLock.java

Purpose: `TestFSNamesystemLock` validates the NameNode namesystem read/write lock wrapper: fairness configuration, reentrant compatibility counters, queued waiter counts, long-held lock logging and suppression, stack-trace attribution for read locks, and detailed hold-time metrics.

Important APIs, types, and functions: it targets `FSNamesystemLock`, `DFS_NAMENODE_FSLOCK_FAIR_KEY`, read/write reporting threshold keys, `DFS_LOCK_SUPPRESS_WARNING_INTERVAL_KEY`, `DFS_NAMENODE_LOCK_DETAILED_METRICS_KEY`, `FakeTimer`, `GenericTestUtils.LogCapturer`, `SubjectInheritingThread`, `MetricsRegistry`, `MutableRatesWithAggregation`, and metrics assertions `assertGauge`/`assertCounter`.

Control flow: fairness and compatibility tests directly acquire/release locks and inspect hold counts. Waiter-count testing holds the write lock, starts three reader tasks, and waits until `getQueueLength` equals the blocked thread count. Long-write and long-read tests advance a `FakeTimer` across configured thresholds, clear captured logs, unlock, and assert whether the method name, start date, interval text, and suppression count appear. Read-lock tests also run separate threads to ensure the longest held read lock's stack trace is reported and a shorter concurrent reader is not blamed. Metrics tests unlock with operation names and validate per-operation plus overall nanosecond averages and operation counts.

State and persistence behavior: no persistence; all state is lock-local counters, reentrant hold tracking, suppression timestamps, log buffers, and metrics accumulators. `FakeTimer` makes threshold behavior deterministic without real sleeps.

Dependencies and integration points: integrates with FSNamesystem logging, Hadoop metrics2 rates aggregation, DFS lock configuration keys, thread scheduling, and the lock's operation-name API (`readUnlock("foo")`, `writeUnlock("baz", false)`, suppression variant).

Risks and edge cases: logging assertions depend on message structure and stack trace depth. Concurrent tests can be sensitive to thread scheduling, though latches and `FakeTimer` reduce timing risk. The waiter test starts threads that block on a held write lock and does not explicitly release/stop them in the visible flow, relying on process/test lifecycle behavior after assertion.

Test signals: fairness flag on the underlying lock, read/write hold counts, queued reader count, presence/absence of log text under threshold/suppression conditions, correct longest-reader stack trace, suppression counters, and detailed metrics names/values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFSNamesystemLock.java -->
