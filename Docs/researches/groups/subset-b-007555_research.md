# Research Report: subset-b-007555

This grouped report covers the requested HDFS NameNode quota, erasure-coding reconstruction, re-encryption, checkpoint, secondary NameNode, security, edit-log token, and snapshot path tests. Each file section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestQuotaByStorageType.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestQuotaByStorageType.java

Purpose: Exercises HDFS directory quota accounting by heterogeneous storage type, especially SSD/DISK accounting under storage policies. It validates create, append, delete, rename, truncate, snapshot retention, traditional disk-space quota interaction, content summary reporting, and persistence of per-storage-type quota through edit logs and fsimage checkpoints.

Important APIs and functions: `setUp()` builds a 3 DataNode `MiniDFSCluster` with SSD and default storage per node and caches `FSDirectory`, `DistributedFileSystem`, and `FSNamesystem`. Test helpers call `dfs.setStoragePolicy`, `dfs.setQuotaByStorageType`, `dfs.setQuota`, `DFSTestUtil.createFile`, `DFSTestUtil.appendFile`, `dfs.truncate`, `dfs.saveNamespace`, and `cluster.restartNameNode`. Assertions read `INodeDirectory.getDirectoryWithQuotaFeature().getSpaceConsumed()`, `QuotaCounts`, `computeQuotaUsage`, and `ContentSummary.getTypeConsumed`.

Control flow: Each test creates a directory under `/TestQuotaByStorageType`, applies a storage policy such as `ONESSD`, `ALLSSD`, `HOT`, or `WARM`, sets quota limits, then mutates files and checks live NameNode quota counters. Exception tests deliberately exceed SSD or traditional storage-space limits and verify counters remain at the last valid usage. Persistence tests write quotas and files, restart from edits or save an fsimage in safemode, then refresh NameNode handles and re-read quota limits and consumed type-space.

State and persistence behavior: The tested state lives in `DirectoryWithQuotaFeature` quota and consumption counters attached to INodes, storage-policy-derived block placement, fsimage serialization, and edit-log replay. Snapshot tests ensure deleted file blocks remain counted until the snapshot is removed. Clearing one storage-type quota must reset only that storage type while leaving other type quotas intact.

Dependencies and integration points: Integrates `FSDirectory`, `FSNamesystem`, `BlockStoragePolicySuite`, `ContentSummary`, HDFS client quota RPCs, `SnapshotTestHelper`, and block placement/storage policy accounting. It is a NameNode integration suite rather than an isolated unit test.

Risks: Storage-type accounting can diverge from traditional storage-space accounting when replication, policy fallback, rename rollback, or partial create failure paths are wrong. Assertions that catch broad `Throwable` can hide the exact exception type in some cases. Tests depend on MiniDFSCluster block placement honoring the intended SSD/DISK split.

Test signals: Useful regression signals include exact SSD/DISK consumed bytes after create/append/delete/truncate, expected `QuotaByStorageTypeExceededException` or `DSQuotaExceededException`, content summary type consumption, quota persistence after restart/checkpoint, snapshot retention/reclamation, and per-type quota clear semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestQuotaByStorageType.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestQuotaCounts.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestQuotaCounts.java

Purpose: Unit-tests the `QuotaCounts` value container used by NameNode quota logic for namespace, storage-space, and per-`StorageType` counters. It focuses on arithmetic and the special constant counter instances used for reset/default values.

Important APIs and functions: Tests construct counters with `new QuotaCounts.Builder()`, `nameSpace`, `storageSpace`, and `typeSpaces`, then exercise `addNameSpace`, `addStorageSpace`, `add`, `addTypeSpace`, `subtract`, `setTypeSpaces`, `setNameSpace`, `setStorageSpace`, and `negation`. Assertions inspect `getNameSpace`, `getStorageSpace`, `getTypeSpace`, and internal references `nsSsCounts` and `tsCounts`.

Control flow: The suite creates fresh counters, mutates them with positive and negative deltas, copies type counters from another instance, resets counters to constants, and verifies every `StorageType` value. The reset test validates that builder/setter paths reuse `QuotaCounts.QUOTA_RESET` and `QuotaCounts.STORAGE_TYPE_RESET`/`STORAGE_TYPE_DEFAULT` rather than allocating mutable counters for constant states.

State and persistence behavior: No persistent filesystem state exists. The tested state is in-memory `QuotaCounts` internals, including reference identity for immutable constant counters and mutable enum counter values after arithmetic.

Dependencies and integration points: Depends on `StorageType` enumeration and `HdfsConstants.QUOTA_RESET`. These counters are consumed by inode quota features, content summary, quota checks, and fsimage/edit-log serialization elsewhere.

Risks: Incorrect constant reuse can introduce accidental mutation of shared reset/default counters. Arithmetic sign errors affect quota rollback, snapshot accounting, and over-quota decisions. The tests do not cover overflow boundaries.

Test signals: Passing signals are exact namespace/storage-space values, exact per-storage-type values after add/subtract/negation, and `assertSame` identity checks for constant counter fast paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestQuotaCounts.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestQuotaWithStripedBlocks.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestQuotaWithStripedBlocks.java

Purpose: Verifies quota usage correction for erasure-coded striped block groups. It confirms that quota is initially charged at full block-group block size while a striped block is under construction, then adjusted to actual cell-size-based usage on completion.

Important APIs and functions: `setUp()` configures block size, enables the selected EC policy, creates `/ec`, applies the EC policy, sets namespace/storage-space quota and DISK quota, and sets HOT storage policy. `testUpdatingQuotaCount()` uses `dfs.create`, `DFSTestUtil.addBlockToFile`, `getDirectoryWithQuotaFeature`, and NameNode `complete`.

Control flow: The test opens a file, manually adds a striped block with one cell in each internal block, reads quota consumption before completion, completes the file through the NameNode RPC, then reads quota consumption again. Expected usage changes from `blockSize * groupSize` to `cellSize * groupSize`.

State and persistence behavior: State is transient in the MiniDFSCluster NameNode: an under-construction `INodeFile`, `BlockInfoStriped` quota accounting, and `DirectoryWithQuotaFeature` consumed storage-space and DISK type-space counters. No restart persistence is tested here.

Dependencies and integration points: Integrates EC policy metadata, `FSDirectory`, `DistributedFileSystem`, `DFSTestUtil.addBlockToFile`, quota accounting, and block completion logic. The superclass hook `getEcPolicy()` enables alternate policies in subclasses.

Risks: EC quota accounting can overcharge after completion or undercharge during construction if block-group size and real data length are confused. Manual block injection bypasses normal client write paths, so it targets NameNode accounting directly.

Test signals: The critical signal is the exact quota transition from full block group allocation to actual cell usage for both storage-space and DISK type-space counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestQuotaWithStripedBlocks.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestQuotaWithStripedBlocksWithRandomECPolicy.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestQuotaWithStripedBlocksWithRandomECPolicy.java

Purpose: Reuses `TestQuotaWithStripedBlocks` with a random non-default erasure-coding policy to broaden coverage beyond the default EC layout. It checks that the quota behavior is policy-parameterized rather than hard-coded.

Important APIs and functions: The constructor selects `StripedFileTestUtil.getRandomNonDefaultECPolicy()` and logs the policy name. The only override is `getEcPolicy()`, which returns that selected policy to the inherited setup and test body.

Control flow: JUnit runs the inherited `setUp`, `testUpdatingQuotaCount`, and `tearDown` methods from `TestQuotaWithStripedBlocks`. The subclass changes only the EC policy's data/parity unit counts and cell size.

State and persistence behavior: State is the inherited MiniDFSCluster, EC directory, quota feature, and striped file state. No additional persistent state exists beyond the randomly chosen policy instance held in the test object.

Dependencies and integration points: Depends on `StripedFileTestUtil` and the superclass extension hook. It integrates with all superclass HDFS quota and EC code paths.

Risks: Random policy choice can expose policy-specific arithmetic bugs but may make failures less immediately reproducible unless logs capture the selected policy. The constructor comment points developers to `SystemErasureCodingPolicies` for fixed-policy debugging.

Test signals: Passing inherited quota assertions under a non-default policy demonstrate that quota correction uses policy metadata rather than default constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestQuotaWithStripedBlocksWithRandomECPolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestReconstructStripedBlocks.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestReconstructStripedBlocks.java

Purpose: Integration-tests NameNode scheduling and accounting for erasure-coded striped block reconstruction. It covers missing internal blocks, busy source nodes, duplicate recovery suppression for the same block group, live replica counting with redundant/missing internal blocks, pending reconstruction metrics, storage-type/rack constraints, and excess/redundant block avoidance.

Important APIs and functions: Helpers include `initConf`, `doTestMissingStripedBlock`, `getNumberOfBlocksToBeErasureCoded`, and `writeStripedFile`. Tests use `MiniDFSCluster`, `DFSTestUtil.createStripedFile`, `BlockManagerTestUtil.getComputedDatanodeWork`, `BlockManager.countNodes`, `DatanodeDescriptor.getErasureCodeCommand`, `StripedBlockUtil.parseStripedBlockGroup`, and `StripedFileTestUtil.waitForReconstructionFinished`.

Control flow: Tests create EC files, remove DataNodes or mark them busy by filling pending replication streams, update BlockManager state, compute work, then inspect per-DataNode EC reconstruction commands and BlockManager counters. Later tests stop/restart DNs to produce redundant internal blocks, restart the NameNode to force block-report reconstruction of missing indices, and verify all block indices are eventually present.

State and persistence behavior: State lives in `BlockInfoStriped`, `DatanodeDescriptor` pending EC command queues, low-redundancy EC block group queues, pending reconstruction tracking, and block maps rebuilt after block reports or NameNode restart. The storage-type test uses persistent file storage policy `COLD` plus DataNode storage topology.

Dependencies and integration points: Integrates EC policies, BlockManager redundancy monitor logic, DataNodeManager removal/death handling, client located-block APIs, rack/storage-type placement, and client stats verification.

Risks: Reconstruction scheduling is sensitive to busy-node filtering, priority when only data-unit minimum sources remain, duplicate pending work, and internal block index coverage. Timing-based waits and heartbeat/redundancy intervals can be flaky if cluster scheduling stalls.

Test signals: Signals include exact number of EC tasks queued, pending reconstruction counts, source/target DN counts, `liveReplicas`, `excessReplicas`, `redundantInternalBlocks`, low-redundancy EC group counts, successful full index coverage, and successful reconstruction under insufficient preferred storage type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestReconstructStripedBlocks.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestRedudantBlocks.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestRedudantBlocks.java

Purpose: Regression-tests processing of over-replicated and redundant internal blocks in an erasure-coded striped block group. The class name contains the same misspelling as the source file, but the behavior under test is redundant block cleanup plus reconstruction.

Important APIs and functions: `setup()` configures block size, short redundancy/heartbeat intervals, `SimulatedFSDataset`, a MiniDFSCluster, and an EC directory. `testProcessOverReplicatedAndRedudantBlock()` uses `DFSTestUtil.createStripedFile`, `cluster.injectBlocks`, `triggerBlockReports`, `triggerHeartbeats`, `BlockManager.countNodes`, and `StripedBlockUtil.parseStripedBlockGroup`.

Control flow: The test creates a full striped file, injects all but one internal block into the first DataNodes, reports them, then injects a duplicate internal block as a redundant copy. It triggers block reports and heartbeats so the NameNode deletes redundancy, then triggers reconstruction for the missing internal block and waits until live replicas reach full group size.

State and persistence behavior: State is transient BlockManager block-map membership for `BlockInfoStriped`, live replica counts, redundant internal block tracking, and DataNode simulated block reports. No fsimage/edit-log restart path is exercised.

Dependencies and integration points: Integrates EC located-block parsing, simulated DataNode storage, block reports, heartbeats, BlockManager redundancy cleanup, and reconstruction scheduling.

Risks: Redundant internal blocks can mask a missing index if counting tracks only live replica count rather than unique block indices. The test's waits depend on block reports/heartbeats being processed promptly.

Test signals: The final signal is that parsed internal block IDs form a set of exactly `groupSize` unique IDs after redundant deletion and reconstruction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestRedudantBlocks.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestRedundantEditLogInputStream.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestRedundantEditLogInputStream.java

Purpose: Unit-tests failover behavior in `RedundantEditLogInputStream.nextOp()` when the first edit stream fails during `skipUntil`. It verifies both logging and successful operation retrieval from the next stream.

Important APIs and functions: The test mocks two `EditLogInputStream` instances with Mockito, configures names and txid ranges, makes the first `skipUntil(1)` throw, makes the second skip succeed and `readOp()` return a `MkdirOp`, and captures `RedundantEditLogInputStream.LOG`.

Control flow: A `RedundantEditLogInputStream` is constructed with the mocked stream list and starting txid 1. `nextOp()` attempts the first stream, logs the skip failure and failover, switches to the second stream, reads an operation, and returns it.

State and persistence behavior: No real edit files are persisted. The state under test is the redundant stream's current active stream selection and txid positioning over mocked streams.

Dependencies and integration points: Depends on `FSEditLogOp.MkdirOp`, `EditLogInputStream`, Mockito, and `GenericTestUtils.LogCapturer`. This is a low-level test for NameNode edit-log recovery from multiple storage directories.

Risks: If failover logging changes text, this test may fail despite behavior being correct. Raw `ArrayList` use is unchecked but harmless. It only covers failure during skip, not read failures after partial reads.

Test signals: Passing requires the expected log messages mentioning `FAKE_STREAM0` failover to `FAKE_STREAM1` and identity equality of the returned edit operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestRedundantEditLogInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestReencryption.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestReencryption.java

Purpose: Large integration suite for HDFS encryption-zone re-encryption. It validates admin command semantics, key-version changes, status reporting, queue ordering, restart recovery from edits/fsimage, checkpoint resume, deletion/create/rename races, snapshots, cancellation, safe mode, missing key provider behavior, KMS/updater fault handling, and retriable recovery.

Important APIs and functions: Setup configures a JKS key provider, delegation-token usage, short listing/batch limits, `MiniDFSCluster`, `HdfsAdmin`, wrappers, and `DFSTestUtil.createKey`. Tests call `dfsAdmin.createEncryptionZone`, `reencryptEncryptionZone(START|CANCEL)`, `listReencryptionStatus`, `rollKey`, `getFileEncryptionInfo`, `pauseReencryptForTesting`, `pauseForTestingAfterNthSubmission`, `pauseForTestingAfterNthCheckpoint`, and helper waits over `ReencryptionStatus` and `ZoneReencryptionStatus`.

Control flow: Tests build encryption-zone trees, roll the EZ key, submit re-encryption, and compare file encryption key version names before and after processing. Restart tests pause after queued command or checkpoint, restart the NameNode with re-encryption paused, verify queued zone/checkpoint file recovery, then resume and validate completion. Race tests pause handler/updater work, mutate files or directories, then verify deleted files are skipped, newly created files are not unnecessarily re-encrypted, and renames under re-encryption are rejected.

State and persistence behavior: The suite exercises persistent reencryption status in edit logs and fsimage, per-zone submission/completion metadata, last checkpoint file, canceled flag, failure counters, and encrypted data encryption key versions on INodes. It also checks status visibility without a live provider and completion behavior around safemode.

Dependencies and integration points: Integrates `EncryptionZoneManager`, `ReencryptionHandler`, `ReencryptionUpdater`, `ZoneSubmissionTracker`, `ReencryptionStatus`, `HdfsAdmin`, key providers, snapshots, safemode, FS wrappers, fault injection through `EncryptionFaultInjector`, and Whitebox access to internals.

Risks: The suite is timing-heavy and depends on pauses, sleeps, futures, and background handler/updater ordering. Fault-injection tests distinguish permanent IO failures from `RetriableException`; regressions can leave queues stuck, futures un-canceled, or status counters inconsistent. Snapshot and rename restrictions protect against re-encrypting stale or moved INodes incorrectly.

Test signals: Strong signals include key-version equality/inequality, exact files-reencrypted counts, queued/completed zone counts, queue ordering by inode id, last checkpoint file restoration, canceled/completion time flags, failure counts for KMS/updater faults, rejection messages for invalid commands, and successful re-encryption after cancellation or restart.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestReencryption.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestReencryptionHandler.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestReencryptionHandler.java

Purpose: Unit-tests `ReencryptionHandler` throttling behavior independent of a real NameNode. It verifies configured handler lock-time ratio, invalid throttle configuration rejection, and backpressure when too many reencryption tasks accumulate.

Important APIs and functions: `mockReencryptionhandler()` builds a real `ReencryptionHandler` around mocked `EncryptionZoneManager`, `FSDirectory`, and `FSNamesystem`, with a JKS-backed `KeyProviderCryptoExtension`. Tests use Mockito `StopWatch` mocks and Whitebox to set `throttleTimerAll`, `throttleTimerLocked`, `taskQueue`, and `submissions`.

Control flow: `testThrottle` simulates 30s total elapsed and 20s locked time with ratio 0.5, expecting sleep long enough to reduce locked-time share. `testThrottleNoOp` simulates lower locked time and expects no sleep. `testThrottleConfigs` validates non-positive ratios throw. `testThrottleAccumulatingTasks` fills a `ZoneSubmissionTracker` above processor-count threshold, clears it from another thread after 3s, and verifies throttle waits.

State and persistence behavior: No HDFS persistent state exists. Mutable state is internal handler throttling timers, a blocking task queue, and the submissions map tracking futures per zone.

Dependencies and integration points: Depends on KMS utility provider creation, `JavaKeyStoreProvider`, `KeyProviderCryptoExtension`, `ReencryptionUpdater.ZoneSubmissionTracker`, `SubjectInheritingThread`, Mockito, Whitebox, and the config key `DFS_NAMENODE_REENCRYPT_THROTTLE_LIMIT_HANDLER_RATIO_KEY`.

Risks: Wall-clock sleep assertions are inherently flaky on overloaded systems. Whitebox mutation ties the tests to private field names. The throttle ratio math must avoid negative/zero configuration and avoid deadlock when task futures pile up.

Test signals: Passing signals are measured sleep windows, sub-second no-op throttle, expected `IllegalArgumentException` content for invalid config, and waiting until accumulated tasks are cleared.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestReencryptionHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestReencryptionWithKMS.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestReencryptionWithKMS.java

Purpose: Runs the inherited `TestReencryption` suite against a real `MiniKMS` provider instead of the default local JKS provider, and adds a KMS ACL regression test. It is tagged slow.

Important APIs and functions: Overrides `getKeyProviderURI()` to return a `kms://` URI based on `miniKMS.getKMSUrl()`. `setup()` creates a unique KMS config directory, starts `MiniKMS`, then calls `super.setup()`. `setProvider()` is intentionally empty because the client provider should be the KMS provider. `rollKey()` rolls through `dfsAdmin.getKeyProvider()` without JKS flush.

Control flow: The inherited tests create encryption zones, roll keys, submit/cancel re-encryption, and inspect status through KMS. The local `testReencryptionKMSACLs()` edits `kms-acls.xml` to blacklist get/get_keys ACLs, reloads `KMSWebApp` ACLs, then runs `testReencryptionBasic()` to verify re-encryption does not require those reads.

State and persistence behavior: Persistent state includes the temporary MiniKMS keystore/config directory, KMS ACL XML, NameNode re-encryption status, and KMS key versions. Teardown stops both HDFS and KMS.

Dependencies and integration points: Integrates `MiniKMS`, `KMSClientProvider`, `KMSACLs`, `KMSConfiguration`, `KMSWebApp`, and the full HDFS re-encryption machinery inherited from `TestReencryption`.

Risks: This suite is slower and more environment-sensitive than JKS tests because it depends on an embedded KMS web service and ACL reload behavior. ACL changes must avoid over-constraining operations actually needed by re-encryption.

Test signals: Passing inherited re-encryption behavior through MiniKMS and passing basic re-encryption while GET and GET_KEYS ACLs are blacklisted show correct provider integration and minimal KMS permissions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestReencryptionWithKMS.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestRefreshBlockPlacementPolicy.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestRefreshBlockPlacementPolicy.java

Purpose: Verifies that NameNode block placement policy implementations can be dynamically refreshed from custom configured classes back to defaults for both replicated and erasure-coded placement.

Important APIs and functions: `MockBlockPlacementPolicy` extends `BlockPlacementPolicyDefault` and increments a static `counter` in `chooseTarget`. `setup()` configures both `DFS_BLOCK_REPLICATOR_CLASSNAME_KEY` and `DFS_BLOCK_PLACEMENT_EC_CLASSNAME_KEY` to this mock, then starts a 9-DN cluster. Tests call `NameNode.reconfigurePropertyImpl` with `null` to reset.

Control flow: `verifyRefreshPolicy()` creates a file and confirms the mock counter increases, invokes the supplied refresh function, deletes and recreates the file, then verifies the counter does not change, proving the default policy is active. `testRefreshEcPolicy` first creates an EC directory and enables default EC placement on it.

State and persistence behavior: Runtime state is the active BlockManager placement policy instance and the static invocation counter. The reconfiguration is in-memory for the running NameNode and is not persisted by this test.

Dependencies and integration points: Integrates dynamic reconfiguration, `BlockPlacementPolicyDefault`, replicated and EC placement config keys, `DistributedFileSystem.create`, and NameNode block target selection.

Risks: Static `counter` is shared across tests and relies on relative increments. Use of Java `assert` for the first counter check depends on assertions being enabled; the final `assertEquals` is the stronger JUnit signal.

Test signals: The counter increases before refresh and remains unchanged after refresh for both replicated and EC file creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestRefreshBlockPlacementPolicy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestRefreshNamenodeReplicationConfig.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestRefreshNamenodeReplicationConfig.java

Purpose: Tests dynamic NameNode reconfiguration of replication and reconstruction scheduling parameters without restart, including validation of invalid values.

Important APIs and functions: Setup seeds `DFS_NAMENODE_REPLICATION_MAX_STREAMS_KEY`, `DFS_NAMENODE_REPLICATION_STREAMS_HARD_LIMIT_KEY`, `DFS_NAMENODE_REPLICATION_WORK_MULTIPLIER_PER_ITERATION`, and `DFS_NAMENODE_RECONSTRUCTION_PENDING_TIMEOUT_SEC_KEY`, then reads the active `BlockManager`. Tests call `NameNode.reconfigurePropertyImpl` and inspect `BlockManager` getters.

Control flow: `testParamsCanBeReconfigured()` asserts initial configured values, updates each key to a new positive integer string, and checks BlockManager values update immediately. `testReconfigureFailsWithInvalidValues()` loops over all keys with negative, zero, and nonnumeric values, expecting `ReconfigurationException` with appropriate causes and no state changes.

State and persistence behavior: State is runtime `BlockManager` configuration fields. The tests do not persist or restart after reconfiguration.

Dependencies and integration points: Integrates NameNode reconfiguration plumbing, `BlockManager`, DFS config keys, `LambdaTestUtils.intercept`, and validation logic for positive non-zero integers.

Risks: Error-message assertions are exact and may be brittle if wording changes. The test ensures invalid attempts do not partially mutate any setting, which is important for live clusters.

Test signals: Passing requires immediate getter updates for valid values, `IllegalArgumentException` causes for negative/zero values, `NumberFormatException` for strings, and unchanged defaults after each invalid batch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestRefreshNamenodeReplicationConfig.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestSaveNamespace.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestSaveNamespace.java

Purpose: Comprehensive saveNamespace/checkpoint fault-injection suite for the NameNode. It validates recovery from partial fsimage writes, bad storage directories, VERSION write failures, failed checkpoints, edit-log rolling during save, txid persistence, cancellation cleanup, lease serialization edge cases, snapshot-section filtering, saveNamespace skip thresholds, and seen_txid repair.

Important APIs and functions: Fault helpers `FaultySaveImage`, `FaultyWriteProperties`, and `saveNamespaceWithInjectedFault` use Mockito spies on `FSImage` and `NNStorage`. Tests use `FSNamesystem.loadFromDisk`, `DFSTestUtil.formatNameNode`, `fsn.saveNamespace`, `fsn.rollEditLog`, `NameNodeRpcServer.saveNamespace`, `Canceler`, `GenericTestUtils.DelayAnswer`, `MD5FileUtils`, and local helper `doAnEdit`/`checkEditExists`.

Control flow: Most tests format a two-directory NameNode, inject a failure at a precise save step, enter safemode, run saveNamespace, optionally expect failure, then leave safemode, perform further edits, close, reload from disk, and verify edits survived. Other tests simulate permission-denied storage reinsertion, concurrent cancellation during image save, open/dangling leases, bogus snapshot diffs, checkpoint suppression by recent time/tx gap, and corrupt `seen_txid` in one directory.

State and persistence behavior: The suite directly exercises fsimage files, `.ckpt` temporary images, VERSION files, storage directory removal/reinsertion, edit-log segments, transaction IDs, lease paths, snapshot diff serialization, checkpoint transaction IDs, and `seen_txid` consistency across name dirs.

Dependencies and integration points: Integrates `FSImage`, `NNStorage`, `FSNamesystem`, `FSEditLog`, local filesystem storage, NameNode metrics/init, safemode, leases, snapshots, block ID generation, cancellation, and Mockito/Whitebox fault injection.

Risks: Checkpoint recovery must never leave only corrupt images or orphan temporary files. Cancellation must remove partial fsimage artifacts. Fault tests rely on private implementation call order and storage-directory counts, so refactors to save sequencing or storage iteration may require test updates.

Test signals: Signals include reloadable namespace after failures, removed storage directory count returning to zero, expected save failures when all dirs fail, exact last-written txid progression, only original image/MD5 files after cancellation, successful save with renamed/dangling leases, removal of bogus snapshot feature after restart, checkpoint txid skip/update behavior, and repaired identical `seen_txid` files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestSaveNamespace.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestSecondaryNameNodeUpgrade.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestSecondaryNameNodeUpgrade.java

Purpose: Regression-tests SecondaryNameNode checkpoint directory upgrade behavior when old or inconsistent VERSION files exist. It covers HDFS-3597-style startup with old layout versions and pre-federation metadata.

Important APIs and functions: `cleanupCluster()` removes the MiniDFSCluster base directory before each test. `doIt()` starts a MiniDFSCluster, starts `SecondaryNameNode`, creates directories, runs `doCheckpoint`, collects VERSION files from 2NN storage, shuts down 2NN, corrupts selected VERSION properties using `FSImageTestUtil.corruptVersionFile`, restarts 2NN, and checkpoints again.

Control flow: Success tests corrupt layout version alone or pre-federation fields (`layoutVersion`, empty `clusterID`, empty `blockpoolID`), then expect 2NN restart and checkpoint to recover by downloading a new checkpoint from the NameNode. The failure test changes `namespaceID` and expects an inconsistent checkpoint fields exception.

State and persistence behavior: Persistent state is the SecondaryNameNode checkpoint storage directories and their VERSION metadata. The test verifies which metadata mismatches are upgrade-compatible and which are fatal.

Dependencies and integration points: Integrates `SecondaryNameNode`, `MiniDFSCluster`, NameNode checkpoint image transfer, local VERSION-file corruption utilities, and `ImmutableMap` test inputs.

Risks: Cleanup deletes the cluster base directory, so it assumes isolated test storage. VERSION metadata compatibility is delicate; accepting namespaceID changes would risk checkpointing against the wrong namespace.

Test signals: Passing signals are successful second checkpoint for layout/pre-federation upgrades and `IOException` containing `Inconsistent checkpoint fields` for namespaceID mismatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestSecondaryNameNodeUpgrade.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestSecondaryWebUi.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestSecondaryWebUi.java

Purpose: Tests that SecondaryNameNode JMX/web UI information exposes checkpoint directory settings consistent with the running `SecondaryNameNode` instance.

Important APIs and functions: `setUpCluster()` configures the secondary HTTP address on an ephemeral port, sets checkpoint transaction interval, starts a zero-DN MiniDFSCluster, and creates a `SecondaryNameNode`. `testSecondaryWebUi()` reads attributes from the platform `MBeanServer` object name `Hadoop:service=SecondaryNameNode,name=SecondaryNameNodeInfo`.

Control flow: The single test fetches `CheckpointDirectories` and `CheckpointEditlogDirectories` JMX attributes and compares them with `snn.getCheckpointDirectories()` and `snn.getCheckpointEditlogDirectories()`.

State and persistence behavior: Runtime state is the registered SecondaryNameNode MXBean and checkpoint directory arrays. No checkpoint or restart persistence is tested.

Dependencies and integration points: Integrates JMX, SecondaryNameNode lifecycle, MiniDFSCluster, and DFS checkpoint configuration.

Risks: JMX object naming and attribute types are part of the operational monitoring contract; changes can break dashboards or web UI. Static cluster lifecycle means setup failure affects the whole class.

Test signals: Passing requires exact array equality for both checkpoint image directories and checkpoint edit-log directories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestSecondaryWebUi.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestSecureNameNode.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestSecureNameNode.java

Purpose: Tests NameNode behavior under Kerberos-secured HDFS configurations generated by `SaslDataTransferTestCase`. It covers authenticated filesystem access, required block token consistency, and NameNodeStatus MXBean security reporting.

Important APIs and functions: Tests call `createSecureConfig`, `MiniDFSCluster.Builder`, `UserGroupInformation.loginUserFromKeytabAndReturnUGI`, privileged `doAs` filesystem access, `DFS_BLOCK_ACCESS_TOKEN_ENABLE_KEY`, and JMX attribute `SecurityEnabled` on `Hadoop:service=NameNode,name=NameNodeStatus`.

Control flow: `testName` starts a secure zero-DN cluster, logs in the HDFS superuser to create `/tmp`, logs in a normal user, and expects an IOException around unauthorized root write while still validating Kerberos method in the protected sequence. `testKerberosHdfsBlockTokenInconsistencyNNStartup` disables block tokens with security enabled and expects NameNode startup to abort. `testNameNodeStatusMXBeanSecurityEnabled` compares MXBean and `NameNode.isSecurityEnabled()` in simple and secure clusters.

State and persistence behavior: State is runtime security configuration, UGI login state, permissions on `/tmp`, and JMX NameNode status. No fsimage persistence is tested.

Dependencies and integration points: Integrates Kerberos test keytabs/principals, Hadoop security config, HDFS permissions, MiniDFSCluster startup validation, and JMX.

Risks: Security tests are sensitive to UGI global configuration and keytab setup. The broad `assertThrows` block in `testName` can obscure which operation failed. Block-token enforcement is a startup safety invariant for secure clusters.

Test signals: Signals include expected IOException for unauthorized access, Kerberos authentication method, startup failure message when block tokens are disabled under security, and correct JMX `SecurityEnabled` values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestSecureNameNode.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestSecureNameNodeWithExternalKdc.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestSecureNameNodeWithExternalKdc.java

Purpose: Optional integration test for running a secure NameNode against an externally supplied KDC, principals, and keytabs. It verifies non-superuser Kerberos access semantics in an environment closer to deployment than the in-process test KDC.

Important APIs and functions: `testExternalKdcRunning()` uses `assumeTrue(isExternalKdcRunning())` to skip when not configured. `testSecureNameNode()` reads system properties for NameNode Kerberos/SPNEGO principals, keytab, user principal, and user keytab; configures `HADOOP_SECURITY_AUTHENTICATION`, NameNode principal keys, and keytab path; then uses UGI keytab login.

Control flow: The test starts a secure zero-DN cluster, uses the current/superuser filesystem to create writable `/tmp`, logs in the specified non-superuser, verifies writing `/users` fails, then creates and lists `/tmp/alpha` and checks Kerberos authentication.

State and persistence behavior: Runtime state includes external Kerberos credentials, NameNode security configuration, filesystem permissions, and UGI authentication method. No persistent NameNode restart is involved.

Dependencies and integration points: Integrates external KDC availability, system properties, HDFS security config, MiniDFSCluster, permissions, and UGI.

Risks: The test is intentionally environment-dependent and skipped unless the external KDC flag/helper says it is available. Misconfigured principals or accidentally superuser credentials invalidate the scenario.

Test signals: Passing requires all required system properties, successful secure cluster startup, denied root-level user write, successful write in `/tmp`, and `AuthenticationMethod.KERBEROS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestSecureNameNodeWithExternalKdc.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestSecurityTokenEditLog.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestSecurityTokenEditLog.java

Purpose: Tests edit-log recording and replay for delegation token operations under concurrency and token expiration. It validates that get, renew, and cancel token operations are durable and that implicit expiration cancellation logs while holding the correct NameNode lock.

Important APIs and functions: Static setup disables fsync for speed. `Transactions` repeatedly calls `FSNamesystem.getDelegationToken`, `renewDelegationToken`, `cancelDelegationToken`, and `editLog.logSync`. `testEditLog()` starts a MiniDFSCluster with delegation tokens always enabled, launches 100 `SubjectInheritingThread`s, closes the edit log, and reloads edits with `FSEditLogLoader`. `testEditsForCancelOnTokenExpire()` uses mocked `FSImage`/`FSEditLog` and a real `FSNamesystem`.

Control flow: The concurrency test writes `NUM_THREADS * NUM_TRANSACTIONS * 3` token transactions plus key and segment transactions, then verifies each finalized edits file loads exactly the expected count. The expiration test creates two tokens, renews one halfway, forces secret-manager scans by stop/start, and verifies implicit cancels are logged only after each token expires.

State and persistence behavior: Persistent state is the NameNode edit log containing delegation token operations and secret-manager master keys. The expiration test checks lock state during logging: read lock held, write lock not held.

Dependencies and integration points: Integrates `DelegationTokenSecretManager`, `DelegationTokenIdentifier`, `FSEditLog`, `FSEditLogLoader`, storage directories, UGI, and FSNamesystem locking through `RwLockMode`.

Risks: High concurrency can expose edit-log corruption or transaction count mismatches. Timing around token expiration uses sleeps and forced scanner restarts. Locking assertions protect against unsafe edit-log rolling interactions.

Test signals: Signals include successful edit-log replay with expected transaction count for every edits directory, exact Mockito verification of get/renew/cancel calls, and read-lock/no-write-lock assertion during expiration cancel logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestSecurityTokenEditLog.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestSnapshotPathINodes.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestSnapshotPathINodes.java

Purpose: Tests `INodesInPath` resolution for normal paths, snapshot paths, deleted snapshot files, newly added files after snapshots, modified files after snapshots, and short-circuit behavior when no snapshottable directories exist.

Important APIs and functions: Class setup starts a 3-DN MiniDFSCluster and caches `FSDirectory`/`DistributedFileSystem`; reset recreates `file1` and `file2`. Helpers include `getSnapshot`, `assertSnapshot`, `assertINodeFile`, and `getNumNonNull`. Tests use `INode.getPathComponents`, `INodesInPath.resolve`, `hdfs.allowSnapshot`, `createSnapshot`, `deleteSnapshot`, `disallowSnapshot`, and `FSDirSnapshotOp.checkSnapshot`.

Control flow: Normal path tests verify component/inode lengths and path strings. Snapshot tests resolve paths containing `/.snapshot/<name>/...`, verify `.snapshot` component handling, snapshot root index, null inode for bare `.snapshot`, and invalid path failures. Deletion/addition/modification tests compare snapshot and current inode resolution after mutating files post-snapshot.

State and persistence behavior: State is in-memory namespace inode tree with snapshot features, snapshot roots, file diffs, deleted inode references, modification timestamps, and latest/path snapshot IDs. No restart serialization is exercised.

Dependencies and integration points: Integrates `SnapshotManager`, `Snapshot`, `INodeDirectory`, `INodeFile`, `INodesInPath`, HDFS snapshot APIs, `DFSTestUtil`, and Mockito for verifying no interactions in the no-snapshot short-circuit case.

Risks: Snapshot path resolution is subtle because `.snapshot` is a virtual component that may not correspond to a real inode, and negative indexes are used to inspect trailing components. Incorrect latest/path snapshot ID handling can break permission checks, mutation routing, or content lookup.

Test signals: Signals include exact inode array lengths, correct snapshot flags and IDs, `Snapshot.Root` at the expected index, null last inode for bare `.snapshot` or missing snapshot file, preserved modification time for snapshot file, changed current file modification time, expected `FileNotFoundException`s, and zero interactions when there are no snapshottable directories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestSnapshotPathINodes.java -->
