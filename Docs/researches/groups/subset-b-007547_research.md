# Research: subset-b-007547

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/FSXAttrBaseTest.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/FSXAttrBaseTest.java

Purpose: JUnit 5 base suite for HDFS NameNode extended attribute APIs. It exercises create, replace, set, get, list, remove, rename, raw namespace behavior, ACL-driven access, and the `security.hdfs.unreadable.by.superuser` special xattr across edit-log replay and fsimage checkpoint reload.

Important APIs/types/functions: static cluster fixtures use `MiniDFSCluster`, `HdfsConfiguration`, `DistributedFileSystem`, `Path`, `XAttrSetFlag`, `UserGroupInformation`, and `FsPermission`. Test helpers include `createFileSystem()`, `createFileSystem(UserGroupInformation)`, `initCluster(boolean)`, `restart(boolean)`, `verifySecurityXAttrExists()`, and `verifyFileAccess()`. The suite also uses `NameNodeAdapter.enterSafeMode()` and `saveNamespace()` to force fsimage persistence.

Control flow: `@BeforeAll` enables xattrs and ACLs, sets small per-inode and per-xattr limits, and starts one DataNode. `@BeforeEach` allocates unique normal and `/.reserved/raw` paths. Mutation tests set xattrs, validate maps/lists and error cases, restart without checkpoint for edit-log replay, then restart with checkpoint for fsimage coverage. Permission tests run operations as synthetic users and expect either `AccessControlException`, `RemoteException`, or successful access depending on path mode and ACLs.

State and persistence: persistent state is HDFS inode xattr metadata stored in edit logs and fsimage. Tests deliberately verify cleanup after xattr removal, rename retention, null-value normalization to empty byte arrays, raw namespace visibility only through raw paths, and the special security xattr's non-removable/no-value semantics.

Dependencies and integration points: integrates NameNode xattr enforcement, ACL permission checks, raw reserved paths, WebHDFS-compatible exception behavior, edit-log replay, checkpointing, and `DFSTestUtil` file creation.

Risks and test signals: important risks are namespace filtering mistakes, permission bypasses, max-count/size regressions, raw xattr leakage, and loss of xattrs after restart. Test signals are successful restart/checkpoint assertions, exact xattr map contents, expected exception text, and access behavior for superuser vs non-superuser.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/FSXAttrBaseTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/FileNameGenerator.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/FileNameGenerator.java

Purpose: small package-private helper that generates a balanced tree of test file or directory names for NameNode throughput benchmarks, limiting entries per directory.

Important APIs/types/functions: constructors accept `baseDir` and optional `filesPerDir`; `getNextFileName(String)` is synchronized and returns the next leaf path; `getNextDirName(String)` advances the path index vector; `getFileCount()`, `getFilesPerDirectory()`, and `getCurrentDir()` expose generator state.

Control flow: `reset()` fills a fixed 20-level index array with `-1`. Each new file increments `fileCount`; when `fileCount % filesPerDirectory == 0`, a new current directory is built by incrementing the first non-full level or extending depth. Names are formed by concatenating `baseDir`, directory prefixes, and the monotonically increasing file number.

State and persistence: all state is in memory: `pathIndecies`, `currentDir`, `filesPerDirectory`, and `fileCount`. There is no filesystem mutation; callers create the generated paths.

Dependencies and integration points: used by `NNThroughputBenchmark` create/open/delete/rename/mkdir/block-report setup to avoid huge flat directories that would distort benchmark behavior.

Risks and test signals: the fixed 20-level array bounds total generated paths and can throw `ArrayIndexOutOfBoundsException` for extreme workloads; benchmark callers catch that to suggest a different per-directory value. Synchronization protects concurrent calls, but `getFileCount()` is unsynchronized. Signals are deterministic path ordering and bounded directory fanout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/FileNameGenerator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/MockNameNodeResourceChecker.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/MockNameNodeResourceChecker.java

Purpose: test double for `NameNodeResourceChecker` that lets tests force NameNode resource availability or exhaustion without depending on real disk state.

Important APIs/types/functions: constructor delegates to the real checker with `Configuration`; `hasAvailableDiskSpace()` returns a volatile flag; `setResourcesAvailable(boolean)` mutates the flag.

Control flow: consumers call the checker through the normal NameNode resource-monitor path. Tests flip the flag to simulate low-resource safe mode or recovery, and subsequent calls observe the new value immediately because the flag is volatile.

State and persistence: state is only the in-memory `hasResourcesAvailable` flag. It does not inspect or persist disk usage.

Dependencies and integration points: extends the production `NameNodeResourceChecker`, so it can be injected wherever the NameNode expects the real resource checker.

Risks and test signals: it bypasses real volume checks and only models a single aggregate condition. Test signal is NameNode behavior changing when `setResourcesAvailable(false/true)` is called.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/MockNameNodeResourceChecker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/NNThroughputBenchmark.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/NNThroughputBenchmark.java

Purpose: command-line benchmark harness that measures NameNode throughput for namespace and block-management operations by calling NameNode protocols directly, with either an embedded NameNode or a remote HDFS URI.

Important APIs/types/functions: top-level implements `Tool`. `OperationStatsBase` owns common argument parsing, thread scheduling, timing, cleanup, safe-mode/save behavior, and stats aggregation. `StatsDaemon` runs per-thread operations. Concrete operations are `CleanAllStats`, `CreateFileStats`, `MkdirsStats`, `OpenFileStats`, `DeleteFileStats`, `AppendFileStats`, `FileStatusStats`, `RenameFileStats`, `BlockReportStats`, and `ReplicationStats`. `TinyDatanode` simulates DataNode registration, heartbeats, block reports, and block-received reports.

Control flow: `run()` parses `-op`, builds one or more operation objects, starts an embedded NameNode when no HDFS URI is configured, initializes protocol handles and block-pool ID, then benchmarks and cleans each operation before printing stats. Each operation pre-generates inputs, launches `StatsDaemon` threads, busy-waits until they finish, and aggregates local counts/timing. Namespace operations create generated paths and call `ClientProtocol`; block-report and replication benchmarks register simulated DataNodes, create files/blocks, submit reports, decommission nodes, and force block-manager work computation.

State and persistence: benchmark state includes generated test paths under `/nnThroughputBenchmark`, static protocol handles, include/exclude host files under `hadoop.tmp.dir`, simulated DataNode block lists, and NameNode namespace/edit-log state. `-keepResults` preserves benchmark namespace and may save a checkpoint; default cleanup deletes the base dir.

Dependencies and integration points: depends on NameNode client, datanode, namenode, and refresh-user-mapping protocols, `DFSTestUtil`, `FileNameGenerator`, `BlockManagerTestUtil`, `DatanodeProtocolClientSideTranslatorPB`, and Hadoop `ToolRunner`/generic options.

Risks and test signals: risks include static global protocol state, busy-waiting, direct protocol calls that bypass client behavior, remote replication benchmark limitations, and simulated DataNodes that only model selected DataNode behavior. Test signals are benchmark logs showing inputs, operations executed, elapsed time, average latency, ops/sec, block distribution, decommissioned blocks, and pending replications.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/NNThroughputBenchmark.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/NameNodeAdapter.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/NameNodeAdapter.java

Purpose: test-only facade exposing otherwise internal NameNode and FSNamesystem functions to HDFS unit tests.

Important APIs/types/functions: exposes namesystem, RPC server, FSImage-in-HTTP-server swapping, delegation-token manager, heartbeat sending, replication changes, lease manager/lease fields, service state, datanode descriptors, stats, generation stamps, block allocation without journaling, block persistence, stored-block lookup, mkdir edit-log op helpers, safe-mode counters, edits file path lookup, and checkpoint start.

Control flow: methods are thin wrappers around production internals. Some acquire explicit `FSNamesystem` read/write locks with `RwLockMode` before accessing directory or block-manager state. `getFileInfo()` mirrors `FSNamesystem#getFileInfo()` permission-checker setup and lock discipline. `addBlockNoJournal()` creates and saves a block under global write lock, while `persistBlocks()` journals block state under FS write lock.

State and persistence: most methods inspect or mutate live NameNode state. `saveNamespace()`, `abortEditLogs()`, `persistBlocks()`, `addBlockNoJournal()`, and checkpoint helpers affect persistent namespace/edit-log state; other methods expose transient locks, leases, safe-mode counters, and block-manager maps.

Dependencies and integration points: integrates tests with `FSNamesystem`, `FSDirectory`, `FSDirWriteFileOp`, `BlockManagerTestUtil`, `LeaseManager`, `NameNodeHttpServer`, `NNStorage`, and HA/checkpoint protocols.

Risks and test signals: because it bypasses normal API boundaries, callers must preserve lock and journaling expectations. Risks are stale internal coupling, no-journal block additions, and whitebox field access for safe-mode state. Signals are unit tests that need deterministic access to leases, blocks, safemode, edit logs, and HTTP FSImage state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/NameNodeAdapter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/NameNodeAdapterMockitoUtil.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/NameNodeAdapterMockitoUtil.java

Purpose: Mockito-based companion utility for replacing selected NameNode internals with spies during tests.

Important APIs/types/functions: `spyOnBlockManager()`, `spyOnFsLock()`, `spyOnFsImage()`, `spyOnJournalSet()`, `spyOnNamesystem()`, `spyOnEditLog()`, and `spyDelayMkDirTransaction()` create spies and install them into the relevant production objects.

Control flow: each method spies the current internal object, then uses public testing setters, `DFSTestUtil`, `Whitebox`, or Apache Commons `FieldUtils` to update back-references. `spyOnNamesystem()` locks old and new namesystems while replacing `NameNode.namesystem` and related references in RPC server, block manager, lease manager, datanode manager, and heartbeat manager. `spyDelayMkDirTransaction()` intercepts `FSEditLogAsync.doEditTransaction()` only for `OP_MKDIR` and sleeps before delegating.

State and persistence: state changes are in-memory test substitutions. Edit-log and journal spies still wrap real persistent components, so intercepted calls can delay or observe real persistence without replacing behavior unless a test stubs it further.

Dependencies and integration points: depends on Mockito, `FieldUtils`, `Whitebox`, `DFSTestUtil`, `BlockManagerTestUtil`, and HA `EditLogTailer`.

Risks and test signals: risks are fragile private-field names and incomplete back-reference replacement causing mixed real/spy state. Test signals are successful verification/stubbing of NameNode internal calls, lock behavior, edit-log delays, and block-manager interactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/NameNodeAdapterMockitoUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/OfflineEditsViewerHelper.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/OfflineEditsViewerHelper.java

Purpose: helper for offline edits viewer tests that generates an edits file containing broad NameNode operation coverage.

Important APIs/types/functions: `generateEdits()` runs operations and returns the finalized edits path; `startCluster(String)` configures and starts a one-name-dir MiniDFSCluster; `shutdownCluster()` tears it down; private `runOperations()` and `getEditsFilename(CheckpointSignature)` produce and locate the rolled edits segment.

Control flow: `startCluster()` configures name/checkpoint dirs, block size, auth-to-local mapping, delegation token usage, ACLs, and nine DataNodes. `runOperations()` obtains the `DistributedFileSystem`, delegates broad operation generation to `DFSTestUtil.runOperations()`, manually logs rolling-upgrade start/finalize opcodes, then rolls the edit log. `getEditsFilename()` uses the returned checkpoint signature to compute the finalized edits file ending at `curSegmentTxId - 1`.

State and persistence: creates real MiniDFSCluster namespace state and finalized edit logs on local disk under the provided directory. It intentionally limits edits storage to one directory for deterministic lookup.

Dependencies and integration points: integrates MiniDFSCluster, `DFSTestUtil`, `FSImage`, `NNStorage`, storage-directory iteration, delegation-token opcodes, ACL opcodes, and rolling-upgrade edit-log APIs.

Risks and test signals: risks include opcode coverage drifting with `DFSTestUtil.runOperations()` and assumptions about one edits directory. Test signal is an existing finalized edits file that offline viewer tests can parse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/OfflineEditsViewerHelper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/PatternMatchingAppender.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/PatternMatchingAppender.java

Purpose: simple Log4j test appender that records whether a log message matching a fixed metric pattern was seen.

Important APIs/types/functions: extends `AppenderSkeleton`; constructor compiles `^.*FakeMetric.*$`; `append(LoggingEvent)` checks event messages; `isMatched()` returns a volatile boolean; `close()` and `requiresLayout()` satisfy appender contract.

Control flow: when attached to a logger, each `LoggingEvent` message is converted to string and matched. The first match flips `matched` to true and it remains true for the appender lifetime.

State and persistence: in-memory only: compiled `Pattern` and volatile `matched`. No log storage or layout handling.

Dependencies and integration points: integrates with legacy Log4j appenders in NameNode tests that need to assert metric log emission.

Risks and test signals: null messages would throw through `toString()`, and the pattern is hard-coded to `FakeMetric`. Signal is `isMatched()` becoming true after expected logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/PatternMatchingAppender.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestAclConfigFlag.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestAclConfigFlag.java

Purpose: verifies that disabling `dfs.namenode.acls.enabled` rejects ACL API operations while still allowing NameNode startup from edits/fsimage containing ACL metadata.

Important APIs/types/functions: uses `MiniDFSCluster`, `DistributedFileSystem`, `DFSConfigKeys.DFS_NAMENODE_ACLS_ENABLED_KEY`, `AclTestHelpers.aclEntry()`, and `NameNodeAdapter` checkpoint helpers. `expectException(Executable)` asserts `AclException` and configuration-key text.

Control flow: individual tests start a cluster with ACLs disabled, create `/path`, and assert `modifyAclEntries`, `removeAclEntries`, `removeAcl`, `setAcl`, and `getAclStatus` fail. Persistence tests first enable ACLs, set an ACL, then restart with ACLs disabled either from edit logs or after saving a checkpoint.

State and persistence: writes ACL metadata to the namespace when enabled, then tests replay/load with ACL support disabled. No final persistent state is needed after teardown.

Dependencies and integration points: covers DFS client ACL APIs, NameNode ACL config gates, edit-log loading, fsimage loading, and safe-mode namespace saving.

Risks and test signals: risks are accidentally allowing ACL mutation/read APIs when disabled or rejecting existing namespace metadata during upgrade/restart. Signals are exact `AclException` failures and successful restarts with stored ACLs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestAclConfigFlag.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestAclTransformation.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestAclTransformation.java

Purpose: pure unit tests for `AclTransformation` algorithms, cross-validated against Linux ACL behavior, covering removal/filter, default filtering, merge, and replace semantics.

Important APIs/types/functions: statically imports `AclTransformation.filterAclEntriesByAclSpec()`, `filterDefaultAclEntries()`, `mergeAclEntries()`, and `replaceAclEntries()`. Test data uses `AclEntry`, scopes `ACCESS`/`DEFAULT`, entry types `USER`/`GROUP`/`MASK`/`OTHER`, and `AclTestHelpers.aclEntry()`.

Control flow: each test builds immutable existing ACL lists, mutable ACL specs, expected lists, and compares transformation output or asserts `AclException`. The suite enumerates unchanged paths, entry removal, named user/group ordering, access and default mask recalculation/preservation, automatic default base entries, empty specs, input/result size limits, duplicate entries, named mask/other rejection, and missing required base entries for replace.

State and persistence: no filesystem or NameNode state is used. State is local Java ACL lists only.

Dependencies and integration points: directly validates the transformation layer consumed by NameNode ACL mutation operations before metadata is persisted to inodes.

Risks and test signals: risks are subtle POSIX ACL compatibility regressions: wrong ordering, mask calculation, default ACL completion, duplicate detection, or maximum-entry enforcement. Signals are exact list equality and expected `AclException` on invalid ACL specs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestAclTransformation.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestAddBlock.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestAddBlock.java

Purpose: tests that AddBlock edit-log operations are written and replayed correctly for complete files and an under-construction append.

Important APIs/types/functions: uses `MiniDFSCluster`, `DFSTestUtil.createFile()`, `DistributedFileSystem`, `FSDataOutputStream`, `DFSOutputStream.hsync(UPDATE_LENGTH)`, `FSDirectory`, `INodeFile`, `BlockInfo`, and `BlockUCState`.

Control flow: setup starts a three-DataNode cluster with 1 KiB block size. `testAddBlock()` creates files with lengths around one and two block boundaries, restarts the NameNode, then inspects inode block arrays for count, length, and `COMPLETE` state. `testAddBlockUC()` appends without closing, hsyncs length, restarts, and verifies the original block is complete while the new block is `UNDER_CONSTRUCTION`.

State and persistence: block metadata is persisted through edit logs and replayed on NameNode restart. The under-construction block retains UC state after restart.

Dependencies and integration points: covers client create/append, edit-log add-block replay, inode block metadata, and lease/under-construction behavior.

Risks and test signals: risks include off-by-one block lengths, losing UC state, or replaying wrong block counts. Signals are direct assertions on `INodeFile.getBlocks()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestAddBlock.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestAddBlockRetry.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestAddBlockRetry.java

Purpose: regression coverage for addBlock retry races and retry-after-restart behavior.

Important APIs/types/functions: uses NameNode RPC `create`, `addBlock`, and `getBlockLocations`; internal `FSDirWriteFileOp.validateAddBlock()`, `chooseTargetForNewBlock()`, and `storeAllocatedBlock()`; `FSNamesystem` locks; Mockito `FSPermissionChecker`; and helper `checkFileProgress()`.

Control flow: `testRetryAddBlockWhileInChooseTarget()` manually runs the first addBlock through validation and target selection, pauses before storing, runs a second full RPC addBlock, then resumes the first store and asserts both return the same block and one located block with expected replication. `testAddBlockRetryShouldReturnBlockWithLocations()` allocates a block, restarts the NameNode, retries addBlock, and checks the same block is returned with locations reselected.

State and persistence: tests live block allocation, blocks map state, and edit-log replay across restart. Locations are intentionally not persisted, so retry must reconstruct them.

Dependencies and integration points: covers `FSDirWriteFileOp`, `FSNamesystem` locking/progress checks, block placement targets, NameNode RPC semantics, and `LocatedBlocks`.

Risks and test signals: risks are duplicate block allocation, missing locations after retry, and races between validation and storage. Signals are block identity equality, single located block, replication count, and file-progress success.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestAddBlockRetry.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestAddOverReplicatedStripedBlocks.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestAddOverReplicatedStripedBlocks.java

Purpose: tests NameNode handling of over-replicated erasure-coded striped block groups, including partial groups, corrupt internal blocks, and a disabled missing-block scenario.

Important APIs/types/functions: uses default `ErasureCodingPolicy`, `MiniDFSCluster`, `SimulatedFSDataset`, `DFSTestUtil.createStripedFile()`, `LocatedStripedBlock`, `BlockInfoStriped`, `BlockManager.findAndMarkBlockAsCorrupt()`, `cluster.injectBlocks()`, block reports, and heartbeats.

Control flow: setup enables EC on `/striped`, configures simulated storage, short heartbeat/redundancy intervals, and disables replication streams. Tests create striped files, inject duplicate internal blocks into extra DataNodes, trigger block reports/heartbeats so the NameNode schedules invalidations, and verify located striped blocks contain the expected number of live internal blocks. Corrupt-block coverage marks one internal block corrupt and verifies redundant copies are not deleted before reconstruction.

State and persistence: state is in the NameNode block map, corrupt replica map, over-replication invalidation queues, and DataNode simulated block reports. No restart persistence is exercised.

Dependencies and integration points: covers EC block-group accounting, block reports, heartbeat invalidations, corrupt replica tracking, and `StripedFileTestUtil.verifyLocatedStripedBlocks()`.

Risks and test signals: risks are deleting needed redundant EC blocks when a block is corrupt/missing, or retaining excess replicas for complete groups. Signals are located block indices/locations counts and corrupt replica counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestAddOverReplicatedStripedBlocks.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestAddStripedBlockInFBR.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestAddStripedBlockInFBR.java

Purpose: verifies that full block reports can establish NameNode block-to-DataNode mappings for striped blocks when an incremental block report is ignored.

Important APIs/types/functions: uses `MiniDFSCluster`, default EC policy, Mockito spy on `BlockManager`, `Whitebox.setInternalState()`, `processIncrementalBlockReport()`, `cluster.triggerBlockReports()`, `BlockInfoStriped`, and `NumberReplicas`.

Control flow: setup starts `groupSize` DataNodes and enables EC. The test spies the block manager and suppresses one DataNode's incremental block report processing, creates replicated files plus one EC file, then repeatedly triggers full block reports until the striped block has zero excess replicas and `groupSize` live replicas.

State and persistence: state is the live in-memory block map updated by full block reports. No edit-log or fsimage persistence is exercised.

Dependencies and integration points: covers DataNode FBR handling, EC block-group replica accounting, Mockito/Whitebox internals, and `GenericTestUtils.waitFor()`.

Risks and test signals: risks are relying only on IBRs for striped mappings or marking FBR-added striped replicas as excess. Signal is `NumberReplicas.liveReplicas() == groupSize` and `excessReplicas() == 0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestAddStripedBlockInFBR.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestAddStripedBlocks.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestAddStripedBlocks.java

Purpose: broad tests for adding and reporting erasure-coded striped blocks, including scheduled-block accounting, block ID spacing, edit-log/fsimage persistence, located block contents, under-construction replica updates, corrupt replica detection, and client block-location striped flags.

Important APIs/types/functions: uses `DFSStripedOutputStream`, `BlockInfoStriped`, `BlockInfoStripedUnderConstruction` data via `getUnderConstructionFeature()`, `DatanodeStorageInfo`, `StorageReceivedDeletedBlocks`, `StorageBlockReport`, `BlockListAsLongs`, `ReplicaBeingWritten`, `BlockManagerTestUtil`, and `BlockLocation.isStriped()`.

Control flow: setup starts `groupSize` DataNodes, enables default EC, and sets EC policy on root. Tests write/flush striped data, inspect scheduled counters before and after block reports, verify new block IDs advance by `MAX_BLOCKS_IN_GROUP`, restart and save namespace while checking UC striped metadata, compare `LocatedStripedBlock` expected DataNodes and indices, simulate IBR and FBR updates to UC replica storage IDs, inject correct/wrong-sized internal block reports, and compare replicated vs striped `BlockLocation` flags.

State and persistence: exercises live NameNode block-manager state, under-construction striped block expected locations, corrupt replica maps, edit-log replay, and fsimage checkpoint reload.

Dependencies and integration points: covers EC client writes, NameNode block allocation, DataNode reports, block corruption accounting, safemode saveNamespace, and public filesystem block-location APIs.

Risks and test signals: risks include ID collisions across block groups, stale scheduled counts, lost UC expected locations after restart, wrong block indices, and corrupt EC accounting errors. Signals are direct assertions on inode blocks, located block arrays, storage IDs, corrupt counters, and `isStriped()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestAddStripedBlocks.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestAllowFormat.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestAllowFormat.java

Purpose: tests NameNode format behavior controlled by `dfs.namenode.support.allow.format` and verifies non-file shared edits directories are ignored by local format handling.

Important APIs/types/functions: uses `NameNode.format()`, `MiniDFSCluster`, `DFS_NAMENODE_NAME_DIR_KEY`, `DFS_DATANODE_DATA_DIR_KEY`, `DFS_NAMENODE_CHECKPOINT_DIR_KEY`, `DFS_NAMENODE_SUPPORT_ALLOW_FORMAT_KEY`, HA setup through `HATestUtil`, and `DummyJournalManager`.

Control flow: `@BeforeAll` prepares multiple name directories, pre-creating one empty dir to guard against unwanted prompts, configures data/checkpoint dirs, and sets a default HDFS URI. `testAllowFormat()` formats through MiniDFSCluster startup, shuts down, asserts manual format fails when allow-format is false, then succeeds when true. `testFormatShouldBeIgnoredForNonFileBasedDirs()` configures HA shared edits with a `dummy://` URI and verifies `NameNode.format()` handles it without trying file-directory formatting.

State and persistence: creates and deletes local DFS base directories and NameNode storage metadata. The second test exercises configuration parsing more than persistent shared-edits state.

Dependencies and integration points: covers NameNode storage formatting, MiniDFSCluster directory-management flags, HA shared edits config, non-file journal plugins, and test directory cleanup.

Risks and test signals: risks are accidental formatting despite disabled config, hanging on prompts for empty dirs, or treating non-file shared edits as local paths. Signals are expected `IOException` text and successful format calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestAllowFormat.java -->
