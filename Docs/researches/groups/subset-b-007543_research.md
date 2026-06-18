# subset-b-007543 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestIncrementalBlockReports.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestIncrementalBlockReports.java

Purpose: This JUnit 5 integration test verifies DataNode incremental block report generation and NameNode/standby handling for received, deleted, duplicate, stale, and HA-delayed block notifications.

Important APIs/types/functions: `MiniDFSCluster`, `DataNode`, `BPOfferService`, `BPServiceActor`, `IncrementalBlockReportManager`, `ReceivedDeletedBlockInfo`, `StorageReceivedDeletedBlocks`, `DatanodeProtocolClientSideTranslatorPB.blockReceivedAndDeleted`, `HATestUtil`, `BlockManager.getPendingDataNodeMessageCount`, and `numCorruptReplicas`.

Control flow: The single-NameNode tests spy on the DataNode-to-NameNode protocol, inject fake received/deleted reports into a selected storage, and assert immediate versus heartbeat-delayed RPC behavior. The HA tests rebuild the cluster with two NameNodes, intercept IBRs sent to the standby with Mockito `doAnswer`, coordinate delayed delivery with a `Phaser`, write and append a file to create generation-stamp changes, wait for edit-log catch-up, then replay selected IBRs before failover.

State and persistence behavior: Tests mutate BPOS IBR queues, DataNode storage identity, real HDFS file blocks, standby pending DataNode message queues, and NameNode corrupt-replica accounting. Cluster instances are explicitly shut down and rebuilt for HA scenarios.

Dependencies and integration points: Coverage spans DataNode asynchronous IBR scheduling, block report RPCs, HA edit tailing, standby block-op queues, block generation stamps, and failover promotion behavior.

Risks and test signals: Signals are Mockito RPC counts, `sendImmediately()` clearing, pending-message counts reaching zero or three, and corrupt-replica counts after failover. Timing risks come from sleeps, phaser coordination, async RPC delivery, and standby catch-up assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestIncrementalBlockReports.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestIncrementalBrVariations.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestIncrementalBrVariations.java

Purpose: This class verifies NameNode handling of incremental block reports from one DataNode across combined reports, per-storage split reports, DataNode report coalescing, and reports for newly discovered storages.

Important APIs/types/functions: `MiniDFSCluster`, `DFSClient.getLocatedBlocks`, `StorageReceivedDeletedBlocks`, `ReceivedDeletedBlockInfo`, `NameNodeRpcServer.blockReceivedAndDeleted`, `BlockManager.flushBlockOps`, `DatanodeStorageInfo`, and NameNode metrics counter `BlockReceivedAndDeletedOps`.

Control flow: Setup starts a single-DataNode cluster, captures block pool and registration, and creates test files with ten blocks. `verifyIncrementalBlockReports` walks DataNode volumes, finds one located block per storage, fabricates deleted-block IBR entries, sends them either as one combined RPC or one RPC per storage, flushes block operations, and expects missing-block count to equal storage count. Additional tests delete all file blocks through DataNode notification to prove the DataNode sends one coalesced IBR, and send a received block on a random new `DatanodeStorage`.

State and persistence behavior: Real HDFS file and block-location state is created; later tests inject synthetic deletion/received reports directly into NameNode state. The new-storage test persists storage metadata in `DatanodeDescriptor`.

Dependencies and integration points: It connects DataNode volume IDs, client located-block metadata, NameNode block manager async queues, NameNode activity metrics, and storage discovery through IBRs.

Risks and test signals: Key signals are missing-block count, exact metric increment, and non-null storage info. Timing risk appears in the fixed sleep after triggering DataNode report emission.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestIncrementalBrVariations.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestLargeBlockReport.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestLargeBlockReport.java

Purpose: This integration test validates that very large DataNode block reports are rejected or accepted according to the RPC maximum data length configuration.

Important APIs/types/functions: `IPC_MAXIMUM_DATA_LENGTH`, `MiniDFSCluster`, `BPOfferService.getActiveNN`, `DatanodeProtocolClientSideTranslatorPB.blockReport`, `BlockReportContext`, `BlockListAsLongs.decodeLongs`, and `StorageBlockReport`.

Control flow: Each test configures the IPC length limit, starts a one-DataNode cluster, obtains the active NameNode proxy and current storage ID, constructs a fake six-million-block report using old-style long-list decoding, and invokes `blockReport`. The low-limit case expects the RPC to fail; the high-limit case expects the call to complete.

State and persistence behavior: The block report content is synthetic and not intended to represent persisted blocks. The persistent state under test is RPC framing/deserialization acceptance rather than NameNode block map mutation.

Dependencies and integration points: It exercises Hadoop IPC server request-size checks, protobuf deserialization path tolerance, DataNode protocol block-report RPC, and MiniDFSCluster block-pool registration setup.

Risks and test signals: The rejection test intentionally avoids asserting exception type or message because server disconnect details are log-dependent. Runtime and memory pressure are risks due to constructing enormous report payloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestLargeBlockReport.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestNNHandlesBlockReportPerStorage.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestNNHandlesBlockReportPerStorage.java

Purpose: This subclass runs the shared `BlockReportTestBase` scenarios while sending one block report RPC per storage, matching modern post-HDFS-2832 DataNode behavior.

Important APIs/types/functions: `BlockReportTestBase`, `sendBlockReports`, `DatanodeRegistration`, `StorageBlockReport`, `NameNodeRpcServer.blockReport`, and `BlockReportContext`.

Control flow: The override loops through the provided `StorageBlockReport[]`, wraps each entry in a singleton array, and sends each RPC with `BlockReportContext(reports.length, i, System.nanoTime(), 0L)` so the NameNode can treat them as parts of one full-report cycle.

State and persistence behavior: This file owns no setup state; all files, blocks, storage mutations, and assertions come from the base test. Its behavior changes only how report batches are transported and indexed.

Dependencies and integration points: It integrates the base block-report correctness matrix with the NameNode path for split storage reports and report-context part numbering.

Risks and test signals: Signals are inherited from `BlockReportTestBase`. Local risk is that incorrect total/index context would make the base tests fail through NameNode block-report processing rather than obvious local assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestNNHandlesBlockReportPerStorage.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestNNHandlesCombinedBlockReport.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestNNHandlesCombinedBlockReport.java

Purpose: This subclass runs `BlockReportTestBase` with legacy behavior where one DataNode sends all storage reports in a single combined block-report RPC.

Important APIs/types/functions: `BlockReportTestBase`, `sendBlockReports`, `DatanodeRegistration`, `StorageBlockReport[]`, `NameNodeRpcServer.blockReport`, and `BlockReportContext`.

Control flow: The override logs the registration and sends the complete `reports` array in one RPC with a one-part `BlockReportContext(1, 0, System.nanoTime(), 0L)`.

State and persistence behavior: All durable block, storage, and NameNode state changes are inherited from the base class. This file only controls report batching semantics and therefore tests compatibility with older logical-single-storage DataNode behavior.

Dependencies and integration points: It connects the base NameNode block-report tests to the combined-report protocol path and verifies the NameNode still accepts reports that are not split per storage.

Risks and test signals: Signals are inherited base assertions about block report correctness. The main local risk is regression in backward compatibility if combined report contexts are mishandled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestNNHandlesCombinedBlockReport.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestProvidedReplicaImpl.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestProvidedReplicaImpl.java

Purpose: This unit test validates `ProvidedReplica` read behavior for finalized replicas backed by byte ranges in an external local file.

Important APIs/types/functions: `FinalizedProvidedReplica`, `ProvidedReplica.blockDataExists`, `getBlockURI`, `getDataInputStream`, `getBlockDataLength`, `BoundedInputStream`, `ReadableByteChannel`, and `FileSystemTestHelper`.

Control flow: Setup creates a deterministic local backing file if missing, divides it into 128 KiB provided replicas, and records one `FinalizedProvidedReplica` per range. The test iterates replicas, asserts backing data exists and the block URI matches, then compares each replica stream against the corresponding slice of the local file. After deleting the file, it asserts every replica reports missing backing data.

State and persistence behavior: The test creates and deletes a real local file under the test root. Replica objects hold URI, offset, length, generation stamp, and configuration but no HDFS DataNode cluster state.

Dependencies and integration points: It covers the provided-storage replica abstraction, Java stream/channel reads, range-bounded comparison, and local filesystem URI handling.

Risks and test signals: Signals are byte-for-byte equality, URI equality, and `blockDataExists` before/after deletion. Risks include leftover local files, slow byte-by-byte file creation, and limited coverage of nonzero seek offsets beyond stream start.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestProvidedReplicaImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestReadOnlySharedStorage.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestReadOnlySharedStorage.java

Purpose: This integration test verifies `READ_ONLY_SHARED` DataNode storage semantics: read-only replicas are returned as read locations but do not count as live replicas or corrupt replicas for replication accounting.

Important APIs/types/functions: `SimulatedFSDataset`, `DatanodeStorage.State.READ_ONLY_SHARED`, `MiniDFSCluster.dataNodeConfOverlays`, `cluster.injectBlocks`, `DFSClient.getLocatedBlocks`, `BlockManager.countNodes`, `NumberReplicas`, `BlockManagerTestUtil`, and `DFSTestUtil.waitForReplication`.

Control flow: Setup starts three simulated DataNodes, configures one DataNode storage as `READ_ONLY_SHARED`, creates a one-block file with replication one, identifies the normal and read-only nodes, injects the block into the read-only node, and waits for two locations. Tests then raise replication, stop the normal replica host to force recovery from a read-only source, and report a read-only replica as bad.

State and persistence behavior: The test mutates NameNode block maps, DataNode storage reports, simulated dataset block inventory, replication factor, and dead-node/corrupt-replica state. Read-only injected blocks are not counted as normal persistent replicas.

Dependencies and integration points: It covers storage-state propagation, client block-location responses, NameNode replication accounting, inter-DataNode replication from read-only replicas, and bad-block reporting.

Risks and test signals: Signals are location counts, live/corrupt/excess/low-redundancy counts, and successful replication restoration. Risks are retry-loop timing and reliance on simulated storage fidelity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestReadOnlySharedStorage.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestRefreshNamenodes.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestRefreshNamenodes.java

Purpose: This test validates that a DataNode refreshes its NameNode/BPOfferService list in a federated cluster and does not deadlock when lifeline configuration changes while offer-service locks are delayed.

Important APIs/types/functions: `MiniDFSNNTopology`, `MiniDFSCluster.addNameNode`, `DataNode.getAllBpOs`, `BPOfferService`, `BPServiceActor.getNNSocketAddress`, `DataNode.refreshNamenodes`, `DataNodeFaultInjector.delayWhenOfferServiceHoldLock`, and `DFS_NAMENODE_LIFELINE_RPC_ADDRESS_KEY`.

Control flow: The federation test starts with one NameNode, adds three more, then compares the set of NameNode addresses in the cluster with the set held by the DataNode’s BPS actors. The deadlock test starts three DataNodes, injects a one-second delay while offer service holds a lock, mutates one DataNode’s nameservice/lifeline configuration, and calls `refreshNamenodes` under a ten-second timeout.

State and persistence behavior: It mutates in-memory cluster topology and DataNode configuration; no file data is written. The persistent signal is DataNode BPOS membership reflecting current NameNode topology.

Dependencies and integration points: It covers federation topology updates, DataNode BPOS lifecycle, BP service actor address mapping, lifeline RPC address parsing, and fault-injection hooks.

Risks and test signals: Signals are BPOS counts, empty symmetric address difference, and timeout-free refresh. Risks include hard-coded ports and global `DataNodeFaultInjector` side effects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestRefreshNamenodes.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestSimulatedFSDataset.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestSimulatedFSDataset.java

Purpose: This unit test exercises the in-memory `SimulatedFSDataset` implementation for factory registration, block writes/reads, metadata, storage accounting, block reports, block injection, invalidation, invalid-block failures, and concurrent block-pool creation.

Important APIs/types/functions: `SimulatedFSDataset.setFactory`, `FsDatasetSpi.Factory`, `createRbw`, `ReplicaInPipeline.createStreams`, `finalizeBlock`, `getBlockReports`, `injectBlocks`, `invalidate`, `getMetaDataInputStream`, `BlockMetadataHeader`, `DataChecksum.Type.NULL`, and `SubjectInheritingThread`.

Control flow: Helpers create deterministic block IDs and lengths, write simulated bytes through RBW streams, finalize blocks, and read them back using `simulatedByte`. Tests verify empty/non-empty reports, inject block reports into another dataset, enforce capacity failure, invalidate two blocks, and create thousands of block pools concurrently while immediately creating a temporary replica in each.

State and persistence behavior: State is in-memory per block pool and storage; capacity, DFS-used, remaining space, replica maps, block reports, and null-checksum metadata are the core persisted model. Negative block IDs are explicitly tested.

Dependencies and integration points: It validates the simulated dataset contract used by MiniDFSCluster tests without requiring physical block files, while still matching `FsDatasetSpi` report and storage APIs.

Risks and test signals: Signals are exact byte counts, block-report counts/lengths, IOExceptions for invalid/capacity cases, and no concurrency failures. Risks include use of Java `assert` in one threaded check and limited realism versus `FsDatasetImpl`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestSimulatedFSDataset.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestSimulatedFSDatasetWithMultipleStorages.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestSimulatedFSDatasetWithMultipleStorages.java

Purpose: This subclass reuses `TestSimulatedFSDataset` with two configured data directories to validate multi-storage behavior in the simulated dataset.

Important APIs/types/functions: `DFS_DATANODE_DATA_DIR_KEY`, `SimulatedFSDataset.getStorageReports`, inherited `pTestSimulatedFSDataset`, and inherited block-report assertions.

Control flow: The constructor sets the inherited expected storage count to two. Setup calls the parent configuration factory setup and then sets the DataNode data-dir key to `data1,data2`. The local test instantiates a simulated dataset and asserts two storage reports; inherited tests now expect two storage block-report entries.

State and persistence behavior: Storage state is in-memory but follows the configured DataNode directory list. No local directories are required because this is simulated storage.

Dependencies and integration points: It checks that common `SimulatedFSDataset` behavior remains correct when the DataNode presents multiple storages, which affects block-report map sizes and storage-report arrays.

Risks and test signals: Signal is the two-entry storage report count plus inherited block-report storage count assertions. Risk is low, but it depends on configuration parsing matching real DataNode storage semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestSimulatedFSDatasetWithMultipleStorages.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestStartSecureDataNode.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestStartSecureDataNode.java

Purpose: This security-oriented integration test verifies secure MiniDFSCluster startup with an externally supplied Kerberos KDC and clear failures when secure DataNode streaming or HTTP bind ports are already occupied.

Important APIs/types/functions: `MiniDFSCluster`, secure DataNode/NameNode configuration keys, `SecurityUtilTestHelper.isExternalKdcRunning`, JUnit `assumeTrue`, `SecureDataNodeStarter.getSecureResources`, `DFS_DATANODE_ADDRESS_KEY`, `DFS_DATANODE_HTTP_ADDRESS_KEY`, `NetUtils.getFreeSocketPort`, and `BindException`.

Control flow: The secure-start test first skips unless an external KDC is declared running, reads NameNode/DataNode principals and keytabs from system properties, configures Kerberos authentication and low DataNode ports, starts a one-DataNode MiniDFSCluster with DataNode address checking, and asserts the DataNode is up. The bind tests reserve a server socket on the intended streaming or web address, call `SecureDataNodeStarter.getSecureResources`, and expect `BindException` containing the occupied address.

State and persistence behavior: The class mutates Hadoop security configuration, consumes external principal/keytab system properties, and binds local network ports. It does not focus on HDFS file persistence; state under test is process/socket startup configuration and secure resource acquisition.

Dependencies and integration points: It crosses HDFS secure mode config, external KDC/keytab setup, MiniDFSCluster secure startup, DataNode privileged port/resource setup, HTTP/streaming bind paths, and local socket binding.

Risks and test signals: Signals are successful cluster startup for valid external Kerberos config and `BindException` for occupied ports. Risks include platform/network sensitivity, privileged-port/root assumptions, skipped coverage without external KDC properties, and local service interference.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestStartSecureDataNode.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestStorageReport.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestStorageReport.java

Purpose: This integration test ensures DataNode heartbeat storage reports include configured storage type and normal storage state.

Important APIs/types/functions: `MiniDFSCluster.storageTypes`, `StorageReport`, `DatanodeStorage`, `StorageType.SSD`, `DataNodeTestUtils.triggerHeartbeat`, `DatanodeProtocolClientSideTranslatorPB.sendHeartbeat`, `SlowPeerReports`, and `SlowDiskReports`.

Control flow: Setup starts a one-DataNode cluster with two SSD storages. The test installs a spy on the DataNode-to-NameNode protocol, triggers a heartbeat, captures the `StorageReport[]` passed to `sendHeartbeat`, and asserts each report has the SSD type and `DatanodeStorage.State.NORMAL`.

State and persistence behavior: No file data is created. The relevant state is DataNode volume configuration, block-pool ID, and heartbeat payload metadata.

Dependencies and integration points: It tests storage-type propagation from cluster builder to DataNode storage reports and through the NameNode heartbeat RPC shape, including compatibility with slow peer/disk report parameters.

Risks and test signals: Signals are captured heartbeat arguments and per-report assertions. Risk is low but tied to Mockito signature matching; adding heartbeat parameters would require test updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestStorageReport.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestTransferRbw.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestTransferRbw.java

Purpose: This test verifies transferring a replica-being-written from one DataNode to another while preserving block identity, generation stamp, and visible length.

Important APIs/types/functions: `ReplicaBeingWritten`, `LocalReplicaInPipeline`, `FsDatasetTestUtil.getReplicas`, `DFSTestUtil.transferRbw`, `DFSClientAdapter.getDFSClient`, `BlockOpResponseProto`, `Status.SUCCESS`, and `DFS_DATANODE_DATA_WRITE_BANDWIDTHPERSEC_KEY`.

Control flow: The test starts one DataNode, creates `/foo`, writes random data with repeated `hflush` while leaving the stream open, retrieves the RBW from the original DataNode, then starts a second DataNode with bandwidth throttling enabled. It obtains live DataNode reports, maps the new and old registrations, invokes the RBW transfer helper, and reads the new node’s RBW state.

State and persistence behavior: A real under-construction HDFS block remains open during transfer. The test inspects physical dataset replica state and xceiver write throttler configuration on both DataNodes.

Dependencies and integration points: It covers DataTransferProtocol RBW transfer, DFS client/DataNode identity mapping, DataNode write throttling, and FsDataset RBW materialization.

Risks and test signals: Signals are transfer `SUCCESS`, exactly one RBW on each relevant node, and matching block ID/generation/visible length. Risks include random data size and polling for replica appearance with fixed sleeps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestTransferRbw.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestTriggerBlockReport.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestTriggerBlockReport.java

Purpose: This HA integration test verifies manual DataNode block-report triggering for full versus incremental reports and for all NameNodes versus one specified NameNode.

Important APIs/types/functions: `DataNode.triggerBlockReport`, `BlockReportOptions.Factory`, `MiniDFSNNTopology.simpleHATopology`, `InternalDataNodeTestUtils.spyOnBposToNN`, `StorageBlockReport`, `StorageReceivedDeletedBlocks`, `IbrManager.addRDBI`, and `DatanodeProtocolClientSideTranslatorPB`.

Control flow: The helper configures very long automatic block-report and heartbeat intervals, starts a one-DataNode HA cluster, spies on both NameNode protocol proxies, creates a file and waits for the initial IBR to both NameNodes, verifies no automatic full reports follow, injects a fake deleted-block IBR into each BP service actor, and calls `triggerBlockReport` with incremental/full and optional target NameNode address. Tests run all four combinations.

State and persistence behavior: The file creates one HDFS file and mutates each actor’s IBR queue with a synthetic deleted block. Report routing is asynchronous and uses DataNode’s internal BPOS state.

Dependencies and integration points: It covers client-facing block-report admin options, HA NameNode routing, BP service actor IBR queues, and DataNode protocol RPCs.

Risks and test signals: Signals are exact Mockito counts on full and incremental RPCs. Risks include long timeout reliance, asynchronous trigger return, and target-address matching against service RPC address.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestTriggerBlockReport.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/checker/TestDatasetVolumeChecker.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/checker/TestDatasetVolumeChecker.java

Purpose: This parameterized unit test verifies `DatasetVolumeChecker` classification for every `VolumeCheckResult` plus thrown exceptions, both for single-volume async callbacks and full-dataset synchronous checks.

Important APIs/types/functions: `DatasetVolumeChecker`, `DatasetVolumeChecker.Callback`, `AsyncChecker`, `Checkable`, `FsVolumeSpi.check`, `FsDatasetSpi.FsVolumeReferences`, `FakeTimer`, `Futures.immediateFuture`, `VolumeCheckResult`, and disk-check configuration keys.

Control flow: `data()` supplies `HEALTHY`, `DEGRADED`, `FAILED`, and `null` as exception case. `testCheckOneVolume` builds one mocked volume, installs a `DummyChecker` that immediately invokes `check`, schedules `checkVolume`, waits for the callback, and verifies healthy versus failed sets. `testCheckAllVolumes` builds a mocked dataset with two volumes and asserts failed-volume set size. Bad config tests instantiate the checker with invalid timeout, min-gap, and tolerated-failures values.

State and persistence behavior: No disk state is persisted. State under test is checker counters, callback arguments, mocked volume references, and validation of configuration-derived thresholds.

Dependencies and integration points: It validates the bridge between `DatasetVolumeChecker` and pluggable `AsyncChecker`, plus FsDataset volume-reference acquisition.

Risks and test signals: Signals are callback counts, Mockito `check` invocations, failed-set sizes, and exact exception messages. Risk is mostly mock fidelity and parameterized repetition of config tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/checker/TestDatasetVolumeChecker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/checker/TestDatasetVolumeCheckerFailures.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/checker/TestDatasetVolumeCheckerFailures.java

Purpose: This companion test covers `DatasetVolumeChecker` failure cases not covered by the parameterized suite: hung checks, closed volumes, and minimum synchronous-check gap enforcement.

Important APIs/types/functions: `DatasetVolumeChecker.checkAllVolumes`, `FakeTimer`, `DFS_DATANODE_DISK_CHECK_TIMEOUT_KEY`, `DFS_DATANODE_DISK_CHECK_MIN_GAP_KEY`, `ClosedChannelException`, `FsVolumeSpi.obtainReference`, and checker counters `getNumSyncDatasetChecks`/`getNumSkippedChecks`.

Control flow: Setup configures a one-second minimum disk-check gap. `testTimeout` creates a volume whose `check` sleeps forever and expects it to be reported failed with a one-second timeout. `testCheckingClosedVolume` makes `obtainReference` throw `ClosedChannelException`, expecting no failed volume and no check invocation. The min-gap test checks once, immediately checks again and expects skip, then advances `FakeTimer` and expects another real check.

State and persistence behavior: All volumes are mocks. The persistent checker state is its last-check timestamp and counters.

Dependencies and integration points: It exercises volume reference acquisition, async timeout handling, and rate limiting of full-dataset disk checks.

Risks and test signals: Signals are failed-set sizes, check invocation count, and counter values. Risk comes from sleeping forever in a worker and relying on timeout cancellation/shutdown behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/checker/TestDatasetVolumeCheckerFailures.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/checker/TestDatasetVolumeCheckerTimeout.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/checker/TestDatasetVolumeCheckerTimeout.java

Purpose: This timeout-focused unit test verifies `DatasetVolumeChecker.checkVolume` reports a slow volume as failed when its check exceeds the configured disk-check timeout.

Important APIs/types/functions: `DatasetVolumeChecker`, `DatasetVolumeChecker.Callback`, `DFS_DATANODE_DISK_CHECK_TIMEOUT_KEY`, `FakeTimer`, `FsVolumeSpi.check`, `FsVolumeReference`, `ReentrantLock`, and `VolumeCheckResult`.

Control flow: Static configuration sets a ten-millisecond disk-check timeout. `makeSlowVolume` returns a mocked volume whose `check` blocks on a shared lock and eventually returns healthy. The test locks before scheduling, registers a callback that expects zero healthy and one failed volume, sleeps long enough for timeout, unlocks, and verifies the underlying check was invoked once and the callback ran once.

State and persistence behavior: There is no filesystem state. The test coordinates thread state with a static `ReentrantLock` and checks callback/counter state.

Dependencies and integration points: It validates how `DatasetVolumeChecker` maps `ThrottledAsyncChecker` timeout behavior into DataNode failed-volume reporting.

Risks and test signals: Signals are failed callback arguments and single check invocation. Risks are timing sensitivity from millisecond sleeps and a static lock that must be released on normal completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/checker/TestDatasetVolumeCheckerTimeout.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/checker/TestStorageLocationChecker.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/checker/TestStorageLocationChecker.java

Purpose: This unit test validates startup-time `StorageLocationChecker` filtering, tolerated failed-volume thresholds, timeout classification, and invalid configuration handling.

Important APIs/types/functions: `StorageLocationChecker.check`, `StorageLocation.check`, `StorageLocation.CheckContext`, `VolumeCheckResult`, `DFS_DATANODE_FAILED_VOLUMES_TOLERATED_KEY`, `DFS_DATANODE_DISK_CHECK_TIMEOUT_KEY`, `FakeTimer`, and `HadoopIllegalArgumentException`.

Control flow: Mock-location helpers produce locations returning configured health results or sleeping for configured delays. Tests assert all-healthy locations survive, one failed location is filtered below threshold, too many failures throw `IOException` with details, tolerated-failures equal to configured volume count is invalid, and a slow check times out while a fast location remains. Invalid config tests intercept exact constructor/check failures.

State and persistence behavior: No actual storage directories are used. State is mocked location identity strings, filter lists, and checker timeout/toleration configuration.

Dependencies and integration points: It covers DataNode startup storage filtering before volumes become `FsVolumeSpi`, sharing checker semantics with dataset volume checks.

Risks and test signals: Signals are filtered-list sizes, per-location `check` calls, and exception messages. Risks include real sleep in timeout test and brittle message matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/checker/TestStorageLocationChecker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/checker/TestThrottledAsyncChecker.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/checker/TestThrottledAsyncChecker.java

Purpose: This unit test verifies generic `ThrottledAsyncChecker` scheduling, per-target minimum-gap throttling, concurrent check suppression, context forwarding, exception propagation, and exception caching.

Important APIs/types/functions: `ThrottledAsyncChecker`, `Checkable`, `ListenableFuture`, `FakeTimer`, `ScheduledThreadPoolExecutor`, `GenericTestUtils.waitFor`, and internal test checkables `NoOpCheckable`, `ThrowingCheckable`, and `StalledCheckable`.

Control flow: Scheduler tests schedule two no-op targets, assert first checks run, re-schedule before and after advancing the fake timer, and verify counts. Concurrent scheduling starts a stalled check and expects a second schedule for the same target to return empty. Context test switches boolean context between runs. Exception tests inspect `ExecutionException` cause and verify a failed target is not rechecked inside the min gap.

State and persistence behavior: State is in-memory: per-target last check timestamps, in-flight futures, cached failures, and atomic check counters.

Dependencies and integration points: It validates the async primitive used by disk/location checkers independent of HDFS storage classes.

Risks and test signals: Signals are optional future presence, check counters, and exception type. Risks are executor threads that sleep indefinitely and reliance on async callback completion timing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/checker/TestThrottledAsyncChecker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/checker/TestThrottledAsyncCheckerTimeout.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/checker/TestThrottledAsyncCheckerTimeout.java

Purpose: This timeout suite verifies `ThrottledAsyncChecker` futures fail with `TimeoutException`, invoke exactly one callback for timed-out checks, and complete successfully for non-blocking checks.

Important APIs/types/functions: `ThrottledAsyncChecker`, `ListenableFuture`, Guava `Futures.addCallback`, `FutureCallback`, `MoreExecutors.directExecutor`, `FakeTimer`, `TimeoutException`, and the lock-based `DummyCheckable`.

Control flow: Tests create a checker with zero min gap and ten-millisecond timeout. Timeout tests lock before scheduling so `DummyCheckable.check` blocks, attach callbacks, wait for callback result or Mockito timeout verification, then unlock. The single-callback test then schedules a second check after unlock and confirms one success and no extra failure. The good-disk test schedules without lock contention and expects no throwable.

State and persistence behavior: State is only checker future/callback state and a per-test `ReentrantLock`. There is no disk or HDFS persistence.

Dependencies and integration points: This validates timeout mechanics beneath `DatasetVolumeChecker` and `StorageLocationChecker`.

Risks and test signals: Signals are failure/success callback counts and `TimeoutException` type. Risks include millisecond timeout sensitivity and executor thread cleanup for timed-out but later-unblocked tasks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/checker/TestThrottledAsyncCheckerTimeout.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/erasurecode/ErasureCodingTestHelper.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/erasurecode/ErasureCodingTestHelper.java

Purpose: This tiny helper exposes the erasure-coding DataNode reconstructor buffer pool to tests.

Important APIs/types/functions: `ErasureCodingTestHelper.getBufferPool`, `StripedReconstructor.getBufferPool`, and `ByteBufferPool`.

Control flow: The class is `final` with a private constructor and one static method that delegates directly to `StripedReconstructor.getBufferPool()`.

State and persistence behavior: No state is owned here. The returned pool is whatever static/shared buffer pool the reconstructor uses, so consumers may observe shared allocation/reuse behavior outside this helper.

Dependencies and integration points: It gives tests in or near the erasure-coding package access to internal reconstruction buffer-pool state without widening production APIs.

Risks and test signals: There are no local assertions. Risk is that this helper couples tests to `StripedReconstructor` internals; if buffer-pool ownership changes, tests using the helper may need updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/erasurecode/ErasureCodingTestHelper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/extdataset/ExternalDatasetImpl.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/extdataset/ExternalDatasetImpl.java

Purpose: This class is a minimal external-package `FsDatasetSpi` implementation used as a compile-time and construction contract test for third-party DataNode dataset plugins.

Important APIs/types/functions: `FsDatasetSpi<ExternalVolumeImpl>`, `DatanodeStorage`, `StorageReport`, `BlockListAsLongs.EMPTY`, `ReplicaHandler`, `ExternalReplica`, `ExternalReplicaInPipeline`, `ReplicaRecoveryInfo`, `BlockLocalPathInfo`, `DataNodeMetricHelper.getMetrics`, and many FsDataset lifecycle/cache/recovery methods.

Control flow: Most methods return neutral values, no-op, or throw where unsupported. Methods required for instantiation and basic protocol shape return one normal default storage report, empty block reports, placeholder replicas/handlers, null input/output stream wrappers, and zero capacity/usage metrics. `getMetrics` delegates to `DataNodeMetricHelper` and swallows exceptions.

State and persistence behavior: The only durable-like field is one generated `DatanodeStorage`. No real blocks, volumes, cache entries, trash, rolling-upgrade markers, or replica files are persisted.

Dependencies and integration points: It deliberately lives outside `org.apache.hadoop.hdfs.server.datanode` to prove external implementations can compile against all public or otherwise accessible required types.

Risks and test signals: Signal is compilation and explicit instantiation in `TestExternalDataset`. Behavior is not production-correct; null/no-op methods would fail real DataNode workflows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/extdataset/ExternalDatasetImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/extdataset/ExternalReplica.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/extdataset/ExternalReplica.java

Purpose: This minimal external `Replica` implementation exists to verify that third-party code can implement the DataNode replica contract outside the DataNode package.

Important APIs/types/functions: `Replica`, `ReplicaState.FINALIZED`, `FsVolumeSpi`, and replica identity/length methods such as `getBlockId`, `getGenerationStamp`, `getNumBytes`, `getVisibleLength`, `getStorageUuid`, and `getVolume`.

Control flow: Every method returns a neutral placeholder: zero IDs/lengths, `FINALIZED` state, `null` storage/volume, and non-transient storage false.

State and persistence behavior: The class stores no fields and represents no actual block file. It is a compile-time stub, not a meaningful replica implementation.

Dependencies and integration points: It is returned by `ExternalDatasetImpl.getReplica` and instantiated in `TestExternalDataset`, ensuring the `Replica` interface remains externally implementable.

Risks and test signals: Signal is successful construction and compilation. Risk is mistaking this for behavioral coverage; it does not validate actual replica data, lifecycle transitions, or storage identity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/extdataset/ExternalReplica.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/extdataset/ExternalReplicaInPipeline.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/extdataset/ExternalReplicaInPipeline.java

Purpose: This external-package `ReplicaInPipeline` stub verifies that write-pipeline replica contracts can be implemented by a third-party dataset.

Important APIs/types/functions: `ReplicaInPipeline`, `ReplicaOutputStreams`, `ChunkChecksum`, `DataChecksum`, `ReplicaState.FINALIZED`, writer-management methods, byte-ack/length methods, and `FsVolumeSpi`.

Control flow: Mutators no-op, metrics return zero, `getLastChecksumAndDataLen` returns a zero/null checksum, `createStreams` returns `ReplicaOutputStreams` with null streams and the requested checksum, and writer methods return false or no-op.

State and persistence behavior: No bytes, writer thread, checksum, or storage UUID are retained. It does not create data or metadata files.

Dependencies and integration points: It is used by `ExternalDatasetImpl` methods that create temporary, RBW, append, and recovery handlers, and instantiated directly by `TestExternalDataset`.

Risks and test signals: Signal is type construction and accessibility of pipeline APIs. It provides no behavioral safety for real write pipelines because stream fields are null and state changes are ignored.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/extdataset/ExternalReplicaInPipeline.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/extdataset/ExternalVolumeImpl.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/extdataset/ExternalVolumeImpl.java

Purpose: This external `FsVolumeSpi` implementation is a compile-time contract stub for DataNode volume plugins.

Important APIs/types/functions: `FsVolumeSpi`, `FsVolumeReference`, `StorageType.DEFAULT`, `StorageLocation`, `DF`, `BlockIterator`, `ScanInfo`, `FileIoProvider`, `DataNodeVolumeMetrics`, and `VolumeCheckResult`.

Control flow: Most methods return null, zero, or no-op. The storage ID is hard-coded as `test`, storage type is default, transient/RAM flags are false, and `check` returns `VolumeCheckResult.HEALTHY`.

State and persistence behavior: The class has no real base URI, disk usage, block pool list, iterator state, file I/O provider, or metrics object. Space reservation and release do not persist counters.

Dependencies and integration points: It proves an external package can implement all volume methods needed by `FsDatasetSpi` without package-private access. `ExternalDatasetImpl` is parameterized on this type and `TestExternalDataset` constructs it.

Risks and test signals: Signal is successful compilation/construction and healthy check return. Risk is that null-heavy behavior only protects API accessibility, not runtime integration with real DataNode volume management.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/extdataset/ExternalVolumeImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/extdataset/TestExternalDataset.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/extdataset/TestExternalDataset.java

Purpose: This suite explicitly tests that external implementations of `FsDatasetSpi`, `Replica`, `ReplicaInPipeline`, and `FsVolumeSpi` can be instantiated outside Hadoop’s DataNode package.

Important APIs/types/functions: `ExternalDatasetImpl`, `ExternalReplica`, `ExternalReplicaInPipeline`, `ExternalVolumeImpl`, `FsDatasetSpi`, `Replica`, `ReplicaInPipeline`, and `FsVolumeSpi`.

Control flow: Four simple JUnit tests each construct one external implementation and assign it to the corresponding Hadoop interface/supertype. The class-level comments explain that compilation itself is the primary contract signal.

State and persistence behavior: No HDFS cluster, files, blocks, or persistent state are created. Instances are local objects whose stub methods are mostly uncalled.

Dependencies and integration points: It is a guardrail for external dataset plugin API surface. If new abstract methods, constructor visibility changes, or inaccessible return types are introduced, this package should fail to compile or instantiate.

Risks and test signals: Signal is successful compile/test execution. It intentionally does not test method accessibility or behavioral correctness beyond construction, so runtime plugin compatibility still requires deeper tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/extdataset/TestExternalDataset.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/TestAvailableSpaceVolumeChoosingPolicy.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/TestAvailableSpaceVolumeChoosingPolicy.java

Purpose: This unit test validates `AvailableSpaceVolumeChoosingPolicy` behavior for balanced fallback, preference toward high- or low-free-space volumes, insufficient selected-volume space, dynamic available-space changes, and randomized selection ratios.

Important APIs/types/functions: `AvailableSpaceVolumeChoosingPolicy`, `VolumeChoosingPolicy.chooseVolume`, `FsVolumeSpi.getAvailable`, configuration keys for balanced-space threshold and preference fraction, `ReflectionUtils`, `GenericTestUtils.assertValueNear`, and shared `TestRoundRobinVolumeChoosingPolicy` helpers.

Control flow: Tests configure policies with a one-megabyte threshold and varying preference fractions, build mocked volumes with specified available bytes, and assert exact selected-volume sequences. Randomized tests use a seeded `Random`, ten thousand iterations, and expected high/low-space selection ratios based on preference fraction.

State and persistence behavior: There is no disk state; mocked `getAvailable` values model changing capacity. The policy maintains round-robin cursors and random choices internally across calls.

Dependencies and integration points: It checks the policy used by DataNode block placement over FsDataset volumes and reuses round-robin tests for balanced cases and exception message coverage.

Risks and test signals: Signals are exact volume identity choices and randomized count tolerance. Risks include probabilistic flakiness, though seed and allowed error reduce it, and mock sequences that may diverge from real disk changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/TestAvailableSpaceVolumeChoosingPolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/TestRoundRobinVolumeChoosingPolicy.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/TestRoundRobinVolumeChoosingPolicy.java

Purpose: This unit test validates `RoundRobinVolumeChoosingPolicy` volume selection by order, requested block size, additional reserved free space, out-of-space messages, and independent cursors for heterogeneous storage types.

Important APIs/types/functions: `RoundRobinVolumeChoosingPolicy`, `VolumeChoosingPolicy.chooseVolume`, `FsVolumeSpi.getAvailable`, `FsVolumeSpi.getStorageType`, `StorageType.DISK/SSD`, `DFS_DATANODE_ROUND_ROBIN_VOLUME_CHOOSING_POLICY_ADDITIONAL_AVAILABLE_SPACE_KEY`, and `DiskOutOfSpaceException`.

Control flow: Helper methods build mocked volume lists and assert chosen volume sequences. Basic RR alternates two volumes, skips too-small volumes for larger blocks, and throws when none fit. Additional-space tests require configured headroom. Exception-message tests verify exact message including largest available bytes and block size. Storage-type tests call the same policy with separate disk and SSD lists and assert independent round-robin behavior.

State and persistence behavior: State is policy cursor state and mocked available space; no real volumes are touched.

Dependencies and integration points: It covers the default DataNode volume chooser and provides reusable helper methods for `AvailableSpaceVolumeChoosingPolicy`.

Risks and test signals: Signals are exact selected mock objects and exception messages. Risk is brittleness if messages or cursor semantics change intentionally.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/TestRoundRobinVolumeChoosingPolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/FsDatasetImplTestUtils.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/FsDatasetImplTestUtils.java

Purpose: This private test utility implements `FsDatasetTestUtils` for file-backed `FsDatasetImpl`, giving tests controlled access to replica files, metadata files, volume maps, block-pool directories, and corruption helpers.

Important APIs/types/functions: `FsDatasetImpl`, `FsDatasetTestUtils`, `MaterializedReplica`, `ReplicaInfo`, `FinalizedReplica`, `ReplicaBeingWritten`, `LocalReplicaInPipeline`, `ReplicaUnderRecovery`, `ReplicaMap`, `FsVolumeImpl`, `FsDatasetUtil`, `BlockMetadataHeader`, `DataChecksum`, and `DataStorage`.

Control flow: Constructor asserts the DataNode uses `FsDatasetImpl`. Creation helpers pick a volume, create finalized/tmp/RBW/RWR/RUR replicas, create block and meta files, write checksum headers, and add entries to `dataset.volumeMap`. `MaterializedReplica` supports corrupting, truncating, deleting, or relocating block/meta files. Other methods reload replicas from disk, fetch stored length/generation, rename metadata to change generation stamp, inject corrupt replicas, inspect pending async deletions, and verify block-pool directory presence/absence.

State and persistence behavior: This class directly mutates real DataNode storage directories, metadata files, block files, volume maps, and async delete queues. It is intentionally invasive and test-only.

Dependencies and integration points: It bridges black-box tests to `FsDatasetImpl` internals and physical layout conventions.

Risks and test signals: Signals are IO exceptions, file existence, replica map contents, and stored metadata. Risks include high coupling to on-disk layout, direct internal-field access, and corruption helpers that can affect unrelated tests if misused.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/FsDatasetImplTestUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/FsDatasetTestUtil.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/FsDatasetTestUtil.java

Purpose: This static utility exposes selected `FsDatasetImpl` internals to tests for locating block/meta files, fetching replicas, stopping lazy writer, breaking hard links, and verifying storage file locks are released.

Important APIs/types/functions: `FsDatasetImpl.getReplicaInfo`, `FsDatasetUtil.getMetaFile`, `LocalReplica.breakHardLinksIfNeeded`, `volumeMap.replicas`, `FsDatasetImpl.LazyWriter.stop`, `StorageLocation.parse`, `Storage.STORAGE_FILE_LOCK`, `RandomAccessFile`, `FileChannel.tryLock`, and `FileLock`.

Control flow: File helpers cast `FsDatasetSpi` to `FsDatasetImpl`, resolve `ReplicaInfo`, and return block or metadata files. Replica helpers fetch internal replica collections. `stopLazyWriter` stops the lazy writer runnable. `assertFileLockReleased` parses a storage URI, opens the lock file, tries to acquire/release the lock, and fails on null lock or overlapping lock exceptions.

State and persistence behavior: It reads real storage state and may stop the DataNode lazy writer daemon or break replica hard links. The lock assertion touches the OS file lock for a storage directory.

Dependencies and integration points: It is used by low-level DataNode tests that need to inspect or manipulate file-backed dataset state beyond public APIs.

Risks and test signals: Signals are returned file handles, replica collections, and file-lock acquisition success. Risks include direct casts, platform-specific locking semantics, and side effects from stopping lazy writer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/FsDatasetTestUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/LazyPersistTestCase.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/LazyPersistTestCase.java

Purpose: This abstract base class provides cluster setup, file creation, polling, JMX, deletion, and verification helpers for lazy-persist/RAM_DISK DataNode tests.

Important APIs/types/functions: `MiniDFSCluster`, `DistributedFileSystem`, `DFSClient`, `StorageType.RAM_DISK`, `CreateFlag.LAZY_PERSIST`, `FsDatasetImpl.evictLazyPersistBlocks`, `FsVolumeImpl.getBlockPoolSlice`, `DatanodeUtil.idToBlockDir`, `DataNodeTestUtils.triggerBlockReport`, `JMXGet`, `TemporarySocketDirectory`, `NativeIO.POSIX.CacheManipulator`, `BlockManager`, and `FSNamesystem`.

Control flow: `startUpCluster` configures block size, lazy writer/scrubber intervals, heartbeat, RAM disk capacity, locked memory, short-circuit reads, storage types, and MiniDFSCluster. File helpers create deterministic lazy or normal files. Verification helpers wait for replicas on a given storage type, wait for lazy-persist copies in non-transient `lazypersist` directories, trigger full block reports and wait for report counters, verify deletion from transient/finalized and lazy-persist dirs, read random contents, inspect JMX metrics, force eviction, shut down DataNodes, and wait for corrupt/low-redundancy/scrubber/redundancy/file-state changes.

State and persistence behavior: It orchestrates real HDFS files, RAM_DISK and persistent block files, lazy-persist directories, DataNode async deletions, NameNode replication/corrupt counters, JMX state, native cache-manipulator state, and temporary domain socket directories.

Dependencies and integration points: It centralizes lazy-persist integration across NameNode placement, DataNode storage tiers, local reads, memory locking, lazy writer, scrubber, and block reports.

Risks and test signals: Signals are storage-type locations, saved/deleted block files, JMX metrics, report counters, and NameNode counters. Risks include extensive timing waits, global native cache manipulator replacement, and cleanup needs for sockets and clusters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/LazyPersistTestCase.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestAddBlockPoolException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestAddBlockPoolException.java

Purpose: This unit test verifies `AddBlockPoolException` correctly reports whether it holds volume failures and merges exception maps without overwriting the first error per volume.

Important APIs/types/functions: `AddBlockPoolException`, `getFailingVolumes`, `hasExceptions`, `mergeException`, `ConcurrentHashMap<FsVolumeSpi, IOException>`, `FsVolumeImpl`, and Mockito volume mocks.

Control flow: The first test checks a default exception has no failures, then builds one with a map containing one mocked volume and expects `hasExceptions` true. The merge test creates two maps where both contain `vol1` with different messages and the second contains `vol2`, merges, and asserts two total failures with the original `vol1` message retained. The final test merges two empty exceptions and expects no failures.

State and persistence behavior: State is the in-memory concurrent map of failing volumes to exceptions. No disk or block-pool directories are touched.

Dependencies and integration points: It protects error aggregation used when adding a block pool across multiple volumes in `FsDatasetImpl`.

Risks and test signals: Signals are map size, boolean state, and retained exception messages. Risk is low; behavior is focused on aggregation semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestAddBlockPoolException.java -->
