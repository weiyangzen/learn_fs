# subset-b-007522 Research

Grouped research for Hadoop HDFS tests under `sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestAppendSnapshotTruncate.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestAppendSnapshotTruncate.java

Purpose: Stress-tests random interleavings of HDFS append, snapshot, and truncate operations against a local filesystem mirror. It is intended to catch NameNode, snapshot, lease, and block recovery regressions where file contents or snapshot views diverge after concurrent mutation.

Important APIs, types, and functions: `MiniDFSCluster`, `DistributedFileSystem`, `FSDataOutputStream`, `dfs.allowSnapshot`, `dfs.createSnapshot`, `dfs.deleteSnapshot`, `dfs.append`, `dfs.truncate`, `TestFileTruncate.checkBlockRecovery`, and `AppendTestUtil.checkFullFile`. The nested `DirWorker`, `FileWorker`, and abstract `Worker` classes drive the test. `Worker.State` tracks `IDLE`, `RUNNING`, `STOPPED`, and `ERROR` with `AtomicReference`, `AtomicBoolean`, and `SubjectInheritingThread`.

Control flow: `startUp` configures a 4-DataNode cluster with small 1 KiB blocks/checksums, short heartbeats, short reconstruction pending timeout, and best-effort datanode replacement. `testAST` creates `/dir`, enables snapshots, initializes a local test directory, starts ten `FileWorker` threads plus one `DirWorker`, runs for 20 seconds, then stops and verifies all files and remaining snapshots. `FileWorker.call` randomly checks full contents, appends random bytes, truncates by arbitrary byte counts, or truncates to block boundaries. `DirWorker.call` randomly pauses all file workers, snapshots the HDFS directory while copying local files to a local snapshot directory, checks existing snapshots, or deletes snapshots.

State and persistence behavior: The test keeps two state stores in sync: HDFS and a local filesystem mirror under `GenericTestUtils.getTestDir`. Snapshot metadata is tracked in `snapshotPaths`, while local snapshot copies model point-in-time contents. Truncate may return not-ready, so the test explicitly waits for HDFS block recovery before comparing bytes. Error state is persisted in each worker's `thrown` field and surfaced during final verification.

Dependencies and integration points: Integrates with the HDFS client write path, NameNode snapshot subsystem, file truncate recovery, local `FileUtil`/Commons IO copying, and test logging through `NameNode.stateChangeLog`. It also depends on random scheduling and HDFS lease/block recovery behavior.

Risks: This is intentionally timing-sensitive and can be flaky if worker pause detection, thread interruption, heartbeat timing, or local file cleanup changes. The local mirror is authoritative for expected bytes, so any non-atomic local/HDFS update ordering bug in the test can masquerade as an HDFS regression. The test is long-running by unit-test standards and has broad integration blast radius.

Test signals: Success means all worker threads stop without `ERROR`, every live HDFS file matches its local mirror, every remaining snapshot path has the same entries and byte contents as its local snapshot copy, and append/truncate recovery completed where required.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestAppendSnapshotTruncate.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestApplyingStoragePolicy.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestApplyingStoragePolicy.java

Purpose: Validates the user-visible `DistributedFileSystem` storage policy semantics for default, explicit, unset, and inherited policies on nested directories and files.

Important APIs, types, and functions: `MiniDFSCluster`, `DistributedFileSystem`, `DFSTestUtil.createFile`, `BlockStoragePolicySuite.createDefaultSuite`, `BlockStoragePolicy`, `setStoragePolicy`, `getStoragePolicy`, and `unsetStoragePolicy`. The tests compare against the default `HOT`, `WARM`, and `COLD` policies from the default suite.

Control flow: Each test starts a single-DataNode MiniDFSCluster in `clusterSetUp` and shuts it down in `clusterShutdown`. `testStoragePolicyByDefault` creates `/foo/bar/wow` and asserts all existing paths resolve to `HOT`; a missing path should throw `FileNotFoundException`. `testSetAndUnsetStoragePolicy` explicitly sets `WARM`, `COLD`, and `HOT` at different levels, verifies retrieval, unsets all three, and verifies fallback to `HOT`. `testNestedStoragePolicy` unsets from the leaf upward and checks nearest-ancestor inheritance. `testSetAndGetStoragePolicy` covers file and parent policy setting through the same DFS API.

State and persistence behavior: The tests manipulate in-memory NameNode metadata in a fresh cluster per method. They do not restart the NameNode, so edit-log/fsimage persistence is left to `TestBlockStoragePolicy`. The relevant state is the policy ID stored on inode metadata and the effective policy resolved from ancestors when an inode has no explicit policy.

Dependencies and integration points: Integrates the public DFS client API with the NameNode storage-policy manager and default policy suite. It also exercises exception translation for nonexistent paths.

Risks: The tests catch semantic regressions in inheritance but not physical block placement. They use broad `catch (Exception)` blocks and then `instanceof` checks, so unexpected exception subclasses could be less clearly diagnosed than `assertThrows`.

Test signals: Success means existing files and directories resolve to the expected explicit or inherited policy, missing paths consistently produce `FileNotFoundException`, and unsetting leaf/ancestor policies walks back through nearest ancestor and finally default `HOT`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestApplyingStoragePolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestBalancerBandwidth.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestBalancerBandwidth.java

Purpose: Ensures DataNode balancer bandwidth is initialized from configuration, can be changed dynamically through HDFS admin APIs, and is reported correctly by `dfsadmin -getBalancerBandwidth`.

Important APIs, types, and functions: `DFS_DATANODE_BALANCE_BANDWIDTHPERSEC_KEY`, `DistributedFileSystem.setBalancerBandwidth`, `DataNode.getBalancerBandwidth`, `DFSAdmin`, `ToolRunner.run`, and `GenericTestUtils.waitFor`. `runGetBalancerBandwidthCmd` captures `System.out` to validate CLI output.

Control flow: The test configures the default bandwidth to 1 MiB/s, starts a two-DataNode cluster, verifies both DataNodes have the configured value, and checks the admin command for each DataNode IPC address. It then sets bandwidth to 12 MiB/s and waits until both DataNodes expose the new value. A later call with `0` is expected to leave the current value unchanged. Finally, the CLI accepts `1t` and rejects `1e`.

State and persistence behavior: The bandwidth value is DataNode runtime state. The test does not assert restart persistence; it checks initialization from config and live NameNode-to-DataNode command propagation. CLI output capture is transient process state, restored in a `finally` block.

Dependencies and integration points: Exercises `DistributedFileSystem`, DataNode runtime config update handling, DFSAdmin command parsing, IPC listener address construction, unit parsing, and stdout formatting.

Risks: Timing depends on asynchronous propagation, hence the 60-second wait. The test mutates global `System.out`, so failure to restore it would affect later tests; the helper protects this with `finally`. It also uses a static `Configuration`, making accidental cross-test mutation a possible maintenance hazard.

Test signals: Success means DataNodes expose configured and updated bandwidth values, setting `0` does not overwrite the previous value, `-getBalancerBandwidth` prints the expected bytes-per-second string, and DFSAdmin unit parsing behaves as expected for tera and exa suffix examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestBalancerBandwidth.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestBatchedListDirectories.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestBatchedListDirectories.java

Purpose: Tests the experimental batched listing APIs for files, directories, located statuses, repeated paths, missing paths, relative paths, limits, and access-control failures.

Important APIs, types, and functions: `DistributedFileSystem.batchedListStatusIterator`, `batchedListLocatedStatusIterator`, `PartialListing<FileStatus>`, `PartialListing<LocatedFileStatus>`, `RemoteIterator`, `CommonPathCapabilities.FS_EXPERIMENTAL_BATCH_LISTING`, `DFS_LIST_LIMIT`, `DFS_NAMENODE_BATCHED_LISTING_LIMIT`, `FsPermission`, and `UserGroupInformation.doAs`.

Control flow: `beforeClass` starts a one-DataNode cluster with small listing limits and calls `loadData`. The fixture creates two first-level directories, three subdirectories under each, five files per subdirectory, an empty directory, a standalone data file, and a no-permission directory containing a file. Helpers convert `PartialListing` iterators into lists while preserving per-source listed paths. Tests cover empty input, empty directories, files, missing paths, mixtures of missing and valid paths, relative working-directory behavior, capability declaration, batches of many file paths, batches of directory paths, too many source paths, repeated paths, located status block metadata, and listing as a non-owner user.

State and persistence behavior: Static lists `SUBDIR_PATHS` and `FILE_PATHS` mirror the fixture tree for expected ordering and path assertions. The cluster is static for the test class and shut down once. Permission state is persisted in HDFS inode metadata by setting the inaccessible directory to mode `0000`.

Dependencies and integration points: Integrates the HDFS batched listing implementation with `FileSystem` path qualification, NameNode list batching, partial exception reporting, located block lookup, path capabilities, and Hadoop security/permission checks.

Risks: The expected ordering relies on fixture insertion/listing order and on `LinkedHashMap` grouping. Some missing-path behavior is lazy: exceptions are raised by `PartialListing.get()`, so callers must not assume iterator construction alone validates every path. Static mutable fixture lists would be problematic if the setup were rerun in the same JVM without class isolation.

Test signals: Success means batch iterators preserve path grouping and duplicate inputs, return correct file counts and qualified paths, surface `FileNotFoundException` and `AccessControlException` at the expected time, respect configured path limits, expose block locations for located listing, and advertise the experimental capability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestBatchedListDirectories.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestBlockMissingException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestBlockMissingException.java

Purpose: Verifies that deleting the only physical replica of a block causes HDFS reads to fail with `BlockMissingException`.

Important APIs, types, and functions: `MiniDFSCluster`, `DistributedFileSystem`, `FSDataOutputStream`, `FSDataInputStream`, `LocatedBlocks`, `getBlockLocations`, `corruptBlockOnDataNodesByDeletingBlockFile`, and `BlockMissingException`.

Control flow: The test starts a three-DataNode cluster with short client retry windows, creates a four-block file with replication factor one, asks the NameNode for block locations, deletes the first block file on the DataNode, then attempts to read the file sequentially. `validateFile` reads until EOF or exception and asserts that `BlockMissingException` was observed.

State and persistence behavior: The key state is on-disk block storage in the MiniDFSCluster's DataNode directories and NameNode block-location metadata. The test physically deletes the block file through cluster test utilities but does not wait for block reports; it relies on the client discovering the missing replica during read.

Dependencies and integration points: Exercises client read retry/error translation, NameNode block location lookup, DataNode storage files, and the cluster's block corruption/deletion test hooks.

Risks: If missing-block detection behavior changes from read-time exception to earlier metadata reporting, the test may need adjustment. The file creation helper writes zero-filled blocks, so this is an availability/error-path test rather than a content integrity test.

Test signals: Success means the client read path sees an unrecoverable missing block and raises `BlockMissingException` instead of silently returning EOF, another exception, or stale data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestBlockMissingException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestBlockRecoveryCauseStandbyNameNodeCrash.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestBlockRecoveryCauseStandbyNameNodeCrash.java

Purpose: Reproduces a high-availability erasure-coded lease recovery scenario where commit block synchronization after deleting/committing an EC block group must not crash the standby NameNode.

Important APIs, types, and functions: `MiniDFSNNTopology.simpleHATopology`, `DistributedFileSystem`, `DFSStripedOutputStream`, `StripedDataStreamer`, `DataNodeTestUtils.pauseIBR/resumeIBR`, `Whitebox.setInternalState`, `GenericTestUtils.waitFor`, `recoverLease`, and `DataStreamer.waitForAckedSeqno`.

Control flow: `setup` configures EC block size, socket timeout, heartbeats, HA edit tailing/log rolling, and a two-NameNode HA cluster with `dataBlocks + parityBlocks` DataNodes. It enables the default EC policy on a test directory. The test pauses incremental block reports on parity-plus-one DataNodes, creates an EC file, writes slightly more than one full EC block group, waits for every striped streamer to ack queued packets, replaces each streamer's `blockStream` with a null output stream to simulate a quiet client failure, and invokes lease recovery as another user. Finally it resumes paused IBRs.

State and persistence behavior: NameNode HA edit state, EC block group metadata, DataNode IBR queues, and client streamer internals are deliberately manipulated. The test is not asserting file content; it asserts recovery and standby edit processing survive this interleaving. `newConf` points clients at the cluster configuration for active NameNode access.

Dependencies and integration points: Deeply integrates EC writing, striped streamers, lease recovery, HA standby tailing, DataNode IBR behavior, fake UGI users, and test-only whitebox mutation of streamer internals.

Risks: This is timing-sensitive and relies on internal field names (`blockStream`) and EC policy defaults. It can become brittle if streamer internals, HA timing, or EC block group accounting changes. The assertion is mostly absence of failure; a standby crash manifests indirectly as an exception or timeout.

Test signals: Success means manual lease recovery completes within the wait window after the simulated client failure and paused IBR condition, with no thrown failure from the active/standby NameNode path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestBlockRecoveryCauseStandbyNameNodeCrash.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestBlockStoragePolicy.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestBlockStoragePolicy.java

Purpose: Provides the broad regression suite for HDFS block storage policy definitions, policy selection algorithms, public set/get behavior, persistence through edits/fsimage, snapshot policy visibility, replication changes, block placement, block token storage restrictions, and configurable defaults.

Important APIs, types, and functions: `BlockStoragePolicySuite`, `BlockStoragePolicy`, `StorageType`, `HdfsConstants` policy IDs/names, `DistributedFileSystem.setStoragePolicy/getStoragePolicy`, `DFSClient.setStoragePolicy/getStoragePolicy`, `HdfsFileStatus`, `HdfsLocatedFileStatus`, `DirectoryListing`, `LocatedBlocks`, `BlockPlacementPolicy.chooseTarget`, `DatanodeStorageInfo`, `DatanodeDescriptor`, `BlockManagerTestUtil`, `SnapshotTestHelper`, `BlockTokenSecretManager.checkAccess`, and `FileSystem.getAllStoragePolicies`.

Control flow: The early tests check storage-policy enablement config and the default policy suite's string forms, type sequences, creation fallbacks, and replication fallbacks. The `CheckChooseStorageTypes` strategy interface runs the same expected placement matrix across basic, unavailable-storage, and new/non-new block variants. Later tests verify excess replica selection, invalid policy/path handling, directory-listing policy IDs, NameNode restart and saveNamespace persistence, DFSClient direct set/get, snapshot paths reflecting latest policy, replication factor increases/decreases for HOT/WARM/COLD across DISK/ARCHIVE storage, placement with topology, SSD preference, adding a DataNode to an ALL_SSD pipeline, policy inheritance after NameNode restart, listing all policy names, enum ordering, block-token access checks for storage types and storage IDs, and configured default policy creation/file behavior.

State and persistence behavior: This file explicitly validates NameNode metadata persistence by restarting from edit logs and from fsimage after `saveNamespace`. It tests effective policy state stored on inodes and inherited from parents, plus physical storage-type state in located blocks. Some tests construct standalone NameNodes and synthetic topology/storage descriptors rather than full clusters.

Dependencies and integration points: Covers NameNode policy metadata, client protocols, block placement policy, network topology, DataNode storage reports, snapshots, safe mode namespace save, block token secret manager authorization, configuration parsing, and `FileSystem` SPI exposure.

Risks: This is a large, mixed unit/integration class. Many assertions encode exact default-policy string output and placement matrices, so policy evolution requires deliberate test updates. Several tests use sleeps and manual heartbeat/block-report triggers, which can be slow or timing-sensitive. Standalone NameNode setup mutates shared static `conf` and filesystem test directories, so isolation matters.

Test signals: Success means storage policy behavior is internally consistent across policy suite calculations, DFS APIs, metadata listing, restart persistence, snapshots, block placement, replication changes, token access control, and configured default policy selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestBlockStoragePolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestBlockTokenWrappingQOP.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestBlockTokenWrappingQOP.java

Purpose: Verifies that, when enabled, the NameNode sends the negotiated RPC quality-of-protection value back to the client inside block access tokens for add-block, append, and block-location calls.

Important APIs, types, and functions: Extends `SaslDataTransferTestCase`; uses `createSecureConfig`, `DFS_NAMENODE_SEND_QOP_ENABLED`, `DFS_BLOCK_ACCESS_TOKEN_ENABLE_KEY`, `HADOOP_RPC_PROTECTION`, `IngressPortBasedResolver`, `DFSClient.namenode.addBlock`, `append`, `getBlockLocations`, `LocatedBlock`, `LastBlockWithStatus`, and token `decodeIdentifier().getHandshakeMsg()`.

Control flow: Parameterized tests run for `privacy -> auth-conf`, `integrity -> auth-int`, and `authentication -> auth`. `setup` creates a secure config with an auxiliary NameNode RPC port, service RPC port, ingress-port SASL resolver, block tokens, and QOP-return enabled. The client connects through the auxiliary URI. `testAddBlockWrappingQOP` creates a file and calls `addBlock`; `testAppendWrappingQOP` writes one byte before append so a last block exists; `testGetBlockLocationWrappingQOP` writes one byte and checks every returned located block token.

State and persistence behavior: The relevant state is runtime security negotiation and the handshake message embedded in issued block tokens. The tests do not check persistence; clusters are rebuilt per parameter invocation and shut down after each test.

Dependencies and integration points: Integrates Hadoop RPC SASL configuration, ingress-port-specific QOP resolution, HDFS block token issuance, NameNode client protocol methods, and DFS client connection setup through an auxiliary port.

Risks: Security configuration is sensitive to port and resolver behavior. If RPC address handling changes, the auxiliary/service RPC split may need updates. The test decodes token internals directly, so token identifier format changes would affect assertions.

Test signals: Success means every tested NameNode response that carries a block token embeds the expected negotiated QOP string for the configured protection level.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestBlockTokenWrappingQOP.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestBlocksScheduledCounter.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestBlocksScheduledCounter.java

Purpose: Tests `DatanodeDescriptor.getBlocksScheduled()` accounting for normal writes, abandoned blocks, deleted files, and truncation while reconstruction work is pending.

Important APIs, types, and functions: `DatanodeManager.fetchDatanodes`, `DatanodeDescriptor.getBlocksScheduled`, `BlockManager`, `BlockManagerTestUtil.computeAllPendingWork/updateState/waitForMarkedDeleteQueueIsEmpty`, `NameNodeAdapter.getBlockLocations`, `findAndMarkBlockAsCorrupt`, `DataNodeTestUtils.setHeartbeatsDisabledForTests`, `DistributedFileSystem.truncate`, and namesystem block-manager write locks.

Control flow: The basic test creates a file, writes and `hflush`es to allocate a block, checks one scheduled block, then closes and checks zero. The abandoned-block test stops one DataNode before a replicated write and ensures the stopped target is not left scheduled while live targets are. The deleted-block test creates a replicated file, disables heartbeats, marks replicas corrupt under the BM write lock, computes pending reconstruction, deletes the file, drains the delete queue, and sums scheduled counts. The truncate test stops/restarts a DataNode to create under-replication, disables heartbeats, computes pending work, truncates the file, and checks scheduled counts clear.

State and persistence behavior: The tests target in-memory NameNode block-management counters and pending reconstruction queues. They also manipulate DataNode heartbeat state and corruption metadata. There is no restart persistence check; correctness is immediate counter cleanup when lifecycle events happen.

Dependencies and integration points: Integrates client writes, hflush block allocation, DataNode liveness, corruption marking, block reconstruction scheduling, file deletion, truncation, and internal NameNode locking.

Risks: These tests depend on internal block manager APIs and manual lock discipline. Timing is controlled by disabling heartbeats and direct state updates, but the surrounding cluster behavior can still be sensitive to asynchronous deletion and reconstruction queues.

Test signals: Success means scheduled block counters increment only while work is genuinely scheduled and return to zero after close, abandon, delete, or truncate clears pending work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestBlocksScheduledCounter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestByteBufferPread.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestByteBufferPread.java

Purpose: Validates positional read (`pread`) and `readFully` behavior when reading into heap and direct `ByteBuffer` instances.

Important APIs, types, and functions: `FSDataInputStream.read(long, ByteBuffer)`, `FSDataInputStream.readFully(long, ByteBuffer)`, heap `ByteBuffer.allocate`, direct `ByteBuffer.allocateDirect`, buffer `position`, `limit`, `hasRemaining`, and content checks with `assertArrayEquals`.

Control flow: `setup` starts a three-DataNode cluster with 4 KiB HDFS blocks and writes a deterministic 12-block random file. `testPreadWithHeapByteBuffer` and `testPreadWithDirectByteBuffer` run the same helper matrix. Helpers read the whole file with repeated preads, attempt a read into a full buffer, read into a half-limited buffer, read into a buffer whose initial position is half full, pread starting at the file midpoint, and use `readFully` for the entire file.

State and persistence behavior: Static test state includes the cluster, filesystem, deterministic byte array, file path, and seeded `Random`. The test file persists only for the class lifetime and is deleted during `shutdown`.

Dependencies and integration points: Exercises HDFS client input streams, positional read code paths, block boundary traversal across a multi-block file, direct-buffer handling, and standard Java NIO buffer state semantics.

Risks: The shared `Random` is advanced by helper calls that fill dummy buffers, but those bytes are only compared to same-call snapshots. The file content is deterministic, making regressions reproducible. The suite is less exhaustive than legacy `TestPread` and focuses on ByteBuffer-specific behavior.

Test signals: Success means reads advance buffer positions correctly, respect limits and existing positions, do not modify full buffers, return correct half-file slices for positioned reads, and produce byte-for-byte equality for both heap and direct buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestByteBufferPread.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestClientProtocolForPipelineRecovery.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestClientProtocolForPipelineRecovery.java

Purpose: Large slow-test suite covering DFS client and NameNode protocol behavior during write pipeline recovery, lease validation, DataNode restarts/upgrades, delayed packets/acks, transferBlock replacement, close-stage failures, and slow-node eviction.

Important APIs, types, and functions: `NamenodeProtocols.updateBlockForPipeline`, `DFSOutputStream`, `DataStreamer`, `PipelineAck`, `BlockConstructionStage`, `DFSAdmin -shutdownDatanode/-evictWriters`, `DataNodeFaultInjector`, `DFSClientFaultInjector`, `DataNodeTestUtils`, `DatanodeProtocolClientSideTranslatorPB.registerDatanode`, `ReplicaInPipeline`, `GenericTestUtils.waitFor`, and `SubjectInheritingThread`.

Control flow: `testGetNewStamp` rejects finalized, nonexistent, non-lease-holder, and null-lease-holder update attempts, then accepts the real lease holder for an RBW block. Other tests inject packet failure, dropped heartbeat packets, delayed upstream acks, restart OOB messages, writer eviction, restart timeout failure, rolling upgrade restarts with generation-stamp recovery, remote upgrade while a background writer keeps flushing, zero-byte partial-block recovery, transferBlock with end-of-chunk extra bytes, dead DataNode re-registration followed by repeated `updatePipeline`, adding a DataNode/failing nodes during `PIPELINE_CLOSE`, and marking a slow downstream node bad after threshold slow acks.

State and persistence behavior: Tests manipulate active write pipeline state: generation stamps, streamer node arrays, pipeline recovery counters, DataNode liveness, replica bytes acked/on disk, bad-node/slow-node tracking, and client lease ownership. State is mostly runtime and cluster-local; the key persistence-like signal is that closed files remain readable after recovery scenarios.

Dependencies and integration points: Integrates the DFS client write path, NameNode lease/block protocols, DataNode data-transfer pipeline, admin commands, fault injectors, rolling upgrade shutdown/restart handling, block reports, and block reader verification.

Risks: Marked `@Tag("slow")` because many cases depend on sleeps, socket timeouts, background writers, and asynchronous shutdown threads. It reaches into internal streamers and fault injectors, so refactors in write pipeline internals can require careful test updates. Several tests assert absence of corruption by reading after complex failure injection rather than inspecting every intermediate state.

Test signals: Success means expected protocol calls fail or succeed with correct lease/block states, generation stamps advance on recovery, pipeline recovery counters remain correct for upgrade waits, failed/slow nodes are replaced as intended, close and repeated close remain safe where expected, and files remain readable after injected pipeline failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestClientProtocolForPipelineRecovery.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestClientReportBadBlock.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestClientReportBadBlock.java

Purpose: Tests when a DFS client should report corrupt block replicas to the NameNode: always for a single replica, only for partial corruption when some replicas remain good, and not when all replicas of a multi-replica block are corrupt from the client's perspective.

Important APIs, types, and functions: `DFSTestUtil.createFile/waitReplication`, `MiniDFSCluster.corruptReplica`, `DFSInputStream.read`, positioned `read`, `ChecksumException`, `BlockMissingException`, `getBlockLocations`, `LocatedBlock.isCorrupt`, `NamenodeFsck`, `DFSck`, and `ToolRunner`.

Control flow: Each test creates a one-block file and corrupts selected replicas. `testOneBlockReplica` corrupts the only replica and exercises sequential and positioned reads, expecting the block to be marked corrupt and fsck to report corruption. `testCorruptAllOfThreeReplicas` corrupts all replicas and expects the client not to report them as corrupt to the NameNode, leaving fsck healthy. `testCorruptTwoOutOfThreeReplicas` corrupts two replicas, rereads until only the good replica remains in block locations, then checks fsck reports under-replication but not corrupt-file listing. Helpers verify replica counts, corrupt flags, read behavior, and fsck output/error codes.

State and persistence behavior: DataNode replica files are corrupted on disk via cluster test hooks. NameNode corrupt-replica state changes only when the client reports bad replicas during reads. The tests disable the block scanner so client reporting is the primary signal.

Dependencies and integration points: Integrates client checksum verification and bad-block reporting, NameNode located-block filtering, fsck health/corrupt-file reporting, DataNode replica corruption, and retry timing.

Risks: The partial-corruption test loops because MiniDFSCluster block-location ordering is pseudo-random by network distance; this can be slow if the good replica is not tried promptly. The expected policy is subtle: all-corrupt multi-replica reads should not report, while one-replica all-corrupt should.

Test signals: Success means located-block corrupt flags, returned replica counts, fsck health strings, and fsck error codes match the reporting policy after client read attempts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestClientReportBadBlock.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestClose.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestClose.java

Purpose: Checks close semantics for an HDFS output stream: writes after close must fail with `ClosedChannelException`, while repeated close calls must be harmless.

Important APIs, types, and functions: `MiniDFSCluster`, `FileSystem.get`, `FileSystem.create`, `OutputStream.write`, `OutputStream.close`, and `ClosedChannelException`.

Control flow: The test starts a default MiniDFSCluster, creates `/test`, writes `"foo"`, closes the stream, attempts another write and expects `ClosedChannelException`, then calls `close` a second time and expects no failure. The cluster is shut down in a `finally` block.

State and persistence behavior: The only persisted HDFS state is a small created file. The test is about client stream lifecycle state after close, not file content or restart persistence.

Dependencies and integration points: Integrates Hadoop `FileSystem` stream creation with HDFS client output stream state and Java channel-style close exception behavior.

Risks: This is a narrow behavior test. It does not assert file length or bytes; it only verifies post-close stream API behavior.

Test signals: Success means the client refuses writes after close with the specific expected exception and tolerates idempotent close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestClose.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestConnCache.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestConnCache.java

Purpose: Verifies DFS client connection caching when repeatedly reading different offsets of a file served entirely by one DataNode.

Important APIs, types, and functions: `BlockReaderTestUtil`, `DFSClient`, `DFSInputStream`, `ClientContext.getFromConf`, `PeerCache`, `HdfsClientConfigKeys.DFS_CLIENT_CONTEXT`, and `DFS_CLIENT_SOCKET_TIMEOUT_KEY`.

Control flow: The test sets a unique client context and very long socket timeout, creates a single-DataNode helper cluster, writes a three-block test file, opens it through a raw `DFSClient`, and calls `pread` at multiple offsets plus one sequential read. After closing the stream and client, it checks that the peer cache size is one.

State and persistence behavior: Client-side connection cache state is keyed by the configured context name. The test file is written by `BlockReaderTestUtil` and authentic bytes are retained in memory for verification. The final assertion observes cached peer state after the stream closes.

Dependencies and integration points: Exercises block reader socket reuse, DFS input seeking/reading, `ClientContext` isolation, and peer-cache retention under a long timeout.

Risks: The helper `pread` appears to reduce `length` to zero before its verification loop, so the content verification loop as written does not iterate; the main signal is connection-cache size and successful reads. Changes to peer-cache eviction timing would affect the assertion, hence the large socket timeout and unique context.

Test signals: Success means multiple seeks/reads against one DataNode do not require multiple cached sockets and leave exactly one cached peer in the client context.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestConnCache.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestCrcCorruption.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestCrcCorruption.java

Purpose: Tests HDFS checksum/corruption handling during writes and reads, including corruption injected into packet data and entirely corrupt files across one or more DataNodes.

Important APIs, types, and functions: `DFSClientFaultInjector`, `MiniDFSCluster`, `DFSTestUtil`, `DataNode`, `ReplicaInfo`, `ExtendedBlock`, `FSDataInputStream`, `FSDataOutputStream`, `ChecksumException`, `BlockMissingException`, and `IOUtils`. The file uses Mockito to mock client fault injection.

Control flow: `setUp` installs a mocked DFS client fault injector. `testCorruptionDuringWrt` writes initial data, flushes, injects one corrupt packet followed by an uncorrupt packet and expects the final file to read successfully; it then creates the file again, injects corruption without repair, and expects write/close to fail after retry exhaustion. `testCrcCorruption` runs `thistest` twice, once with default checksum/block settings and once with 17-byte checksums and 34-byte blocks. `thistest` creates 40 replicated files, waits for replication, then on the first DataNode cycles through finalized replicas deleting meta files, truncating meta files to two bytes, or corrupting meta files. The surviving second replica should keep all files readable. `testEntirelyCorruptFileOneNode` and `testEntirelyCorruptFileThreeNodes` call a shared helper that corrupts every replica of the first block and verifies reads eventually throw instead of looping forever.

State and persistence behavior: The tests modify DataNode on-disk replica/checksum metadata and global `DFSClientFaultInjector` process state. Cluster lifetime is local to each helper/test path, and corruption state is deliberately local to the MiniDFSCluster. The mock injector is reset to non-corrupting behavior in `testCorruptionDuringWrt`'s `finally` block, but the class does not preserve and restore a previous injector instance.

Dependencies and integration points: Integrates packet checksum creation, client write fault injection, DataNode replica storage, client checksum verification, block-location retry behavior, and read exception translation.

Risks: These tests are sensitive to low-level replica/meta file layout and fault-injector semantics. They use random fixture generation and DataNode internals, so changes in checksum chunk sizing, replica storage abstraction, or client retry policy can change observable exceptions. The disabled replication-reduction validation notes a historical unresolved risk around deleting excess corrupt replicas.

Test signals: Success means injected corruption is detected rather than silently accepted, client reads either recover from good replicas or raise the expected checksum/missing-block failure when every replica is corrupt, and global fault injection state is restored after each test.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestCrcCorruption.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSAddressConfig.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSAddressConfig.java

Purpose: Tests MiniDFSCluster DataNode address configuration behavior for default localhost binding and explicit `dfs.datanode.*.address` settings.

Important APIs, types, and functions: `DFS_DATANODE_ADDRESS_KEY`, `DFS_DATANODE_HTTP_ADDRESS_KEY`, `DFS_DATANODE_IPC_ADDRESS_KEY`, `MiniDFSCluster.startDataNodes`, `stopDataNode`, `DataNode.getXferAddress`, `DataNodeProperties`, and `StartupOption.REGULAR`.

Control flow: The test starts a default cluster and asserts the DataNode transfer address contains `127.0.0.1`. It stops the DataNode, unsets all DataNode address config keys, restarts DataNodes with the option to check configuration, and again expects localhost. It then stops the DataNode, sets transfer/http/ipc addresses to `0.0.0.0:0`, restarts, and expects the transfer address to contain `0.0.0.0`.

State and persistence behavior: DataNode processes are stopped and restarted inside one MiniDFSCluster, while the mutable `Configuration` controls bind address selection. No NameNode metadata persistence is involved.

Dependencies and integration points: Exercises MiniDFSCluster's DataNode startup API, configuration key handling, DataNode socket binding/reporting, and restart lifecycle.

Risks: Assertions inspect string forms of socket addresses, which can vary with Java/network stack formatting. The test does not use try/finally around the final cluster shutdown, so an earlier assertion failure could leave cleanup to the test harness.

Test signals: Success means MiniDFSCluster defaults to loopback when DataNode address keys are absent and honors explicit wildcard bind addresses when configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSAddressConfig.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSClientExcludedNodes.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSClientExcludedNodes.java

Purpose: Ensures DFSClient excludes failed DataNodes during writes without aborting unnecessarily, and later forgives excluded nodes after the configured expiry interval.

Important APIs, types, and functions: `MiniDFSCluster.stopDataNode/restartDataNode`, `FSDataOutputStream`, `FileSystem.create`, `HdfsClientConfigKeys.Write.EXCLUDE_NODES_CACHE_EXPIRY_INTERVAL_KEY`, `hflush`, `ThreadUtil.sleepAtLeastIgnoreInterrupts`, and `DataNodeProperties`.

Control flow: `testExcludedNodes` starts three DataNodes, stops a random one, creates a replicated file, writes a byte, and asserts close succeeds despite the single DataNode failure. `testExcludedNodesForgiveness` sets exclude cache expiry to 2.5 seconds, writes one block to all three DataNodes, stops two DataNodes to force exclusion, writes another block with one remaining node, restarts the two stopped nodes, waits longer than expiry, stops the last originally good node, and then writes/flushes/closes another block, expecting the forgiven nodes to be usable.

State and persistence behavior: The key state is the DFS client excluded-node cache across multiple block writes on the same output stream. DataNode lifecycle state changes in the cluster simulate failures and recoveries. No NameNode restart persistence is tested.

Dependencies and integration points: Integrates DFS client write pipeline selection, DataNode failure handling, exclude-cache expiry, block-size/checksum configuration, and MiniDFSCluster lifecycle controls.

Risks: The forgiveness test depends on wall-clock sleeps and DataNode restart timing. If expiry semantics or pipeline replacement policy changes, the test can become flaky. The first test uses a random DataNode index, though all three nodes are symmetric.

Test signals: Success means a single failed DataNode does not abort a write, and previously excluded but restarted DataNodes can re-enter the pipeline after cache expiry so later writes still succeed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSClientExcludedNodes.java -->
