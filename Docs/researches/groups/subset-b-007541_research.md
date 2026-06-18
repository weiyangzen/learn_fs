# subset-b-007541 Research

Grouped source research for Hadoop HDFS DataNode test coverage under `hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode`. Each marker-delimited section preserves the original source path and is intended for reconciliation into the corresponding source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeFSDataSetSink.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeFSDataSetSink.java

## Purpose

`TestDataNodeFSDataSetSink` verifies that a `SimulatedFSDataset` registered as a Hadoop Metrics2 source emits the expected FS dataset metrics and tags to a registered sink. The test is a metrics publication smoke test for DataNode dataset capacity, cache, failure, context, and host fields rather than a filesystem data-path test.

## Important APIs, Types, and Functions

The file defines one nested sink, `FSDataSetSinkTest`, implementing `MetricsSink`. Its `init` method seeds a `TreeSet` of expected names: `DfsUsed`, `Capacity`, `Remaining`, `StorageInfo`, failed-volume fields, cache fields, `Context`, and `Hostname`. `putMetrics` scans `MetricsRecord.metrics()` and `MetricsRecord.tags()` once, incrementing `count` for each expected metric or tag found. `testFSDataSetMetrics` constructs `HdfsConfiguration`, `SimulatedFSDataset`, `MetricsSystemImpl`, registers source and sink, publishes immediately, and asserts that all expected keys were observed.

## Control Flow

The test creates a simulated dataset, adds a block pool, initializes and starts a dedicated `MetricsSystemImpl`, registers the dataset as `FSDataSetSource`, registers the custom sink as `FSDataSetSink`, starts MBeans, and calls `publishMetricsNow`. It then sleeps four seconds to allow asynchronous delivery before shutting down Metrics2 state and comparing expected-key count with discovered-key count.

## State and Persistence Behavior

All state is in memory: static metrics system instance, simulated dataset, sink key set, and callback count. There is no disk-backed HDFS cluster and no block persistence. The test does exercise process-global metrics registration and MBean startup/shutdown, so cleanup order matters to avoid leaking metrics state between tests.

## Dependencies and Integration Points

The test integrates Hadoop Metrics2 (`MetricsSystemImpl`, `MetricsSink`, `MetricsRecord`, `MetricsTag`), HDFS configuration, and `SimulatedFSDataset` as the dataset metrics source. It checks the DataNode FS dataset metrics surface that external sinks and JMX consumers rely on.

## Risks and Edge Cases

The sink only counts the first metrics record (`count == 0`), so later records cannot repair a partial first callback. The fixed `Thread.sleep(4000)` is timing-sensitive. Because `MetricsSystemImpl` is static, missed shutdown or duplicate names could cause cross-test interference. The assertion is sensitive to metric/tag renames or removals but does not validate metric values.

## Test Signals

Primary signal is `assertEquals(sink.getMapCount(), sink.getFoundKeyCount())`. Failures indicate a missing expected metrics/tag name, callback delivery failure, or Metrics2 registration problem. There is no negative-path or value-level coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeFSDataSetSink.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeFaultInjector.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeFaultInjector.java

## Purpose

`TestDataNodeFaultInjector` verifies that DataNode fault-injection hooks which delay write-pipeline activity are measured as slow I/O and surfaced through the injected delay logging callbacks. It targets delay accounting around acknowledgements to upstream nodes and packet forwarding to downstream nodes.

## Important APIs, Types, and Functions

The nested `MetricsDataNodeFaultInjector` extends `DataNodeFaultInjector`, exposing `delayOnce`, `logDelay`, and `getDelayMs`. It sleeps once for `DELAY = 2000` ms and records durations at least as large as the delay. `testDelaySendingAckToUpstream` overrides `delaySendingAckToUpstream` and `logDelaySendingAckToUpstream`; `testDelaySendingPacketDownstream` overrides `stopSendingPacketDownstream` and `logDelaySendingPacketDownstream`. Both delegate to `verifyFaultInjectionDelayPipeline`.

## Control Flow

`verifyFaultInjectionDelayPipeline` installs the custom injector in the static `DataNodeFaultInjector`, configures a three-DataNode `MiniDFSCluster`, lowers the slow-I/O warning threshold to `DELAY / 2`, lengthens the client socket timeout to avoid pipeline failure, and enables replacement-on-failure with policy `ALWAYS`. It writes one byte to a replication-2 file, calls `hflush` and `hsync`, closes the stream, and asserts the logged injected duration exceeds the configured slow threshold.

## State and Persistence Behavior

State includes the process-global DataNode fault injector, a temporary test base directory, and a short-lived MiniDFSCluster. The test always restores the previous injector in `finally` and shuts down the cluster. File data is persisted only in the temporary cluster directories long enough to drive the write pipeline.

## Dependencies and Integration Points

The file integrates `DataNodeFaultInjector`, client write-pipeline operations (`FSDataOutputStream`, `hflush`, `hsync`), slow-I/O configuration (`DFS_DATANODE_SLOW_IO_WARNING_THRESHOLD_KEY`), client socket timeouts, and DataNode replacement policy. It validates that pipeline fault hooks connect to the delay logging path rather than only delaying I/O.

## Risks and Edge Cases

The tests depend on real sleeping and a 60-second timeout. If the cluster or client path changes so the specific hook is not exercised for a one-byte replication-2 write, the delay will remain zero. The static injector is hazardous if not restored. Timing must be high enough to exceed threshold but not high enough to trigger client socket timeout.

## Test Signals

The core signal is `assertTrue(mdnFaultInjector.getDelayMs() > datanodeSlowLogThresholdMs)`. A passing run proves the delay hook executed, the slow-I/O logging hook received a measured duration, and the write pipeline survived the injected stall.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeFaultInjector.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeHotSwapVolumes.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeHotSwapVolumes.java

## Purpose

`TestDataNodeHotSwapVolumes` is a broad integration suite for live DataNode volume reconfiguration. It verifies parsing of changed storage directories, adding and removing volumes, federation behavior, block-report consequences, file-lock cleanup, concurrent add/list races, active-write removal, disk-failure reload, and same-mount tiering rejection.

## Important APIs, Types, and Functions

Important helpers include `startDFSCluster`, `setConfiguration`, `addVolumes`, `createFile`, `verifyFileLength`, `getNumReplicas`, `waitReplication`, `getDataDirs`, `triggerDeleteReport`, `getNumBlocksReport`, and `assertFileLocksReleased`. The suite exercises `DataNode.parseChangedVolumes`, `DataNode.reconfigurePropertyImpl(DFS_DATANODE_DATA_DIR_KEY, ...)`, `DataStorage`, `BlockPoolSliceStorage`, `FsDatasetSpi`, `FsVolumeSpi`, `FsVolumeImpl`, `FsDatasetTestUtil`, DataNode block reports, and `DataNodeTestUtils` disk-failure helpers.

## Control Flow

Cluster setup lowers block size, heartbeat, DF, heartbeat recheck, disk-check gap, and tolerated failed volumes for fast test feedback. Parsing tests compare new, removed, and unchanged `StorageLocation` lists and reject empty input or storage-type changes. Add-volume tests create new MiniDFSCluster instance storage directories, reconfigure `dfs.datanode.data.dir`, verify the effective configuration and `current` metadata directories, write files, and inspect block reports for distribution across old and new volumes. Removal tests reconfigure to a subset of directories, check file locks, schedule reports, then verify block missing behavior, new writes, replication recovery, or re-add behavior.

Concurrency coverage spies on `FsDatasetSpi.addVolume` and runs delayed add-volume operations in separate `SubjectInheritingThread`s while another thread repeatedly lists storage directories. Active-write removal uses `DataNodeFaultInjector.logDelaySendingAckToUpstream` plus barriers so a reconfiguration thread removes the volume while the write pipeline is blocked, then confirms the file remains readable and future writes succeed. Disk-failure reload simulates failed storage with `DataNodeTestUtils.injectDataDirFailure`, waits for disk error detection, restores the directory, reconfigures the original paths, and confirms a new volume object is used. Full-block-report coverage spies on the BPOS-to-NameNode protocol and expects a block report after removing a volume.

## State and Persistence Behavior

The test intentionally manipulates on-disk DataNode storage directories, `current` metadata directories, block pool storage directories, file locks, and block files. It validates that removed or failed volumes are removed from DataNode in-memory metadata and persistent storage tracking, and that re-added volumes can be formatted or rediscovered. In federation cases, volume changes must appear across namespaces, with empty volumes reported for namespaces that have not written new blocks. `tearDown` shuts down the cluster after each test.

## Dependencies and Integration Points

The suite integrates MiniDFSCluster, federated NameNode topology, `DistributedFileSystem`, `DFSClient`, block reports (`BlockListAsLongs`, `StorageBlockReport`, `BlockReportContext`), DataNode reconfiguration, FsDataset implementations, DataNode disk error detection, Mockito protocol spies, and platform assumptions for disk-failure injection. It is a direct regression surface for HDFS volume hot swap behavior.

## Risks and Edge Cases

Risks covered include storage type mutation of an existing path, partial add failures leaving stale metadata, lost file locks after volume removal, block reports retaining removed storage, re-adding a volume that still has blocks, append distribution after adding volumes, federation block-pool mismatches, replication after removing the volume containing a block, races between asynchronous add volume and storage listing, removing a volume during active writes, and direct reload after disk error. Timing and filesystem behavior are important: many tests depend on heartbeats, block reports, latches, or OS file-lock semantics; disk-failure injection is skipped on Windows.

## Test Signals

Signals include exact changed-volume list sizes and URIs, expected exception messages, effective configuration equality, `current` directory existence, block-report volume counts and block counts, file length and replication waits, `BlockMissingException` after removal, released lock assertions, no concurrent add/list errors, single remaining volume after active-write removal, successful reads and future writes, Mockito verification of one full block report, and rejection of same-mount volume additions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeHotSwapVolumes.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeInitStorage.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeInitStorage.java

## Purpose

`TestDataNodeInitStorage` verifies DataNode startup ordering: the DataNode UUID must be initialized in `DataStorage` before the configured FsDataset factory constructs the dataset.

## Important APIs, Types, and Functions

The nested `SimulatedFsDatasetVerifier` extends `SimulatedFSDataset`. Its nested `Factory` extends `FsDatasetSpi.Factory<SimulatedFSDataset>` and constructs `SimulatedFsDatasetVerifier`. `setFactory` writes `DFS_DATANODE_FSDATASET_FACTORY_KEY` into configuration. The verifier constructor logs and asserts `storage.getDatanodeUuid()` is non-null and non-empty.

## Control Flow

The test builds `HdfsConfiguration`, installs the custom dataset factory, starts a one-DataNode MiniDFSCluster, waits for active, and shuts it down. Dataset construction is the assertion point: if DataNode UUID assignment has not happened before FsDataset initialization, the constructor assertion fails during cluster startup.

## State and Persistence Behavior

The test observes DataNode storage identity state, specifically the in-memory `DataStorage` UUID loaded or created during startup. The MiniDFSCluster owns temporary storage directories, but the test does not inspect files directly.

## Dependencies and Integration Points

It integrates DataNode storage initialization, the pluggable FsDataset factory key, `FsDatasetSpi.Factory`, and MiniDFSCluster startup. It is a regression test for startup sequencing between `DataStorage` and dataset construction.

## Risks and Edge Cases

The assertions use Java `assert`, which only fires when assertions are enabled in the test JVM. The test only covers simulated dataset factory construction and does not verify UUID persistence across restarts. A startup refactor could bypass the custom factory or change constructor timing.

## Test Signals

The cluster reaches `waitActive()` without assertion failure. The meaningful signal is the constructor assertion that `storage.getDatanodeUuid()` exists before `SimulatedFSDataset` initialization finishes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeInitStorage.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeLifeline.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeLifeline.java

## Purpose

`TestDataNodeLifeline` validates DataNode lifeline RPC behavior when normal heartbeats are blocked, timely, ignored for dead nodes, or encounter NameNode-side update errors. Lifelines are intended to keep a DataNode from becoming stale or dead while the regular heartbeat channel is delayed.

## Important APIs, Types, and Functions

The suite uses `DatanodeLifelineProtocolClientSideTranslatorPB`, `DatanodeProtocolClientSideTranslatorPB`, `BPServiceActor`, `BPOfferService`, `FSNamesystem`, `DataNodeMetrics`, `BlockManagerFaultInjector`, `SlowPeerReports`, `SlowDiskReports`, and Mockito spies. Helper answer classes `LatchAwaitingAnswer` and `LatchCountingAnswer` coordinate heartbeat and lifeline RPC calls through `CountDownLatch`. `setup` enables the lifeline RPC address, short heartbeat/lifeline intervals, and short stale interval, then replaces BP service actor NameNode proxies with spies.

## Control Flow

`testSendLifelineIfHeartbeatBlocked` blocks `sendHeartbeat` until ten lifelines have been observed, counts down on `sendLifeline`, repeatedly asserts the NameNode sees one live, zero dead, and zero stale DataNodes, and even reconfigures a data directory while waiting for the next heartbeat. `testNoLifelineSentIfHeartbeatsOnTime` counts ten normal heartbeats and verifies no lifeline RPCs were sent. `testLifelineForDeadNode` disables heartbeats, marks DataNodes dead, sends a test lifeline, verifies capacity remains zero, then reenables heartbeat and waits for re-registration. `testHeartbeatAndLifelineOnError` injects `UnknownError` into heartbeat/lifeline update paths and verifies aggregate capacity remains unchanged after triggering both operations.

## State and Persistence Behavior

State includes live/dead/stale DataNode membership in the NameNode, DataNode capacity accounting, lifeline metrics counters, BP service actor RPC proxies, and a process-global `BlockManagerFaultInjector.instance`. The test also touches DataNode data-dir reconfiguration inside the blocked-heartbeat loop. Cluster state is temporary and shutdown asserts no lifeline threads remain.

## Dependencies and Integration Points

The file integrates DataNode lifeline scheduling, regular heartbeat scheduling, NameNode datanode manager statistics, lifeline RPC protocol, DataNode metrics (`LifelinesNumOps`), block-manager fault injection, Mockito proxy replacement, and MiniDFSCluster. It checks the contract between BP service actor scheduling and NameNode liveness accounting.

## Risks and Edge Cases

Timing is central: lifeline interval, heartbeat interval, stale interval, and latch waits must align. The tests depend on being able to spy and replace internal RPC translators. Static fault injector state may leak if not restored by surrounding code. The blocked-heartbeat test performs data-dir reconfiguration repeatedly, which adds coverage but also a possible source of incidental failure.

## Test Signals

Signals include Mockito verification that lifeline was called at least once or never, `LifelinesNumOps` counter checks, live/dead/stale DataNode counts during blocked or timely heartbeat periods, capacity remaining zero for a dead-node lifeline, re-registration restoring capacity, exception message containing `Unknown exception`, and unchanged capacity after injected errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeLifeline.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeMXBean.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeMXBean.java

## Purpose

`TestDataNodeMXBean` verifies the JMX `DataNodeInfo` MXBean exposes DataNode identity, version, ports, topology, storage, thread counters, security state, block counts, slow disks, block-report sizing, and heartbeat timing accurately.

## Important APIs, Types, and Functions

The tests use the platform `MBeanServer` and object name `Hadoop:service=DataNode,name=DataNodeInfo`. They read MXBean attributes such as `ClusterId`, `Version`, `DNStartedTimeInMillis`, `SoftwareVersion`, `RpcPort`, `HttpPort`, `NamenodeAddresses`, `DatanodeHostname`, `VolumeInfo`, `XceiverCount`, `XmitsInProgress`, `BPServiceActorInfo`, `SlowDisks`, `SecurityEnabled`, and heartbeat timing fields. Helpers include `replaceDigits`, `getTotalNumBlocks`, and `assertLastHeartbeatSentTime`.

## Control Flow

`testDataNodeMXBean` starts a cluster and compares JMX attributes to direct DataNode getter values. `testDataNodeMXBeanSecurityEnabled` starts clusters with simple and SASL secure configuration and verifies `SecurityEnabled`, then resets UGI configuration. `testDataNodeMXBeanBlockSize` writes 100 files, triggers block report, parses JSON `BPServiceActorInfo`, and compares `maxDataLength` with `ipc.maximum.data.length` while requiring positive `maxBlockReportSize`. `testDataNodeMXBeanBlockCount` creates five files, checks volume `numBlocks`, restarts the DataNode, deletes one file, and waits for count to drop. `testDataNodeMXBeanSlowDisksEnabled` injects a slow disk into disk metrics and reads it through JMX. `testDataNodeMXBeanLastHeartbeats` uses HA topology, stops the standby NameNode, and verifies heartbeat-sent times remain fresh while one heartbeat-response time ages.

## State and Persistence Behavior

The suite observes live DataNode process state through JMX and persistent block state through `VolumeInfo`. It verifies block counts survive DataNode restart and update after deletion. HA heartbeat timing state is stored in BP service actor info maps and exposed as JSON-like strings. Slow disk state is injected into `DiskMetrics` for testing.

## Dependencies and Integration Points

Dependencies include MiniDFSCluster, HA topology, NameNode lifecycle, Jackson `ObjectMapper`, Jetty JSON parser, `SaslDataTransferTestCase`, UGI, `DFSTestUtil`, DataNode disk metrics, and the Java management API. It is an integration test for external observability clients that consume DataNode JMX.

## Risks and Edge Cases

The test normalizes digits in `VolumeInfo` because capacity and path values vary. JMX object name collisions can occur if clusters are not shut down. JSON parsing assumes DataNode string formats remain stable. Heartbeat timing assertions use a five-second threshold and polling, so slow test hosts can cause flakiness. Security-enabled tests mutate global UGI configuration and must reset it.

## Test Signals

Signals are direct equality between JMX attributes and DataNode getters, boolean checks for security mode, parsed `BPServiceActorInfo` size values, total block counts before restart, after restart, and after delete, slow disk JSON containing the injected path, and heartbeat timing assertions for active and stopped standby NameNodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeMXBean.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeMetrics.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeMetrics.java

## Purpose

`TestDataNodeMetrics` is the main DataNode metrics integration suite. It verifies counters, gauges, quantiles, inverse quantiles, JMX network error reporting, local-client metrics, DataNode xceiver gauges, DataNode dataset lock metrics, heartbeat RPC metric naming across topology modes, and protection against deleting blocks when local file opening fails.

## Important APIs, Types, and Functions

The tests use `MetricsAsserts` helpers (`assertCounter`, `assertCounterGt`, `assertQuantileGauges`, `assertInverseQuantileGauges`, `getLongCounter`, `getMetrics`), `MiniDFSCluster`, `DFSTestUtil`, `DataNodeFaultInjector`, `DFSOutputStream`, `BlockSender`, `DataNodeMetrics`, `MetricsRecordBuilder`, `MBeanServer`, `DomainSocket`, and `TemporarySocketDirectory`. Helper `verifyBlockLocations` waits for expected located-block replica count.

## Control Flow

Basic write metrics use `SimulatedFSDataset` and a file longer than `Integer.MAX_VALUE` to verify `BytesWritten` handles long values and that incremental block reports occur. Packet-send and receive tests configure percentile intervals, perform reads or writes with `hsync`, then check packet transfer, blocked-on-network, flush, fsync counters, and quantile gauges after rollover. Slow packet tests use a mocked `DataNodeFaultInjector` to sleep in downstream send and disk/cache hooks, identify the head pipeline DataNode, and assert slow-packet counters. Dataset metrics write a file and create a temporary block to increment create/finalize counters.

Additional tests cover ack round-trip quantiles by slowing a write pipeline, network error metrics by injecting `writeBlockAfterFlush` failure and reading JMX `DatanodeNetworkCounts`, total read/write time and read-transfer-rate inverse quantiles, `BlocksReplicated` after adding a DataNode, active xceiver gauges and MXBean active thread count, preservation of blocks after a `Too many open files` `BlockSender` failure, heartbeat RPC metric names for non-HA, HA, federation, and HA federation, slow flush/ack counters through `DataNodeFaultInjector.delay`, node-local read/write counters via domain sockets, read/write active xceiver gauges during open streams, and dataset read/write lock acquisition counters.

## State and Persistence Behavior

Most state is runtime metrics state held by DataNode metrics sources and the Metrics2 system. The tests also create and delete HDFS files, temporary block replicas, pipeline streams, domain sockets, and JMX data. Static `DataNodeFaultInjector` is saved and restored in tests that replace it. The `Too many open files` case explicitly verifies the block remains valid in the FsDataset and visible in block locations after the failure.

## Dependencies and Integration Points

The suite integrates client write/read paths, packet responder and pipeline ack logic, FsDatasetImpl operations, NameNode RPC heartbeat metrics, JMX DataNodeInfo, short-circuit local reads, Unix domain sockets, block sending, DataNode xceiver server state, and topology-specific BP service actor names. It heavily depends on MiniDFSCluster and Metrics2 record snapshots.

## Risks and Edge Cases

The tests are timing-sensitive around percentile rollovers, artificial slowdowns, pipeline creation, heartbeat intervals, and active xceiver gauges. Some assertions depend on exact packet counts for tiny files. Domain-socket coverage is skipped if native domain sockets are unavailable. Fault injection is global and must be restored. The `Too many open files` regression checks a critical edge case where a local I/O error must not cause block invalidation.

## Test Signals

Signals include exact counters for bytes, packets, flush/fsync operations, dataset create/finalize operations, network errors, heartbeat names, local reads/writes, and lock acquisitions; positive counters for incremental reports, ack round trips, read/write time, slow operations, and replicated blocks; quantile/inverse-quantile gauge existence; JMX network error strings; valid block state after file-open failure; and active xceiver gauges transitioning from zero to one and back.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeMetricsLogger.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeMetricsLogger.java

## Purpose

`TestDataNodeMetricsLogger` verifies the DataNode periodic metrics logger can be enabled or disabled, uses asynchronous log4j delivery, and logs MBeans in the Hadoop metrics domain.

## Important APIs, Types, and Functions

`startDNForTest` starts a standalone DataNode against a mock NameNode using `InternalDataNodeTestUtils.startDNWithMockNN`, with `DFS_DATANODE_METRICS_LOGGER_PERIOD_SECONDS_KEY` set to one second or zero. `tearDown` shuts down the DataNode and deletes its data directory. Test support includes `TestFakeMetricMXBean`, `TestFakeMetric`, `MBeans.register`, `PatternMatchingAppender`, log4j `AsyncAppender`, and `DataNode.METRICS_LOG_NAME`.

## Control Flow

The first two tests start a DataNode with metrics logging enabled or disabled and check `dn.getMetricsLoggerTimer()` is present or absent. `testMetricsLoggerIsAsync` inspects appenders on the DataNode metrics logger and requires the first appender to be an `AsyncAppender`. `testMetricsLogOutput` registers a fake Hadoop-domain MBean, starts the DataNode with logging enabled, retrieves the `PATTERNMATCHERAPPENDER`, and waits until the configured pattern is matched.

## State and Persistence Behavior

The file creates a real DataNode data directory under the MiniDFSCluster base directory and deletes it after each test. Metrics logger state is a timer inside the DataNode. Logging state is global log4j appender configuration. The fake MBean is registered in the process MBean server for the duration of the test.

## Dependencies and Integration Points

It integrates DataNode standalone startup with mock NameNode, DataNode metrics logging configuration, log4j asynchronous appenders, Hadoop MBean registration utilities, pattern-matching test appenders, and filesystem cleanup.

## Risks and Edge Cases

The asynchronous log-output test can be timing-sensitive and waits up to 60 seconds. The helper `addAppender` exists but is unused, so appender setup is assumed to come from test logging configuration. Global logger and MBean state may leak if external test setup is inconsistent. The data directory path is shared by this class and must be deleted reliably.

## Test Signals

Signals are non-null or null metrics logger timer depending on configuration, first appender being `AsyncAppender`, and `PatternMatchingAppender.isMatched()` eventually becoming true after registering `TestFakeMetric`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeMetricsLogger.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeMultipleRegistrations.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeMultipleRegistrations.java

## Purpose

`TestDataNodeMultipleRegistrations` validates DataNode registration and handshake behavior across federated NameNodes, HA nameservices, cluster-ID mismatches, invalid storage after reformat, and MiniDFSCluster support for adding NameNodes.

## Important APIs, Types, and Functions

The tests use `MiniDFSNNTopology`, `MiniDFSCluster`, `NameNode`, `FSImageTestUtil`, `BPOfferService`, `BPServiceActor`, `RunningState`, `StartupOption.FORMAT`, `DFSTestUtil.formatNameNode`, and `FSNamesystem` namespace directories. Helper `getNNSocketAddress` extracts the single BP service actor socket address for a `BPOfferService`.

## Control Flow

`test2NNRegistration` starts a two-NameNode federated cluster, reads block-pool IDs, cluster IDs, layout versions, and namespace IDs from both FSImages, verifies namespace IDs differ while cluster IDs match, inspects DataNode volume info, orders BPOfferServices by NameNode address, and checks each BPOS registered with the expected block pool and namespace. `testFedSingleNN` verifies a single NameNode registration and triggers a test block report, then shuts down and asserts all BPOfferServices are gone. `testClusterIdMismatch` adds a compatible third NameNode, then changes the startup cluster ID before adding a fourth and verifies the DataNode remains registered with only three.

`testClusterIdMismatchAtStartupWithHA` builds two nameservices where one has a bad cluster ID, then starts a DataNode and expects only one BPOfferService while the DataNode stays up. `testDNWithInvalidStorageWithHA` starts a valid HA nameservice, stops the DataNode and NameNodes, reformats NameNodes with a different cluster ID, restarts, and waits until BP service actors report `FAILED`. `testMiniDFSClusterWithMultipleNN` verifies NameNodes can be added to federated clusters but not to a non-federated cluster.

## State and Persistence Behavior

The suite validates persistent namespace identity fields: cluster ID, namespace ID, block pool ID, and layout version. It manipulates NameNode formatting and copies namespace directories to create invalid storage scenarios. DataNode BPOfferService lifecycle state is observed before and after cluster shutdown and restart.

## Dependencies and Integration Points

It integrates federated and HA NameNode topology, DataNode BPOfferService registration, FSImage metadata, MiniDFSCluster dynamic NameNode addition, NameNode formatting, and DataNode running-state transitions. It is a regression surface for multi-namespace DataNode identity safety.

## Risks and Edge Cases

The tests use sleeps for registration after adding NameNodes, which can be timing-sensitive. `StartupOption.FORMAT.setClusterId` is process-global state. Ordering of BPOfferServices is not guaranteed and is corrected manually. The invalid-storage test relies on reformatting and restarting NameNodes with copied namespace directories, which is sensitive to storage layout changes.

## Test Signals

Signals include exact BPOfferService counts, matching NameNode socket addresses and block-pool IDs, equal cluster IDs across valid namespaces, distinct namespace IDs, DataNode staying up with only valid services, BP service actor `FAILED` state after invalid storage, and expected `IOException` when adding a NameNode to a non-federated cluster.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeMultipleRegistrations.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodePeerMetrics.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodePeerMetrics.java

## Purpose

`TestDataNodePeerMetrics` verifies rolling-average peer latency metrics for downstream packet sending, including JSON reporting and stale record removal/reuse.

## Important APIs, Types, and Functions

The suite uses `DataNodePeerMetrics.create`, `MutableRollingAverages`, `MetricsTestHelper.replaceRollingAveragesScheduler`, `DFS_DATANODE_PEER_STATS_ENABLED_KEY`, and `DFS_DATANODE_PEER_METRICS_MIN_OUTLIER_DETECTION_SAMPLES_KEY`. Helper `genPeerAddress` creates randomized `[ip:9801]` peer strings.

## Control Flow

`testGetSendPacketDownstreamAvgInfo` enables peer stats, replaces the rolling average scheduler with two five-second windows, records 1000 random latencies for a new peer in each of three iterations, sleeps until after each rollover, dumps JSON through `dumpSendPacketDownstreamAvgInfoAsJson`, and checks the peer address appears. `testRemoveStaleRecord` configures a short validity period, records enough samples for three peers, waits for stats to appear, verifies JSON contains all peers, waits until stale records are removed and JSON becomes `{}`, then records the peers again and verifies metrics resume normally.

## State and Persistence Behavior

All metrics state is in memory in `MutableRollingAverages` and the peer metrics object. Records age out based on scheduler windows and validity milliseconds. There is no MiniDFSCluster or persisted filesystem state.

## Dependencies and Integration Points

The file integrates DataNode peer metrics, rolling-average scheduling, outlier-detection sample thresholds, metrics test helper scheduler replacement, and JSON dumping. It covers the peer-latency data source used by slow-peer detection/reporting.

## Risks and Edge Cases

The tests depend on real time and scheduler rollover, including computed sleeps. Random peer addresses prevent accidental key reuse but make logs nondeterministic. If rolling-average validity or JSON key naming changes, assertions may fail. The stale-record test verifies that eviction is not permanent by adding records again after JSON empties.

## Test Signals

Signals are JSON containing the active peer address after each rollover, rolling stats size becoming three, JSON becoming `{}` after stale eviction, and stats returning to three after re-adding samples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodePeerMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeReconfiguration.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeReconfiguration.java

## Purpose

`TestDataNodeReconfiguration` verifies live DataNode reconfiguration for transfer throttles, block/cache reports, peer and disk outlier detection, disk usage refresh behavior, disk balancer settings, slow-I/O threshold, and balancer mover concurrency. It ensures new values are validated, applied to runtime objects, written into DataNode configuration, and reverted to defaults without restart.

## Important APIs, Types, and Functions

The suite exercises `DataNode.reconfigureProperty` and `reconfigurePropertyImpl` for many keys: `DFS_DATANODE_BALANCE_MAX_NUM_CONCURRENT_MOVES_KEY`, block report interval/split/initial delay, max receiver threads, transfer/write/read bandwidth, cache report interval, peer stats/outlier keys, disk outlier and profiling keys, `FS_DU_INTERVAL_KEY`, `FS_GETSPACEUSED_JITTER_KEY`, `FS_GETSPACEUSED_CLASSNAME`, disk balancer enable/plan-valid interval, and slow-I/O warning threshold. Helpers include `startDFSCluster`, `createDNsForTest`, `testAcquireOnMaxConcurrentMoversReconfiguration`, and nested `DummyCachingGetSpaceUsed`.

## Control Flow

Each test starts from a ten-DataNode MiniDFSCluster unless it explicitly starts standalone DataNodes with a mock NameNode. Reconfiguration tests generally try invalid values first, expect `ReconfigurationException` with `NumberFormatException` or `IllegalArgumentException`, apply a valid value, assert runtime object state, then apply `null` to revert and verify defaults and absent config keys. Balancer mover tests acquire all throttler permits before and after max changes and cover failed downsize when current permits are busy. Block-report changes are checked through each `BPServiceActor` scheduler. Data xceiver changes inspect `DataXceiverServer` max count and throttler bandwidth objects. Peer/disk slow metrics update `DataNodePeerMetrics`, `DiskMetrics`, file I/O profiling hooks, and slow detector thresholds.

Disk usage tests update refresh interval and jitter inside each `BlockPoolSlice` `CachingGetSpaceUsed`, then revert to defaults. `testDfsUsageKlass` changes the space-used implementation to `DummyCachingGetSpaceUsed` and observes a static counter increasing after refreshes. Disk balancer tests toggle enablement and parse plan validity intervals in raw milliseconds and time-unit strings. Slow-I/O threshold reconfiguration checks invalid strings/negative values, a valid value, and default restoration.

## State and Persistence Behavior

The suite mutates live DataNode configuration and runtime service objects across all DataNodes. It observes state in xceiver throttlers, BP service actor schedulers, DataNode configuration, peer/disk metrics detectors, file I/O profiling hooks, block pool slices, and disk balancer. Temporary standalone DataNode directories are deleted in `tearDown`. `DummyCachingGetSpaceUsed.counter` is static and demonstrates periodic refresh behavior after class reconfiguration.

## Dependencies and Integration Points

The file integrates DataNode reconfiguration infrastructure, MiniDFSCluster federation topology, mock-NameNode DataNode startup, block report and outlier report schedulers, xceiver server throttling, peer metrics, disk metrics, file I/O profiling, FsDataset volume internals, disk balancer, and Hadoop `GetSpaceUsed` implementations. It is a broad runtime-config regression suite.

## Risks and Edge Cases

The primary risks are partial application where configuration changes but runtime objects do not, failed validation accepting bad values, default reversion leaving stale config keys, and concurrency limits shrinking below active usage. Some tests instantiate a new `BlockPoolManager` for scheduler verification, which is a narrow check of refreshed scheduler config. `testDfsUsageKlass` uses sleeps and static counter state, so it can be timing-sensitive. The repeated loop across ten DataNodes increases coverage but also test runtime.

## Test Signals

Signals include expected exceptions for invalid values, exact runtime values after valid reconfiguration, null config entries after default reversion, throttler acquire success/failure counts, failed concurrent-mover downsize, BP service actor scheduler intervals, peer/disk detector threshold values, profiling hook enablement and sample range, `CachingGetSpaceUsed` interval/jitter values, increasing dummy space-used refresh counter, disk balancer enablement and validity intervals, and slow-I/O warning threshold restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeReconfiguration.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeRollingUpgrade.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeRollingUpgrade.java

## Purpose

`TestDataNodeRollingUpgrade` verifies DataNode behavior during HDFS rolling upgrade prepare, finalize, rollback, regular upgrade after rolling upgrade, block trash handling, layout-version changes, and DataXceiver peer tracking.

## Important APIs, Types, and Functions

Key helpers are `startCluster`, `shutdownCluster`, `triggerHeartBeats`, `getBlockForFile`, `getTrashFileForBlock`, `deleteAndEnsureInTrash`, `ensureTrashRestored`, `isTrashRootPresent`, `isBlockFileInPrevious`, `startRollingUpgrade`, `finalizeRollingUpgrade`, `rollbackRollingUpgrade`, `rollingUpgradeAndFinalize`, and static `addDataNodeLayoutVersion`. The suite uses `DFSAdmin -rollingUpgrade prepare/finalize`, `MiniDFSCluster` restart APIs, `BlockLocalPathInfo`, `ReplicaInfo`, `BlockPoolSliceStorage`, `DataNodeLayoutVersion`, and `LayoutVersion.updateMap`.

## Control Flow

Setup starts a one-DataNode cluster with one-MiB block size and captures the NameNode, DataNode, filesystem, and block pool ID. Rolling-upgrade prepare enters safemode, runs DFSAdmin prepare, triggers heartbeats, and expects dataset trash enabled. Deleting a file during rolling upgrade moves its block file from current storage into DataNode trash. Finalize runs DFSAdmin finalize, triggers heartbeats, and expects trash disabled and deleted files to remain deleted. Rollback stops the DataNode, restarts the NameNode with `-rollingupgrade rollback`, restarts the DataNode with `-rollback`, and expects trash-restored blocks and contents.

The layout-change tests start rolling upgrade, delete files into trash, stop the DataNode, inject an older DataNode layout version, restart to trigger layout upgrade, and verify trash is moved to `previous`. Finalize removes `previous`; rollback restores the first two files and leaves no trash/previous block files. `testDatanodeRUwithRegularUpgrade` performs a rolling upgrade/finalize, restarts NameNode with regular `-upgrade`, writes another file, and finalizes upgrade. `testDatanodePeersXceiver` opens three DFS clients and streams, writes large buffers, and checks DataNode peer/xceiver accounting remains internally consistent before and after close.

## State and Persistence Behavior

The suite directly validates on-disk block files, trash directories, `previous` directories, DataNode block pool storage, and layout-version metadata. It uses `@TempDir` for cluster base storage. Rolling upgrade state is persisted through NameNode/DataNode restart and rollback paths. File contents are read before deletion and compared after rollback.

## Dependencies and Integration Points

It integrates DataNode FsDataset block-local path lookup, block pool trash, NameNode rolling-upgrade commands, DFSAdmin, MiniDFSCluster restart/rollback options, layout-version feature maps, client DFS streams, and DataXceiver peer tracking. It is a critical persistence regression suite for upgrade safety.

## Risks and Edge Cases

The tests are tagged slow and have long timeouts because upgrade/rollback and heartbeats are timing-heavy. They assume test files have a single block. `addDataNodeLayoutVersion` mutates global layout-version state for testing. The path rewrite in `isBlockFileInPrevious` depends on storage directory naming. A failed cleanup or missed heartbeat can make trash state appear stale.

## Test Signals

Signals include dataset trash enabled/disabled at the right phases, block files moving from current to trash, trash restoration after rollback, deleted files remaining deleted after finalize, file contents matching after rollback, block files moving to and out of `previous` across layout changes, successful regular upgrade after rolling finalize, and stable peer/xceiver counts around multiple open streams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeRollingUpgrade.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeTcpNoDelay.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeTcpNoDelay.java

## Purpose

`TestDataNodeTcpNoDelay` verifies HDFS client/DataNode sockets apply TCP_NODELAY according to default and explicit configuration across normal data writes and DataNode block-transfer replication.

## Important APIs, Types, and Functions

The suite uses `HADOOP_RPC_SOCKET_FACTORY_CLASS_DEFAULT_KEY` to install `SocketFactoryWrapper`, `NetUtils.getDefaultSocketFactory`, MiniDFSCluster, `DFSTestUtil`, and configuration keys for client/server data transfer and IPC TCP_NODELAY. `SocketFactoryWrapper` extends `StandardSocketFactory` and wraps all created sockets in `SocketWrapper`. `SocketWrapper` delegates socket operations and records the last value passed to `setTcpNoDelay`.

## Control Flow

`testTcpNoDelayEnabled` leaves defaults in place, installs the wrapper socket factory, starts a three-DataNode cluster, creates replicated data, forces a block transfer by increasing replication from one to two, and asserts all tracked sockets had TCP_NODELAY enabled. `testTcpNoDelayDisabled` sets data-transfer client, data-transfer server, IPC client, and IPC server TCP_NODELAY keys to false, performs the same data creation and transfer, and asserts the tracked sockets were not all TCP_NODELAY enabled.

## State and Persistence Behavior

State is kept in the static `SocketFactoryWrapper.sockets` list and per-wrapper `tcpNoDelay` booleans. HDFS files are created only to drive socket creation and block transfer. The wrapper is reset and the cluster is shut down in each `finally` block.

## Dependencies and Integration Points

The file integrates Hadoop socket factory configuration, RPC and data-transfer TCP_NODELAY keys, DFS client writes, replication-driven DataNode `transferBlocks`, and Java socket delegation. It checks both client-facing and inter-DataNode transfer paths.

## Risks and Edge Cases

The wrapper records whether `setTcpNoDelay` was ever called with true or false, not whether the first send happened before configuration. The disabled test only asserts not all sockets were true because parts of the client write path always enable TCP_NODELAY. Static socket tracking must be reset between tests. Coverage depends on all relevant sockets being created through the configured default socket factory.

## Test Signals

Signals are `SocketFactoryWrapper.wasTcpNoDelayActive()` returning true under defaults and false when all known TCP_NODELAY settings are disabled after exercising both file creation and block transfer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeTcpNoDelay.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeTransferSocketSize.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeTransferSocketSize.java

## Purpose

`TestDataNodeTransferSocketSize` verifies DataNode transfer-server receive buffer sizing for explicit configuration and kernel auto-tuning mode.

## Important APIs, Types, and Functions

Both tests configure `DFS_DATANODE_TRANSFER_SOCKET_RECV_BUFFER_SIZE_KEY`, install `SimulatedFSDataset`, start a MiniDFSCluster, retrieve the first `DataNode`, and inspect `datanode.getXferServer().getPeerServer().getReceiveBufferSize()`.

## Control Flow

`testSpecifiedDataSocketSize` sets the receive buffer to 4 KiB, starts the cluster, and asserts the peer server receive buffer size equals 4096. `testAutoTuningDataSocketSize` sets the value to zero, starts the cluster, and asserts the resulting receive buffer size is positive, indicating the platform/kernel default is in effect.

## State and Persistence Behavior

There is no persistent file data. Runtime state is the DataNode transfer server's socket receive buffer configuration. Clusters are shut down in `finally`.

## Dependencies and Integration Points

The file integrates DataNode xfer server setup, peer server socket options, MiniDFSCluster, simulated dataset configuration, and the HDFS transfer socket receive buffer config key.

## Risks and Edge Cases

The explicit-size test assumes the requested buffer is observable exactly through the peer server. The auto-tuning test only verifies positivity, not a specific OS default. Both tests depend on the peer server being initialized by cluster startup.

## Test Signals

Signals are equality to `4 * 1024` for configured size and greater-than-zero for auto-tuning size.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeTransferSocketSize.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeUUID.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeUUID.java

## Purpose

`TestDataNodeUUID` verifies DataNode UUID generation when absent and UUID preservation when one configured storage directory is wiped but another still contains the original identity.

## Important APIs, Types, and Functions

`testDatanodeUuid` directly constructs a `DataNode` with empty `StorageLocation` list and calls `checkDatanodeUuid`. `testUUIDRegeneration` uses two explicit data directories, `MiniDFSCluster.manageDataDfsDirs(false)`, `MiniDFSCluster.DataNodeProperties`, Apache Commons `FileUtils`, and DataNode startup state `isDatanodeFullyStarted`.

## Control Flow

The direct UUID test configures ephemeral DataNode RPC/HTTP/IPC addresses and default FS URI, creates a DataNode with no locations, asserts `getDatanodeUuid()` is null, calls `checkDatanodeUuid`, and asserts it becomes non-null. The regeneration test deletes two test disks, starts a one-DataNode cluster with both directories, records the DataNode UUID, stops the DataNode, deletes and recreates the second disk to simulate wipe/unmount-root replacement, restarts the same DataNode, waits until fully started, and asserts the UUID equals the original UUID from the intact first disk.

## State and Persistence Behavior

The first test observes only in-memory UUID assignment. The second validates persistent UUID storage across multiple configured disks and restart, ensuring DataNode identity is recovered from any intact storage directory instead of regenerated because one disk was wiped.

## Dependencies and Integration Points

The file integrates DataNode identity management, `DataStorage`, MiniDFSCluster restart APIs, manual data-dir management, filesystem directory deletion/recreation, and configured DataNode address/default URI setup.

## Risks and Edge Cases

Direct `new DataNode` construction can create resources without the usual MiniDFSCluster lifecycle. The regeneration test polls startup with a sleep loop under a 10-second timeout. It covers only one wiped disk with another intact disk, not all disks wiped or conflicting UUIDs across disks. Manual directory management requires reliable cleanup by the test environment.

## Test Signals

Signals are null-to-non-null UUID transition after `checkDatanodeUuid` and exact equality between the original and restarted DataNode UUID after one storage directory is deleted and recreated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeUUID.java -->
