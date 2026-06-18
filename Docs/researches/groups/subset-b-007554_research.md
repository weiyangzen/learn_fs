# Research Report: subset-b-007554

This grouped report covers the requested Hadoop HDFS NameNode test files. Each file section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameNodeReconfigure.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameNodeReconfigure.java

Purpose: Exercises NameNode runtime reconfiguration for caller context, IPC backoff and slow RPC logging, heartbeat intervals, SPS mode, block invalidation, parallel image loading, slow node/peer tracking, decommission backoff monitor settings, block placement minimums, FSNamesystem lock metrics, slow peer collection interval, and max directory items.

Important APIs and functions: The suite uses `NameNode.reconfigureProperty` and `reconfigurePropertyImpl` as the main API under test. It inspects `FSNamesystem`, `NameNodeRpcServer`, `DatanodeManager`, `BlockManager`, `StoragePolicySatisfyManager`, `SlowPeerTracker`, `FSImageFormatProtobuf`, and `FSDirectory` getters after reconfiguration. Helpers include `verifyReconfigureCallerContextEnabled`, `verifyReconfigureIPCBackoff`, `verifySPSEnabled`, and `validatePeerReport`.

Control flow: `setUp` starts a `MiniDFSCluster` with a custom block invalidation limit. Each test mutates one or more configuration keys, verifies both in-memory subsystem state and `NameNode` configuration state, checks invalid values through `ReconfigurationException`, and often resets to defaults with a null value. Some tests create alternate clusters with special initial configuration, such as storage policy disabled, backoff decommission monitor class, or lock metrics disabled.

State and persistence behavior: The file validates live mutable NameNode state rather than disk persistence. Reconfigured values are expected to update existing objects in place, including RPC server flags, heartbeat timing, block placement thresholds, slow peer tracking settings, SPS manager state, and FSDirectory limits. `shutDown` stops the cluster after each test to isolate state.

Dependencies and integration points: Depends on MiniDFSCluster, HDFS config keys, datanode administration monitor classes, block management, SPS, IPC server controls, slow peer outlier metrics, and JUnit/LambdaTestUtils. It is an integration test for NameNode dynamic reconfiguration wiring across RPC, namesystem, block manager, datanode manager, and storage policy components.

Risks: Many assertions pin exact default values and exception messages, so harmless wording or default changes can break tests. Tests that interact with background slow peer collectors and SPS mode can be timing-sensitive. The broad surface makes missing a reconfiguration hook likely to appear as stale in-memory state even when configuration storage changes.

Test signals: Passing signals include invalid values rejected with expected causes, config values reflected in live subsystem getters, null reverts restoring defaults, SPS disabled requests failing as expected, slow peer JSON respecting max-node limits, and FSDirectory refusing negative max directory item updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameNodeReconfigure.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameNodeRecovery.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameNodeRecovery.java

Purpose: Tests NameNode metadata recovery from edit logs containing padding, oversized operations, garbage, truncated tails, and finalized or in-progress corruption. The class is parameterized to run with synchronous and asynchronous edit log logging.

Important APIs and types: `runEditLogTest` drives low-level `EditLogFileOutputStream` and `EditLogFileInputStream` behavior using `nextOp` and `nextValidOp`. `EditLogTestSetup` describes edit log scenarios. Corruptors implement `Corruptor` with `TruncatingCorruptor`, `PaddingCorruptor`, and `SafePaddingCorruptor`. `testNameNodeRecoveryImpl` validates full cluster recovery with `StartupOption.RECOVER` and `MetaRecoveryContext.FORCE_ALL`.

Control flow: Low-level tests create a temporary edit log, write transaction records or raw bytes, flush and reopen the log, assert normal reading fails or succeeds at the expected transaction boundary, then use recovery-mode reads to skip bad regions. Full-cluster tests create directories, optionally prevent log finalization with a Mockito spy, corrupt the latest edits file, prove normal startup fails when recovery is required, run recovery startup, then restart normally and verify namespace contents survive.

State and persistence behavior: The target state is persisted edit-log data and NameNode storage directories. `setupRecoveryTestConf` creates HA-suffixed name and checkpoint directories to exercise generic key initialization. Recovery mutates on-disk edit logs so subsequent normal startup succeeds.

Dependencies and integration points: Uses MiniDFSCluster, FSImage, NNStorage, FSEditLog, edit log op classes, `DFSUtil.addKeySuffixes`, Apache commons file utilities, Mockito, and parameterized JUnit. It covers integration between edit log parsing, log segment finalization, recovery startup options, and namespace loading.

Risks: The tests rely on byte-level edit log formats and padding semantics; layout changes can require updates. Static `recoverStartOpt` and `EditLogFileOutputStream.setShouldSkipFsyncForTesting(true)` affect global test behavior. The async edit log parameter increases coverage but also sensitivity to flush/finalization behavior.

Test signals: Expected signals are correct last-valid transaction detection, `nextValidOp` recovering all intended transaction ids, normal startup rejection only when required, recovery startup completing without IOException, and post-recovery namespace paths still existing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameNodeRecovery.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameNodeResourceChecker.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameNodeResourceChecker.java

Purpose: Verifies NameNode disk/resource checking, low-resource safe mode transitions, duplicate volume de-duplication, manually checked volumes, and required versus redundant volume policy behavior.

Important APIs and types: Main APIs under test are `NameNodeResourceChecker.hasAvailableDiskSpace`, `getVolumesLowOnSpace`, `setVolumes`, and `setMinimumReduntdantVolumes`. It also touches `FSNamesystem.NameNodeResourceMonitor` and `NameNodeResourceChecker.CheckedVolume`. `MockNameNodeResourceChecker` is injected into the namesystem resource checker slot.

Control flow: Setup configures an edits directory under a test directory. Simple tests set `DFS_NAMENODE_DU_RESERVED_KEY` to zero or `Long.MAX_VALUE` to force available and unavailable outcomes. The resource monitor test starts a cluster with a one millisecond resource check interval, replaces the checker with a controllable mock, scans live threads for the monitor, then waits for safe mode enter and leave. Volume tests configure multiple name dirs or checked volumes on the same filesystem and assert one physical volume check. The policy test replaces the internal volume map with Mockito `CheckedVolume` instances and flips their availability.

State and persistence behavior: State is runtime-only: resource availability gates safe mode and volume maps inside the checker. Test directories are local filesystem artifacts, not NameNode persisted namespace data.

Dependencies and integration points: Integrates HDFS config keys, MiniDFSCluster, FSNamesystem resource monitoring, Mockito volume mocks, PathUtils test directories, and thread inspection. It validates the path from checker status to NameNode safe mode.

Risks: Thread-name matching and sleep/wait loops can be fragile under slow hosts. Tests that assume two configured paths share a volume depend on local test directory layout. Mocked volume maps bypass path normalization and focus purely on policy.

Test signals: Passing requires correct available/unavailable decisions, safe mode toggling on resource changes, duplicate same-volume checks collapsed to one entry, and required volumes immediately causing resource unavailability when low.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameNodeResourceChecker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameNodeResourcePolicy.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameNodeResourcePolicy.java

Purpose: Unit-tests `NameNodeResourcePolicy.areResourcesAvailable` across combinations of required and redundant resources, including excessive minimum redundant resource settings.

Important APIs and functions: `testResourceScenario` builds mocked `CheckableNameNodeResource` instances with controlled `isRequired` and `isResourceAvailable` responses. Public tests cover single redundant, single required, multiple redundant, multiple required, mixed required/redundant, and excessive minimum redundant resources. The excessive-minimum test also captures logs from `NameNodeResourcePolicy`.

Control flow: Each scenario constructs a collection containing a requested count of redundant and required resources. It marks the first N resources in each category unavailable, then calls `areResourcesAvailable(resources, minimumRedundantResources)`. Assertions encode the policy: all required resources must be available, and at least the configured minimum count of redundant resources must be available.

State and persistence behavior: No persistence exists. All state is mocked in-memory resource availability for a single policy call.

Dependencies and integration points: Depends on Mockito, JUnit assertions, SLF4J logger capture through `GenericTestUtils.LogCapturer`, and the `CheckableNameNodeResource` interface. It isolates the pure policy used by `NameNodeResourceChecker`.

Risks: The test is concise but pins policy behavior tightly. A future policy that distinguishes no redundant resources from insufficient redundant resources would require scenario updates. The log assertion couples the excessive-minimum path to message content.

Test signals: Passing means required-resource failures always make the policy unavailable, redundant-resource failures are tolerated only down to the configured minimum, impossible minimums fail, and the failure path emits a "Resources not available." log signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameNodeResourcePolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameNodeRespectsBindHostKeys.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameNodeRespectsBindHostKeys.java

Purpose: Confirms NameNode RPC, service RPC, lifeline RPC, HTTP, and HTTPS listeners honor explicit bind-host configuration keys and do not bind wildcard addresses by default in the tested cases.

Important APIs and functions: Helper methods read listener addresses from `NameNodeRpcServer.getClientRpcServer`, `getServiceRpcServer`, and `getLifelineRpcServer`, plus `NameNode.getHttpAddress` and `getHttpsAddress`. `setupSsl` creates SSL test keystores using `KeyStoreTestUtil`.

Control flow: Each bind-host test starts one cluster without the bind-host key and checks the listener is not `0.0.0.0`, shuts down, sets the corresponding bind key to `0.0.0.0`, starts another cluster, and asserts the listener uses the wildcard. Service and lifeline tests first set their advertised addresses to `127.0.0.1:0`. HTTPS configures test SSL resources and `HTTPS_ONLY` policy before repeating the same pattern.

State and persistence behavior: State is startup-time listener binding and temporary SSL keystore files under a test directory. There is no NameNode namespace persistence under test. HTTPS cleanup removes generated SSL configuration.

Dependencies and integration points: Uses `MiniDFSCluster`, `HdfsConfiguration`, DFS bind host/address keys, Hadoop HTTP policy, `KeyStoreTestUtil`, and AssertJ/JUnit assertions. It tests configuration integration between NameNode startup and IPC/HTTP server socket creation.

Risks: Tests are sensitive to address string formatting such as leading slashes from `InetAddress.toString`. HTTPS setup shares static `keystoresDir` and `sslConfDir`. Port binding behavior can vary if local networking rules restrict wildcard binding.

Test signals: Correct signals are non-wildcard listener addresses without bind keys, exact wildcard listener addresses with bind keys, and successful SSL cluster startup and cleanup for HTTPS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameNodeRespectsBindHostKeys.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameNodeRetryCacheMetrics.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameNodeRetryCacheMetrics.java

Purpose: Verifies NameNode retry cache metrics for non-idempotent RPC retries in an HA cluster when client responses are deliberately dropped.

Important APIs and functions: Setup enables `DFS_NAMENODE_ENABLE_RETRY_CACHE_KEY`, disables random failover order, and sets `DFS_CLIENT_TEST_DROP_NAMENODE_RESPONSE_NUM_KEY` to 2. It reads `RetryCacheMetrics` from `FSNamesystem.getRetryCache().getMetricsForTests`. `trySaveNamespace` enters safe mode, calls `saveNamespace`, then leaves safe mode.

Control flow: The test starts a simple HA topology with three DataNodes, transitions NameNode 0 to active, configures failover, and obtains a failover `DistributedFileSystem`. Initial metrics are zero. Saving namespace causes two dropped responses and subsequent retries, so cache hits become 2 and updates become 1. Closing the namesystem clears the retry cache and increments the cleared metric.

State and persistence behavior: The operation being retried, `saveNamespace`, persists namespace state, but the test focuses on retry cache counters. Cache state lives in the active namesystem and is cleared by `namesystem.close`.

Dependencies and integration points: Uses MiniDFSCluster HA topology, `HATestUtil`, client failover configuration, safe mode actions, HDFS client test fault injection, and IPC retry cache metrics. It validates client retry behavior against NameNode metric accounting.

Risks: The exact hit/update counts depend on the configured response drop count and retry behavior. Calling `namesystem.close` directly is a strong lifecycle action and assumes metrics remain readable after close.

Test signals: Passing requires metrics `(0,0,0)` initially, `(2,0,1)` after a retried save namespace, and `(2,1,1)` after namesystem close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameNodeRetryCacheMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameNodeRpcServer.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameNodeRpcServer.java

Purpose: Tests NameNode RPC server binding, client IP proxying through caller context for block locality, HA failback with proxy users, and Observer NameNode handling of stale `addBlock` requests.

Important APIs and functions: `testNamenodeRpcBindAny` inspects `NameNodeRpcServer` listener host. `getPreferredLocation` uses `DistributedFileSystem.getClient().getLocatedBlocks`. Proxy tests use `CallerContext.CLIENT_IP_STR`, `DFS_NAMENODE_IP_PROXY_USERS`, and `UserGroupInformation.doAs`. Observer handling calls `NameNodeRpcServer.addBlock` directly and expects `ObserverRetryOnActiveException`.

Control flow: The bind test starts a cluster with `dfs.namenode.rpc-bind-host` set to `0.0.0.0`. Client IP proxy tests create clusters with known racks/hosts or QJM HA, set caller context, compare unauthorized random placement with authorized proxied placement, and verify failover/failback access. The observer test creates a three-NameNode QJM HA cluster, transitions one NameNode to observer, stops its edit log tailer, creates a file on active, confirms observer is stale, then asserts `addBlock` asks the client to retry on active.

State and persistence behavior: File creation persists blocks for placement and stale observer checks. Caller context is thread-local and restored in finally blocks. HA state transitions mutate NameNode roles.

Dependencies and integration points: Integrates MiniDFSCluster, MiniQJMHACluster, NameNode RPC protocols, block placement locality, caller context, UGI, observer reads, edit log tailing, and HDFS client located-block APIs.

Risks: Locality tests use randomness and repeat 20 trials, so they are probabilistic. CallerContext must be restored to avoid leaking into later tests. Observer behavior depends on stopping the edit log tailer to create a controlled stale namespace.

Test signals: Expected signals include wildcard RPC host binding, authorized proxy user consistently receiving the requested preferred host, HA failover preserving file status access, and stale observer `addBlock` throwing `ObserverRetryOnActiveException`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameNodeRpcServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameNodeRpcServerMethods.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameNodeRpcServerMethods.java

Purpose: Covers targeted NameNode RPC method regressions for invalid snapshot names and datanode storage reports reflecting nonzero block counts.

Important APIs and functions: `setup` starts a MiniDFSCluster and captures `NamenodeProtocols` from `cluster.getNameNode().getRpcServer`. `testDeleteSnapshotWhenSnapshotNameIsEmpty` invokes `deleteSnapshot` with null and empty names. `testGetDatanodeStorageReportWithNumBLocksNotZero` writes one block and calls `getDatanodeStorageReport(HdfsConstants.DatanodeReportType.ALL)`.

Control flow: Each test runs with a fresh cluster. The snapshot test expects IOException for both null and empty snapshot names and checks the diagnostic message. The storage report test writes 1024 bytes to a file with one megabyte block size and replication 1, closes the stream, sums `getNumBlocks` across reported datanodes, and asserts the total is one.

State and persistence behavior: The storage report test persists a one-block file in the namespace and block manager, then reads DataNode report state through RPC. Snapshot invalid-name calls should not mutate namespace state.

Dependencies and integration points: Uses `NamenodeProtocols`, `DistributedFileSystem`, `FSDataOutputStream`, HDFS constants, MiniDFSCluster lifecycle, and GenericTestUtils exception matching. It validates RPC argument checking and report population from block manager/datanode state.

Risks: The storage count assumes block reporting has reached the NameNode by the time the file is closed. The snapshot test pins an exact validation substring.

Test signals: Passing means invalid snapshot names fail early with the expected message, and datanode storage reports include a nonzero block count after a simple file write.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameNodeRpcServerMethods.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameNodeStatusMXBean.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameNodeStatusMXBean.java

Purpose: Verifies the `NameNodeStatusMXBean` JMX surface mirrors live `NameNode` state and includes slow disk reporting when DataNode disk profiling reports an outlier.

Important APIs and functions: Tests query the platform `MBeanServer` for `Hadoop:service=NameNode,name=NameNodeStatus`. Attributes checked include `NNRole`, `State`, `HostAndPort`, `SecurityEnabled`, `LastHATransitionTime`, `BytesWithFutureGenerationStamps`, `SlowPeersReport`, and `SlowDisksReport`. Slow disk setup uses `DataNode.getDiskMetrics().addSlowDiskForTesting`.

Control flow: The first test starts a cluster, retrieves the NameNode, reads JMX attributes, and compares every value to the corresponding NameNode getter. The slow-disks test enables DataNode file IO profiling and a short outlier report interval, injects a slow disk path into the single DataNode, waits until `DatanodeManager.getSlowDisksReport` is non-null, then compares and inspects the JMX value.

State and persistence behavior: State is runtime metrics and management data, not persistent namespace data. Slow disk state is injected into DataNode metrics and propagated to NameNode/DatanodeManager reports.

Dependencies and integration points: Integrates JMX, MiniDFSCluster, DatanodeManager, DataNode disk metrics, DFS profiling configuration, GenericTestUtils polling, and NameNode status getters.

Risks: Slow disk propagation is asynchronous and relies on polling up to 100 seconds. JMX object names and attribute names are API-like contracts; renaming them breaks the test. Injected path matching is string-based.

Test signals: Passing requires JMX attributes exactly matching live NameNode getters, slow disk report becoming available, and the JMX slow disk report containing the injected slow volume path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameNodeStatusMXBean.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameNodeXAttr.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameNodeXAttr.java

Purpose: Extends the common HDFS xattr base test suite with a NameNode symlink-specific xattr scenario, ensuring xattr operations through symlink paths affect the target inode as expected.

Important APIs and functions: Inherits cluster and xattr fixtures such as `fs`, `name1`, `name2`, `name3`, `value1`, and `value2` from `FSXAttrBaseTest`. The local test uses `DistributedFileSystem` methods `mkdirs`, `createSymlink`, `setXAttr`, `getXAttrs`, `removeXAttr`, and `delete`.

Control flow: The test creates separate link and target parent directories, creates a target file, creates a symlink to it, sets two xattrs on the target, reads them through the symlink, adds a third empty xattr through the symlink, verifies target-side visibility, removes xattrs through link and target paths, and finally deletes both parent directories.

State and persistence behavior: Xattrs are persisted on the target inode, not on the symlink path. Empty xattr values are represented as zero-length byte arrays. The test mutates namespace xattr state and then cleans up.

Dependencies and integration points: Depends on HDFS symlink resolution, NameNode xattr storage, `DFSTestUtil.createFile`, inherited xattr cluster setup, and Java map/byte-array assertions. It specifically tests interaction between symlink resolution and xattr APIs.

Risks: The test assumes all xattr operations follow symlinks. Any future API mode that supports no-follow xattr operations would need separate coverage. Byte array assertions are necessary because map equality would not compare array contents safely.

Test signals: Passing means xattrs set on target are visible through the link, xattrs set or removed through the link mutate the target, empty xattr values round-trip as `new byte[0]`, and cleanup succeeds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameNodeXAttr.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNamenodeCapacityReport.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNamenodeCapacityReport.java

Purpose: Tests NameNode capacity, non-DFS usage, block pool usage percentages, same-disk storage tiering accounting, and xceiver load statistics for live, dead, decommissioning, and maintenance DataNodes.

Important APIs and functions: Uses `FSNamesystem` capacity getters, `DatanodeDescriptor` capacity fields, `DFSUtilClient` percent helpers, `FsDatasetTestUtils`, `DataNodeTestUtils.triggerHeartbeat`, and `DatanodeManager` admin operations. Helpers `checkClusterHealth`, `getNumDNInService`, `getInServiceXceiverAverage`, `startDecommissionOrMaintenance`, and `stopDecommissionOrMaintenance` centralize assertions.

Control flow: `testVolumeSize` configures reserved space, verifies DataNode and NameNode capacity arithmetic, creates open streams to account for reserved replica space, and triggers heartbeats. `testVolumeSizeWithSameDiskTiering` runs DISK and ARCHIVE volumes sharing a disk and verifies reserved/non-DFS space is not double counted. `testXceiverCountInternal` starts eight DataNodes, kills and restarts nodes, opens replicated write pipelines, transitions nodes into decommission or maintenance, closes streams, and checks total and in-service load after each stage.

State and persistence behavior: Namespace files and open write pipelines create block and xceiver state. Capacity state is reported through DataNode heartbeats into the NameNode. Admin states change DataNode service membership and affect in-service averages.

Dependencies and integration points: Integrates DataNode storage reports, FSNamesystem aggregate stats, block manager cluster stats, maintenance/decommission paths, HDFS client write pipeline behavior, and same-disk tiering configuration.

Risks: Capacity values depend on local filesystem capacity and MiniDFSCluster storage layout, so assertions use relationships rather than fixed totals. Xceiver load requires timely heartbeat propagation and short sleeps. Closing streams with decommissioned pipeline nodes can throw and is conditionally tolerated.

Test signals: Passing shows capacity excludes reserved space, percentages match helper math, same-disk tiering avoids double counting, and live/in-service node and xceiver load counts track node death and admin state transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNamenodeCapacityReport.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNamenodeRetryCache.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNamenodeRetryCache.java

Purpose: Verifies NameNode retry cache correctness for non-idempotent RPCs by manually controlling RPC call ids and client ids, and verifies retry cache rebuild from edit logs after restart.

Important APIs and types: `DummyCall` extends `Server.Call` to install controlled call metadata via `Server.getCurCall`. Tests call `NamenodeProtocols` methods: `concat`, `delete`, `createSymlink`, `create`, `append`, deprecated `rename`, `rename2`, `updatePipeline`, snapshot methods, and `FSNamesystem.initRetryCache`. `testRetryCacheRebuild` inspects `LightWeightCache<CacheEntry, CacheEntry>`.

Control flow: Setup enables retry cache and starts a cluster with enough DataNodes for the default erasure coding policy. `newCall` increments a shared call id to represent a new RPC; reusing the same call id simulates retries. Each operation first succeeds, then repeated same-call invocations must replay the cached result, while a new call id should fail or return false because the namespace already changed. HA update pipeline verifies a retry after standby failure does not hang. Rebuild test runs a standard operation set, snapshots cache entries, restarts NameNode, and verifies the same 39 entries are rebuilt.

State and persistence behavior: Retry cache entries are persisted in edit log records for reconstructable operations and rebuilt on NameNode restart. Namespace mutations from create/delete/rename/snapshot operations are intentionally used to distinguish retry replay from fresh duplicate requests.

Dependencies and integration points: Integrates IPC server call context, NameNode RPC implementation, retry cache serialization, edit log replay, snapshots, append/create semantics, HA standby exceptions, ACL config, and erasure coding policy sizing.

Risks: The hard-coded expected cache size of 39 is sensitive to `DFSTestUtil.runOperations`. Static call id/client state must be reset carefully. Directly setting thread-local server calls is test-only and can leak if future code uses async execution.

Test signals: Passing means repeated same-call RPCs replay success, new-call duplicates fail naturally, standby retry does not deadlock, disabling retry cache returns null, and restart rebuilds all expected cache entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNamenodeRetryCache.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNamenodeStorageDirectives.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNamenodeStorageDirectives.java

Purpose: Ensures storage type and storage ID directives chosen by the NameNode are honored by DFSClient/DataNode writes across HDFS storage policies.

Important APIs and types: Cluster setup configures storage types, storage counts, `VolumeChoosingPolicy`, and `BlockPlacementPolicy`. `verifyFileReplicasOnStorageType` uses `DFSClient.getLocatedBlocks` to inspect `LocatedBlock.getStorageTypes`. `TestVolumeChoosingPolicy` asserts the storage ID passed into volume choice, and `TestBlockPlacementPolicy` returns a controlled `DatanodeStorageInfo`.

Control flow: `testTargetStorageTypes` runs multiple cluster layouts and root storage policies, creates a replicated test file, then verifies expected storage types appear and unexpected types do not. Policies covered include `ONE_SSD`, `ALL_SSD`, `HOT`, `WARM`, `COLD`, `LAZY_PERSIST`, and `ALL_NVDIMM`. `testStorageIDBlockPlacementSpecific` installs custom block placement and volume choosing policies, forces placement to one specific storage, and verifies the same storage ID reaches volume selection during file creation.

State and persistence behavior: Created files persist blocks on storage volumes with specific storage types. Datanode storage state is runtime MiniDFSCluster state, and block location metadata exposes storage types and ids.

Dependencies and integration points: Uses MiniDFSCluster federation topology, DFSClient, block placement, datanode volume choosing, storage policy names, `StorageType`, heartbeat/disk interval tuning, and DataNode failure tolerance configuration.

Risks: Tests can be sensitive to block placement availability when requested storage types are scarce. Custom static fields in nested policy classes must be set before file creation. The verification counts storage type appearances rather than exact complete layout.

Test signals: Passing means block locations contain policy-appropriate storage types, exclude disallowed types, and the storage ID selected by NameNode placement is passed through to DataNode volume selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNamenodeStorageDirectives.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNestedEncryptionZones.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNestedEncryptionZones.java

Purpose: Tests nested HDFS encryption zone behavior, including persistence across edit logs and fsimage, rename restrictions between zones, root-directory zone behavior, and trash placement for nested zones.

Important APIs and functions: Setup configures a Java key store provider, creates encryption keys with `DFSTestUtil.createKey`, and uses `DistributedFileSystem.createEncryptionZone`. Helpers `initTopEZDirAndNestedEZDir`, `verifyEncryption`, and `renameChildrenOfEZ` create zones/files and assert encryption behavior. Trash behavior is checked through `FileSystem.getTrashRoot`, `FsShell`, and `ToolRunner`.

Control flow: The main nested-zone test creates a top and nested zone, verifies file encryption and raw file inequality, restarts NameNodes to load edit logs, checkpoints and restarts to load fsimage, then tests allowed and forbidden renames. It rejects moving a separate zone into an existing zone, allows renaming the top zone root, and allows renaming the nested zone within the same top zone. The root-zone test creates the top zone at `/`, validates rename restrictions, then verifies trash roots for top and nested zone files and confirms shell delete moves files into the correct per-zone trash.

State and persistence behavior: Encryption zone definitions, keys, file contents, and rename changes are persisted through edits and fsimage. Raw path comparisons validate ciphertext differs between zones. Trash paths are namespace state under each encryption zone's trash root.

Dependencies and integration points: Integrates NameNode encryption zone manager, key provider configuration, delegation token key use, raw reserved paths, safe mode and saveNamespace, FsShell trash, UGI current user, and HDFS rename validation.

Risks: JKS provider flushing requires setting the client provider to the NameNode provider. Rename rejection checks use exception message substrings. Trash behavior depends on configured trash interval and current user naming.

Test signals: Passing means nested zones reload after restart/checkpoint, encrypted status stays true, plaintext comparisons match while raw ciphertext differs, illegal cross-zone moves fail, legal zone-root renames succeed, and trash roots are zone-local.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNestedEncryptionZones.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNetworkTopologyServlet.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNetworkTopologyServlet.java

Purpose: Tests the NameNode `/topology` HTTP servlet in text and JSON modes for clusters with racked DataNodes and for clusters with no DataNodes.

Important APIs and functions: Tests start `MiniDFSCluster` with rack arrays, retrieve `cluster.getHttpUri(0)`, open `HttpURLConnection` to `/topology`, optionally set `Accept: application/json`, and parse JSON with Jackson `ObjectMapper`. `StaticMapping.resetMap` clears network topology mappings before each scenario.

Control flow: Text format test starts ten DataNodes across five racks, downloads the servlet response, wraps it with banner text for matching, asserts every rack label appears, and counts `127.0.0.1` occurrences. JSON format test repeats the topology, requests JSON, parses rack nodes, asserts five rack entries, and counts all DataNode entries. No-DataNode tests start zero-DataNode clusters and assert text or JSON-requested response contains "No DataNodes".

State and persistence behavior: No persistent namespace state is relevant. Runtime DataNode registration and rack mapping state feeds servlet output.

Dependencies and integration points: Integrates NameNode HTTP server, network topology/rack mapping, MiniDFSCluster DataNode registration, Jackson JSON parsing, and HTTP content negotiation through the Accept header.

Risks: Text counting assumes local DataNode host strings contain `127.0.0.1`. JSON shape traversal assumes the servlet response is a rack object containing child fields whose values are node arrays. Connections are not wrapped in cluster shutdown finally blocks, so failures before test exit could leave temporary clusters until JVM cleanup.

Test signals: Passing requires rack names and all DataNodes present in text output, JSON rack count and DataNode count matching the cluster layout, and explicit "No DataNodes" output for empty clusters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNetworkTopologyServlet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestParallelImageWrite.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestParallelImageWrite.java

Purpose: Verifies DFS namespace integrity and identical fsimage files across multiple NameNode image directories when images are written in parallel during restart and saveNamespace.

Important APIs and functions: `testRestartDFS` creates files with `DFSTestUtil`, restarts MiniDFSCluster without formatting, forces checkpoint-on-startup with `DFS_NAMENODE_CHECKPOINT_TXNS_KEY`, calls `saveNamespace`, and compares metadata. Static helper `checkImages` inspects `NNStorage`, image `StorageDirectory` instances, and `FSImageTestUtil` hash/equality helpers.

Control flow: The test starts a formatted cluster, records the configured number of NameNode name dirs, creates 200 files under `/srcdat`, records root and directory status, mutates root owner and directory group, and shuts down. It restarts without formatting, confirms files and metadata persisted, checks that all image dirs contain identical newest images, mutates the namespace by cleanup/recreate, enters safe mode, saves namespace, rechecks image equality, and verifies the fsimage hash changed after namespace mutation.

State and persistence behavior: This is a persistence-focused test. It validates namespace metadata in fsimage files across restarts and explicit saveNamespace, and checks all image storage directories have non-empty identical images.

Dependencies and integration points: Uses MiniDFSCluster, FSNamesystem, FSImage/NNStorage, name dir configuration, DFSTestUtil, safe mode RPC, and FSImageTestUtil MD5 comparisons ignoring transaction id.

Risks: Requires more than one image directory in MiniDFSCluster. Hash comparison ignores txid but still assumes deterministic image contents across directories. The test writes many files and can be IO-sensitive.

Test signals: Passing means file tree and metadata survive restart, every image directory remains active, parallel image files are identical, newest images match, and a later namespace save produces a different image hash.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestParallelImageWrite.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestPathComponents.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestPathComponents.java

Purpose: Unit-tests conversion between path strings and byte-array path components in `DFSUtil`, including fully qualified absolute paths, relative paths, root handling, repeated slashes, and trailing slash normalization.

Important APIs and functions: The file tests `DFSUtil.getPathComponents`, `DFSUtil.bytes2String`, and `DFSUtil.byteArray2PathString` overloads. Helper `testString` converts returned components back to strings and asserts the normalized reconstructed path.

Control flow: Absolute-path tests expect root paths to produce a single null component, while non-root absolute paths begin with an empty component. Relative-path tests omit that leading empty component. Byte-array-to-string tests exercise full conversion and offset/length slices for root, absolute `/1/2/3`, and relative `1/2/3`.

State and persistence behavior: Pure stateless utility tests; no filesystem or NameNode state is created.

Dependencies and integration points: Depends only on `DFSUtil`, JUnit, and Java arrays. The tested conversion logic is used by NameNode namespace path handling and edit/image serialization code that stores path components as byte arrays.

Risks: The tests encode subtle distinctions between null root component, empty absolute-path leading component, and relative components. Changes to normalization semantics for duplicate or trailing slashes would break multiple cases.

Test signals: Passing means repeated slashes collapse, trailing slashes are removed except root, absolute and relative component arrays reconstruct correctly, and slice-based reconstruction returns expected prefixes or relative fragments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestPathComponents.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestPersistentStoragePolicySatisfier.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestPersistentStoragePolicySatisfier.java

Purpose: Tests persistence and cleanup of Storage Policy Satisfier work for files and directories, especially SPS xattrs across checkpoints, restarts, dropped SPS mode, already-satisfied files, and parent/child directory interactions.

Important APIs and types: Setup starts MiniDFSCluster with DISK/ARCHIVE/SSD storage types and external SPS mode, creates `NameNodeConnector`, `StoragePolicySatisfier`, and `ExternalSPSContext`, and uses `DistributedFileSystem.satisfyStoragePolicy`. Tests inspect `XATTR_SATISFY_STORAGE_POLICY`, `INode`, `XAttrFeature`, and `XAttrStorage`. `restartCluster` restarts DataNodes and NameNodes and triggers heartbeats.

Control flow: Tests set storage policies (`WARM`, `COLD`, `ONE_SSD`), request satisfaction, checkpoint or restart clusters, and wait for expected storage types. Other tests lower SPS recheck time, ensure repeated satisfy calls work after xattr removal, change SPS mode to NONE and wait for xattr cleanup, ensure already-satisfied files do not leak xattrs, restart after child and parent requests, and stop/restart a DataNode to observe xattr persistence while movement is blocked.

State and persistence behavior: This file is centered on persisted SPS request xattrs and storage placement across edit logs, fsimage checkpointing, NameNode restarts, and DataNode restarts. Successful block movement should remove satisfy xattrs from files or directories.

Dependencies and integration points: Integrates external SPS, NameNodeConnector/Mover identity, block storage policies, DataNode storage types, secondary NameNode checkpointing, HA failover optional setup, xattr storage, and DFSTestUtil storage-type wait helpers.

Risks: Marked slow and uses long timeouts because it depends on block movement, heartbeats, and SPS polling. Direct sleeps, especially 30 seconds before restart, are timing-heavy. Static cluster/filesystem fields require careful cleanup.

Test signals: Passing means requested files reach expected storage types after checkpoint/restart, SPS xattrs are removed on completion/drop/already-satisfied cases, parent directory xattrs do not leak to children, and NameNode restarts tolerate child plus parent SPS requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestPersistentStoragePolicySatisfier.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestProcessCorruptBlocks.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestProcessCorruptBlocks.java

Purpose: Tests NameNode/block manager processing of corrupt replicas, ensuring corrupt replicas are removed only when enough good replicas exist and are retained when all replicas are corrupt.

Important APIs and functions: Tests create files with `DFSTestUtil.createFile`, get the first `ExtendedBlock`, corrupt replicas through `corruptBlock`, and inspect `BlockManager.countNodes` via `countReplicas`. They use `FSNamesystem.setReplication`, `DFSTestUtil.waitReplication`, `MiniDFSCluster.stopDataNode/restartDataNode`, materialized replica truncation, and `DataNodeTestUtils.runDirectoryScanner`.

Control flow: Decreasing-replication tests corrupt one replica, wait until two good replicas remain, then lower replication to two or one and assert corrupt replicas are removed. Extra-DataNode test starts with four DataNodes, stops one, corrupts a replica among the three active nodes, then restarts the fourth to create a new good replica and remove the corrupt one. All-corrupt test corrupts all replicas, lowers replication, and asserts corrupt replicas remain because no good copy exists.

State and persistence behavior: Block replica state is persisted on DataNode storage files and reported to the NameNode through scans, restarts, and block reports. NameNode block maps track live and corrupt replica counts.

Dependencies and integration points: Integrates DataNode directory scanner, block reports, MiniDFSCluster materialized replicas, block manager replica accounting, reconstruction timeout configuration, and replication changes.

Risks: `corruptBlock` always truncates the materialized replica at DataNode index 0 before using `dnIndex` for log cleanup, so the comments note index changes after restarts. Tests rely on sleeps and short block report intervals. Corrupt replica removal timing can vary with block report processing.

Test signals: Passing means corrupt replica counts remain while good replicas are below replication, drop to zero once good replicas meet replication, new DataNode replication cleans corruption, and all-corrupt blocks are preserved.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestProcessCorruptBlocks.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestProtectedDirectories.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestProtectedDirectories.java

Purpose: Verifies `fs.protected.directories` and protected subdirectory behavior for delete, trash, rename, runtime reconfiguration, path normalization, canonicalization, root handling, and invalid configured paths.

Important APIs and types: `setupTestCase` configures `FS_PROTECTED_DIRECTORIES`, starts a NameNode-only MiniDFSCluster, and creates protected/unprotected paths. `TestMatrixEntry` stores expected delete/rename outcomes. Tests call `FileSystem.delete`, `Trash.moveToAppropriateTrash`, `FileSystem.rename`, `NameNode.reconfigureProperty`, `FSDirectory.parseProtectedDirectories`, `FSDirectory.normalizePaths`, and `FSDirectory.getProtectedDirectories`.

Control flow: Matrix builders describe many layouts: empty/non-empty protected dirs, nested protected and unprotected trees, disjoint trees, string-prefix edge cases, trailing separators, and protected subdirectory mode. Delete, trash, and rename tests iterate sorted paths and compare actual success to matrix expectations, also checking failed delete leaves file counts unchanged. Reconfigure test changes protected directories at runtime and then resets to default. Normalization tests parse redundant slashes, trailing slashes, `..`, root, schemes, and reserved paths.

State and persistence behavior: Protected directory configuration is held in NameNode/FSDirectory runtime state and can be reconfigured. Namespace directories are created for each matrix case but not persisted across cluster instances.

Dependencies and integration points: Integrates CommonConfigurationKeys, DFS protected subdirectory enablement, MiniDFSCluster, FSDirectory policy parsing, HDFS delete/rename authorization, Trash behavior, AccessControlException handling, Guava-compatible collection helpers, and AssertJ assertions.

Risks: Matrix expectations are dense and path-order dependent. `testMoveProtectedSubDirsToTrash` compares `moveToTrash` with a second call to itself, which can mask expected-matrix intent and may be a weak assertion. Path canonicalization behavior is security-sensitive, especially for prefixes and reserved paths.

Test signals: Passing means protected paths and ancestors with protected children resist destructive operations when expected, trash follows the same access policy, runtime reconfiguration updates FSDirectory and config, and parser normalization rejects invalid paths while preserving root.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestProtectedDirectories.java -->
