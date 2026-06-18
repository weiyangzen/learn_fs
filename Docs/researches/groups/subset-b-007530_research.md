# Research: subset-b-007530

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestMaintenanceState.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestMaintenanceState.java

## Purpose
This slow HDFS integration test validates DataNode maintenance admin states for replicated blocks. It covers configuration bounds, transitions among `NORMAL`, `ENTERING_MAINTENANCE`, `IN_MAINTENANCE`, `DECOMMISSION_INPROGRESS`, and `DECOMMISSIONED`, read-location filtering, replication repair, expiration, dead-node handling, restart behavior, write allocation, invalidation, open-file close, and `DFSAdmin -report` output.

## Important APIs, Types, And Functions
The class extends `AdminStatesBaseTest` and relies on its cluster, host-file, node-state, and file-writing helpers. Key tests include `testMaintenanceMinReplConfigRange`, `testTakeNodeOutOfEnteringMaintenance`, `testPutDeadNodeToMaintenance`, `testExpectedReplications`, `testFileBlockReplicationAffectingMaintenance`, `testTransitionToDecommission`, `testMultipleNodesMaintenance`, `testChangeReplicationFactors`, `testTakeDeadNodeOutOfMaintenance`, `testWithNNAndDNRestart`, `testWriteAfterMaintenance`, `testInvalidation`, `testFileCloseAfterEnteringMaintenance`, and `testReportMaintenanceNodes`. Shared verification is in `checkFile`, `checkWithRetry`, `getFirstBlockFirstReplicaUuid`, and `getFirstBlockReplicasDatanodeInfos`.

## Control Flow
Most tests start a `MiniDFSCluster`, create a file with a chosen replication factor, select the first replica location, write host-manager maintenance/decommission state through base helpers, refresh the NameNode, and wait for block placement or admin-state convergence. Verification opens a raw `HdfsDataInputStream`, inspects `LocatedBlock` locations exposed to readers, and separately walks `BlockManager.getStorages` to confirm maintenance replicas remain in the block map while being hidden from client reads. Restart scenarios stop DataNodes, restart NameNodes, then validate that block maps and replica counts converge again.

## State And Persistence
State under test is NameNode-maintained DataNode admin state, maintenance expiration timestamps, live/dead maintenance counters in `FSNamesystem`, block-manager storage membership, pending/under-replicated counts, and file replication state. Persistence-sensitive tests verify maintenance replicas across NameNode restart, DataNode restart, and invalidation decisions. The test also confirms that maintenance nodes are excluded from new block allocation and invalidation, but their replicas remain accounted where appropriate.

## Dependencies And Integration Points
The file integrates `MiniDFSCluster`, `DFSClient`, `DistributedFileSystem`, `FSNamesystem`, `BlockManager`, `DatanodeStorageInfo`, `NameNodeAdapter`, `DFSAdmin`, combined host-file management, `GenericTestUtils.waitFor`, and HDFS protocol classes such as `DatanodeInfo`, `LocatedBlock`, and `LocatedBlocks`.

## Risks
These tests are race-sensitive because maintenance transitions depend on heartbeat, redundancy, and block-placement timing. `checkWithRetry` catches and ignores exceptions while polling, so persistent failures may surface only as timeout behavior. Tests that change shared configuration call `setup`/`teardown` manually inside helper loops and would be fragile if base-class lifecycle behavior changes. Output redirection in `testReportMaintenanceNodes` is process-global and can interfere with concurrent tests.

## Test Signals
Strong signals are exact live/dead/entering/in-maintenance counters, expected `LocatedBlock` replica counts, absence of maintenance nodes in read locations, presence of maintenance replicas in block-manager storage lists, successful recovery after NN/DN restart, successful close of files whose last-block nodes are entering maintenance, and DFSAdmin report text listing only the requested maintenance categories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestMaintenanceState.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestMaintenanceWithStriped.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestMaintenanceWithStriped.java

## Purpose
This test validates DataNode maintenance behavior for erasure-coded striped block groups. It ensures HDFS reconstructs enough live internal blocks when several DataNodes holding striped block pieces enter maintenance, while preserving file checksum correctness.

## Important APIs, Types, And Functions
`setup` creates a `MiniDFSCluster` with the default EC policy, combined host-file management, fast heartbeat/block-report/redundancy intervals, disabled load consideration, and an EC directory. `testInMaintenance` writes a striped file, selects five storages from the first striped block group, places those DataNodes into `IN_MAINTENANCE`, and checks `BlockManager.countNodes`. Helpers include `writeStripedFile`, `maintenanceNode`, `getDfsClient`, and `refreshNodes`.

## Control Flow
The test writes one EC block group, records its checksum, obtains `INodeFile` and `BlockInfoStriped` metadata from the NameNode, then writes maintenance entries into the JSON host file. After `refreshNodes`, it waits for each selected DataNode to reach `IN_MAINTENANCE`, fetches current block locations, resolves the stored striped block, and asserts a split between live reconstructed internal blocks and maintenance-not-for-read internal blocks. It finishes by comparing pre/post-maintenance checksums.

## State And Persistence
State under test includes EC policy assignment, host-file maintenance expiration entries, `FSNamesystem` live maintenance counters, `BlockManager` striped block storage accounting, and checksum-visible file content. The test is not restart-oriented, but it exercises NameNode in-memory reconstruction accounting after maintenance transition.

## Dependencies And Integration Points
It uses `StripedFileTestUtil`, `ErasureCodingPolicy`, `LocatedStripedBlock`, `BlockInfoStriped`, `BlockManager`, `HostsFileWriter`, `CombinedHostFileManager`, `NameNodeAdapter`, and client-side checksum APIs. It directly couples to NameNode internal metadata via `INodeFile` and block-manager storage arrays.

## Risks
The test assumes a stable ordering of storages in the first block group when choosing maintenance nodes. It is timing-sensitive around redundancy work and host refresh. The configured striped read buffer size is deliberately small, so EC reconstruction regressions or checksum path changes can expose failures that are hard to distinguish from maintenance-state bugs.

## Test Signals
Passing signals are zero under-replicated blocks before maintenance, exactly five live in-maintenance DataNodes, six live replicas/internal blocks after reconstruction, five maintenance-not-for-read replicas/internal blocks, and identical file checksums before and after maintenance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestMaintenanceWithStriped.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestMiniDFSCluster.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestMiniDFSCluster.java

## Purpose
This file tests `MiniDFSCluster` construction, isolation, restart, storage, host, topology, and DataNode port-configuration behavior. It protects the local test harness itself rather than a single HDFS feature.

## Important APIs, Types, And Functions
Key tests are `testClusterWithoutSystemProperties`, `testClusterSetStorageCapacity`, `testIsClusterUpAfterShutdown`, `testClusterSetDatanodeHostname`, `testClusterSetDatanodeDifferentStorageType`, `testClusterNoStorageTypeSetForDatanodes`, `testSetUpFederatedCluster`, and `testStartStopWithPorts`. Helpers `newCluster` and `verifyStorageCapacity` construct DataNodes with two volumes and inspect `FsVolumeImpl` capacities through `FsDatasetSpi.FsVolumeReferences`.

## Control Flow
Each test builds a cluster with specific builder options, waits active, then inspects resulting directories, DataNode configuration, NameNode HA state, HTTP address propagation, storage locations, or explicitly assigned ports. The storage-capacity test creates a file and repeatedly restarts DataNodes and NameNodes in different orders, verifying custom capacities survive. The federated test builds a simple two-namespace HA topology, transitions active NameNodes, and restarts individual NameNodes.

## State And Persistence
State includes MiniDFSCluster base directories, DataNode storage type arrays, storage capacities, configured hostnames, HA NameNode state, per-NameNode suffixed configuration keys, shutdown state returned by `isClusterUp`, and DataNode IPC/HTTP ports. Capacity persistence across NameNode/DataNode restarts is the main persistence signal.

## Dependencies And Integration Points
The tests use `MiniDFSCluster.Builder`, `MiniDFSNNTopology`, `DFSUtil.addKeySuffixes`, `DataNode.getStorageLocations`, `FsVolumeImpl`, `NetUtils.getFreeSocketPorts`, JUnit assumptions for Linux-only hostname behavior, and `LambdaTestUtils.intercept` for port-list validation errors.

## Risks
Port selection is explicitly racy because another process can bind a free port before cluster startup. Tests use local filesystem paths and system properties, so cleanup and property restoration matter. The storage-capacity helper assumes exactly two volumes per DataNode and casts to `FsVolumeImpl`.

## Test Signals
Signals include correct base data directory selection without `test.build.data`, exact custom capacities after all restart orderings, `isClusterUp` eventually false after shutdown, preserved `dfs.datanode.hostname`, expected storage-location counts, active/standby HA states, consistent federated HTTP address keys, validation exceptions for mismatched port counts, and exact DataNode info/IPC port mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestMiniDFSCluster.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestMissingBlocksAlert.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestMissingBlocksAlert.java

## Purpose
This file tests NameNode accounting and alerting for missing blocks, including JMX attributes backing the NameNode UI, and verifies replication progress when rack topology changes under `AvailableSpaceBlockPlacementPolicy`.

## Important APIs, Types, And Functions
`testMissingBlocksAlert` creates files, corrupts replicas with `MiniDFSCluster.corruptReplica`, forces checksum reporting by reading through `FSDataInputStream`, checks `DistributedFileSystem` missing/low-redundancy counters, inspects `BlockManager.getUnderReplicatedNotMissingBlocks`, and reads `NameNodeInfo` MBean attributes. `testMissReplicatedBlockwithTwoRack` creates a one-rack cluster, adds another rack, raises replication, and waits for replication.

## Control Flow
The missing-block test starts a single-DataNode cluster with small blocks and fast redundancy checks, creates a normal under-replicated file and a corrupt file, corrupts the first block, reads it to trigger a checksum failure report, waits for missing block count, and validates DFS and JMX counters. It deletes the corrupt file to ensure counters return to zero for missing blocks, then repeats with replication factor one to validate the special missing-repl-one counter.

## State And Persistence
State under test is in-memory NameNode block health accounting: missing blocks, missing replication-one blocks, low-redundancy blocks, and under-replicated-but-not-missing blocks. No restart persistence is tested. The second test exercises rack-aware replication state after adding DataNodes on a new rack.

## Dependencies And Integration Points
Dependencies include `MiniDFSCluster`, `DFSTestUtil`, `ChecksumException`, `ExtendedBlock`, `BlockManager`, JMX `MBeanServer`, `ObjectName` for `Hadoop:service=NameNode,name=NameNodeInfo`, and `AvailableSpaceBlockPlacementPolicy`.

## Risks
The first test polls with sleeps instead of bounded `waitFor` in places, so a counter bug can hang until the test framework timeout. Corruption only occurs on one DataNode, making behavior tightly coupled to single-replica/missing logic. JMX attribute names are externally visible contracts and failures may indicate either NameNode accounting or MXBean exposure regressions.

## Test Signals
Signals are missing block count reaching one, low-redundancy/under-replicated counts matching expected normal-plus-corrupt files, JMX `NumberOfMissingBlocks` and `NumberOfMissingBlocksWithReplicationFactorOne` matching DFS counters, counters returning after delete, and successful replication to factor three after adding a second rack.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestMissingBlocksAlert.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestModTime.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestModTime.java

## Purpose
This test validates HDFS file and directory modification-time semantics for create, rename, delete, close, and NameNode edit-log replay.

## Important APIs, Types, And Functions
`testModTime` creates files/directories, captures `FileStatus.getModificationTime`, performs rename and delete operations, and checks which inode mtimes change. `testModTimePersistsAfterRestart` verifies the file mtime updated by close persists after NameNode restart. Helpers `cleanupFile` and `printDatanodeReport` handle cleanup and diagnostics.

## Control Flow
The first test starts a six-DataNode cluster, creates `testdir1/test1.dat`, records file and directory mtimes, creates another file under the directory, creates a second directory, renames the first file into the second directory, and deletes it. Assertions confirm a file's mtime is preserved by rename, source and destination directories change on rename, unrelated directories do not change on delete, and the deletion target directory does change. The restart test creates an open file, sleeps, closes it, restarts the NameNode, and compares mtimes before and after restart.

## State And Persistence
State under test is HDFS inode modification time and edit-log replay of OP_CLOSE-related mtime updates. `testModTimePersistsAfterRestart` is the persistence-sensitive regression path: the later close time must be reflected after NameNode restart rather than reverting to create/open time.

## Dependencies And Integration Points
The file uses `MiniDFSCluster`, `DFSClient`, `FileSystem`, `FileStatus`, `DFSTestUtil`, `ThreadUtil.sleepAtLeastIgnoreInterrupts`, and datanode reports for diagnostics.

## Risks
Mtime assertions compare coarse wall-clock values; very fast operations or filesystem clock behavior can make equality/inequality checks sensitive. The test prints diagnostics to standard output and relies on real sleeping to force an observable mtime increase. Rename semantics must distinguish file inode mtime from parent directory mtime.

## Test Signals
Signals include nonzero file mtimes, unchanged file mtime after rename, changed parent directory mtimes on namespace updates, unchanged unrelated directory mtime after deletion elsewhere, increased mtime after close, and exact preservation of close mtime after NameNode restart.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestModTime.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestMultiThreadedHflush.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestMultiThreadedHflush.java

## Purpose
This file stress-tests concurrent `hflush` and write behavior on a single `FSDataOutputStream`, including races between repeated flushes and stream close. It also contains a CLI benchmark wrapper for manual throughput/latency measurements.

## Important APIs, Types, And Functions
`WriterThread` extends `SubjectInheritingThread` and repeatedly writes a shared random buffer then calls `hflush`. `testMultipleHflushersRepl1` and `testMultipleHflushersRepl3` call `doTestMultipleHflushers`. `testHflushWhileClosing` creates flusher threads that loop until `ClosedChannelException`. `doMultithreadedWrites` coordinates workers with `CountDownLatch` and captures failures in `AtomicReference`. `CLIBenchmark` exposes the workload through `ToolRunner`.

## Control Flow
The main workload opens a file, performs several empty and non-empty flushes, starts writer threads simultaneously, waits for completion, propagates any thread exception, and closes the stream. The close-race test starts ten flusher threads, writes bytes in the main thread, closes the stream while flushers are active, joins all flushers, and fails on any unexpected exception.

## State And Persistence
State is mostly client-side stream state: current packet buffer, DFSOutputStream close state, DataStreamer interactions, and concurrent error visibility through `AtomicReference`. The test does not restart the cluster or validate persisted bytes directly; successful close and absence of unexpected exceptions are the main durability-adjacent signals.

## Dependencies And Integration Points
It uses `MiniDFSCluster`, `FileSystem`, `FSDataOutputStream.hflush`, `SubjectInheritingThread`, `StopWatch`, `SampleQuantiles`, and Hadoop `Tool`/`Configured` for the benchmark path.

## Risks
The test intentionally maximizes races on one stream, so timing and thread scheduling can affect reproducibility. Shared `SampleQuantiles` is updated by multiple writer threads, relying on the metrics implementation. The close-race expects `ClosedChannelException`; changes in stream-close exception wrapping may break it even if behavior is acceptable.

## Test Signals
Passing signals are no deferred exceptions from writer threads, expected `ClosedChannelException` termination for flushers during close, successful stream close after concurrent writes, and printed latency quantiles for manual benchmark visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestMultiThreadedHflush.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestMultipleNNPortQOP.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestMultipleNNPortQOP.java

## Purpose
This security integration test verifies that a NameNode exposed on multiple RPC ports can apply different SASL quality-of-protection values and communicate the established QOP through block tokens for DataNode data transfer.

## Important APIs, Types, And Functions
The class extends `SaslDataTransferTestCase`. `setup` creates a secure config with auxiliary RPC ports `12001`, `12101`, and `12201`, maps ingress ports to authentication, integrity, and privacy QOPs, sets service RPC separately, and enables NameNode QOP sending. Tests are `testAuxiliaryPortSendingQOP`, `testMultipleNNPort`, and `testMultipleNNPortOverwriteDownStream`. `getHandshakeSecret` decodes `BlockTokenIdentifier` from `DFSTestUtil.getBlockToken`, and `doTest` writes/reads files and checks block locations.

## Control Flow
Tests start a secure three-DataNode cluster, create client URIs for each auxiliary port, and remove the server-side resolver from client configuration. The handshake test confirms the primary port does not include a handshake secret while auxiliary ports do. The port/QOP test performs file operations through each QOP-specific URI and inspects each DataNode's `SaslDataTransferServer.getNegotiatedQOP`. The overwrite test enables downstream QOP override and checks DataNode SASL client/server QOP state.

## State And Persistence
State includes port-to-QOP resolver configuration, block-token handshake message bytes, SASL server negotiated QOP, SASL client target QOP, and file/block placement state. There is no restart persistence; the focus is live negotiation and token contents.

## Dependencies And Integration Points
It integrates NameNode auxiliary RPC ports, `IngressPortBasedResolver`, `HADOOP_RPC_PROTECTION`, HDFS block tokens, `SaslDataTransferServer`, DataNode SASL clients, `FileSystem.get(URI, conf)`, and downstream encryption/QOP override keys.

## Risks
The test uses fixed ports, so parallel test environments can collide. It assumes exact QOP string mappings (`auth`, `auth-int`, `auth-conf`) and that at least two DataNodes appear in upstream positions when downstream QOP is overwritten. Security config ordering is important because service RPC must not resolve to an auxiliary client port.

## Test Signals
Signals include empty handshake secret on the primary port, non-empty secrets on auxiliary ports, successful file reads and three-host block locations for all QOPs, exact DataNode negotiated QOP strings, and downstream override causing at least two target QOPs to become `auth`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestMultipleNNPortQOP.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestParallelRead.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestParallelRead.java

## Purpose
This subclass runs the shared `TestParallelReadUtil` workload over the normal TCP HDFS read path. It is also a regression guard that configured domain socket paths are ignored when both short-circuit local reads and UNIX-domain data traffic are disabled.

## Important APIs, Types, And Functions
`setupCluster` creates an `HdfsConfiguration`, sets `HdfsClientConfigKeys.Read.ShortCircuit.KEY` false, sets `DFS_CLIENT_DOMAIN_SOCKET_DATA_TRAFFIC` false, gives `DFS_DOMAIN_SOCKET_PATH_KEY` a path that should not be created, and delegates to `TestParallelReadUtil.setupCluster`. `teardownCluster` delegates to the base utility.

## Control Flow
JUnit `@BeforeAll` prepares one shared `BlockReaderTestUtil` cluster with default replication. The inherited tests then create files, start multiple `ReadWorker` threads, and exercise copying, direct `ByteBuffer`, mixed, and no-checksum read workloads. `@AfterAll` shuts down the utility cluster.

## State And Persistence
State is inherited from `TestParallelReadUtil`: static cluster utility, `DFSClient`, random seed, file data, open `DFSInputStream`s, and checksum verification flag. This subclass contributes transport configuration state only and has no restart persistence concerns.

## Dependencies And Integration Points
It integrates the HDFS TCP block reader path, `DFSInputStream`, client read configuration, and the base parallel-read workload.

## Risks
Because the subclass has no test methods of its own, any lifecycle failure prevents inherited tests from running. The bogus domain socket path intentionally verifies ignored configuration; if future code validates it unconditionally this test should fail.

## Test Signals
Signals are all inherited parallel-read checks passing while short-circuit and domain socket paths are disabled, plus absence of attempts to create or bind the configured impossible socket path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestParallelRead.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestParallelReadUtil.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestParallelReadUtil.java

## Purpose
This disabled base class supplies the shared multi-threaded DFSInputStream read workload used by TCP, short-circuit, legacy local, and UNIX-domain read subclasses. It verifies concurrent positional and non-positional reads across different API styles produce exact file bytes.

## Important APIs, Types, And Functions
Important types are `ReadWorkerHelper`, `DirectReadWorkerHelper`, `CopyingReadWorkerHelper`, `MixedWorkloadHelper`, `ReadWorker`, and `TestFileInfo`. Static lifecycle helpers are `setupCluster` and `teardownCluster`. `runParallelRead` creates test files and workers, while `runTestWorkload` exercises 1 file/4 workers, 1 file/16 workers, and 2 files/4 workers. Inherited test methods are `testParallelReadCopying`, `testParallelReadByteBuffer`, `testParallelReadMixed`, and `testParallelNoChecksums`.

## Control Flow
Subclasses initialize `BlockReaderTestUtil` and `DFSClient` with a transport-specific configuration. Each workload writes authentic random file data, opens a `DFSInputStream`, creates worker threads, and runs 1024 iterations per worker. Workers randomly choose mostly positional reads and occasional small seek/read operations, then compare every returned byte with the authentic data. Results and errors are collected after thread joins.

## State And Persistence
State includes static cluster/client references, the random generator, per-file authentic data, per-worker byte counters, and `verifyChecksums`. There is no persistence or restart behavior; the focus is concurrent client-side stream/block-reader state under shared access.

## Dependencies And Integration Points
The utility depends on `BlockReaderTestUtil`, `DFSClient`, `DFSInputStream`, `SubjectInheritingThread`, direct `ByteBuffer` reads, positional `read(position, buffer, offset, length)`, checksum toggling, and DataNode client-trace logging.

## Risks
The shared static `Random` is accessed by multiple worker threads and can affect reproducibility. Direct reads synchronize on the stream around seek/read, while positional reads do not; this reflects intended API differences but makes regressions timing-sensitive. `@Disabled` ensures this base is not executed alone; subclasses must provide lifecycle.

## Test Signals
Signals include no worker byte mismatches, no worker error flags, successful copying/direct/mixed/no-checksum workloads, logged throughput summaries, and proper cleanup of all `DFSInputStream`s and the test cluster.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestParallelReadUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestParallelShortCircuitLegacyRead.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestParallelShortCircuitLegacyRead.java

## Purpose
This subclass runs the shared parallel-read workload against the legacy short-circuit local block reader path, with TCP reads disabled so the local path is mandatory.

## Important APIs, Types, And Functions
`setupCluster` sets `DFSInputStream.tcpReadsDisabledForTesting`, clears `DFS_DOMAIN_SOCKET_PATH_KEY`, enables `DFS_CLIENT_USE_LEGACY_BLOCKREADERLOCAL`, disables domain-socket data traffic, enables short-circuit reads, keeps checksum verification enabled, sets `DFS_BLOCK_LOCAL_PATH_ACCESS_USER_KEY` to the current short username, disables domain socket bind-path validation, and delegates to the base setup with replication one.

## Control Flow
The class does only lifecycle setup/teardown. Once configured, inherited tests run copying, direct, mixed, and no-checksum workloads through the legacy local reader. `@AfterAll` shuts down the base cluster.

## State And Persistence
State is the process-global `DFSInputStream.tcpReadsDisabledForTesting` toggle plus legacy block-reader configuration. It has no persistence behavior.

## Dependencies And Integration Points
It integrates `DFSInputStream`, legacy `BlockReaderLocal`, local path access user configuration, `UserGroupInformation`, and `DomainSocket.disableBindPathValidation`.

## Risks
The static TCP-disable flag can leak between tests if teardown does not restore it elsewhere in the suite. The test depends on local filesystem access permissions and current user short name. Empty domain-socket path behavior is specific to the legacy local reader path.

## Test Signals
Signals are inherited parallel-read correctness with TCP disabled and legacy short-circuit enabled, demonstrating the workload can complete only through the intended local block-reader path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestParallelShortCircuitLegacyRead.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestParallelShortCircuitRead.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestParallelShortCircuitRead.java

## Purpose
This subclass runs the shared parallel-read workload against the modern short-circuit local read path using UNIX domain socket file descriptors, with checksum verification enabled.

## Important APIs, Types, And Functions
`setupCluster` skips setup if native domain sockets failed to load, disables TCP reads for testing, creates a `TemporarySocketDirectory`, configures `DFS_DOMAIN_SOCKET_PATH_KEY`, enables short-circuit reads, disables checksum skipping, disables bind-path validation, and delegates to `TestParallelReadUtil.setupCluster`. `before` uses AssertJ assumptions to skip tests when domain sockets are unavailable. `teardownCluster` closes the socket directory and utility cluster.

## Control Flow
The subclass contributes only environment setup. Inherited tests then run the same concurrent read workloads through short-circuit local reads. Lifecycle skips cleanly on platforms without domain socket support.

## State And Persistence
State includes the temporary socket directory, domain socket path template, static TCP-disable flag, and inherited base utility state. There is no persistence behavior.

## Dependencies And Integration Points
It integrates `DomainSocket`, `TemporarySocketDirectory`, HDFS short-circuit read configuration, and the common DFSInputStream workload.

## Risks
Native domain socket support and filesystem permissions affect test availability. The static TCP-disable flag and temporary socket cleanup are shared-process concerns. A platform without domain sockets will skip rather than exercise the code path.

## Test Signals
Signals are inherited read-data correctness with modern short-circuit enabled, checksum verification active, TCP disabled, and proper socket directory cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestParallelShortCircuitRead.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestParallelShortCircuitReadNoChecksum.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestParallelShortCircuitReadNoChecksum.java

## Purpose
This subclass validates the modern short-circuit local read path when client short-circuit checksum verification is skipped.

## Important APIs, Types, And Functions
It mirrors `TestParallelShortCircuitRead` but sets `HdfsClientConfigKeys.Read.ShortCircuit.SKIP_CHECKSUM_KEY` to true. It uses `TemporarySocketDirectory`, `DomainSocket`, `DFS_DOMAIN_SOCKET_PATH_KEY`, `DFSInputStream.tcpReadsDisabledForTesting`, and inherited parallel-read tests.

## Control Flow
Setup is skipped if domain sockets cannot load. Otherwise the cluster is configured for short-circuit local reads over a temporary domain socket path, with TCP reads disabled and checksum skipping enabled. The inherited concurrent workloads verify returned bytes against known data.

## State And Persistence
State is short-lived client/cluster configuration plus the static TCP-disable test flag. No NameNode or DataNode restart persistence is exercised.

## Dependencies And Integration Points
The file integrates the short-circuit local reader, checksum-skip option, domain socket native support, and the base read utility.

## Risks
Because byte validation still happens in the test, corruption should be caught by comparison even when HDFS checksum verification is skipped. Platform domain socket absence skips the path. Static testing flags and socket cleanup remain shared-environment risks.

## Test Signals
Signals are successful inherited copying/direct/mixed/no-checksum workloads while short-circuit checksum skipping is enabled and TCP fallback is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestParallelShortCircuitReadNoChecksum.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestParallelShortCircuitReadUnCached.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestParallelShortCircuitReadUnCached.java

## Purpose
This subclass is a regression test for uncached short-circuit local reads, stale sockets, and encrypted-transfer configuration not interfering with short-circuit local reads.

## Important APIs, Types, And Functions
`setupCluster` creates a temporary socket directory, enables short-circuit reads and domain-socket data traffic, enables data-transfer encryption and block access tokens, disables short-circuit checksum skipping, sets a short DataNode socket reuse keepalive, configures client socket cache expiry/capacity, sets short-circuit streams cache size to zero, disables bind-path validation, disables TCP reads, and delegates to the base setup. `before` skips if domain sockets are unavailable.

## Control Flow
After setup, inherited parallel-read workloads repeatedly open and read files without using the FileInputStream cache. The config deliberately allows stale socket scenarios and domain socket traffic while forcing local read behavior.

## State And Persistence
State includes socket cache and streams cache settings, encrypted transfer and block token settings, temporary socket path, and inherited read workload state. No persistence is tested.

## Dependencies And Integration Points
It integrates HDFS short-circuit local reads, domain socket data traffic, client socket caching, DataNode socket reuse, data transfer encryption, block access tokens, and base DFSInputStream concurrency tests.

## Risks
The test is environment-sensitive to domain socket support. It intentionally combines features that can interact subtly: encryption, tokens, socket caching, and disabled local stream cache. Static TCP-disable state must be isolated by the broader test suite.

## Test Signals
Signals are inherited read correctness with no FileInputStream cache, no TCP fallback, and no failure caused by encryption/token settings when using short-circuit local reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestParallelShortCircuitReadUnCached.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestParallelUnixDomainRead.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestParallelUnixDomainRead.java

## Purpose
This subclass runs the shared parallel-read workload over UNIX domain socket data transfer while short-circuit local reads are disabled.

## Important APIs, Types, And Functions
`setupCluster` skips if domain sockets are unavailable, disables TCP reads, creates a `TemporarySocketDirectory`, configures `DFS_DOMAIN_SOCKET_PATH_KEY`, disables `Read.ShortCircuit.KEY`, enables `DFS_CLIENT_DOMAIN_SOCKET_DATA_TRAFFIC`, disables bind-path validation, and delegates to the base setup with replication one. `before` skips when domain sockets failed to load.

## Control Flow
The subclass sets transport options only. Inherited tests then perform multi-threaded positional and seek/read workloads; because TCP is disabled and short-circuit is off, data transfer should use UNIX domain sockets.

## State And Persistence
State is transport configuration, temporary socket path, and inherited static cluster/client state. No persistence behavior is involved.

## Dependencies And Integration Points
It integrates HDFS domain socket data traffic, `DomainSocket`, `TemporarySocketDirectory`, and common DFSInputStream read paths.

## Risks
Domain socket availability determines whether tests run. The static TCP-disable flag and socket directory cleanup need external lifecycle hygiene. Because short-circuit is disabled, failures distinguish domain socket data-transfer regressions from local short-circuit reader regressions.

## Test Signals
Signals are inherited parallel-read byte correctness and successful workload completion using domain socket data traffic without short-circuit local reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestParallelUnixDomainRead.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestPersistBlocks.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestPersistBlocks.java

## Purpose
This file tests NameNode edit-log persistence of blocks for unclosed, flushed, hflushed, abandoned, partial, appended, and older-version files. It guards against losing block allocation state across NameNode restart and upgrade.

## Important APIs, Types, And Functions
Tests include `testRestartDfsWithFlush`, `testRestartDfsWithSync`, `testRestartDfsWithAbandonedBlock`, `testRestartWithPartialBlockHflushed`, `testRestartWithAppend`, and `testEarlierVersionEditLog`. Shared data arrays are `DATA_BEFORE_RESTART` and `DATA_AFTER_RESTART`. The tests use `DFSClientAdapter`, `HdfsFileStatus`, `LocatedBlocks`, `abandonBlock`, `FSImage`, `FSNamesystem`, `StartupOption.UPGRADE`, and old image tar extraction.

## Control Flow
Core tests create a file with small blocks, write multiple blocks, call either `flush` or `hflush`, wait until length becomes visible, restart the NameNode without closing the stream, and verify length is not lost before writing and closing additional data. Abandoned-block coverage explicitly calls NameNode `abandonBlock` for the last block before restart and verifies length/data exclude it. Partial-block coverage writes a byte into a partial block, restarts, then continues writing to ensure the final block was not prematurely completed. The older-version test loads a Hadoop 1.0 image and appends to a multi-block file after upgrade.

## State And Persistence
State under test is edit-log persistence of block allocations, file length, lease/open-file state, abandoned block removal, partial last-block construction state, appended block state, and upgrade-time block reconstruction from older OP_CLOSE semantics.

## Dependencies And Integration Points
It integrates `MiniDFSCluster`, `FSDataOutputStream`, `FSDataInputStream`, `DFSClient`, NameNode RPCs, `FSImage`, `FSNamesystem`, local test cache tar files, `FileUtil.unTar`, and `StartupOption.UPGRADE`.

## Risks
Tests depend on visible length polling and an external cached tar file for the older-version image. Leaving a stream open through restart intentionally stresses DFSClient retry/lease behavior. The abandoned-block test uses internal NameNode RPC calls and exact block counts.

## Test Signals
Signals include post-restart length at least the pre-restart visible length, exact byte equality before and after restart, abandoned-block length reduced by one block, ability to continue writing a partial block after restart, append data intact after restart, and successful read/append of an upgraded Hadoop 1.0 multi-block file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestPersistBlocks.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestPipelines.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestPipelines.java

## Purpose
This test validates write-pipeline replica state after appending to a closed file, writing more data, and hflushing. It ensures replicas remain in `RBW` while the append stream is open.

## Important APIs, Types, And Functions
The primary test is `pipeline_01`. Lifecycle methods start and stop a three-DataNode `MiniDFSCluster`. `setConfiguration` tunes block size, checksum size, packet size, and socket timeout. `initLoggers` raises NameNode, DataNode, and DFSClient logging. Helper `writeData` generates random write payloads but is not used by the active test.

## Control Flow
`pipeline_01` creates a replicated file, appends to it, writes additional bytes, calls `DFSOutputStream.hflush` through the wrapped stream, fetches located blocks for the tail of the file, then inspects every DataNode's dataset test utility for the replica corresponding to that block. Each replica must exist and be in `HdfsServerConstants.ReplicaState.RBW` before the stream is closed.

## State And Persistence
State under test is DataNode replica lifecycle state, especially the transition back to replica-being-written for an appended block after hflush. The test does not persist through restart.

## Dependencies And Integration Points
It uses `DistributedFileSystem.append`, `DFSOutputStream.hflush`, NameNode block-location RPCs, DataNode dataset test utilities, `Replica`, custom client write packet/checksum configuration, and cluster logging controls.

## Risks
The test directly casts the wrapped stream to `DFSOutputStream`, so changes in `FSDataOutputStream` wrapping could break it. It inspects internal DataNode replica state, making it sensitive to replica state-machine changes. Only one active scenario is covered; `pipeline_02_03` is a placeholder pointing to `TestReadWhileWriting`.

## Test Signals
Signals are successful append/hflush and every DataNode returning a non-null replica for the last block with exact state `RBW`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestPipelines.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestPread.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestPread.java

## Purpose
This file comprehensively tests HDFS positional reads (`pread`) across normal DFS, no-checksum, hedged reads, simulated storage, local filesystem, DataNode restarts, truncation, injected DataNode failures, and changed block locations.

## Important APIs, Types, And Functions
Core helpers are `writeFile`, `pReadFile`, `doPread`, `datanodeRestartTest`, `dfsPreadTest`, `testGetFromOneDataNodeExceptionLogging`, `testFetchFromDataNodeExceptionLoggingFailedRequest`, and `doPreadTestWithChangedLocations`. Tests include `testPreadDFS`, `testPreadDFSNoChecksum`, `testHedgedPreadDFSBasic`, `testHedgedReadLoopTooManyTimes`, `testMaxOutHedgedReadPool`, `testPreadDFSSimulated`, `testPreadLocalFS`, `testTruncateWhileReading`, `testHedgedReadFromAllDNFailed`, and changed-location scenarios. It uses `DFSClientFaultInjector`, `DFSHedgedReadMetrics`, Mockito, `SimulatedFSDataset`, and `BlockMissingException`.

## Control Flow
Basic coverage writes deterministic multi-block files, checks empty-file boundary behavior, then mixes sequential reads and positional reads that cross one or more block boundaries. It verifies pread does not disturb the stream's sequential position and that cached block locations can be refreshed after DataNode restart. Hedged-read tests inject sleeps and checksum/IO exceptions to force loop, pool saturation, current-thread fallback, and all-DN-failed behavior. Logging tests inject failures and count expected retry/error log lines. Changed-location tests move a replica, stop a stale location, reorder reported locations through a spied `DFSClient`, and assert read succeeds within a bounded failure count.

## State And Persistence
State includes DFSInputStream block-location cache, read statistics, hedged read metrics, failure counters, client retry settings, log capture output, file length after truncation, and DataNode replica locations. Persistence is limited to DataNode restart survival for cached streams; most tests focus on live client recovery behavior.

## Dependencies And Integration Points
The file integrates `MiniDFSCluster`, `DistributedFileSystem`, `DFSInputStream`, `DFSClient`, `DFSTestUtil`, `DataTransferProtocol`, `SimulatedFSDataset`, `GenericTestUtils`, Mockito fault injection, executor services, and HDFS hedged-read configuration.

## Risks
This is highly timing-sensitive: hedged reads rely on injected sleeps and thread-pool saturation, while changed-location tests depend on block movement and heartbeat convergence. Static `DFSClientFaultInjector` must be reset after each fault test. Some assertions count exact log messages, which are fragile across logging wording changes.

## Test Signals
Signals include byte-perfect reads for all cross-block pread patterns, preserved sequential stream position after preads, correct read-stat increments, DataNode restart recovery on the same input stream, EOF instead of infinite loop after truncation, hedged metrics and loop counts matching expectations, expected retry/error log counts, `BlockMissingException` when all DNs fail, and successful read after block locations change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestPread.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestQuota.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestQuota.java

## Purpose
This large integration test validates namespace quotas, disk-space quotas, storage-type quotas, DFSAdmin quota commands, WebHDFS content summaries, quota exception behavior, rename accounting, append/flush/close failures, permissions, root quota handling, and content-summary yielding.

## Important APIs, Types, And Functions
Class setup creates a shared three-DataNode `MiniDFSCluster`, redirects stdout/stderr to byte arrays, and opens both DFS and WebHDFS clients. Important tests include `testQuotaCommands`, `testNamespaceCommands`, `testSpaceCommands`, `testQuotaByStorageType`, `testRenameInodeWithStorageType`, `testMaxSpaceQuotas`, `testBlockAllocationAdjustsUsageConservatively`, `testMultipleFilesSmallerThanOneBlock`, `testSetSpaceQuotaWhenStorageTypeIsWrong`, `testHugeFileCount`, command validation helpers for set/clear space quota, `testSpaceQuotaExceptionOnClose`, `testSpaceQuotaExceptionOnFlush`, `testClrQuotaOnRoot`, `testRename`, and `testSpaceQuotaExceptionOnAppend`. Helpers include `runCommand`, `compareQuotaUsage`, `checkContentSummary`, `scanIntoList`, and `checkQuotaAndCount`.

## Control Flow
The command tests invoke `DFSAdmin` through `ToolRunner` or direct `admin.run`, set and clear quotas with numeric and suffixed values, then verify `ContentSummary` and `QuotaUsage`. Namespace and space tests construct nested directory trees, perform mkdir, rename, delete, append, and setReplication operations, and assert quota counts before and after each mutation. Storage-type tests apply storage policies and quotas, then validate quota-consumed/type-consumed accounting through create, delete, and rename. Failure tests deliberately exceed quotas on create, flush, close, and append, then verify files under construction and lease-renewer state are cleaned up.

## State And Persistence
State under test includes namespace quota, space quota, per-storage-type quota, file/directory counts, consumed bytes, consumed bytes by storage type, root quota restoration, content-summary yield count, lease renewal membership, and `FSDirectory` files-under-construction accounting. There is little restart persistence except shared-cluster reinitialization; the emphasis is live namespace/accounting consistency after every operation.

## Dependencies And Integration Points
The file integrates `DistributedFileSystem`, `FileSystem` WebHDFS, `DFSAdmin`, `ContentSummary`, `QuotaUsage`, `StorageType`, storage policies, `LeaseRenewer`, HDFS quota exception classes, `UserGroupInformation.doAs`, `FSImageTestUtil`, `PathUtils`, and stdout/stderr parsing for CLI behavior.

## Risks
The test uses a shared cluster and process-global stream redirection, so failures can leak quota or output state into later tests. Many assertions depend on exact CLI wording and exception behavior. Quota accounting is sensitive to block-size rounding, replication, conservative block-allocation charging, content-summary yielding, and storage policy inheritance. Some tests create secondary clusters and WebHDFS clients that must be shut down cleanly.

## Test Signals
Signals include matching `ContentSummary` and `QuotaUsage`, correct quota fields after DFSAdmin operations, expected `NSQuotaExceededException`, `DSQuotaExceededException`, and `QuotaByStorageTypeExceededException`, WebHDFS content summaries matching DFS, default root namespace quota as `Long.MAX_VALUE`, exact CLI error output for invalid arguments/no access/non-directory/missing directory, zero files under construction after quota failures, empty lease-renewer after flush failure, and matching type-consumed values between quota usage and content summary after storage-policy rename.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestQuota.java -->
