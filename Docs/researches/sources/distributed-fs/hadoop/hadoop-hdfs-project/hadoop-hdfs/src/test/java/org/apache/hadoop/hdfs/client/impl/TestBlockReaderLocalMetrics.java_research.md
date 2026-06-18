<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/client/impl/TestBlockReaderLocalMetrics.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/client/impl/TestBlockReaderLocalMetrics.java

Purpose: Tests `BlockReaderLocalMetrics` and `BlockReaderIoProvider` latency recording for short-circuit local file-channel reads.

Important APIs/types/functions: Uses `BlockReaderLocalMetrics.create`, `getShortCircuitReadRollingAverages`, `MetricsTestHelper.replaceRollingAveragesScheduler`, `BlockReaderIoProvider.read`, `FakeTimer`, Hadoop metrics assertions, and Mockito `FileChannel.read`.

Control flow: Each test creates a metrics instance, replaces the rolling average scheduler with short test windows, mocks one or more `FileChannel` reads to advance a fake timer, performs reads through `BlockReaderIoProvider`, waits until thread-local metric state is collected, then reads the `HdfsShortCircuitReads` metrics record and checks `[ShortCircuitLocalReads]RollingAvgLatencyMs`.

State and persistence behavior: Metrics are in-process Hadoop Metrics2 state with rolling average windows and thread-local samples. No filesystem state is persisted. The static `FakeTimer` advances monotonically across tests, which is acceptable because assertions compare deltas recorded by the provider.

Dependencies and integration points: Covers the client metrics path between short-circuit read IO, thread-local metric collection, rolling averages, and Metrics2 publication.

Risks: Random delays in `testSlowShortCircuitReadsAverageLatencyValue` can include zero-delay samples, making assertions intentionally lower-bound rather than exact. Async metrics collection requires `GenericTestUtils.waitFor`, so scheduler timing can affect flakiness.

Test signals: Passing tests indicate slow short-circuit reads are sampled, multiple providers contribute to the same rolling average, and the published latency is at least the expected average delay.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/client/impl/TestBlockReaderLocalMetrics.java -->
