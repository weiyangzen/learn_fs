# Research: subset-b-007558

This grouped report covers the Hadoop HDFS NameNode HA and metrics tests assigned to subset `subset-b-007558`. Each section is keyed by the exact source path for downstream reconciliation.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestObserverReadProxyProvider.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestObserverReadProxyProvider.java

Purpose: validates `ObserverReadProxyProvider` client-side routing for HDFS observer reads, active writes, standby fallback, observer state changes, non-`ClientProtocol` proxies, and HA-state probe timeout behavior. The tests use mocked `ClientProtocol` endpoints instead of a real cluster so they can precisely model active, standby, observer, unreachable, slow, and retry-on-active responses.

Important APIs and types: `ObserverReadProxyProvider<T>`, `ClientHAProxyFactory`, `HAProxyFactory`, `NNProxyInfo`, `ClientProtocol`, `GetUserMappingsProtocol`, `HAServiceState`, `ObserverRetryOnActiveException`, `StandbyException`, `RemoteException`, `Future<HAServiceState>`, and the provider configuration keys `NAMENODE_HA_STATE_PROBE_TIMEOUT` and `OBSERVER_PROBE_RETRY_PERIOD_KEY`. `NameNodeAnswer` is the local state machine used by Mockito `Answer` objects.

Control flow: `setupProxyProvider` builds logical nameservice configuration, registers mocked proxies by address, disables random failover order, sets observer-read enabled, and injects a custom proxy factory. Read calls are represented by `checkAccess("/", READ)` and writes by `reportBadBlocks`. Tests then mutate `NameNodeAnswer` flags and assert `proxyProvider.getLastProxy().proxyInfo` points at the expected endpoint. Timeout tests call `getHAServiceStateWithTimeout` with mocked futures and assert returned states, cancellation, and log messages.

State and persistence behavior: no persistent namespace state is used; all state is in the proxy provider's current/last proxy index and the mock answers. The test explicitly covers state transitions from observer to active or standby, unreachable observers, retry-active exceptions that force active service, and slow HA-state probes.

Dependencies and integration points: integrates with Hadoop HA proxy configuration parsing, retry/failover provider logic, UGI-aware proxy creation, Mockito, and `GenericTestUtils.LogCapturer`. It is a narrow unit-style guard for client routing rather than NameNode server behavior.

Risks and test signals: risks include stale observer choice, writes sent to observer/standby, delayed reads due to slow standby probes, failure to cancel timed-out probe tasks, and regressions for non-client HA proxy interfaces. Strong signals are endpoint assertions after every operation, cache/index behavior across observer recovery, log-count checks for timeout paths, and a JUnit timeout around the short-probe slow-node path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestObserverReadProxyProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestPendingCorruptDnMessages.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestPendingCorruptDnMessages.java

Purpose: verifies that standby NameNodes correctly manage pending DataNode block messages when reports arrive for replicas whose storage identity or referenced block state changes before failover.

Important APIs and types: `MiniDFSCluster`, `MiniDFSNNTopology.simpleHATopology`, `HATestUtil.configureFailoverFs`, `HATestUtil.waitForStandbyToCatchUp`, `ExtendedBlock`, `DataNodeProperties`, `DataNodeTestUtils.runDirectoryScanner`, `BlockManager.getPendingDataNodeMessageCount`, `DatanodeDescriptor`, and `DatanodeReportType.ALL`.

Control flow: `testChangedStorageId` starts one DN and two NNs, creates a file, waits for standby catch-up, mutates the block generation stamp backward on the DataNode, runs the directory scanner, stops the DN, restarts the standby NN, and restarts the DN so the initial block report queues a corrupt pending message on the standby. It records the registered DN UUID, reformats and restarts the DN on the same transfer port, waits for the UUID to change, then asserts the pending message queue is cleared before failing over to the standby. `testRemoveBlockCleansUpPendingDNMessages` follows a similar setup but mutates the generation stamp into the future, queues a pending message, deletes the file on the active, rolls/tails edits, and verifies the standby pending queue is empty.

State and persistence behavior: the tests exercise standby-only pending DN message queues, DataNode UUID/storage identity changes caused by reformatting, block generation stamp metadata in replicas and edit logs, and deletion edits that remove pending messages for blocks no longer in the namespace.

Dependencies and integration points: these are MiniDFSCluster integration tests touching DataNode storage, directory scanning, NameNode restart, block reports, edit log tailing, and HA failover.

Risks and test signals: a leak in `pendingDNMessages` can block failover correctness or keep corrupt/future reports against obsolete storage. Signals include waiting for exactly one queued message, waiting for a changed DN UUID, asserting queue count returns to zero, and performing a final transition to active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestPendingCorruptDnMessages.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestPipelinesFailover.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestPipelinesFailover.java

Purpose: stress and regression coverage for HDFS write pipelines, block allocation/completion idempotence, lease recovery, block synchronization, and DataNode failure handling across HA NameNode failover.

Important APIs and types: `MiniDFSCluster`, `MiniDFSNNTopology.simpleHATopology(NN_COUNT)`, `FSDataOutputStream`, `AppendTestUtil`, `DistributedFileSystem.recoverLease`, `BlockManagerTestUtil`, `RetryInvocationHandler`, `DatanodeProtocolClientSideTranslatorPB.commitBlockSynchronization`, `InternalDataNodeTestUtils.spyOnBposToNN`, `DelayAnswer`, `HAStressTestHarness`, and `MultithreadedTestUtil`.

Control flow: `doWriteOverFailoverTest` writes a block and a half, flushes, fails over either gracefully or by restarting the old active, verifies the new active has no pending/corrupt/missing block state, then either forces another `allocateBlock` or closes to test `completeFile` idempotence before checking contents. DN-failure tests continue writes after failover, stop DNs, fail back, and validate data. Lease recovery tests create an under-construction file, fail over, recover the lease as another user, and then fail back. The synchronization test delays a DN's `commitBlockSynchronization`, fails over while delayed, confirms the old standby rejects the write, and retries recovery on the new active. The stress test runs many pipeline/lease recovery threads while a harness triggers replication work and periodic failovers.

State and persistence behavior: exercises under-construction file leases, block IDs and generation stamps, edit-log replay to standbys, client retry/failover state, DataNode-to-NameNode block recovery RPCs, and pipeline membership after DN loss.

Dependencies and integration points: integrates client failover, block manager accounting, DataNode BPOfferService RPC translators, user impersonation, shell debug collection, and HA stress harness threads.

Risks and test signals: risks include duplicate block allocation, file completion replay bugs, lost block locations, lease recovery stuck on the old active, and failed pipeline updates after DN loss. Signals include full file content checks, block-manager zero-count assertions, expected standby write rejection during delayed synchronization, and multi-threaded stress completion without propagated exceptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestPipelinesFailover.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestQuotasWithHA.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestQuotasWithHA.java

Purpose: verifies quota metadata and quota read RPC behavior under HA, especially standby namespace tracking when standby reads are enabled and correct `StandbyException` behavior when they are disabled.

Important APIs and types: `MiniDFSCluster`, `HAUtil.setAllowStandbyReads`, `DistributedFileSystem.setQuota`, `ContentSummary`, `getContentSummary`, `getQuotaUsage`, `StandbyException`, `FSDataOutputStream.append`, and `DFSTestUtil.createFile`.

Control flow: setup creates a two-NN HA cluster with one DN, short tailing period, 1 KB blocks, standby reads enabled, and NN0 active. `testQuotasTrackedOnStandby` creates a directory, sets namespace and diskspace quotas, writes a multi-block file, waits for standby catch-up, and reads `ContentSummary` directly from NN1's RPC server. It then appends data, checks updated space usage on standby, deletes the file, and checks file count and consumed space drop to zero while quotas remain. The other two tests disable standby reads in NN1 configuration, restart NN1, and assert direct standby RPCs for content summary and quota usage throw `StandbyException`.

State and persistence behavior: quota fields and usage counters are persisted through edit logs and reconstructed by standby tailing. Appends and deletes are used to cover delta accounting, not just initial creation.

Dependencies and integration points: integrates HA edit tailing, FileSystem failover client, NameNode RPC service, quota accounting, and standby-read policy.

Risks and test signals: risks include stale standby quota usage after append/delete, incorrect directory or file counts, and accidental read availability when standby reads are disabled. Signals are exact quota, space, directory-count, and file-count assertions plus explicit exception assertions for disabled standby reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestQuotasWithHA.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestRemoteNameNodeInfo.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestRemoteNameNodeInfo.java

Purpose: verifies parsing of remote NameNode metadata from HA configuration when a nameservice has more than two NameNodes.

Important APIs and types: `RemoteNameNodeInfo.getRemoteNameNodes`, `MiniDFSNNTopology`, `MiniDFSCluster.configureNameNodes`, `DFS_HA_NAMENODE_ID_KEY`, and `DFS_NAMENODE_RPC_ADDRESS_KEY`-derived topology configuration.

Control flow: the test builds an empty configuration, constructs a nameservice `ns1` with three NN IDs and IPC ports, asks `MiniDFSCluster.configureNameNodes` to materialize the HA keys, marks `nn1` as local, and calls `RemoteNameNodeInfo.getRemoteNameNodes(conf)` as well as `getRemoteNameNodes(conf, nameservice)`. It asserts both lists are equal.

State and persistence behavior: there is no cluster runtime or persistent namespace state. The only state is the configuration keyspace that maps nameservice and NN IDs to RPC addresses and local identity.

Dependencies and integration points: integrates with MiniDFS topology configuration helpers and production parsing logic for remote NameNode upload/checkpoint destinations.

Risks and test signals: the main risk is parsing only two peers or treating explicit nameservice and inferred nameservice paths differently. The equality assertion is a compact signal that both parsing entry points produce the same `RemoteNameNodeInfo` set for a three-NN HA topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestRemoteNameNodeInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestRetryCacheWithHA.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestRetryCacheWithHA.java

Purpose: validates HA retry-cache replication and at-most-once semantics when a client operation succeeds on one NameNode but the response is lost and the client retries after failover.

Important APIs and types: `RetryCache`, `LightWeightCache<CacheEntry, CacheEntry>`, `DFSClient`, `NameNodeProxiesClient`, `RetryInvocationHandler`, `FailoverProxyProvider`, `AtMostOnceOp`, `SubjectInheritingThread`, and many `ClientProtocol` operations including snapshot, create, append, rename, concat, delete, symlink, updatePipeline, cache directive/pool, and xattr operations. It also tests `RemoteIterator` behavior for cache pools/directives across active changes.

Control flow: setup starts a two-NN HA cluster with enough DNs for the default erasure coding policy, configures failover, enables ACLs and xattrs, and tunes cache listing response sizes. `testRetryCacheOnStandbyNN` runs a standard operation suite, captures retry-cache entries on NN0, rolls/tails edits, shuts down NN0, activates NN1, and verifies the same 39 entries exist. `genClientWithDummyHandler` wraps the failover proxy in `DummyRetryInvocationHandler`, which can throw after the server has processed the operation. Each `AtMostOnceOp` prepares state, invokes an RPC, checks the NameNode has applied the mutation before the client receives success, then failover is forced and the handler is unblocked. The common verifier waits for a result, cache hits, and cache updates on both NNs, checking operation-specific update counts where tracked. Listing tests iterate cache pools/directives while alternating active NNs mid-iteration.

State and persistence behavior: retry cache entries are persisted through edit logs and replayed on standby. The tested namespace state spans snapshots, files, blocks, cache manager state, and xattrs. Client retry state is intentionally desynchronized from server mutation state.

Dependencies and integration points: covers client failover, retry policy, NameNode edit tailing, cache manager pagination, EC-aware DN counts, ACL/xattr configuration, and internal retry cache metrics.

Risks and test signals: risks include duplicate non-idempotent mutations, lost retry-cache entries after failover, wrong cached responses, and iterator breakage when active changes. Signals include operation effect polling before failover, cache-hit/update metric assertions on both NameNodes, exact retry-cache size/entry checks, and pool/directive set reconciliation after failover during iteration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestRetryCacheWithHA.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestSeveralNameNodes.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestSeveralNameNodes.java

Purpose: stress-tests an HA cluster with three NameNodes under continuous failover while multiple clients create and verify linked lists of files.

Important APIs and types: `HAStressTestHarness`, `MiniDFSCluster`, `HdfsClientConfigKeys.Failover`, `MultithreadedTestUtil.TestContext`, `RepeatingTestThread`, `FileSystem`, `FSDataOutputStream`, and `FSDataInputStream`.

Control flow: the test configures the harness for three NameNodes, starts a failover thread every second, increases client failover attempts, and starts NN0 as active. It creates three `CircularWriter` threads under separate directories. Each writer repeatedly creates files named by index and writes the next index as a byte until it reaches length 50, then reads the chain back to ensure every referenced file exists. The outer test waits up to 100 seconds for all writers to signal completion and fails with thread state if any remain.

State and persistence behavior: namespace mutations are simple create/delete-like writes under separate directories, but they are performed while active service moves among three NNs. The file content acts as a small persisted pointer to the next expected path.

Dependencies and integration points: integrates with the HA stress harness's failover thread and failover FileSystem client, plus Hadoop's multithreaded test context for exception propagation.

Risks and test signals: risks include client retry exhaustion, failed create/open during multi-NN failover, namespace inconsistency visible to later reads, and three-NN bugs hidden by two-NN tests. Completion of all writers and full traversal of every circular-list directory are the core signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestSeveralNameNodes.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestStandbyBlockManagement.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestStandbyBlockManagement.java

Purpose: ensures standby and observer NameNodes ingest block state but do not perform active-only block management work such as invalidation or redundant replica processing.

Important APIs and types: `MiniDFSCluster`, `HAUtil.setAllowStandbyReads`, `BlockManagerTestUtil.computeAllPendingWork`, `BlockManager.getPendingDeletionBlocksCount`, `BlockManager.getExcessBlocksCount`, `DFSTestUtil.waitReplication`, and NameNode state assertions.

Control flow: `testInvalidateBlock` creates a two-NN, three-DN HA cluster, writes a file, rolls edits so the standby catches up, deletes the file on the active, computes pending work on the active, rolls edits again, and asserts the standby has zero pending deletion blocks before and after heartbeats/block reports. `testNotHandleRedundantReplica` starts four DNs, confirms active/standby states and empty excess maps, writes a file with replication four, lowers replication to three, waits for standby catch-up and DN deletion reports, and asserts both active and standby have zero excess blocks after the active-driven deletion completes.

State and persistence behavior: deletion and replication-factor edits are tailed by standby, but scheduling deletion and excess-replica bookkeeping must remain active-owned. Standby state should reflect block locations without enqueuing deletion work.

Dependencies and integration points: integrates NameNode block manager queues, DataNode heartbeat/block/deletion reports, HA tailing, replication monitor calculations, and standby reads.

Risks and test signals: risks include standby issuing invalidations, accumulating excess replica state, or double-processing block-management actions after failover. Signals are exact zero counts for pending deletion and excess blocks around triggered reports and replication changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestStandbyBlockManagement.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestStandbyCheckpoints.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestStandbyCheckpoints.java

Purpose: broad integration coverage for standby checkpoint creation, upload, cancellation, multi-NameNode/observer distribution, image transfer failures, lock behavior, legacy OIV image handling, and checkpoint timing metrics.

Important APIs and types: `StandbyCheckpointer`, `FSImage`, `JournalSet`, `NameNodeAdapterMockitoUtil`, `HATestUtil.waitForCheckpoint`, `FSImageTestUtil`, `TransferFsImageUpload` threads, `RemoteNameNodeInfo`, `DFS_NAMENODE_CHECKPOINT_*` keys, `DFS_IMAGE_TRANSFER_RATE_KEY`, `DFS_NAMENODE_CHECKPOINT_PARALLEL_UPLOAD_ENABLED_KEY`, `Canceler`, `LogVerificationAppender`, and `SlowCodec`.

Control flow: setup starts a three-NN HA topology with low checkpoint thresholds, short edit tailing, compressed fsimage using `SlowCodec`, legacy OIV output directory, and NN0 active. Tests create edits, wait for standby catch-up/checkpoints, and assert fsimage txids on active, standby, and observer. They cover initializing new name dirs after checkpoint upload, simultaneous standby checkpointing, observer image upload, putImage before HTTP FSImage initialization, no-op repeated checkpoints at same txid, cancellation during local save and throttled upload, parallel upload thread count, expected `StandbyException` while checkpointing, JMX/read access while cp-lock is held, non-primary standby uploads, OIV save exceptions, last checkpoint time updates, and partial fsimage upload failure tolerance.

State and persistence behavior: exercises local and shared edits, fsimage files in each NameNode storage directory, legacy OIV image artifacts, checkpoint txids, last checkpoint timestamps, and background transfer thread lifecycle. It also asserts standby should not purge shared edits.

Dependencies and integration points: integrates HTTP image transfer, HA state transitions, observer state, edit log rolling/tailing, FSNamesystem locks, compression codecs, log capture, filesystem storage layout, and checkpoint cleanup.

Risks and test signals: risks include missing checkpoint uploads, aborts during duplicate checkpoint receipt, leaked transfer threads, standby read/write lock deadlocks, corrupt image acceptance after canceled upload, failed observer sync, and bad behavior when only part of upload fanout fails. Signals include exact checkpoint txid waits, parallel-file identity checks, Mockito verification of no shared-log purge and save counts, thread inspection, log-message verification, lock queue assertions, and timestamp comparisons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestStandbyCheckpoints.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestStandbyInProgressTail.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestStandbyInProgressTail.java

Purpose: validates standby tailing of in-progress edit logs through QJM, including default disabled behavior, enabled catch-up, failover catch-up across multiple segments, non-uniform configuration, journal cache use, corrupt cache fallback, and operation without cache.

Important APIs and types: `MiniQJMHACluster`, `MiniDFSCluster`, `DFS_HA_TAILEDITS_INPROGRESS_KEY`, `QJM_RPC_MAX_TXNS_KEY`, `JournalTestUtil.corruptJournaledEditsCache`, `NNStorage.getInProgressEditsFileName`, `NameNodeAdapter.getFileInfo`, `EditLogTailer.doTailEdits`, and JournalNode edit cache settings.

Control flow: setup enables in-progress tailing, slows normal tailing to 20 minutes, limits QJM RPC transaction batches, allows standby reads, and starts QJM HA. `testDefault` restarts with in-progress tailing disabled and confirms the standby neither has local edit files nor sees unfinalized edits until failover. Enabled tests create mkdir edits, wait until standby sees paths before log rolls, restart standby without finalizing shared edits, and verify state survives. Additional tests exercise partially started tailing, initial tail of finalized plus in-progress segments, new in-progress segments after prior tailing, transition-to-active catch-up across three rolled segments, active without in-progress tailing, cache-only serving after deleting finalized edit files, corrupt cache fallback across remaining JournalNodes, and disabled cache fallback to log files.

State and persistence behavior: tracks local NameNode edits directories, shared QJM logs, in-progress and finalized segment names, JournalNode edit caches, committed txid visibility, and standby namespace file info.

Dependencies and integration points: integrates QJM JournalNodes, HA edit tailer, storage directory inspection, manual RPC mkdir/roll operations, DFSUtil nameservice lookup, and test utilities for cache corruption.

Risks and test signals: risks include double replay from mid-segment restart, failure to tail current edits, relying incorrectly on local standby edit files, failover with under-tailed segments, and cache corruption causing lost edits. Signals include `assertNoEditFiles`, `assertEditFiles`, repeated `waitForFileInfo` with manual tailing, deletion/corruption of journal artifacts, and final namespace visibility checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestStandbyInProgressTail.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestStandbyIsHot.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestStandbyIsHot.java

Purpose: verifies that a standby NameNode is "hot" not only for namespace metadata but also for block-location information from block reports, replication changes, and DataNode restarts.

Important APIs and types: `MiniDFSCluster`, `HAUtil.setAllowStandbyReads`, `NameNodeAdapter.getBlockLocations`, `LocatedBlocks`, `DatanodeInfo`, `BlockManagerTestUtil`, `DataNodeProperties`, and `GenericTestUtils.waitFor`.

Control flow: `testStandbyIsHot` starts two NNs and three DNs, writes a file, rolls the active edit log, waits for the standby to report three block locations, triggers heartbeats/block reports, lowers replication to one and waits for both active and standby location counts, then raises replication back to three and waits again. `testDatanodeRestarts` creates a five-block file with one DN, waits for standby catch-up, stops the DN, manually notices it dead on both NNs, verifies the active has five under-replicated blocks while the standby has zero needed-replication queue entries, confirms standby block locations are empty, restarts the DN, waits for first block reports, and confirms both NNs report healthy state and standby locations return.

State and persistence behavior: standby state includes block-location maps and DataNode liveness derived from reports, but not active scheduling queues. Replication-factor edits and DataNode restart reports update observable standby read results.

Dependencies and integration points: integrates block reports, heartbeats, replication work computation, standby reads, NameNode adapter block-location calls, and DataNode lifecycle controls.

Risks and test signals: risks include standby stale block locations, slow or missing DataNode re-registration, standby incorrectly managing under-replication queues, and failover to a cold standby. Signals are exact replica-count polling, under-replicated count differences between active and standby, and block-location length changes from one to zero and back to one.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestStandbyIsHot.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestStateTransitionFailure.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestStateTransitionFailure.java

Purpose: verifies that a NameNode shuts down when transition to active fails partway through service startup.

Important APIs and types: `MiniDFSCluster`, `MiniDFSNNTopology.simpleHATopology`, `CommonConfigurationKeys.FS_TRASH_INTERVAL_KEY`, `ExitUtil.ExitException`, and `GenericTestUtils.assertExceptionContains`.

Control flow: the test configures an illegal negative trash interval, starts a two-NN HA cluster with zero DNs and `checkExitOnShutdown(false)`, waits for startup, and attempts `cluster.transitionToActive(0)`. A successful transition fails the test. The expected path catches `ExitException` and asserts it contains the trash emptier startup error.

State and persistence behavior: no namespace persistence is central here. The relevant state is HA service transition state and daemon process shutdown behavior when active services cannot be fully initialized.

Dependencies and integration points: integrates HA state transition code with trash emptier initialization and Hadoop's exit trapping utility used in tests.

Risks and test signals: risk is a partially active NameNode remaining alive after initialization failure, which could serve inconsistent or incomplete active services. The explicit `ExitException` content check is the signal that failure is both detected and routed through shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestStateTransitionFailure.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestUpdateBlockTailing.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestUpdateBlockTailing.java

Purpose: regression coverage for generation-stamp consistency when standby NameNodes tail block update operations while also processing incremental block reports.

Important APIs and types: `MiniQJMHACluster`, `DFS_HA_TAILEDITS_INPROGRESS_KEY`, `FSNamesystem`, `NameNodeAdapter.addBlockNoJournal`, `NameNodeAdapter.persistBlocks`, `NameNodeAdapter.getGenerationStamp`, `NameNodeAdapter.getImpendingGenerationStamp`, `ReceivedDeletedBlockInfo`, `StorageReceivedDeletedBlocks`, `DatanodeStorageInfo`, `INodeFile`, and `ClientProtocol.updateBlockForPipeline`.

Control flow: class-level setup starts a two-NN QJM HA cluster with one DN and in-progress tailing enabled, activates NN0, creates a test directory, and caches FSNamesystem and DataNode references. `testStandbyAddBlockIBRRace` manually adds a block on the active without journaling, tails the generation-stamp increment to standby, sends an IBR for that new block to standby, persists the block/update transaction on active, tails it, and asserts both block and global generation stamps align and the standby retained the replica. It then updates the block for pipeline, fails over, and verifies the new active restores the old active's global generation stamp. Other tests create files and exercise append without new block, append with `NEW_BLOCK`, and truncate, tailing the relevant edit operations and asserting generation-stamp equality after each.

State and persistence behavior: focuses on global and impending generation stamps, block info stored in the namesystem, INode block lists, edit log operations such as `OP_SET_GENSTAMP_V2`, `OP_ADD_BLOCK`, `OP_UPDATE_BLOCKS`, `OP_APPEND`, and `OP_TRUNCATE`, plus IBR-derived replica state.

Dependencies and integration points: integrates QJM in-progress tailing, active edit logging, standby IBR processing, DataNode storage lookup, client append/truncate APIs, and failover.

Risks and test signals: risks include standby generation stamp going backward or ahead, losing replica association after update-block tailing, and failover choosing an unsafe generation stamp. Signals are exact equality assertions for active/standby global and impending stamps and storage-info presence on the tailed block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestUpdateBlockTailing.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestXAttrsWithHA.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestXAttrsWithHA.java

Purpose: verifies extended attributes are tailed by standby NameNodes and remain available after failover.

Important APIs and types: `MiniDFSCluster`, `HAUtil.setAllowStandbyReads`, `FileSystem.setXAttr`, `FileSystem.getXAttrs`, `NameNode.getRpcServer().getXAttrs`, `XAttr`, `XAttrSetFlag`, and `HATestUtil.waitForStandbyToCatchUp`.

Control flow: setup creates a two-NN HA cluster with standby reads enabled, one DN, short tailing period, and NN0 active. The test creates `/file`, sets two `user.*` xattrs with `CREATE`, waits for standby catch-up, and reads xattrs directly from NN1's RPC server to confirm two entries. It then shuts down NN0, transitions NN1 active, reads xattrs through the failover filesystem, checks both byte arrays exactly, and deletes the file.

State and persistence behavior: xattr namespace metadata is persisted via edit logs and reconstructed on standby; after failover, the former standby must serve the same byte values as active metadata.

Dependencies and integration points: integrates HA edit tailing, xattr feature enablement defaults, standby reads, NameNode RPC xattr retrieval, and failover FileSystem access.

Risks and test signals: risks include missing xattr edits on standby, xattr values corrupted during failover, or failover client not seeing metadata on new active. Signals are direct standby count assertions and byte-for-byte `assertArrayEquals` checks after activation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestXAttrsWithHA.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/metrics/TestNNMetricFilesInGetListingOps.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/metrics/TestNNMetricFilesInGetListingOps.java

Purpose: validates the NameNodeActivity metric `FilesInGetListingOps`, which counts the number of file entries returned by getListing operations.

Important APIs and types: `MiniDFSCluster`, `DistributedFileSystem`, `DFSTestUtil.createFile`, `NameNodeRpcServer.getListing`, `HdfsFileStatus.EMPTY_NAME`, `MetricsAsserts.getMetrics`, and `MetricsAsserts.assertCounter`.

Control flow: setup starts a standard MiniDFSCluster with small block/checksum sizes and fast heartbeat/redundancy intervals. The test creates two files in `/tmp1` and two files in `/tmp2`, invokes the NameNode RPC `getListing` for `/tmp1`, and asserts the counter is 2. It then lists `/tmp2` and asserts the cumulative counter is 4.

State and persistence behavior: filesystem namespace state consists of four files across two directories. The metric is cumulative in the `NameNodeActivity` source and reflects RPC listing result sizes, not persistent metadata.

Dependencies and integration points: integrates NameNode RPC listing implementation, HDFS file creation, metrics2 counters, and direct test metrics assertions.

Risks and test signals: risk is undercounting or overcounting listed entries, especially with multiple calls. The cumulative counter checks after each directory listing provide simple exact signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/metrics/TestNNMetricFilesInGetListingOps.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/metrics/TestNameNodeMetrics.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/metrics/TestNameNodeMetrics.java

Purpose: broad coverage for metrics emitted by NameNodeActivity, FSNamesystem, JVM, RPC detailed metrics, HA edit tailing, encryption, resource health checks, block health, DataNode liveness, file operations, and erasure-coded block accounting.

Important APIs and types: `MetricsAsserts`, `DefaultMetricsSystem`, `MiniDFSCluster`, `FSNamesystem`, `BlockManager`, `NameNodeAdapter`, `BlockManagerTestUtil`, `DataNodeTestUtils`, `HostsFileWriter`, `HdfsAdmin`, `JavaKeyStoreProvider`, `NNHAServiceTarget`, `RpcDetailedMetrics`, `LocatedBlocks`, `LocatedStripedBlock`, and many metrics names such as `CapacityTotal`, `StaleDataNodes`, `VolumeFailuresTotal`, `FilesCreated`, `LowRedundancyBlocks`, `CorruptBlocks`, `MissingBlocks`, `TransactionsSinceLastCheckpoint`, `SyncsNumOps`, `EditLogTailTime`, and `CommitBlockSynchronizationNumOps`.

Control flow: setup builds a cluster with enough DNs for the XOR EC policy, enables EC on `/testNameNodeMetrics/ec`, initializes include/exclude host files, and records `FSNamesystem`/`BlockManager`. Tests then create replicated and striped files, corrupt replicas/EC cells, lower replication, delete files, manipulate DataNode heartbeat timestamps, inject disk failure, decommission and expire DNs, rename files, read files to increment block-location counters, open multiple under-construction streams across clients, create encryption zones, monitor HA health, start a separate HA cluster for checkpoint/tailing metrics, and inspect RPC detailed metrics.

State and persistence behavior: metrics reflect live NameNode and block-manager state rather than standalone persisted state. The suite deliberately mutates namespace, block maps, DataNode descriptors, volume health, checkpoint txids, edit logs, encryption-zone keys, and client lease tables, then polls metrics sources until expected gauges/counters settle.

Dependencies and integration points: integrates metrics2, MiniDFSCluster, erasure coding, DataNode storage volumes, host include/exclude files, HA standby checkpoints, safe mode/saveNamespace, KMS/key-provider setup, NameNode health monitor RPC, and RPC detailed metrics registration.

Risks and test signals: risks include stale or misnamed metrics, replicated/EC aggregate mismatches, block health counters not resetting after delete, DataNode liveness/decommission regressions, missing quantile gauges, and HA metrics not registered under the right source. Signals are exact gauge/counter assertions, aggregate tally helper checks, polling helpers for asynchronous deletion/replication, quantile gauge assertions, and RPC metric existence checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/metrics/TestNameNodeMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/metrics/TestTopMetrics.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/metrics/TestTopMetrics.java

Purpose: verifies that the NameNode top-user metrics source publishes expected records and counters for operation totals and per-user operation counts.

Important APIs and types: `TopConf`, `TopMetrics`, `TOPMETRICS_METRICS_SOURCE_NAME`, `MetricsAsserts.getMetrics`, `MetricsCollector`, `MetricsRecordBuilder`, `Interns.info`, and Mockito `verify`.

Control flow: the test constructs `TopMetrics` with default reporting windows from `TopConf`, reports the user `test` performing `listStatus` three times, retrieves metrics, and verifies the collector receives records for the 60s, 300s, and 1500s windows. It then verifies each window emits `op=listStatus.TotalCount`, wildcard `op=*.TotalCount`, and `op=listStatus.user=test.count` counters with value 3.

State and persistence behavior: all state is in-memory rolling-window top metrics. There is no filesystem namespace or persistent state.

Dependencies and integration points: integrates top metrics aggregation with Hadoop metrics2 collection naming conventions and interned metric metadata.

Risks and test signals: risks include missing reporting windows, broken wildcard totals, incorrect per-user counter naming, or metrics source record naming changes. Mockito verification of three records and three counter emissions per metric is the main signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/metrics/TestTopMetrics.java -->
