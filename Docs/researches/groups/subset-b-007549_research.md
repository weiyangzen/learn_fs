# subset-b-007549 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestCheckpoint.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestCheckpoint.java

Purpose: Broad regression coverage for HDFS NameNode checkpoint creation, transfer, import, storage locking, namespace persistence, and SecondaryNameNode behavior. It uses `MiniDFSCluster`, `SecondaryNameNode`, `FSImage`, `NNStorage`, `NamenodeProtocols`, `TransferFsImage`, and `CheckpointFaultInjector` to exercise both normal checkpoint flows and many interrupted flows.

Important APIs and helpers: `startSecondaryNameNode`, `checkFile`, `cleanupFile`, `assertLockFails`, `assertClusterStartFailsWhenDirLocked`, `assertParallelFilesInvariant`, and `DoCheckpointThread`. The test suite drives public operations such as `SecondaryNameNode.doCheckpoint`, `NameNode.format`, `DFSAdmin -saveNamespace`, `NamenodeProtocols.rollEditLog`, `saveNamespace`, `restoreFailedStorage`, `TransferFsImage.downloadImageToStorage`, `downloadEditsToStorage`, and `uploadImageFromStorage`. Mockito fault injection hooks simulate failures before/after edit rolling, image upload, MD5 rename, edit rename, merge, and image transfer corruption.

Control flow: Each test starts with isolated MiniDFS storage, installs a mock `CheckpointFaultInjector`, and tears down with a thread leak assertion for SecondaryNameNode threads. The main checkpoint test creates files, performs checkpoints, restarts the cluster with `format(false)`, and verifies namespace survival. Failure tests interrupt checkpoint phases, reset the fault injector, then prove recovery by restarting the NameNode or running a later checkpoint. Concurrent checkpoint tests use two SecondaryNameNodes and `DelayAnswer` to force races around image save or edit manifest retrieval.

State and persistence behavior: The file is centered on persistent metadata: `fsimage_N`, finalized and in-progress edit segments, MD5 files, VERSION storage metadata, storage locks, checkpoint directories, legacy OIV image retention, and most-recent-checkpoint txid. It validates that incomplete transfers do not truncate images, temporary edits are cleaned on SecondaryNameNode startup, out-of-order checkpoints preserve the highest checkpoint txid, duplicate checkpoints are handled gracefully, failed storage directories can be restored, and import checkpoints re-save images only when the active NameNode has no image.

Dependencies and integration points: It integrates with HTTP image transfer via `ImageServlet`/`TransferFsImage`, RPC via `NamenodeProtocol`, DFSAdmin, metrics `NameNodeActivity`, safe mode, delegation tokens, lease manager state in fsimage, federated NameNode topologies, storage directory permissions, and platform-sensitive lock behavior. It also checks namespace identity through `StorageInfo` and `CheckpointSignature` so a SecondaryNameNode cannot exchange files with a different namespace.

Risks: Many tests depend on exact txid counts, local filesystem permission semantics, timing-sensitive checkpoint threads, and Java-version-specific transfer error text. Fault injection must be reset in finally blocks or later tests can inherit artificial failures. Concurrent checkpoint assertions are sensitive to retention policies and file purge timing.

Test signals: Assertions cover file existence and replication after restart, checkpoint txid lists with `FSImageTestUtil.assertNNHasCheckpoints`, metrics counters/gauges for get/edit/put image operations, absence of temp image/edit files, expected exceptions, storage lock failures, correct CLI parsing, lease/delegation-token reload behavior, and parallel file identity across NameNode and SecondaryNameNode current directories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestCheckpoint.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestClientNameNodeAddress.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestClientNameNodeAddress.java

Purpose: Verifies `NameNodeUtils.getClientNamenodeAddress` chooses the correct client-visible NameNode address for WebHDFS redirects across simple, missing, federated, and HA configurations.

Important APIs/types/functions: Uses `HdfsConfiguration`, `FS_DEFAULT_NAME_KEY`, `DFS_NAMESERVICES`, `DFS_HA_NAMENODES_KEY_PREFIX`, and `DFS_NAMENODE_RPC_ADDRESS_KEY`. The only production API under test is `NameNodeUtils.getClientNamenodeAddress(Configuration, String)`.

Control flow: Each test constructs an in-memory configuration, sets the minimum keys for one topology, and asserts either an address string or null. Simple cases cover `hdfs://host:port`, no port, no default FS, and no host. Federation tests distinguish HA logical nameservice results from non-HA physical RPC addresses.

State and persistence behavior: No persistent state is created. The tested state is purely configuration-derived address resolution.

Dependencies and integration points: This is an integration point for WebHDFS redirect generation and client-facing address publication. It guards behavior where the current nameservice ID influences the address returned in federated deployments.

Risks: The test intentionally returns null for incomplete default FS settings; callers must handle null without producing malformed redirects. In HA, the result is the logical nameservice ID, not a host:port endpoint.

Test signals: AssertJ equality checks and JUnit null assertions are the signals. The file is fast and deterministic because it avoids cluster startup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestClientNameNodeAddress.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestClusterId.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestClusterId.java

Purpose: Validates NameNode format behavior around cluster IDs, command-line options, interactive and non-interactive format decisions, force formatting, and reformat-disabled protection.

Important APIs/types/functions: Uses `NameNode.format`, `NameNode.createNameNode`, `StartupOption.FORMAT`, `DFSTestUtil.formatNameNode`, `FSImage`, `NNStorage`, `StorageDirectory`, and `Storage.readPropertiesFile`. Helper `getClusterId` reads the `clusterID` property from a formatted VERSION file.

Control flow: `setUp` disables real JVM exit handling, resets `StartupOption.FORMAT` flags, and points `dfs.namenode.name.dir` at a clean test directory. Tests invoke either direct format or command-line creation, catch `ExitUtil.ExitException`, and inspect VERSION file presence and cluster ID values. Interactive tests replace `System.in` with `Y` or `N`; invalid option tests capture `System.err` and expect usage text.

State and persistence behavior: The persistent state is the NameNode storage directory and its `current/VERSION` metadata. Tests confirm generated cluster IDs are non-empty, explicit IDs are preserved, new formats get new IDs, invalid options do not create VERSION, and reformat-disabled mode rejects non-empty metadata directories while allowing first-time format.

Dependencies and integration points: Integrates CLI parsing, `ExitUtil`, storage metadata, `DFS_REFORMAT_DISABLED`, and user prompts. `NameNode.initMetrics` is required for the reformat-disabled direct format cases.

Risks: Global static `StartupOption.FORMAT` and `System.in/System.err` mutations must be reset or isolated. Assertions rely on filesystem cleanup and on `createNameNode` exiting through `ExitUtil`.

Test signals: Exit statuses, usage text, VERSION file existence, and cluster ID values provide coverage for success, abort, and invalid input paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestClusterId.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestCommitBlockSynchronization.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestCommitBlockSynchronization.java

Purpose: Unit-level regression tests for idempotence and validation in `FSNamesystem.commitBlockSynchronization`, the NameNode path used by DataNodes during lease recovery block commitment.

Important APIs/types/functions: Builds a spied `FSNamesystem` around mocked `FSEditLog`, `FSImage`, `INodeFile`, `BlockInfoContiguous`, `DatanodeStorageInfo`, and `ExtendedBlock`. Helper `makeNameSystemSpy` creates an under-construction block, adds the file to the inode map, and stubs `getStoredBlock`, `getBlockCollection`, `isFileDeleted`, `closeFileCommitBlocks`, and `getEditLog`.

Control flow: Tests call `commitBlockSynchronization` repeatedly with the same block state to verify retries are harmless. Variants cover normal commit, generation-stamp mismatch, delete-block behavior, close-file behavior, and closing with target DataNodes/storage IDs that do not exist in the NameNode.

State and persistence behavior: The test does not write durable state, but it models NameNode in-memory block state transitions from under-construction to completed, block removal on delete, and file close side effects. It verifies the method tolerates a block already committed or already removed.

Dependencies and integration points: The production integration point is DataNode recovery RPC into `FSNamesystem`, edit logging, inode map membership, and block collection lookup.

Risks: Heavy Mockito stubbing can mask integration issues outside the exact modeled path. The important risk being guarded is that DataNode retry or duplicate RPCs must not corrupt namespace state or throw after a successful first commit.

Test signals: Absence of exceptions is the primary success signal for idempotent paths; the mismatched generation-stamp case must throw `IOException`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestCommitBlockSynchronization.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestCommitBlockWithInvalidGenStamp.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestCommitBlockWithInvalidGenStamp.java

Purpose: Cluster-level regression test that the NameNode rejects file completion when the client submits a last block with a generation stamp that does not match NameNode state.

Important APIs/types/functions: Uses `MiniDFSCluster`, `DistributedFileSystem`, `FSDirectory`, `DFSTestUtil.addBlockToFile`, `ExtendedBlock`, and the client protocol method `complete`.

Control flow: The test creates `/file`, obtains its writable `INodeFile`, injects a block through `DFSTestUtil.addBlockToFile`, clones the block, mutates the submitted `ExtendedBlock` generation stamp to `123`, and calls `complete`. It expects an `IOException`, then retries completion with the correct block and expects success.

State and persistence behavior: The in-memory NameNode block map and INode under-construction state are the focus. Durable restart is not tested here; the issue is rejecting a stale or forged commit before namespace completion.

Dependencies and integration points: Exercises real cluster client-to-NameNode completion flow rather than a mocked FSNamesystem. It ties together DFS client identity, file ID, block pool ID, and block generation stamp checking.

Risks: The test is sensitive to the exact error message containing both NameNode and client block descriptions. It manually injects blocks, so helper behavior must stay aligned with NameNode block construction.

Test signals: Expected exception text includes `Commit block with mismatching GS`; a second `complete` call with the correct block returns true.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestCommitBlockWithInvalidGenStamp.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestCorrectnessOfQuotaAfterRenameOp.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestCorrectnessOfQuotaAfterRenameOp.java

Purpose: Verifies HDFS quota accounting remains correct after directory rename operations, including renames between parents with identical and different storage policies.

Important APIs/types/functions: Uses `DistributedFileSystem.rename`, `setQuota`, `setStoragePolicy`, `ContentSummary`, `FSDirectory.resolvePath`, `INodesInPath`, `QuotaCounts`, `BlockStoragePolicySuite`, and `INode.computeQuotaUsage`.

Control flow: The same-policy test creates parent directories with quotas, creates two replicated files under a source directory, renames the source into another parent, and compares `ContentSummary` before/after. It then tests overwrite rename into an existing directory. The different-policy test sets HOT and ONE_SSD policies, computes the source quota usage as it should count under the destination policy, performs the rename, and compares the delta in destination quota counts.

State and persistence behavior: The target state is cached quota usage on `INodeDirectory` and computed quota usage under storage policy inheritance. No restart persistence is checked.

Dependencies and integration points: Integrates filesystem rename semantics, storage policy suite, snapshots' `CURRENT_STATE_ID`, and quota feature accounting.

Risks: Incorrect policy conversion during rename can leave cached quota counts inconsistent with computed usage. Overwrite rename adds risk because source and destination directory trees must be accounted atomically.

Test signals: `ContentSummary.equals` validates same-policy moves; `QuotaCounts.subtract(...).equals(srcCounts)` validates the storage-policy conversion case.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestCorrectnessOfQuotaAfterRenameOp.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestCreateEditsLog.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestCreateEditsLog.java

Purpose: Verifies the `CreateEditsLog` utility emits edit logs that a NameNode can load successfully after being moved into a formatted name directory.

Important APIs/types/functions: Uses `DFSTestUtil.formatNameNode`, `CreateEditsLog.main`, local `FileContext` glob/rename, `MiniDFSCluster.Builder.format(false)`, and `manageNameDfsDirs(false)`.

Control flow: The test deletes prior cluster/test directories, formats a NameNode storage directory, runs `CreateEditsLog -f 1000 0 1 -d <testdir>`, moves generated edit files into `name/current`, then starts a MiniDFSCluster without reformatting or managing dirs. Loading without exception is the pass condition.

State and persistence behavior: Persistent state is generated edits in local storage. The test proves the utility's serialized edit operations are compatible with NameNode startup replay.

Dependencies and integration points: Connects an offline metadata-generation tool to real NameNode edit log loading. It depends on local filesystem globbing and the exact storage layout under `current`.

Risks: This test does not inspect namespace contents after replay; it only guards parse/load compatibility. File cleanup failures can pollute later runs because paths are shared under MiniDFSCluster base directories.

Test signals: Successful NameNode startup and `waitClusterUp` with no thrown exception.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestCreateEditsLog.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestDeadDatanode.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestDeadDatanode.java

Purpose: Ensures NameNode behavior is correct for DataNodes that have transitioned to dead: protocol requests are rejected or redirected appropriately, dead nodes are excluded from placement, and capacity/non-DFS metrics are restored after re-registration.

Important APIs/types/functions: Uses `MiniDFSCluster`, `InternalDataNodeTestUtils.getDNRegistrationForBP`, `DFSTestUtil.waitForDatanodeState`, `DatanodeProtocol.blockReceivedAndDeleted`, `blockReport`, `sendHeartbeat`, `BlockManager.chooseTarget4NewBlock`, `DatanodeManager`, and `RegisterCommand`.

Control flow: `testDeadDatanode` starts a cluster, shuts down its DataNode, waits until the NameNode marks it dead, then submits IBRs, block reports, and heartbeats using the old registration. `testDeadNodeAsBlockTarget` verifies placement excludes the dead local client node. `testNonDFSUsedONDeadNodeReReg` disables heartbeats, marks a node dead, checks aggregate capacity/non-DFS accounting, reenables heartbeats, and waits for live re-registration.

State and persistence behavior: No durable restart is tested. In-memory DataNode descriptor liveness, registration state, aggregate capacity, and non-DFS-used counters are the target state.

Dependencies and integration points: Covers DataNode protocol RPCs, asynchronous incremental block report processing, heartbeat commands, block placement policy, and NameNode capacity accounting.

Risks: Timing-sensitive liveness waits depend on heartbeat intervals. IBR processing is asynchronous, so the test explicitly flushes block operations before checking registration state.

Test signals: Dead IBRs do not re-register the node, block report throws `IOException`, heartbeat returns one register command, placement results exclude the dead descriptor, and aggregate space counters match live descriptors before and after re-registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestDeadDatanode.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestDecommissioningStatus.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestDecommissioningStatus.java

Purpose: Tests DataNode decommissioning status counters, CLI/API reporting, dead-node decommission cases, and recovery when decommissioning risks data loss.

Important APIs/types/functions: Uses `HostsFileWriter`, `DatanodeManager.refreshNodes`, `DatanodeAdminManager`, `DatanodeDescriptor.getLeavingServiceStatus`, `BlockManagerTestUtil.recheckDecommissionState`, `DFSAdmin.report -decommissioning`, `DistributedFileSystem.getDataNodeStats`, and MiniDFSCluster DataNode stop/restart helpers.

Control flow: Setup config disables load-based placement, creates hosts/exclude files, speeds heartbeat/redundancy/decommission intervals, and starts two DataNodes. Helpers add nodes to the exclude file, wait for tracked nodes, verify initial block-report state, and compare expected status counters. Tests decommission one and then two nodes with closed and open files; restart a decommissioning DN; decommission an already-dead DN; and decommission all replicas, then add capacity so reconstruction can recover missing/low-redundancy blocks.

State and persistence behavior: Focuses on in-memory admin state: `DECOMMISSION_INPROGRESS`, `DECOMMISSIONED`, tracked node counts, under-replicated counts, out-of-service-only replicas, and open-file under-replication. It also manipulates exclude-host files as external configuration state.

Dependencies and integration points: Integrates block reports, replication monitor, lease/open-file behavior, DFSAdmin output parsing, Java API DataNode reports, dead DataNode handling, and reconstruction queues.

Risks: These tests are timing-sensitive and depend on block reports reaching the BlockManager before decommission begins. The base test uses sleeps/waits to avoid flakiness around total block counts and descriptor block counts.

Test signals: Expected decommission status triples, DFSAdmin count parsing, Java decommissioning reports, descriptor admin states, missing/low-redundancy counters, pending reconstruction counters, and cleanup through empty exclude files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestDecommissioningStatus.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestDecommissioningStatusWithBackoffMonitor.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestDecommissioningStatusWithBackoffMonitor.java

Purpose: Runs the decommission status scenario with `DatanodeAdminBackoffMonitor` instead of the default monitor, proving the alternative monitor updates externally visible counters correctly.

Important APIs/types/functions: Extends `TestDecommissioningStatus`, reuses its helpers and fixture accessors, and sets `DFS_NAMENODE_DECOMMISSION_MONITOR_CLASS` to `DatanodeAdminBackoffMonitor` implementing `DatanodeAdminMonitorInterface`.

Control flow: Overridden `setUp` builds the base config, injects the backoff monitor class, calls `createCluster`, then stores the inherited cluster/filesystem/hosts writer. The test body mirrors the base `testDecommissionStatus`: create one closed file and one incomplete file, trigger block reports, decommission each node, recheck state, and validate counters and DFSAdmin output. It explicitly calls `BlockManagerTestUtil.recheckDecommissionState` a second time after each decommission because the backoff monitor updates stats on a later pass.

State and persistence behavior: Same decommissioning status state as the base class, but with monitor-specific progression. No durable restart is tested.

Dependencies and integration points: Integration point is pluggable decommission monitor selection through configuration and compatibility with the existing DFSAdmin/API status surfaces.

Risks: Because it subclasses a full test class, inherited tests may also run under the alternate monitor unless overridden by the test runner's method discovery. The explicit second recheck documents a behavioral difference that future monitor changes could affect.

Test signals: Decommissioning node list size, expected leaving-service counters, DFSAdmin report count, and final cleanup through exclude-host reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestDecommissioningStatusWithBackoffMonitor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestDeduplicationMap.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestDeduplicationMap.java

Purpose: Unit test for `FSImageFormatProtobuf.SaverContext.DeduplicationMap`, confirming stable numeric IDs for repeated values during protobuf fsimage save.

Important APIs/types/functions: Uses `DeduplicationMap.newMap()` and `getId(T)`.

Control flow: Creates a map, requests IDs for `"1"`, `"2"`, and `"3"`, then requests the same values again. The first pass should allocate monotonically increasing IDs starting at 1; the second pass should return the previously assigned IDs.

State and persistence behavior: The state is in-memory deduplication metadata used during image serialization. No filesystem or NameNode state is involved.

Dependencies and integration points: The production integration is fsimage protobuf saving, where repeated strings or other values are represented by stable compact IDs.

Risks: A regression could allocate duplicate IDs or reassign an existing value, corrupting references in serialized images.

Test signals: Six `assertEquals` checks validate ID allocation and reuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestDeduplicationMap.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestDefaultBlockPlacementPolicy.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestDefaultBlockPlacementPolicy.java

Purpose: Verifies default block placement choices for local, rack-local, remote, decommissioned, no-local-rack, and DFSNetworkTopology scenarios.

Important APIs/types/functions: Uses `MiniDFSCluster` with configured racks/hosts, `StaticMapping`, `FSNamesystem.startFile`, `NamenodeProtocols.addBlock`, `abandonBlock`, `DatanodeManager`, `DatanodeAdminManager`, `DFSNetworkTopology`, `CreateFlag.NO_LOCAL_RACK`, and `AddBlockFlag.NO_LOCAL_RACK`.

Control flow: Setup creates five DataNodes across racks `/RACK0`, `/RACK2`, and `/RACK3`. `testPlacement` starts files and calls `addBlock` five times, asserting first replica rack when applicable. Dedicated tests map a remote client to a rack, use a local DataNode as client, set NO_LOCAL_RACK flags, rebuild the cluster with DFSNetworkTopology enabled, decommission the only local-rack node, and test an unmapped remote client.

State and persistence behavior: Focuses on live in-memory placement decisions and decommission state. It abandons allocated blocks after each check and does not test restart persistence.

Dependencies and integration points: Integrates NameNode file creation, block allocation, network topology resolution, static rack mapping, and decommission filtering.

Risks: The test checks placement order, especially first replica location, so policy changes that remain valid but alter ordering can fail it. One assertion uses `!=` before `assertNotEquals`, but the meaningful check is the value comparison.

Test signals: Replica count equals replication factor, first replica rack matches expected rack when local/rack-local placement is required, local rack is excluded for NO_LOCAL_RACK and decommissioned cases, and topology implementation is `DFSNetworkTopology` when configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestDefaultBlockPlacementPolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestDeleteRace.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestDeleteRace.java

Purpose: Regression coverage for races between delete/rename and block allocation, lease recovery, commit block synchronization, open access-time updates, and snapshot diff state.

Important APIs/types/functions: Uses a custom `SlowBlockPlacementPolicy`, `SubjectInheritingThread` delete/rename workers, `SnapshotTestHelper`, `DelayAnswer`, spied `DatanodeProtocolClientSideTranslatorPB.commitBlockSynchronization`, `FSNamesystem.renameTo`, `getBlockLocations`, `RwLockMode`, and snapshot manager APIs.

Control flow: Delete/add-block tests slow target selection, delete the file concurrently, and expect the writer's `hsync` to fail with `FileNotFoundException`, with and without snapshots. Rename race writes while renaming a parent and restarts the NameNode to ensure edit replay uses the correct path. Commit synchronization tests create under-construction files across several paths, optionally snapshot, delay DataNode commit RPC, delete an ancestor, optionally recreate directories, then allow the commit and restart NameNodes. Other tests cover lease hard-limit recovery after deleting a snapshotted open file, ordered open/rename lock interleaving, and failed deletion of a snapshottable directory.

State and persistence behavior: The tests stress namespace mutations while block and lease state are mid-transition. Restart checks ensure edit logs remain replayable after races. Snapshot tests ensure deleted inodes retained by snapshots do not corrupt lease recovery or diff reporting.

Dependencies and integration points: Integrates block placement, NameNode write/read locks, lease manager, DataNode recovery RPC, snapshots, edit logging, access-time updates, and FSDirectory removal behavior.

Risks: Highly timing-sensitive tests rely on sleeps, semaphores, and injected delays. Some paths deliberately reinsert a deleted inode into `INodeMap` through Whitebox to reproduce historical edge conditions.

Test signals: Expected exceptions during stale writes, successful NameNode restarts, no propagated commit failure, changed access time after open/rename ordering, successful snapshot diff report, and expected snapshottable-directory count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestDeleteRace.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestDiskspaceQuotaUpdate.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestDiskspaceQuotaUpdate.java

Purpose: Tests cached diskspace and namespace quota accounting across file create, append, hsync length update, quota failures, truncate, quota initialization, and replication changes before/during block commit.

Important APIs/types/functions: Uses `DistributedFileSystem.setQuota`, `setQuotaByStorageType`, `setStoragePolicy`, `ContentSummary`, `FSDirectory.updateCountForQuota`, `INodeDirectory.getDirectoryWithQuotaFeature`, `QuotaCounts`, `DFSOutputStream.hsync(UPDATE_LENGTH)`, `LeaseManager`, and Mockito spying on DataNode-to-NameNode `blockReceivedAndDeleted`.

Control flow: A static four-DataNode cluster is reused. Tests verify quota counts after create and append lengths, hsync while a file is under construction, append/truncate failures over storage quota or storage-type quota, recursive quota cache initialization under many quota directories, and content-summary consistency during block commit. Commit tests stop three DataNodes to control commit timing, spy on the remaining DataNode protocol, optionally change replication inside the block-received callback, and check logs for absence of quota inconsistency messages.

State and persistence behavior: Focuses on cached quota state in `DirectoryWithQuotaFeature`, live file under-construction state, leases, storage-type quotas, and edit-log health after quota exceptions. Several failure tests restart the NameNode to prove edits were not corrupted.

Dependencies and integration points: Integrates NameNode quota cache, DFS client append/truncate paths, storage policies, lease manager, block commit notifications, replication changes, content summary computation, and NameNode logging.

Risks: Quota exceptions during append/truncate must not leave files under construction or dangling leases. Cached space accounting can diverge from computed sizes during partial blocks and replication changes, so tests capture NameNode logs for the historical inconsistency warning.

Test signals: Namespace/storage-space counts equal expected byte lengths times replication, `ContentSummary` equals cached quota, expected quota exceptions occur, files are not UC and have no lease after failed operations, restart succeeds, initialized quota counts remain stable for different update batch sizes, and logs do not contain `BUG: Inconsistent storagespace for directory`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestDiskspaceQuotaUpdate.java -->
