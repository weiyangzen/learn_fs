# subset-b-007526 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDecommission.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDecommission.java

## Purpose
`TestDecommission` is the main slow JUnit coverage for HDFS replicated-block datanode decommissioning. It extends `AdminStatesBaseTest`, builds `MiniDFSCluster` topologies, edits include/exclude host files, calls refresh-nodes paths, and verifies the NameNode and BlockManager converge to the correct `DatanodeInfo.AdminStates` while preserving file readability, replication, capacity accounting, and admin reporting. It covers non-federated, federated, and HA standby/active NameNode behavior.

## Important APIs, Types, and Functions
Key helper APIs are `checkFile(FileSystem, Path, int, String, int)`, `verifyStats(NameNode, FSNamesystem, DatanodeInfo, DataNode, boolean)`, `testDecommission(int, int)`, `getDataNode(DatanodeInfo)`, `verifyOpenFilesBlockingDecommission(...)`, `doDecomCheck(...)`, `assertTrackedAndPending(...)`, `nodeUsageVerification(...)`, `createClusterWithDeadNodesDecommissionInProgress(...)`, and `appendBlock(...)`. The tests exercise `DatanodeManager`, `DatanodeAdminManager`, `BlockManager`, `BlockManagerTestUtil`, `NameNodeAdapter`, `DFSClient`, `DFSAdmin`, `FSNamesystem`, `DatanodeStatistics`, `SimulatedFSDataset`, `DataNodeTestUtils`, and admin-state values `DECOMMISSION_INPROGRESS` and `DECOMMISSIONED`.

## Control Flow
The ordinary decommission path starts a cluster, writes files at controlled replication factors, selects one or more live datanodes through inherited `takeNodeOutofService`, writes exclude-file entries, refreshes nodes, waits for the expected admin state, and then checks client-visible block locations. `checkFile` inspects `HdfsDataInputStream.getAllBlocks()` and enforces that decommissioned replicas are marked decommissioned, sorted after live replicas, and counted as an extra replica when live replication is satisfied.

Several tests inject unusual timing. `testDecommissionOnStandby` uses an HA cluster, slow heartbeats, ANN/SBN refresh ordering, recommission, deletion reports, and a second decommission to guard against standby-side excess-replica invalidation. `testCloseWhileDecommission`, `testDecommissionWithOpenFileAndBlockRecovery`, and `testAllocAndIBRWhileDecommission` keep files under construction, pause or delay incremental block reports, force lease recovery, and verify that close or committed-to-complete transitions remain valid while datanodes are leaving service. `testDecommissionWithOpenfileReporting` runs `DFSAdmin -listOpenFiles -blockingDecommission` and then manually advances redundancy checks until the open files stop blocking.

The monitor-accounting tests configure `DFS_NAMENODE_DECOMMISSION_BLOCKS_PER_INTERVAL_KEY`, `DFS_NAMENODE_DECOMMISSION_MAX_CONCURRENT_TRACKED_NODES`, and the MiniDFSCluster decommission testing interval. They then call `BlockManagerTestUtil.recheckDecommissionState` directly to verify how many nodes are scanned, tracked, pending, or requeued. `testRequeueUnhealthyDecommissioningNodes` and `testDeleteCorruptReplicaForUnderReplicatedBlock` synthesize dead decommissioning nodes, under-replicated blocks, stale heartbeats, corrupt replicas, datanode restarts, and queue clearing to ensure the monitor makes progress.

## State and Persistence Behavior
Persistent state under test includes NameNode in-memory block maps, datanode admin state, include/exclude host files, HA edit tailing, restarted NameNode state, live/dead datanode reports, open-file lease state, pending reconstruction queues, invalidation queues, and datanode capacity statistics. The tests deliberately restart NameNodes or entire clusters to verify that excluded datanodes re-register correctly and that dead/live decommissioned counts survive restart scenarios. The corrupt-replica test depends on generation-stamp state: stopped datanodes keep older replicas, restart, report them, receive invalidations, and later hold valid replicas after reconstruction.

## Dependencies and Integration Points
This class integrates HDFS client APIs (`DistributedFileSystem`, `DFSClient`, `HdfsDataOutputStream`), administrative APIs (`DFSAdmin`, refresh nodes), NameNode internals (`FSNamesystem`, `BlockManager`, `DatanodeManager`, `DatanodeAdminManager`), DataNode test controls (`triggerHeartbeat`, `pauseIBR`, `resumeIBR`, `triggerBlockReport`), HA helpers (`HATestUtil`), simulated storage, JSON node-usage output, and JUnit/AssertJ/GenericTestUtils wait loops. It depends on `AdminStatesBaseTest` for cluster lifecycle and host-file helpers.

## Risks
The tests are intentionally timing-sensitive: heartbeats, block reports, redundancy monitor intervals, and lease recovery are used to expose races. Incorrect changes can introduce flakiness through fixed sleeps, stale `DFSClient` reports after restart, or direct manipulation of `DatanodeDescriptor` state. The assertions also codify client-visible ordering of decommissioned replicas after live replicas; changes to location sorting or replica-count semantics may break downstream client assumptions. Queue-accounting tests are tightly coupled to default vs backoff monitor behavior and should be updated when monitor batching semantics change.

## Test Signals
Strong pass signals are: no live datanode is shut down just because it is decommissioned; files remain readable and correctly replicated; decommissioned capacity and used space are excluded from cluster stats; open files blocking decommission appear in admin listings and disappear after redundancy catches up; pending/tracked monitor counts match configured concurrency; dead decommissioning nodes are requeued without blocking healthy ones forever; corrupt stale replicas are invalidated before the only decommissioning live replica can complete. Failures often indicate regressions in refreshNodes, block reconstruction, NameNode restart persistence, or admin monitor queue logic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDecommission.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDecommissionWithBackoffMonitor.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDecommissionWithBackoffMonitor.java

## Purpose
`TestDecommissionWithBackoffMonitor` reruns the broad replicated-block decommission suite from `TestDecommission` using the alternative `DatanodeAdminBackoffMonitor`. It exists to prove the newer monitor honors the same externally visible decommission semantics as the default monitor while allowing expected differences in monitor-specific batching behavior.

## Important APIs, Types, and Functions
The class overrides `setup()` and `testBlocksPerInterval()`. In `setup`, it calls `super.setup()`, obtains the inherited `Configuration` via `getConf()`, and sets `DFSConfigKeys.DFS_NAMENODE_DECOMMISSION_MONITOR_CLASS` to `DatanodeAdminBackoffMonitor.class` with service type `DatanodeAdminMonitorInterface.class`. It inherits every other test method, helper, cluster lifecycle function, and assertion from `TestDecommission`.

## Control Flow
JUnit runs this subclass as a slow test class. Before each inherited test, the overridden `setup()` mutates the HDFS configuration so any subsequently started MiniDFSCluster NameNode instantiates the backoff monitor for datanode administration. The inherited tests then execute unchanged against replicated-block decommission, recommission, open-file handling, restart behavior, capacity accounting, queue tracking, corrupt replica cleanup, and live/dead node handling. `testBlocksPerInterval()` is overridden as an empty test because that check asserts a default-monitor scan-count contract that is not valid for the backoff monitor.

## State and Persistence Behavior
The class itself persists no state beyond configuration. Its important state effect is class binding: the NameNode's datanode admin monitor implementation is replaced before cluster startup. All file-system state, exclude-host state, block state, open-file state, and NameNode restart behavior are inherited from the parent tests and therefore exercise the same persistence surfaces under a different monitor implementation.

## Dependencies and Integration Points
It depends on the parent suite and on the NameNode config key that selects a `DatanodeAdminMonitorInterface` implementation. It also participates in the parent test's `instanceof TestDecommissionWithBackoffMonitor` branch in `testRequeueUnhealthyDecommissioningNodes`, where one monitor tick has different pending/tracked queue expectations from the default monitor.

## Risks
The main risk is that inherited tests may accidentally assume default-monitor internals. The explicit skip of `testBlocksPerInterval` documents one such incompatibility. New parent tests that assert exact scan counts or pending-node transitions may need backoff-specific branches. Because the class mutates config after `super.setup()`, it relies on clusters being started later by each test rather than during parent setup.

## Test Signals
A passing subclass means the backoff monitor preserves user-visible decommission correctness across the parent suite: safe replication, open-file reporting, restarts, dead-node requeueing, and corrupt replica invalidation. The intentionally empty blocks-per-interval test signals that throughput accounting is not part of this monitor's compatibility contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDecommissionWithBackoffMonitor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDecommissionWithStriped.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDecommissionWithStriped.java

## Purpose
`TestDecommissionWithStriped` is the slow decommission suite for erasure-coded HDFS striped block groups. It verifies that datanode decommissioning preserves EC data availability, internal block indices, block tokens, checksum stability, and reconstruction correctness when some internal blocks are decommissioned, missing, duplicated, busy, or recovered from decommissioned storage.

## Important APIs, Types, and Functions
The fixture uses `MiniDFSCluster`, `DistributedFileSystem`, `DFSClient`, `FSNamesystem`, `BlockManager`, `BlockInfoStriped`, `LocatedStripedBlock`, `DatanodeStorageInfo`, `DatanodeDescriptor`, `DataNodeProperties`, `StripedFileTestUtil`, and `DFSTestUtil`. Important helpers are `createConfiguration()`, `setup(@TempDir)`, `teardown()`, `testDecommission(int, int, int, String)`, `prepareBlockIndexAndTokenList(...)`, `assertBlockIndexAndTokenPosition(...)`, `getDecommissionDatanode(...)`, `writeStripedFile(...)`, `decommissionNode(...)`, `refreshNodes(...)`, `waitNodeState(...)`, `checkFile(...)`, and `getDatanodeOutOfTheBlock(...)`.

## Control Flow
Setup creates local include/exclude files, configures fast heartbeats/block reports/redundancy intervals, lowers EC reconstruction read buffer size, disables load consideration, starts a cluster with `dataBlocks + parityBlocks + 5` datanodes, enables the default EC policy, and marks a test directory as EC. Basic tests write striped files of different sizes, select datanodes that hold internal blocks, snapshot block-index and token associations, decommission one or two nodes via the exclude file and `refreshNodes`, then verify data with `StripedFileTestUtil.checkData`.

More targeted tests manipulate BlockManager internals. Busy-node tests increment pending reconstruction counters on a chosen `DatanodeDescriptor` to ensure the reconstruction scheduler avoids busy nodes while still reconstructing decommissioned internal blocks. Missing-block and failed-replication tests start decommissioning descriptors directly, manually queue EC block replication with `addECBlockToBeReplicated`, stop datanodes, wake pending reconstruction timers, and verify counts of live/decommissioning/decommissioned internal blocks. Recovery tests arrange duplicated internal blocks and decommissioned storage array positions to ensure reconstruction can use appropriate decommissioning sources without corrupting reads.

## State and Persistence Behavior
The class tracks EC policy parameters (`cellSize`, `dataBlocks`, `parityBlocks`, `blockSize`, `blockGroupSize`) as fixture state. Runtime state under test includes local host/exclude files, NameNode block group metadata, `BlockInfoStriped` storage/index arrays, block tokens, datanode admin states, pending replication counters, pending reconstruction queues, and live/dead datanode reports. Cleanup deletes the local decommission directory and shuts down the cluster. There is no disk persistence/restart scenario here; persistence focus is on in-memory EC metadata consistency during decommission operations.

## Dependencies and Integration Points
The suite integrates the EC read/write path (`StripedFileTestUtil`, `ErasureCodingPolicy`), NameNode block-management internals, datanode admin refreshes, token/index metadata in `LocatedStripedBlock`, DataNode lifecycle control, and JUnit ordering/timeouts. It also provides `createConfiguration()` as an extension point used by `TestDecommissionWithStripedBackoffMonitor` to run the same suite with the backoff monitor.

## Risks
These tests are sensitive to exact EC internal block ordering. `assertBlockIndexAndTokenPosition` guards against bugs where sorting locations moves `DatanodeInfo` entries without moving block indices or tokens. Busy-node tests depend on `replicationStreamsHardLimit` and manual pending counters; scheduler changes may require adjusted expectations. Several tests directly mutate descriptor admin state or storage arrays, so they are close to BlockManager internals and may fail after legitimate refactors unless the intended semantics are preserved.

## Test Signals
Passing tests indicate that decommissioned EC replicas are ordered after live replicas, duplicated internal blocks are counted correctly, all required data/parity block indices remain represented, file checksums remain stable, busy nodes are not selected for reconstruction, missing internal blocks can be rebuilt while nodes are decommissioning, and EC pread/read verification succeeds after complex decommission/recovery sequences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDecommissionWithStriped.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDecommissionWithStripedBackoffMonitor.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDecommissionWithStripedBackoffMonitor.java

## Purpose
`TestDecommissionWithStripedBackoffMonitor` runs the erasure-coded striped decommission suite from `TestDecommissionWithStriped` with `DatanodeAdminBackoffMonitor`. Its goal is compatibility coverage for EC block-group decommissioning under the alternative datanode admin monitor.

## Important APIs, Types, and Functions
The only method is `createConfiguration()`. It returns a fresh `Configuration`, sets `DFSConfigKeys.DFS_NAMENODE_DECOMMISSION_MONITOR_CLASS` to `DatanodeAdminBackoffMonitor.class`, and declares the monitor interface as `DatanodeAdminMonitorInterface.class`. The parent class then adds EC, heartbeat, block-report, include/exclude, and block-size settings during setup.

## Control Flow
JUnit instantiates the subclass and calls the parent `setup`. Because the parent invokes `createConfiguration()` before cluster construction, the MiniDFSCluster NameNode uses the backoff monitor while executing all inherited striped decommission tests. No tests are overridden or skipped here, so the full EC compatibility surface runs against the alternate monitor.

## State and Persistence Behavior
The subclass stores no state. Its sole state effect is on configuration before the cluster starts. All EC file state, block-group storage/index arrays, local host files, datanode admin states, and reconstruction queues are managed by the inherited suite.

## Dependencies and Integration Points
It depends on the parent fixture's configuration hook and on the HDFS monitor class-selection config key. It is also tied to the behavior of `DatanodeAdminBackoffMonitor` as an implementation of `DatanodeAdminMonitorInterface`.

## Risks
Because this subclass does not override any parent tests, any parent assertion that depends on default-monitor internals could break this class. The current parent suite is mostly semantic for striped files, so it is appropriate to share. The class creates a plain `Configuration` rather than `HdfsConfiguration`; parent setup must continue to populate all required HDFS defaults and test settings.

## Test Signals
Passing results mean the backoff monitor handles EC decommission scenarios including busy datanodes, missing blocks, failed replication, checksum stability, block-index/token preservation, and recovery with decommissioned storage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDecommissionWithStripedBackoffMonitor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDeprecatedKeys.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDeprecatedKeys.java

## Purpose
`TestDeprecatedKeys` validates backward-compatible Hadoop configuration key aliases used by HDFS. It ensures deprecated property names still populate the modern `DFSConfigKeys` names and, for some keys, that old and new names read back the same configured value.

## Important APIs, Types, and Functions
The single test method `testDeprecatedKeys()` uses `HdfsConfiguration`, `Configuration.set`, `setInt`, `setBoolean`, `setDouble`, and corresponding getters. It checks `DFSConfigKeys.NET_TOPOLOGY_SCRIPT_FILE_NAME_KEY`, `DFS_NAMENODE_REDUNDANCY_INTERVAL_SECONDS_KEY`, `DFS_NAMENODE_REDUNDANCY_CONSIDERLOAD_KEY`, and `DFS_NAMENODE_REDUNDANCY_CONSIDERLOAD_FACTOR`.

## Control Flow
The test creates a new `HdfsConfiguration`, writes deprecated keys such as `topology.script.file.name`, `dfs.replication.interval`, `dfs.replication.considerLoad`, and `dfs.namenode.replication.considerLoad.factor`, then immediately reads modern and legacy aliases. Assertions verify string, integer, boolean, and double values are propagated through the deprecation map.

## State and Persistence Behavior
All state is in-memory `Configuration` state. No cluster, filesystem, XML file, or persistent store is created. The test relies on HDFS configuration initialization registering deprecated keys before lookups occur.

## Dependencies and Integration Points
This is integration coverage between `HdfsConfiguration` static deprecation registration and the generic `Configuration` alias-resolution system. The downstream integration point is any HDFS code that reads only the modern `DFSConfigKeys` constants while users still configure old property names.

## Risks
The test is small but high leverage: removing or renaming deprecated aliases can silently change user deployments. The direct floating-point equality check is safe because the test writes and reads the same literal `5.0`, not a computed value. Additions to deprecation handling should include old-to-new and old-to-old readback when legacy keys remain documented.

## Test Signals
Passing means deprecated topology, redundancy interval, load-consideration, and load-factor keys resolve as expected. Failure indicates a compatibility regression in configuration alias registration or lookup precedence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDeprecatedKeys.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDisableConnCache.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDisableConnCache.java

## Purpose
`TestDisableConnCache` is a regression test for disabling HDFS client peer/socket caching. It verifies that setting the client socket cache capacity to zero prevents reads from leaving cached peers in the `DFSClient` context.

## Important APIs, Types, and Functions
The class defines `BLOCK_SIZE`, `FILE_SIZE`, and one test method, `testDisableCache()`. It uses `HdfsConfiguration`, `HdfsClientConfigKeys.DFS_CLIENT_SOCKET_CACHE_CAPACITY_KEY`, `BlockReaderTestUtil`, `FileSystem.newInstance`, `DFSTestUtil.readFile`, and `DistributedFileSystem.dfs.getClientContext().getPeerCache().size()`.

## Control Flow
The test builds a configuration with socket-cache capacity `0`, starts a one-datanode `BlockReaderTestUtil` mini setup, writes `/testConnCache.dat`, opens a new FileSystem instance using the same configuration, reads the file, and asserts the peer cache size remains zero. Cleanup closes the FileSystem and shuts down the utility in a `finally` block.

## State and Persistence Behavior
The only durable-ish state is a temporary HDFS test file inside the mini cluster. The behavior under test is client-side in-memory peer-cache state after a read. There is no NameNode restart or persisted metadata assertion.

## Dependencies and Integration Points
This test integrates the client config key, block reader setup, DFSClient client context, peer cache implementation, and normal read path. It is directly relevant to resource-management behavior in clients that intentionally disable socket reuse.

## Risks
The test accesses `DistributedFileSystem.dfs` internals and `ClientContext.getPeerCache()`, so refactors of client context visibility or peer-cache accounting may require updates. The assertion should remain about externally intended capacity-zero behavior, not a particular cache implementation.

## Test Signals
Passing means a full file read does not populate the peer cache when capacity is zero. Failure suggests disabled caching is ignored or the peer cache reports retained peers despite the configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDisableConnCache.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDistributedFileSystem.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDistributedFileSystem.java

## Purpose
`TestDistributedFileSystem` is a broad slow integration suite for the HDFS `DistributedFileSystem` client facade and its interaction with `DFSClient`, NameNode RPCs, WebHDFS, storage statistics, erasure-coding administration, encryption/snapshot trash roots, output stream builders, socket timeouts, storage policies, and rack-aware pipeline setup. It verifies both user-facing filesystem behavior and operation-count metrics.

## Important APIs, Types, and Functions
Important helpers are `getTestConfiguration()`, `verifyOpsUsingClosedClient(DFSClient)`, `MyDistributedFileSystem`, `checkStatistics(...)`, `checkReadStatistics(...)`, `testReadFileSystemStatistics(...)`, `checkOpStatistics(...)`, `getOpStatistics(...)`, `testBuilderSetters(...)`, `getMockedIterator(...)`, and `isPathInUserHome(...)`. The tests use `MiniDFSCluster`, `DistributedFileSystem`, `DFSClient`, `LeaseRenewer`, `DFSOpsCountStatistics.OpType`, `GlobalStorageStatistics`, `HdfsDataOutputStreamBuilder`, `HdfsAdmin` trash permissions, `KeyProvider`, `ErasureCodingPolicyManager`, `BlockPlacementPolicyRackFaultTolerant`, `Peer`, `RemoteIterator`, Mockito spies/mocks, and `LambdaTestUtils`.

## Control Flow
Configuration is parameterized by `dualPortTesting` and `noXmlDefaults`. Core client-lifecycle tests create clusters, open files, close filesystems, and then call many `DFSClient` methods to ensure closed clients consistently throw "Filesystem closed". `testDFSCloseOrdering` uses a mocked `DFSClient` to enforce that output streams are closed before delete-on-exit cleanup and final client close. Lease-renewer tests use reflection to check the renewer starts only for writes and stops after the grace period.

Statistics tests reset global HDFS statistics, perform filesystem operations, and compare read/write/large-read counts plus per-operation counters. They cover listing pagination, cache directives, quota, storage policy satisfier, encryption-zone APIs, snapshot listing, trash root lookup, EC policy APIs, concurrent mkdirs, and read-distance bytes using static/script topology mapping. File checksum tests compare HDFS and WebHDFS checksums across random data, zero-byte files, explicit length zero, permission failures, and no-XML/default/dual-port modes.

Feature tests cover located-file status storage IDs/types, custom checksum options, `isFileClosed`, storage policy selection during create, recursive listing under disappearing directories, snapshot-enabled file status, socket read/write timeout behavior through dummy sockets, `getUsed`, close of files being written after deletion, create/append builder semantics, superuser-only operations, EC policy add/remove/enable/disable and topology verification, EC close behavior with committed block groups, and favored-node storage placement. The final rack-failure tests configure `BlockPlacementPolicyRackFaultTolerant` and `ReplaceDatanodeOnFailure.MIN_REPLICATION` to verify when pipeline setup succeeds or fails after one, multiple, or all rack failures.

## State and Persistence Behavior
The suite creates many short-lived MiniDFSClusters and HDFS paths. Persistent surfaces under test include filesystem metadata, leases, open-file state, checksums, storage policies, cache pools/directives, quotas, encryption zones backed by a temporary Java key store provider, snapshot trash roots, EC policy manager state, and NameNode safe-mode/startup behavior. `testNameNodeCreateSnapshotTrashRootOnStartup` explicitly restarts the NameNode after changing `dfs.namenode.snapshot.trashroot.enabled`, then starts a datanode to leave safe mode and checks that `.Trash` is created with the expected permission.

## Dependencies and Integration Points
The class ties together client APIs, NameNode RPC behavior, DataNode block storage metadata, WebHDFS, security/UGI privilege checks, key providers, topology mapping, block placement policies, Mockito verification, and Hadoop global statistics. It is an integration safety net for changes in `DistributedFileSystem`, `DFSClient`, filesystem statistics, EC administration, snapshot trash-root behavior, and block write pipeline setup.

## Risks
Because it covers many surfaces, regressions can be caused by changes outside `DistributedFileSystem` itself. Metrics tests are sensitive to operation-count definitions and list pagination. Timeout tests rely on wall-clock tolerances around socket reads/writes. Trash-root tests combine snapshots and encryption zones and can be affected by permission or safe-mode behavior. Builder tests encode exact flag combinations. Rack-failure tests assert the interaction of block placement and replacement policy thresholds, so block-placement refactors need careful compatibility review.

## Test Signals
Passing signals include consistent closed-client failures, correct lease-renewer lifecycle, accurate global/per-op statistics under single-threaded and concurrent operations, checksum equality across protocols and file sizes, correct storage IDs/types and storage policies, safe recursive listing under namespace races, expected privilege enforcement, correct EC policy lifecycle and topology decisions, proper snapshot/EZ trash-root selection and startup provisioning, reliable socket timeout handling, and correct pipeline setup success/failure according to minimum replication after rack failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDistributedFileSystem.java -->
