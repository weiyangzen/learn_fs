# Research: subset-b-007540

Grouped research for Hadoop HDFS DataNode test sources. Each section preserves the original source path for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestBPOfferService.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestBPOfferService.java

## Purpose
`TestBPOfferService` validates DataNode `BPOfferService` and `BPServiceActor` behavior against one or more NameNodes. It focuses on HA registration, active NameNode selection, full and incremental block reports, command processing, re-registration, block-report lease refresh, slow-node state, and actor command-processing lifecycle.

## Important APIs, Types, and Functions
- `BPOfferService`, `BPServiceActor`, and `BPServiceActor#getIbrManager()` are the primary system under test.
- Mockito-backed `DatanodeProtocolClientSideTranslatorPB` objects emulate NameNode RPC methods: `versionRequest`, `registerDatanode`, `sendHeartbeat`, `blockReport`, `blockReceivedAndDeleted`, `reportBadBlocks`, and `errorReport`.
- `HeartbeatAnswer`, `HeartbeatIsSlownodeAnswer`, and `HeartbeatRegisterAnswer` synthesize `HeartbeatResponse` values containing HA status, DataNode commands, full block report lease IDs, and slow-node flags.
- `setupBPOSForNNs`, `waitForInitialization`, `waitForBothActors`, `waitForBlockReport`, `waitForBlockReceived`, and `countBlockReportItems` are the main harness helpers.
- `DataSetLockManager#lockLeakCheck` is checked after each test to catch leaked dataset locks.

## Control Flow and Behavior
The setup creates a mock DataNode with a `DNConf`, `DataNodeMetrics`, and a spied `SimulatedFSDataset` containing the fake block pool. A `BPOfferService` is built with synthetic NameNode addresses whose `connectToNN` calls return the mock proxies. Tests start the service, wait for actor registration or initialization, manipulate heartbeat responses and command arrays, then trigger heartbeats or block notifications.

`testBasicFunctionality` verifies registration with two NameNodes, block reports to both, and propagation of received-block IBRs to both. `testPickActiveNameNode` advances HA txids and confirms that the actor with the highest active transaction ID is selected, and that stale active claims do not regain active status. `testIgnoreDeletionsFromNonActive` ensures invalidate commands from a standby block report are ignored. `testNNsFromDifferentClusters` verifies one actor fails if namespace information conflicts.

Re-registration and queue behavior are covered by `testMissBlocksWhenReregister`, `testIBRClearanceForStandbyOnReRegister`, `testRefreshNameNodes`, and `testRefreshLeaseId`. These tests stress the boundary between FBR, IBR, actor registration, and block report lease handling. Error and bad-block report tests verify that slow or failing standby calls do not block active processing, that IOExceptions are retried through the actor queue, and that standby exceptions are not requeued.

## State and Persistence
The test uses in-memory mock NameNode state, an in-process simulated dataset, and temporary cluster storage for MiniDFSCluster tests. Stateful fields track heartbeat counts, HA status per NameNode, one-shot commands, lease IDs, timestamps for async queue processing, the current full-block-report lease allocator, and the slow-node flag. Persistent storage is not the target except where MiniDFSCluster creates real DataNode directories for command-processing metric tests.

## Dependencies and Integration Points
The tests integrate `BPOfferService` with `DataNode`, `DNConf`, `DataNodeMetrics`, `FsDatasetSpi`, `SimulatedFSDataset`, NameNode RPC protocol classes, HA heartbeat state, `StorageBlockReport`, `StorageReceivedDeletedBlocks`, `BlockReportContext`, and `MiniDFSCluster`. Metrics assertions use `MetricsAsserts` and DataNode metrics counters such as `NumProcessedCommands`, `SumOfActorCommandQueueLength`, and `ProcessedCommandsOpNumOps`.

## Risks and Edge Cases
The suite targets race-prone code: concurrent re-registration while blocks are being finalized, standby NameNode timeouts while active operations continue, stale block-report leases after RegisterCommand, HA active selection with txid ordering, actor shutdown, and lock leakage. Tests using sleeps and async queues are timing-sensitive; `GenericTestUtils.waitFor` mitigates most but not all flakiness. Because mocks use protocol-level behavior, they may miss failures that depend on real NameNode internal state.

## Test Signals
Strong signals include verified registration calls, block report calls, captured IBR payloads, ignored invalidation calls, active NN identity checks, pending standby IBR size dropping to zero, refreshed NN actor count and registration, lease ID progression from rejected old lease to new lease, slow-node flag toggles, command metrics, and actor command-processing thread termination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestBPOfferService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestBatchIbr.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestBatchIbr.java

## Purpose
`TestBatchIbr` verifies that incremental block reports can be batched while heavy concurrent file creation is happening, and that the NameNode can close files whose blocks are still in `COMMITTED` state before the delayed IBR path catches up.

## Important APIs, Types, and Functions
- `runIbrTest(long ibrInterval)` is the main workload driver.
- `newConf` configures `DFS_BLOCKREPORT_INCREMENTAL_INTERVAL_MSEC_KEY`, `DFS_NAMENODE_MIN_BLOCK_SIZE_KEY`, and best-effort datanode replacement.
- `createExecutor` initializes a fixed pool of 128 worker threads and their thread-local buffers.
- `createFile`, `verifyFile`, `nextBytes`, and `ThreadLocalBuffer` generate deterministic block contents and validate reads.
- `logIbrCounts` reads the `IncrementalBlockReportsNumOps` metric from each DataNode.

## Control Flow and Behavior
For each tested IBR interval, the test starts a four-DataNode MiniDFSCluster, creates 1000 files under `/dir` concurrently, and gives each file a random seed and one to eight blocks. It records aggregate create time, total generated block count, and verification time. As file creation futures complete, read verification futures are submitted so verification overlaps with continued creation. The only test method runs the workload with the default interval and with a 100 ms interval.

## State and Persistence
State is mostly temporary HDFS data in MiniDFSCluster. File names encode seed and block count, making each file self-describing for verification. `ThreadLocalBuffer` avoids per-task allocations and keeps deterministic byte generation isolated per thread.

## Dependencies and Integration Points
The test exercises `DistributedFileSystem`, `MiniDFSCluster`, DataNode IBR scheduling, NameNode block state transitions, DFS client write/read paths, and DataNode metrics. It also depends on the configured minimum block size to allow 1 KiB blocks.

## Risks and Edge Cases
The workload is intentionally concurrent and can expose queueing, batching, and close-vs-IBR races. Runtime can be sensitive to CPU and filesystem performance because it uses 128 threads and 1000 files. Random seeds produce varied block counts, but the deterministic file-name encoding makes failures reproducible for a given file.

## Test Signals
The core signals are successful creation and byte-for-byte verification of all files under both IBR intervals, no failed futures, and logged per-DataNode IBR metric counts that demonstrate batching activity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestBatchIbr.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestBlockCountersInPendingIBR.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestBlockCountersInPendingIBR.java

## Purpose
This test validates DataNode metrics that count pending incremental block report entries by total and by block status: receiving, received, and deleted.

## Important APIs, Types, and Functions
- `BPServiceActor#getIbrManager().addRDBI` adds fake pending IBR entries.
- `ReceivedDeletedBlockInfo` and `BlockStatus` model pending block notifications.
- `DataNode#triggerBlockReport` with `BlockReportOptions#setIncremental(true)` sends the queued IBR.
- `verifyBlockCounters` asserts gauges `BlocksInPendingIBR`, `BlocksReceivingInPendingIBR`, `BlocksReceivedInPendingIBR`, and `BlocksDeletedInPendingIBR`.

## Control Flow and Behavior
The test starts a one-DataNode cluster with long heartbeat and block report intervals so no IBR is sent automatically. It spies on the DataNode-to-NameNode protocol, obtains a `BPServiceActor`, selects a storage from the dataset, adds three pending notifications with different statuses, verifies metrics before send, manually triggers an incremental block report, waits for one `blockReceivedAndDeleted` RPC, then verifies all pending counters return to zero.

## State and Persistence
Pending IBR state lives in the actor's `IncrementalBlockReportManager`. The backing cluster storage is real but the added blocks are fake notification entries rather than files created through DFS. Metrics are sampled from the live DataNode metrics record.

## Dependencies and Integration Points
The test integrates `MiniDFSCluster`, `InternalDataNodeTestUtils.spyOnBposToNN`, `FsDatasetSpi`, `DatanodeStorage`, block-report options, Mockito timeouts, and Hadoop metrics assertions.

## Risks and Edge Cases
It covers manual triggering with background reports disabled and verifies status-specific accounting. The fake block IDs are not backed by actual replicas, so the test is about queue counters and send/drain behavior rather than NameNode block acceptance.

## Test Signals
Signals are absence of pre-existing IBR RPCs, gauge values `3/1/1/1` before send, one observed `blockReceivedAndDeleted` RPC after trigger, and all four gauges returning to zero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestBlockCountersInPendingIBR.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestBlockHasMultipleReplicasOnSameDN.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestBlockHasMultipleReplicasOnSameDN.java

## Purpose
This test verifies NameNode behavior when a single DataNode reports the same block on multiple storages. The expected behavior is that excess replicas on the same DataNode do not inflate block location counts or break block reports.

## Important APIs, Types, and Functions
- `MiniDFSCluster` is started with two DataNodes.
- `DFSTestUtil.createFile` creates a replicated multi-block file.
- `DFSClient#getLocatedBlocks` retrieves observed block locations.
- `BlockListAsLongs.encode`, `StorageBlockReport`, and `BlockReportContext` build a fake full block report containing duplicate storage reports from one DataNode.
- `NameNodeRpc#blockReport` submits that synthetic report.

## Control Flow and Behavior
The test writes a five-block file with replication equal to the two DataNodes. It obtains the located blocks, creates finalized replica objects for the blocks, then builds one identical `BlockListAsLongs` per storage volume on DataNode 0. It sends a block report in which each DataNode storage reports the same block set. After the report, it fetches block locations again and asserts that each block still has two locations with distinct DataNode UUIDs.

## State and Persistence
The cluster has real block files and block metadata. The synthetic report is not created from actual duplicate files on disk; it is a protocol-level report meant to exercise NameNode replica accounting.

## Dependencies and Integration Points
The test exercises NameNode block report processing, DataNode registrations, storage IDs from `FsDatasetSpi.FsVolumeReferences`, `FinalizedReplica`, `BlockListAsLongs`, and DFS client located-block reporting.

## Risks and Edge Cases
The key edge case is duplicate block sightings under one DataNode identity but different storage IDs. The test guards against over-counting replicas and against assertions in NameNode block report processing.

## Test Signals
Signals are successful synthetic block report submission and post-report located blocks with exactly two replicas on two distinct DataNodes for every block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestBlockHasMultipleReplicasOnSameDN.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestBlockPoolManager.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestBlockPoolManager.java

## Purpose
`TestBlockPoolManager` validates how `BlockPoolManager` interprets NameNode and nameservice configuration, creates or refreshes `BPOfferService` instances, filters internal nameservices, and expands a nameservice through DNS resolution.

## Important APIs, Types, and Functions
- A test subclass of `BlockPoolManager` overrides `createBPOS` to return Mockito `BPOfferService` objects and log create, refresh, and stop events.
- Mock `BPServiceActor` instances expose NN IDs and socket addresses.
- `refreshNamenodes(Configuration)` is the primary behavior under test.
- `addNN` writes `dfs.namenode.rpc-address.<ns>` keys via `DFSUtil.addKeySuffixes`.
- `addDNSSettings` enables nameservice resolution and selects `MockDomainNameResolver`.

## Control Flow and Behavior
Each test builds a `Configuration` and invokes `refreshNamenodes`. `testSimpleSingleNS` uses `fs.defaultFS` and expects one creation. `testFederationRefresh` starts with two nameservices, removes one, then adds it back and checks that the retained BPOS is refreshed and the removed one is stopped. `testInternalNameService` verifies that `dfs.internal.nameservices` restricts creation to the internal service. `testNameServiceNeedToBeResolved` configures one nameservice with a mock domain and asserts that it expands into two actor endpoints with generated NN IDs.

## State and Persistence
The test stores state in a `StringBuilder` log and in `BlockPoolManager`'s in-memory map from nameservice ID to `BPOfferService`. No filesystem persistence is involved.

## Dependencies and Integration Points
The file depends on `DFSConfigKeys`, `DFSUtil`, `MockDomainNameResolver`, Mockito, and DataNode block-pool management classes. It is a unit-level configuration parser and lifecycle test rather than a MiniDFSCluster integration test.

## Risks and Edge Cases
Risks covered include accidental recreation instead of refresh, failure to stop removed block pools, ignoring the internal nameservice filter, and bad NN IDs or addresses when DNS resolution expands one logical nameservice into multiple physical endpoints.

## Test Signals
Signals are exact log sequences for create/refresh/stop, `getBpByNameserviceId` membership, actor counts, generated NN IDs, and resolved `InetSocketAddress` values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestBlockPoolManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestBlockPoolSliceStorage.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestBlockPoolSliceStorage.java

## Purpose
This test validates `BlockPoolSliceStorage` path conversion between current block file locations and trash or restore directories.

## Important APIs, Types, and Functions
- `StubBlockPoolSliceStorage` extends `BlockPoolSliceStorage` so the test can call `Storage#addStorageDir` with a dummy root.
- `getTrashDirectory(ReplicaInfo)` maps a block URI under `current` to a corresponding trash directory.
- `getRestoreDirectory(File)` maps a file under the trash root back to the corresponding `current` directory.
- Random helpers generate namespace IDs, block-pool IDs, cluster IDs, IP addresses, and nested subdirectories.

## Control Flow and Behavior
`testGetTrashAndRestoreDirectories` creates one stub storage and iterates over nesting levels 0 to 2. For each nesting level it checks both block data and metadata file names. Trash tests mock `ReplicaInfo#getBlockURI` and compare the returned trash directory to the expected path under `BlockPoolSliceStorage.TRASH_ROOT_DIR`. Restore tests create a random storage, build a deleted-file path under trash, and check that restore resolution points back to `Storage.STORAGE_DIR_CURRENT`.

## State and Persistence
The storage directory is a dummy path and need not exist. State consists of constructed path strings, a single storage directory entry, and random IDs. No actual file moves occur.

## Dependencies and Integration Points
The test uses `Storage`, `BlockPoolSliceStorage`, `ReplicaInfo`, Mockito, `File`, UUIDs, and AssertJ assertions. It is a path-mapping unit test for DataNode block-pool storage layout.

## Risks and Edge Cases
It covers nested `subdir*` paths and both `.meta` and block data filenames. Randomized subdirectory names exercise separator handling, but the test does not cover malformed paths outside the expected storage root.

## Test Signals
Signals are exact string equality between computed and expected trash or restore directories for multiple nesting depths and file suffixes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestBlockPoolSliceStorage.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestBlockRecovery.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestBlockRecovery.java

## Purpose
`TestBlockRecovery` is a broad unit and integration suite for DataNode block recovery. It verifies contiguous replica synchronization rules, failure handling before NameNode commit, striped safe-length calculation, lock behavior while stopping writers, and delayed recovery retry behavior.

## Important APIs, Types, and Functions
- `BlockRecoveryWorker`, `RecoveryTaskContiguous`, `RecoveryTaskStriped`, and `BlockRecord` are the main system-under-test types.
- `ReplicaRecoveryInfo` with `ReplicaState` values `FINALIZED`, `RBW`, `RWR`, and `RUR` drives sync-rule coverage.
- `InterDatanodeProtocol#updateReplicaUnderRecovery` and `DatanodeProtocol#commitBlockSynchronization` are key protocol outputs.
- `initRecoveringBlocks`, `initBlockRecords`, and `testSyncReplicas` assemble synthetic recovery tasks.
- `testStopWorker` verifies lockless behavior for `initReplicaRecovery`, `recoverAppend`, and `recoverClose`.
- Static `testRecoveryWithDatanodeDelayed` is reused by `TestBlockRecovery2` to test slow commit synchronization in a real cluster.

## Control Flow and Behavior
The setup starts a standalone DataNode pointed at a mocked NameNode. Registration and heartbeats are mocked to make the BPOfferService see an active NameNode. The test wraps the DataNode with a spy and constructs a `BlockRecoveryWorker`.

Replica-state tests call `syncBlock` with two mocked inter-DataNode records and assert which replicas are updated and to what length. Finalized replicas must agree on length; RBW/RWR combinations choose the finalized length, RBW length, or minimum length according to recovery rules. Failure-injection tests make `initReplicaRecovery` throw `RecoveryInProgressException` or `IOException`, return zero-length finalized replicas, return RUR replicas, or fail `updateReplicaUnderRecovery`, then assert sync or commit behavior.

Striped recovery coverage constructs `RecoveringStripedBlock` and verifies `getSafeLength` over several block-length suites aligned with the default EC policy. Lock tests create a slow writer owning a replica and then run recovery operations that interrupt and join that writer; while join is in progress the main test calls `getReplicaString`, proving dataset locks are not held while waiting.

## State and Persistence
The standalone DataNode uses a real local `DATA_DIR` that is deleted before and after each test. Tests create RBW replicas and replica streams in the dataset. In MiniDFSCluster integration paths, actual HDFS files, leases, and block recovery timeouts are used.

## Dependencies and Integration Points
This suite integrates DataNode storage (`FsDatasetSpi`), block-pool services, NameNode protocol mocks, recovery protocol classes, replica output streams, checksums, EC policy helpers, MiniDFSCluster, DFS clients, leases, and `GenericTestUtils` fault helpers. It is one of the main tests protecting the DataNode-NameNode recovery protocol contract.

## Risks and Edge Cases
Covered risks include inconsistent finalized replica lengths, skipping stale non-finalized replicas, zero-length recovery commits, all-DataNode failure messages, RUR-only records, mismatched recovery IDs, failed replica updates, avoiding NameNode commit when sync fails, safe-length math for striped block groups, lock contention while interrupting slow writers, and recovery delays exceeding heartbeat intervals. Some assertions only check message prefixes by calling `startsWith` without asserting the result, so those branches may be weaker than intended.

## Test Signals
Signals include Mockito verification of `updateReplicaUnderRecovery` calls and lengths, `commitBlockSynchronization` arguments, absence of commit calls on failure paths, expected exceptions, striped safe-length equality, successful concurrent lock access during writer joins, and real-cluster completion of delayed recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestBlockRecovery.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestBlockRecovery2.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestBlockRecovery2.java

## Purpose
`TestBlockRecovery2` extends block recovery coverage with race, timeout, EC lease recovery, and min-replication scenarios that are easier to express in separate cluster-level tests.

## Important APIs, Types, and Functions
- `startUp` creates a DataNode connected to a mocked active NameNode, similar to `TestBlockRecovery`.
- `testRaceBetweenReplicaRecoveryAndFinalizeBlock` uses a real one-DataNode cluster and concurrent `initReplicaRecovery` versus output-stream close.
- `testRecoveryTimeout` and `testRecoverySlowerThanHeartbeat` call `TestBlockRecovery.testRecoveryWithDatanodeDelayed`.
- `testEcRecoverBlocks` uses a spied `NamenodeProtocols`, `DFSClient`, default EC policy, and delayed `complete` RPC to force lease recovery while close is blocked.
- `testRecoveryWillIgnoreMinReplication` validates recovery when only one of three original replicas remains alive.

## Control Flow and Behavior
Most tests tear down the mocked DataNode fixture and start a MiniDFSCluster. The race test writes and hsyncs a file, starts a recovery thread that sleeps then calls `initReplicaRecovery`, closes the writer, tolerates expected write failure, and then calls `updateReplicaUnderRecovery`. Timeout tests inject delayed or initially lost `commitBlockSynchronization` responses and wait for recovery retry and completion. The EC test delays `complete`, starts stream close in a thread, then repeatedly invokes `recoverLease` until it succeeds before releasing the delayed complete. The min-replication test writes an under-construction replicated file, kills two of three replica DataNodes, expires the lease, waits for file closure, and then waits for replication to restore the target.

## State and Persistence
Tests create real HDFS files, under-construction blocks, leases, dead DataNode state, and EC block groups in MiniDFSCluster. The fixture DataNode has a real temporary data directory that is deleted in teardown.

## Dependencies and Integration Points
The file integrates DataNode recovery APIs, NameNode lease recovery, `DFSClient`, `DistributedFileSystem`, EC policy helpers, `FSNamesystem`, `BlockRecoveryCommand.RecoveringBlock`, heartbeats, and cluster DataNode lifecycle controls.

## Risks and Edge Cases
The suite targets race conditions between writer finalize and recovery, lost recovery commits, recovery work slower than heartbeat scheduling, EC file close blocked by NameNode completion, and recovery below configured `dfs.namenode.replication.min`. Timing waits are long because these are slow integration tests with lease expiration and DataNode death.

## Test Signals
Signals are successful recovery initialization despite close failure, completion under delayed or lost commit synchronization, successful EC `recoverLease` while close is delayed, `dfs.isFileClosed` becoming true after hard lease expiry, and final replication reaching the desired target.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestBlockRecovery2.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestBlockReplacement.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestBlockReplacement.java

## Purpose
`TestBlockReplacement` validates DataNode block replacement and movement behavior, including throttling, invalid replacement cases, pinned blocks, same-node storage-type movement, and HA failover interaction with deletion reports.

## Important APIs, Types, and Functions
- `DataTransferThrottler#throttle` is tested directly.
- `DFSTestUtil.replaceBlock` drives data transfer replacement operations and expected `DataTransferProtos.Status` outcomes.
- `checkBlocks` polls NameNode block locations until expected replicas and locations are observed.
- `MiniDFSCluster`, `DFSClient`, `LocatedBlock`, `DatanodeInfo`, `ExtendedBlock`, and `StorageType` provide cluster and block metadata.
- `InternalDataNodeTestUtils.mockDatanodeBlkPinning` simulates pinned blocks.

## Control Flow and Behavior
The throttler test sends 6 MiB through a 1 MiB/s throttler and checks average throughput. The main replacement test creates a one-block file replicated to three racks, starts a fourth DataNode, identifies source, proxy, and destination nodes, then tests bad proxy, destination-already-has-block, valid replacement, and invalid delete-hint cases. Pinned-block coverage mocks all DataNodes as pinning the block and expects replacement to fail with `ERROR_BLOCK_PINNED`. Same-node movement uses a DataNode with DISK and ARCHIVE storage and replaces a block from DISK to ARCHIVE using the same node as source, proxy, and destination.

The HA test starts a two-NameNode HA cluster, makes NN0 active, writes a block, replaces it to a second DataNode, waits for deletion reporting, fails over to NN1, and asserts the block still has one valid location rather than a standby-generated stale delete.

## State and Persistence
All substantive tests use real MiniDFSCluster block files, storage types, block reports, deletion reports, and NameNode block maps. The replacement operation changes actual replica placement or storage type.

## Dependencies and Integration Points
The test integrates data transfer replacement protocol, rack-aware placement, storage policies/types, pinned block checks, NameNode over-replication deletion, block reports, HA edit tailing, DataNode descriptors through `NameNodeAdapter`, and DFS client block-location APIs.

## Risks and Edge Cases
Covered risks include accepting an invalid proxy source, copying to a destination that already has the block, incorrect delete-hint handling after over-replication, moving pinned blocks, same-node cross-storage transfer, and standby NameNode queuing an invalid delete while an add-block edit is not yet applied.

## Test Signals
Signals include boolean replacement outcomes, expected data-transfer status codes, polled block locations matching target replication and inclusion expectations, storage type changing to ARCHIVE for same-node movement, and stable single replica after HA failover.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestBlockReplacement.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestBlockScanner.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestBlockScanner.java

## Purpose
`TestBlockScanner` validates DataNode block scanner and volume scanner behavior: block iteration, scan scheduling, scan rate limiting, corrupt block detection, cursor persistence across DataNode restarts, multiple block pools, suspect-block rescans, misplaced block handling, append-while-scan safety, recent-access skipping, shutdown join behavior, and iterator robustness when replicas disappear.

## Important APIs, Types, and Functions
- `BlockScanner`, `VolumeScanner`, `VolumeScanner.Statistics`, and `FsVolumeSpi.BlockIterator` are the primary systems under test.
- `TestContext` starts a one-DataNode MiniDFSCluster, optionally federated, collects filesystem handles, block pool IDs, DataNode, scanner, dataset, and volume references.
- `TestScanResultHandler` is a pluggable `ScanResultHandler` configured through `INTERNAL_VOLUME_SCANNER_SCAN_RESULT_HANDLER`; it records good and bad blocks and can block progress with a semaphore.
- `testVolumeIteratorImpl`, `testScanAllBlocksImpl`, `waitForRescan`, and `testDatanodeShutDown` encapsulate shared flows.
- Configuration keys include scanner bytes/sec, scan period, cursor save interval, join timeout, skip-recent-access, and internal scan period in milliseconds.

## Control Flow and Behavior
Iterator tests create files, iterate blocks, save cursor state, rewind, load a saved iterator, and assert no unknown or duplicate unexpected blocks. Scanner enablement tests validate zero or negative bytes/sec disables scanning. Scan-all tests install the recording handler, create ten blocks, release the scanner, and wait for all blocks or repeated rescans depending on scan period. Rate-limit tests throttle scanning to 4096 bytes/s and assert no more than one 4096-byte block per second.

Corruption and cursor tests manipulate real replicas. Corrupt-block handling corrupts one block on disk and expects it in `badBlocks`. Cursor persistence blocks after five scans, shuts down the DataNode, checks `scanner.cursor` under the block pool directory, restarts, and verifies scanning resumes from the saved point. Multiple block-pool scanning waits for three scans in a federated setup and checks aggregate bytes and block counts.

Suspect-block tests mark a scanned block as suspect, verify it is rescanned quickly, then verify recent suspect rate limiting prevents an immediate duplicate rescan. Misplaced-block handling makes one materialized replica unreachable and confirms it is ignored rather than counted good or bad. Append-while-scanning schedules a suspect rescan and appends to the file while scanner reads, expecting no false corruption. Shutdown tests inject scanner interrupt delay and assert DataNode shutdown honors configured join timeout. `testNextBlock` deletes one replica's data and metadata while iterator ordering crosses subdirectories and verifies iteration skips the missing block.

## State and Persistence
This suite heavily exercises on-disk DataNode state: block files, checksum files, scanner cursor files, volume directories, block-pool directories, and materialized replicas. Scanner statistics track bytes scanned in the past hour, blocks scanned since restart/current period, scan errors, scan count, and EOF state. `TestScanResultHandler.infos` is static cross-handler state keyed by storage ID.

## Dependencies and Integration Points
The tests integrate MiniDFSCluster, federated NameNodes, DFS client file creation and append, `FsDatasetSpi`, `FsVolumeImpl`, block iterators, `MaterializedReplica`, `DataNodeFaultInjector`, `VolumeScannerCBInjector`, scanner configuration, and DataNode shutdown. It is both a scanner unit test and a persistent-storage integration test.

## Risks and Edge Cases
Covered risks include stale iterator caches, cursor save/load correctness, scanning too aggressively, corrupt metadata/data handling, scanner persistence across restarts, multiple block-pool traversal, suspect-block priority and rate limiting, ignoring misplaced/unreachable replicas, false positives during append, skipping recent-accessed files, shutdown hanging on scanner threads, and missing files during directory iteration. Static handler state can leak between tests if storage IDs collide, but randomized cluster paths reduce that risk.

## Test Signals
Signals include expected iterator block counts and saved/loaded block equality, scanner enabled/disabled state, good and bad block sets, scanner statistics, presence of `scanner.cursor`, post-restart scan counts, federated scan counts, rate-limited block count bounds, suspect rescan inclusion/exclusion, no bad blocks during append, zero scans for recent-access skipping, and shutdown duration bounded by join timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestBlockScanner.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestBpServiceActorScheduler.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestBpServiceActorScheduler.java

## Purpose
This file unit-tests `BPServiceActor.Scheduler`, which controls when DataNode actors send heartbeats, lifelines, full block reports, and outlier reports to a NameNode.

## Important APIs, Types, and Functions
- `BPServiceActor.Scheduler` is constructed with heartbeat, lifeline, block report, and outlier report intervals.
- Methods under test include `isHeartbeatDue`, `scheduleNextHeartbeat`, `scheduleHeartbeat`, `scheduleBlockReport`, `scheduleNextBlockReport`, `forceFullBlockReportNow`, `scheduleNextLifeline`, `getLifelineWaitTime`, `isOutliersReportDue`, and `scheduleNextOutlierReport`.
- `makeMockScheduler` spies on the scheduler and stubs `monotonicNow`.
- `getTimestamps` supplies boundary and random timestamps including zero, min/max long, near-overflow, positive random, and negative random values.

## Control Flow and Behavior
Every test iterates across timestamp values to detect overflow and sign bugs. Initial state should make heartbeat and block report due. Immediate block report scheduling sets next report time to now, while delayed scheduling chooses a random-ish time before the full delay bound. `scheduleNextBlockReport` is tested for both reset and non-reset modes and for reports delayed past their scheduled time. Heartbeat scheduling is checked to avoid immediate storms after delayed processing. Lifeline scheduling validates due state and nonnegative wait time. Outlier report scheduling validates interval gating.

## State and Persistence
The scheduler is in-memory only. It mutates next heartbeat, lifeline, block report, and outlier report times plus `resetBlockReportTime`.

## Dependencies and Integration Points
The test depends on Mockito spies, AssertJ/JUnit assertions, `Time.monotonicNow`, and `BPServiceActor.Scheduler`. It does not start a DataNode or cluster.

## Risks and Edge Cases
The suite targets arithmetic overflow, negative monotonic values in unit tests, heartbeat storms after delayed processing, forced block report re-scheduling drift, and lifeline wait time under a current time beyond the scheduled time.

## Test Signals
Signals are exact or bounded next-time calculations, due/not-due booleans, modulo alignment for delayed block reports, and nonnegative lifeline wait values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestBpServiceActorScheduler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestCachingStrategy.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestCachingStrategy.java

## Purpose
`TestCachingStrategy` validates HDFS client and DataNode drop-behind caching behavior by intercepting native `posix_fadvise` calls and checking byte ranges dropped from the OS page cache after writes and reads.

## Important APIs, Types, and Functions
- `NativeIO.POSIX.setCacheManipulator` installs `TestRecordingCacheTracker`.
- `Stats` records byte offsets that received `POSIX_FADV_DONTNEED`.
- `createHdfsFile` and `readHdfsFile` optionally call `setDropBehind` on output/input streams.
- Tests use `DFS_DATANODE_DROP_CACHE_BEHIND_READS_KEY`, `DFS_DATANODE_DROP_CACHE_BEHIND_WRITES_KEY`, and client defaults `DFS_CLIENT_CACHE_DROP_BEHIND_READS/WRITES`.
- `BlockSender.CACHE_DROP_INTERVAL_BYTES` and `BlockReceiver.CACHE_DROP_LAG_BYTES` are lowered to 4096 for small deterministic tests.

## Control Flow and Behavior
The class-level setup skips edit-log fsyncs for speed, installs the tracker, and adjusts cache-drop intervals. Write/read tests create a one-DataNode cluster, write a 1 MiB file with explicit or default drop-behind policy, identify the underlying block file, and assert the expected range was dropped or not. The small-read test verifies that a positional 17-byte read does not trigger fadvise. The seek test ensures `FSDataInputStream.seek` works after `setDropBehind(false)` clears a block reader.

## State and Persistence
Temporary HDFS block files are created in MiniDFSCluster. `TestRecordingCacheTracker` keeps a process-global map from native file name to `Stats`. It tracks bytes up to `MAX_TEST_FILE_LEN`.

## Dependencies and Integration Points
The test integrates HDFS read/write streams, DataNode `BlockSender` and `BlockReceiver`, client cache strategy settings, native IO cache manipulation, MiniDFSCluster, and block file lookup via NameNode located blocks.

## Risks and Edge Cases
Covered risks include client defaults overriding DataNode defaults, explicit drop-behind true and false, fadvise lag near write packet boundaries, excessive fadvise for small reads, and stream reader reset after policy changes. Because the tracker calls through to the superclass, behavior can depend on platform native IO support.

## Test Signals
Signals are `Stats` presence or absence, byte-range dropped/not-dropped assertions, successful small-read non-dropping behavior, and successful seek after changing drop-behind policy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestCachingStrategy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestCorruptMetadataFile.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestCorruptMetadataFile.java

## Purpose
This file tests DataNode and metadata-header behavior when block checksum metadata files are truncated or corrupt.

## Important APIs, Types, and Functions
- `BlockMetadataHeader.preadHeader` is tested directly for valid, empty, partial, and invalid headers.
- `DFSTestUtil.getFirstBlock` and `MiniDFSCluster#getBlockMetadataFile` locate the real metadata file for a written HDFS block.
- `LambdaTestUtils.intercept` checks for `BlockMissingException` and `CorruptMetaHeaderException`.

## Control Flow and Behavior
The setup creates a one-DataNode cluster builder and reduces client block acquire failures to speed up failure detection. `testReadBlockFailsWhenMetaIsCorrupt` writes and reads a one-byte file successfully, truncates the `.meta` file to zero, expects read failure, then writes eleven invalid bytes and expects another read failure. It waits for the NameNode block manager to count one corrupt block. `testBlockMetaDataHeaderPReadHandlesCorruptMetaFile` writes a valid seven-byte metadata header, reads it successfully, then checks that empty, partial, and invalid seven-byte headers throw corrupt-header exceptions.

## State and Persistence
The tests directly mutate real metadata files on disk with `RandomAccessFile`. The first test changes cluster-visible corruption state in the NameNode block manager.

## Dependencies and Integration Points
The file integrates MiniDFSCluster, DFS client read path, DataNode block metadata files, `BlockMetadataHeader`, NameNode corrupt block tracking, and Hadoop test exception utilities.

## Risks and Edge Cases
Covered edge cases include zero-length metadata, invalid but non-empty metadata, partial valid headers, invalid full-length headers, and client retry behavior with only one DataNode. Direct file mutation requires careful close handling and can be platform-sensitive if metadata file paths change.

## Test Signals
Signals are intercepted `BlockMissingException` on corrupt metadata reads, corrupt block count reaching one, successful parse of a valid header, and intercepted `CorruptMetaHeaderException` for invalid header cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestCorruptMetadataFile.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDNUsageReport.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDNUsageReport.java

## Purpose
`TestDNUsageReport` validates `DataNodeUsageReportUtil` delta and rate calculations used to report DataNode read/write throughput and block operation rates.

## Important APIs, Types, and Functions
- `DataNodeUsageReportUtil#getUsageReport` is the only behavior under test.
- `DataNodeUsageReport.EMPTY_REPORT` is the expected result for all-zero counters.
- `DataNodeUsageReport` getters validate bytes/sec, blocks/sec, and elapsed read/write times.

## Control Flow and Behavior
The test first requests a report with all zero counters and expects the singleton empty report. It then supplies initial absolute counters and a five-second interval and checks direct division for bytes and blocks per second plus raw read/write times. A subsequent call with interval zero should reuse the previous report. A final call with larger counters and a sixty-second interval checks rates and times are computed as deltas from the previous counters.

## State and Persistence
`DataNodeUsageReportUtil` retains prior counters and the previous report across calls. There is no filesystem or cluster state.

## Dependencies and Integration Points
The test targets the server protocol report object and utility used by DataNode usage reporting, with only JUnit lifecycle and assertions.

## Risks and Edge Cases
It covers zero input, zero elapsed time, initial absolute rate calculation, and subsequent delta calculation. It does not cover counter reset or decreasing counters.

## Test Signals
Signals are equality with `EMPTY_REPORT`, exact integer rate calculations, exact delta times, and report reuse when elapsed time is zero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDNUsageReport.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataDirs.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataDirs.java

## Purpose
`TestDataDirs` validates parsing of `dfs.datanode.data.dir` storage locations, storage type filters based on filesystem, and capacity-ratio parsing for storage locations.

## Important APIs, Types, and Functions
- `DataNode.getStorageLocations(Configuration)` parses configured DataNode data directories.
- `StorageLocation.parseCapacityRatio` parses `[ratio]path` entries.
- Storage types under test include `DISK`, `SSD`, `RAM_DISK`, `NVDIMM`, and `ARCHIVE`.
- `DF` is used to discover the filesystem for `/home` in filesystem-filter tests.

## Control Flow and Behavior
`testDataDirParsing` checks a mixed string with storage type case variants, whitespace, an incomplete `[disk]` entry, and NVDIMM. It then verifies an unknown storage type throws `IllegalArgumentException`, and that entries without explicit type default to DISK. `testDataDirFileSystem` skips macOS, configures DISK and ARCHIVE paths, then filters ARCHIVE out when its configured filesystem does not match and includes it when the configured filesystem equals the actual one. `testCapacityRatioForDataDir` parses valid ratios and checks failures for missing ratios and out-of-range ratios.

## State and Persistence
The tests parse path strings and inspect local filesystem identity for one path. They do not create DataNode storage directories.

## Dependencies and Integration Points
The test integrates `DFS_DATANODE_DATA_DIR_KEY`, `StorageLocation`, `StorageType`, `Path`, local disk filesystem detection through `DF`, and platform checks through `Shell.MAC`.

## Risks and Edge Cases
Covered risks include case-insensitive storage types, whitespace between type and URI, incomplete URI segments, bad media types, default storage type selection, storage type filesystem filtering, malformed capacity ratio config, and ratios outside `[0, 1]`.

## Test Signals
Signals are parsed list sizes, exact storage types and URIs, expected exception messages, and filesystem-filtered location counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataDirs.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeECN.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeECN.java

## Purpose
`TestDataNodeECN` verifies that enabling the DataNode pipeline ECN configuration produces a non-disabled `PipelineAck.ECN` mode in a running DataNode.

## Important APIs, Types, and Functions
- `DFSConfigKeys.DFS_PIPELINE_ECN_ENABLED` controls the feature.
- `MiniDFSCluster` starts the DataNode.
- `DataNode#getECN` returns the selected `PipelineAck.ECN` value.

## Control Flow and Behavior
The test sets pipeline ECN enabled in a plain `Configuration`, starts a one-DataNode MiniDFSCluster, gets the first DataNode's ECN mode, and asserts it is not `PipelineAck.ECN.DISABLED`. The cluster is shut down in a finally block.

## State and Persistence
Only transient MiniDFSCluster state is created. No files are written.

## Dependencies and Integration Points
The test integrates DataNode startup configuration with the data-transfer protocol's `PipelineAck.ECN` enum.

## Risks and Edge Cases
It covers the positive enablement path only. It does not assert a specific non-disabled mode or test the disabled default.

## Test Signals
The signal is a single non-equality assertion that `getECN()` does not return `DISABLED` when the feature flag is true.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeECN.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeErasureCodingMetrics.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeErasureCodingMetrics.java

## Purpose
This test validates DataNode erasure-coding reconstruction metrics for full and partial striped block groups.

## Important APIs, Types, and Functions
- Default EC policy from `StripedFileTestUtil` defines data units, parity units, cell size, and block group geometry.
- `doTest` writes a striped file, kills one DataNode participating in the last block group, forces reconstruction, and waits for completion.
- `getLongMetric` and `getLongMetricWithoutCheck` aggregate metrics across all DataNodes.
- Metrics under test include reconstruction tasks, failed tasks, decoding time, bytes read/written, remote bytes read, and read/decoding/write time millis.
- `setDataNodeDead` marks a DataNode dead in the NameNode block manager.

## Control Flow and Behavior
Setup starts `groupSize + 1` DataNodes, configures block size, enables the default EC policy, and sets it on root. Each test writes a file length chosen to represent full or partial block-group reconstruction. `doTest` generates data, writes the file, waits for block groups to be reported, identifies a DataNode from the last striped block, shuts it down, marks it dead, waits for computed reconstruction work, triggers heartbeats, calculates the expected total block count, and waits for all reconstruction to finish. Tests then assert metric values.

## State and Persistence
The tests create real striped files, block groups, dead DataNode state, and reconstructed blocks. Metrics are sampled from live DataNode metrics records and summed.

## Dependencies and Integration Points
The file integrates MiniDFSCluster, `DistributedFileSystem`, EC policy management, `LocatedStripedBlock`, BlockManager work computation, NameNode adapter access to `DatanodeDescriptor`, and Hadoop metrics assertions.

## Risks and Edge Cases
Covered risks include byte accounting for full group reconstruction, reconstructing a very small partial block, reconstructing a full block in a partial group, reconstructing a partial block in a partial group, and ensuring local reconstruction does not count remote bytes read in these scenarios. Timing depends on block manager work scheduling and heartbeats.

## Test Signals
Signals are zero initial timing counters, one successful reconstruction task, zero failed tasks, positive decoding and timing counters, exact bytes read/written expectations for each file geometry, zero remote bytes read, positive computed datanode work, and reconstruction completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeErasureCodingMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeExit.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeExit.java

## Purpose
`TestDataNodeExit` verifies DataNode liveness behavior as block-pool services exit in a federated cluster, and verifies shutdown tolerates an exception while sending out-of-band messages to peers.

## Important APIs, Types, and Functions
- `MiniDFSNNTopology.simpleFederatedTopology(3)` starts three nameservices.
- `DataNode#getAllBpOs`, `getBpOsCount`, and `isDatanodeUp` expose block-pool service state.
- `BPOfferService#stop` is used to stop selected block-pool services.
- `DataXceiverServer#sendOOBToPeers` is spied to throw in shutdown coverage.

## Control Flow and Behavior
Setup creates a federated three-NameNode MiniDFSCluster and waits for all namespaces active. `testBPServiceState` iterates DataNodes and BPOfferServices and asserts each BPOS is alive. `testBPServiceExit` stops one BPOS and expects the DataNode to remain up, then stops two more and expects the DataNode to go down once all block-pool services are gone. `testSendOOBToPeers` replaces the DataNode xceiver server with a spy that throws `NullPointerException` from `sendOOBToPeers`, then calls `shutdown` and fails if the exception escapes.

## State and Persistence
State is the MiniDFSCluster's live DataNode and BPOfferService threads. No user files are needed. The helper waits up to roughly thirty seconds for BPOS count changes.

## Dependencies and Integration Points
The test integrates DataNode lifecycle management, federated block-pool services, MiniDFSCluster topology, DataXceiverServer shutdown hooks, and Mockito spies.

## Risks and Edge Cases
Covered risks include DataNode exiting too early when only some block pools fail, failing to exit when all block pools are stopped, and shutdown being disrupted by peer OOB notification failures. It does not cover partial restart of a stopped BPOS.

## Test Signals
Signals are all BPOS instances initially alive, exact BPOS count reductions after stop calls, `isDatanodeUp` true after partial stop and false after all services stop, and no thrown exception during shutdown with a failing xceiver server hook.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeExit.java -->
