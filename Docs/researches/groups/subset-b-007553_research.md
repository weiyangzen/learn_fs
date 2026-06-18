# subset-b-007553 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestLeaseManager.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestLeaseManager.java

## Purpose
JUnit 5 coverage for `LeaseManager` bookkeeping, lease expiration, inode-to-lease indexing, restart restoration, and ancestor-directory filtering for open under-construction files. It combines lightweight Mockito-backed `FSNamesystem` tests with one `MiniDFSCluster` persistence/restart scenario.

## Important APIs, Types, and Functions
- Exercises `LeaseManager.addLease`, `removeLease`, `removeAllLeases`, `reassignLease`, `countLease`, `countPath`, `checkLeases`, `getInternalLeaseHolder`, `getLease`, `getINodeIdWithLeases`, `getINodeWithLeases`, `getINodeWithLeases(INodeDirectory)`, and `getUnderConstructionFiles`.
- Uses `FSNamesystem.getFilesBlockingDecom`, `getMaxListOpenFilesResponses`, and lock-state predicates through mocks.
- Builds synthetic `INodeDirectory` and `INodeFile` objects with `PermissionStatus`, `FsPermission`, `BlockInfo.EMPTY_ARRAY`, `Snapshot.CURRENT_STATE_ID`, and `DFSUtil` path component helpers.
- Full-cluster restart path uses `MiniDFSCluster`, `DistributedFileSystem`, `FSDirectory`, `safeMode`, `saveNamespace`, and `restartNameNode(true)`.

## Control Flow
- `testRemoveLeases`, `testCountPath`, and `testCheckLease` validate direct lease map changes and expired lease cleanup.
- `testLeaseRestorationOnRestart` creates an open file, intentionally removes its `LeaseManager` entry while leaving the inode under-construction feature intact, saves namespace, restarts the NameNode, then verifies the lease is rebuilt from inode state.
- `testInodeWithLeases` and `testInodeWithLeasesAtScale` populate mocked inode IDs with under-construction files and verify list/count APIs across empty, small, boundary, and large scales.
- `testInodeWithLeasesForAncestorDir` builds a small in-memory directory tree, leases selected files, and verifies directory-scoped filtering before and after lease removal.
- Helper `verifyINodeLeaseCounts` cross-checks lease-manager counts against `getUnderConstructionFiles` and `FSNamesystem.getFilesBlockingDecom`.

## State and Persistence Behavior
- Direct tests target in-memory lease maps keyed by holder and inode ID.
- Restart test verifies persisted fsimage reconstruction: lease identity must survive when only the inode under-construction state is serialized.
- Ancestor filtering depends on parent pointers and inode map lookups in `FSDirectory`.
- Expiration behavior depends on artificial lease period settings and lock-hold limit `maxLockHoldToReleaseLeaseMs`.

## Dependencies and Integration Points
- Depends on NameNode internals: `FSNamesystem`, `FSDirectory`, `INodeFile`, `INodeDirectory`, `INodesInPath`, `LeaseManager`, `OpenFilesIterator`, and snapshot-aware child lookup.
- Uses Mockito for lock and inode lookup contracts and AssertJ/JUnit assertions for counts.
- Integrates with HDFS persistence through `MiniDFSCluster` and NameNode RPC save namespace.

## Risks and Edge Cases
- Mocked lock state can hide real locking regressions outside `LeaseManager` logic.
- Scale loop is tuned around `INODE_FILTER_WORKER_TASK_MIN` and `INODE_FILTER_WORKER_COUNT_MAX`; changes to parallel filtering thresholds can change runtime.
- Restart scenario depends on saved fsimage behavior and open stream lifetime; cleanup relies on cluster shutdown.
- Directory tree map keys are simple local names, so duplicate names in different branches would collide if added later.

## Test Signals
- Strong signal for lease bookkeeping invariants, inode resolution, expiration progress, and restart restoration.
- Covers no-lease, duplicate-add, nonexistent-remove, reassignment, ancestor scoping, and high-cardinality lease filtering.
- Timeout annotations guard hangs in lease expiration and large-scale filtering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestLeaseManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestListCorruptFileBlocks.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestListCorruptFileBlocks.java

## Purpose
Slow integration tests for the NameNode and DFS client corrupt-file-block listing APIs. The tests create files in a `MiniDFSCluster`, deliberately corrupt or remove block and metadata files on DataNode storage, trigger detection, and validate both server-side counts and client-side iteration/paging.

## Important APIs, Types, and Functions
- Uses `FSNamesystem.listCorruptFileBlocks`, `FSNamesystem.getCorruptFilesCount`, `DistributedFileSystem.listCorruptFileBlocks`, and `CorruptFileBlockIterator.getCallsMade`.
- Creates files via `DFSTestUtil.Builder`, `createFiles`, `waitReplication`, `checkFiles`, and `cleanup`.
- Manipulates storage through `MiniDFSCluster.getFinalizedDir`, `getAllBlockFiles`, `getAllBlockMetadataFiles`, `Block.metaToBlockFile`, `cluster.getInstanceStorageDir`, and raw `RandomAccessFile`/`FileChannel` writes.
- Forces detection using reads that produce `BlockMissingException`, DataNode directory scanner, block report intervals, DataNode restarts, and safe mode transitions.

## Control Flow
- `testListCorruptFilesCorruptedBlock` corrupts bytes near the end of one block file, reads files to trigger detection, and expects one corrupt file.
- `testListCorruptFileBlocksInSafeMode` repeats corruption with safemode/repl-queue settings, restarts the NameNode, waits for replication queues, and verifies corrupt listing still works while safemode remains active.
- `testlistCorruptFileBlocks` deletes all block and metadata files for three files, polls until three corrupt entries appear, then validates cookie-based paging.
- `testlistCorruptFileBlocksDFS` validates the public `DistributedFileSystem` iterator path for the same deletion scenario.
- `testMaxCorruptFiles` creates many one-block files, deletes all blocks, runs scanner/restarts DataNodes, verifies the NameNode response cap, and checks client iteration makes multiple RPC calls.
- `testListCorruptFileBlocksOnRelativePath` sets a working directory and verifies relative path resolution for the DFS client API.

## State and Persistence Behavior
- Corruption is represented by on-disk DataNode block files, block metadata files, and NameNode block state after block reports or read-triggered bad-block reports.
- Safe mode test validates corrupt-block state across NameNode restart while replication queues are repopulating.
- Cookie paging mutates the string-array cookie across server calls.
- Relative path test depends on `FileSystem` working-directory state.

## Dependencies and Integration Points
- Integrates NameNode block manager, DataNode directory scanner, block reports, DFS client iteration, `DFSTestUtil`, and physical storage layout.
- Uses `HdfsClientConfigKeys.Retry.WINDOW_BASE_KEY`, block report intervals, directory scan intervals, and safemode thresholds to reduce wait time and force desired states.
- Tagged `slow`, with long per-test timeouts due to polling and cluster restarts.

## Risks and Edge Cases
- Tests are timing-sensitive around scanner/block-report discovery and include polling loops up to 30 seconds or longer.
- Physical block deletion assumes mini-cluster storage directory layout and number of data directories.
- `testMaxCorruptFiles` relies on default max corrupt files returned and can be expensive because it creates `max * 3` files.
- Direct corruption can surface as expected `BlockMissingException`; other IOExceptions fail the test.

## Test Signals
- Strong end-to-end signal that corrupt file listing is bounded, pageable, path-aware, safe-mode-capable, and accurately reflected in NameNode metrics/counts.
- Covers server API, public DFS API, iterator paging, max-response caps, safemode restart, and relative path behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestListCorruptFileBlocks.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestListOpenFiles.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestListOpenFiles.java

## Purpose
Integration tests for NameNode open-file listing over RPC, DFSAdmin, HA failover, path filtering, invalid path validation, and robustness when leased files disappear from the inode map.

## Important APIs, Types, and Functions
- Exercises `NamenodeProtocols.listOpenFiles`, `OpenFilesIterator.OpenFilesType`, `OpenFileEntry`, `BatchedRemoteIterator.BatchedEntries`, and DFS client `listOpenFiles`.
- Uses `DFSTestUtil.createOpenFiles`, `closeOpenFiles`, and `createFile`.
- HA test uses `MiniDFSNNTopology.simpleHATopology`, `HATestUtil`, `HAUtil.getProxiesForAllNameNodesInNameservice`, `DFSAdmin -listOpenFiles`, and active/standby transitions.
- Direct deletion edge case uses `FSNamesystem.writeLock(RwLockMode.FS)`, `FSDirectory.removeFromInodeMap`, and `leaseManager.removeLease`.

## Control Flow
- `setUp` starts a 3-DataNode cluster with heartbeat interval 1 and list-open-files batch size 5.
- `testListOpenFilesViaNameNodeRPC` validates empty lists, adds open files across several batch sizes, repeatedly lists with last-entry IDs, closes files incrementally, and verifies no blocking-decommission entries.
- `verifyOpenFiles` loops over batched RPC responses until `hasMore` is false, removing expected paths from a set.
- `testListOpenFilesInHA` runs `DFSAdmin -listOpenFiles` repeatedly in a background `SubjectInheritingThread`, shuts down active NN0, transitions NN1 active, and verifies no client-side listing error.
- `testListOpenFilesWithFilterPath` validates prefix filtering for `/base` and `/base/` versus similarly named `/base-open`.
- Invalid path tests distinguish server-side absolute-path checks from client-side wrong-filesystem checks.
- Deleted-path test removes an inode from the inode map while a lease remains and asserts listing does not throw `NullPointerException`.

## State and Persistence Behavior
- Open-file state is live lease/under-construction state held by NameNode, not persisted across these tests.
- HA test depends on active NameNode state and failover configuration; open files are created before failover listing.
- Deleted-path test mutates in-memory inode map under write lock to simulate inconsistency between lease manager and directory state.

## Dependencies and Integration Points
- Integrates NameNode RPC, DFSAdmin CLI, DFS client, HA failover utilities, lease manager, FSDirectory, and FSNamesystem locks.
- Uses `DFS_NAMENODE_LIST_OPENFILES_NUM_RESPONSES` to force pagination.
- Uses `LambdaTestUtils.intercept` to assert exception type/message.

## Risks and Edge Cases
- HA background thread has timing windows around failover and command execution.
- Direct inode-map removal is intentionally invasive and must hold the correct lock to avoid race/NPE behavior.
- Filtering semantics depend on exact server path normalization.
- The test assumes no open files are blocking decommission unless explicitly created for that type.

## Test Signals
- Good signal for batched listing correctness, no duplicates/missing paths, HA command resilience, path validation, and stale lease/inode inconsistency safety.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestListOpenFiles.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestMalformedURLs.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestMalformedURLs.java

## Purpose
Regression test that malformed/untrimmed URL-like configuration values in `hdfs-site.malformed.xml` are read and trimmed correctly enough for `MiniDFSCluster` startup.

## Important APIs, Types, and Functions
- Adds default resource `hdfs-site.malformed.xml`.
- Compares `Configuration.get` and `Configuration.getTrimmed` for `DFS_NAMENODE_HTTP_ADDRESS_KEY`.
- Starts `MiniDFSCluster` from the loaded `Configuration`.

## Control Flow
- `setUp` registers the malformed config resource and creates a fresh `Configuration`.
- `testTryStartingCluster` verifies the raw and trimmed values differ, then builds and activates a cluster.
- `tearDown` shuts down the cluster if startup succeeded.

## State and Persistence Behavior
- No filesystem persistence is intentionally inspected; the key state is configuration parsing and cluster process state.

## Dependencies and Integration Points
- Relies on a test resource named `hdfs-site.malformed.xml` on the test classpath.
- Integrates configuration parsing with NameNode HTTP address binding during mini-cluster startup.

## Risks and Edge Cases
- Only validates one configured key and successful startup, not all malformed URL handling paths.
- Global `Configuration.addDefaultResource` can affect later tests in the same JVM if resource loading behavior changes.

## Test Signals
- Compact startup smoke test for trimming and tolerance of malformed-looking NameNode HTTP address configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestMalformedURLs.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestMetaSave.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestMetaSave.java

## Purpose
Integration tests for NameNode `metaSave` output generation, including live/dead DataNode summaries, under-replication/delete queues, overwrite semantics, and concurrent calls to the same output file.

## Important APIs, Types, and Functions
- Exercises `NamenodeProtocols.metaSave`, `setReplication`, and `delete`.
- Uses `MiniDFSCluster`, `FileSystem`, `DFSTestUtil.createFile`, `BlockManagerTestUtil.noticeDeadDatanode`, `isDatanodeRemoved`, and `waitForMarkedDeleteQueueIsEmpty`.
- Reads output files from `System.getProperty("hadoop.log.dir")`.
- `MetaSaveThread` extends `SubjectInheritingThread` and invokes `metaSave` concurrently.

## Control Flow
- `setUp` starts a two-DataNode cluster with long redundancy interval, short heartbeat/recheck interval, and stale DataNode interval.
- `testMetaSave` creates replicated files, stops one DataNode, increases replication for one file, runs `metaSave`, and validates exact header/live/dead lines plus a file-status line.
- `testMetasaveAfterDelete` creates files, stops a DataNode, sets replication, deletes files, waits for delete queue drain, and checks metasave output for zero reconstruction/missing counts and deletion/corrupt/datanode sections.
- `testMetaSaveOverwrite` calls `metaSave` twice on the same file and asserts only one `Live Datanodes` line exists.
- `testConcurrentMetaSave` starts 10 threads writing the same metasave file and applies the same non-append check.
- `stopDatanodeAndWait` stops a DataNode, notifies NameNode, and waits until it is removed.

## State and Persistence Behavior
- `metaSave` writes diagnostic files in the Hadoop log directory and should overwrite rather than append.
- Cluster state includes dead DataNode detection, replication changes, pending deletions, and block manager queues.
- Concurrent output exercises file write serialization/overwrite behavior.

## Dependencies and Integration Points
- Integrates NameNode RPC, block manager queue accounting, DataNode liveness, test log directory, and filesystem file creation/deletion.
- Uses ordered first test for `testMetaSave`, though each test rebuilds cluster in `BeforeEach`.

## Risks and Edge Cases
- Exact output line assertions are brittle to metasave formatting changes.
- Dead DataNode detection is timing-sensitive and depends on heartbeat/recheck settings.
- Concurrent metasave test swallows IOExceptions inside worker threads, so it primarily detects append corruption, not individual call failures.

## Test Signals
- Strong signal for metasave diagnostic shape, delete-queue accounting, overwrite behavior, and basic concurrency behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestMetaSave.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestMetadataVersionOutput.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestMetadataVersionOutput.java

## Purpose
Validates the `NameNode -metadataVersion` command output for an HA-style name directory configuration, ensuring it prints both stored image layout version and software format version.

## Important APIs, Types, and Functions
- Configures `DFS_NAMESERVICE_ID`, `DFS_HA_NAMENODES_KEY_PREFIX`, `DFS_HA_NAMENODE_ID_KEY`, and nameservice-scoped `DFS_NAMENODE_NAME_DIR_KEY`.
- Uses `MiniDFSCluster.Builder.manageNameDfsDirs(false)`, `checkExitOnShutdown(false)`, and `NameNode.createNameNode`.
- Captures `System.out` with `ByteArrayOutputStream`.
- Compares against `HdfsServerConstants.NAMENODE_LAYOUT_VERSION`.

## Control Flow
- `initConfig` prepares HA-specific NameNode directory keys and unsets the generic name dir.
- Test builds a small cluster, shuts it down without full cleanup, reinitializes config, redirects stdout, invokes `NameNode.createNameNode("-metadataVersion")`, catches expected `ExitUtil` exception, and asserts expected strings are present.
- `tearDown` shuts down any cluster and sleeps briefly.

## State and Persistence Behavior
- Depends on a formatted NameNode storage directory from the mini-cluster run.
- Reads existing metadata version without starting a normal NameNode service.
- Captures process-style exit behavior via `ExitUtil`.

## Dependencies and Integration Points
- Integrates NameNode command-line parsing/startup, HA name-dir resolution, storage metadata, and stdout output.

## Risks and Edge Cases
- Mutates global `System.out`; finally restores it.
- Sleep in teardown indicates sensitivity to shutdown/port cleanup timing.
- Only verifies output contains version substrings, not full command output or exit code object.

## Test Signals
- Focused regression signal for CLI metadata version reporting against HA-scoped storage configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestMetadataVersionOutput.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNNStorageRetentionFunctional.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNNStorageRetentionFunctional.java

## Purpose
Functional `MiniDFSCluster` coverage for `NNStorageRetentionManager` when multiple `NAME_AND_EDITS` directories exist and one directory fails image saving. It checks that image and edits failure states are decoupled for retention/purging.

## Important APIs, Types, and Functions
- Uses `NNStorage.getImageFileName`, `getFinalizedEditsFileName`, and `getInProgressEditsFileName`.
- Configures `DFS_NAMENODE_NUM_EXTRA_EDITS_RETAINED_KEY` and `DFS_NAMENODE_NAME_DIR_KEY`.
- Uses `NameNode.getRpcServer().setSafeMode` and `saveNamespace`.
- Verifies directory contents with `GenericTestUtils.assertGlobEquals`.
- Simulates storage failure through `FileUtil.chmod(current, "000")`.

## Control Flow
- Starts a zero-DataNode cluster with two manually managed name dirs.
- Calls `doSaveNamespace` repeatedly to produce images and finalized/in-progress edits at known transaction IDs.
- After two successful saves, chmods the first current dir unreadable/unwritable, saves namespace, restores permissions, and asserts failed dir retained old files while healthy dir purged and advanced.
- On the next save, asserts the failed dir can purge logs but not images because image storage remains failed.
- Finally restores permissions and shuts down.

## State and Persistence Behavior
- Directly validates on-disk `current` directory contents for `fsimage_*`, finalized `edits_*`, and `edits_inprogress_*`.
- Exercises NameNode storage failure bookkeeping across multiple saveNamespace calls.
- Retention behavior depends on transaction ID progression and extra edits retained set to zero.

## Dependencies and Integration Points
- Integrates real NameNode storage directories, safe mode save namespace RPCs, retention manager, filesystem permissions, and mini-cluster lifecycle.

## Risks and Edge Cases
- `chmod 000` may behave differently on platforms/filesystems that do not enforce POSIX permissions.
- Exact transaction IDs in assertions couple the test to edit-log progression during saveNamespace.
- The finally block attempts chmod even if directory setup failed.

## Test Signals
- High-value functional signal for retention after partial storage failure and for decoupled image-versus-edits failed states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNNStorageRetentionFunctional.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNNStorageRetentionManager.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNNStorageRetentionManager.java

## Purpose
Mock/unit test matrix for `NNStorageRetentionManager` purge decisions over fsimages, finalized edits, in-progress edits, stale logs, separate image/edit dirs, retention cushions, and limited extra retained segments.

## Important APIs, Types, and Functions
- Exercises `NNStorageRetentionManager.purgeOldStorage(NameNodeFile.IMAGE)`.
- Verifies `StoragePurger.purgeImage`, `purgeLog`, and `markStale` via Mockito `ArgumentCaptor`.
- Uses `FSImageStorageInspector.FSImageFile`, `FileJournalManager.EditLogFile`, `FileJournalManager`, `JournalSet`, and mocked `FSEditLog`.
- Synthetic files are named by `NNStorage.getImageFileName`, `getFinalizedEditsFileName`, and `getInProgressEditsFileName`.
- `TestCaseDescription` models roots, files, expected purged images, expected purged logs, and expected stale logs.

## Control Flow
- `setNoExtraEditRetention` defaults extra edits retention to zero for most tests.
- Individual tests populate a `TestCaseDescription` with roots of type `IMAGE`, `EDITS`, or `IMAGE_AND_EDITS`, then mark each file as expected purge/keep/stale.
- `runTest` builds mocked storage and edit log, runs retention, captures purger calls, converts file paths to URI paths, and compares ordered expected/captured paths.
- `mockEditLog` wires `purgeLogsOlderThan` to real `JournalManager.purgeLogsOlderThan` on synthetic `FileJournalManager` instances and `selectInputStreams` to `JournalSet`.

## State and Persistence Behavior
- No real files are required; storage directories and current-directory contents are mocked with path lists.
- Retention decisions are based on parsed transaction IDs and image checkpoints.
- `currentInProgress` is set from the highest in-progress edit file for each fake root.
- Extra retained edits and maximum extra segments change purge thresholds and stale marking.

## Dependencies and Integration Points
- Integrates retention manager with storage inspectors, file journal manager parsing, journal selection, and purger interface without a cluster.
- Uses Hadoop third-party Guava `Joiner`, `Maps`, `Lists` and Mockito.

## Risks and Edge Cases
- Assertions compare ordered joined path strings; ordering changes in purge calls can fail even if sets match.
- Synthetic path roots like `/foo1` are platform-normalized through `File.toURI`.
- Because files are mocked, it does not catch actual filesystem deletion or permission failures.

## Test Signals
- Broad signal for retention policy logic: easy purge, multiple dirs, under-retention, empty/no-log dirs, old in-progress logs, split image/edit dirs, extra edit cushion, limited extra segments, and JournalNode-style stale in-progress files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNNStorageRetentionManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNNThroughputBenchmark.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNNThroughputBenchmark.java

## Purpose
Smoke/integration coverage for `NNThroughputBenchmark` command execution against formatted local storage and remote `MiniDFSCluster` NameNodes, including operation selection, `-fs`, non-superuser mode, append/blockReport operations, base directory selection, and block-size parsing.

## Important APIs, Types, and Functions
- Calls `NNThroughputBenchmark.runBenchmark` with argument arrays for `-op all`, `create`, `append`, `blockReport`, `-fs`, `-nonSuperUser`, `-keepResults`, `-useExisting`, `-baseDirName`, and `-blockSize`.
- Uses `DFSTestUtil.formatNameNode`, `MiniDFSCluster`, `FileSystem.setDefaultUri`, `DistributedFileSystem`, and `FSNamesystem.getListing`.
- Uses `ExitUtil.disableSystemExit` in `BeforeAll` and deletes mini-cluster base directory contents after each test.

## Control Flow
- Local tests format a NameNode name dir and run all benchmark operations with and without explicit `file:///` fs.
- Remote tests start clusters with zero or three DataNodes and run all operations or specific operations against cluster URI/default URI.
- Append test first creates and closes three files while keeping results, captures listing modification times, runs append with `-useExisting`, and verifies modification times changed.
- Block report test starts three DataNodes and runs two block reports.
- Base-dir test verifies custom `/nnThroughputBenchmark1` is used and default `/nnThroughputBenchmark` is not created.
- Block-size tests cover config value `1m`, CLI `-blockSize 32`, and CLI `-blockSize 1m`.

## State and Persistence Behavior
- Local tests write formatted NameNode metadata under `MiniDFSCluster.getBaseDirectory()/name`.
- Remote benchmark operations create directories/files in the cluster; cleanup deletes base directory contents after tests.
- Append test validates metadata mutation through modification time changes.

## Dependencies and Integration Points
- Integrates benchmark CLI parser/executor with NameNode RPCs, file creation/append, block reports, default URI resolution, and block size config parsing.

## Risks and Edge Cases
- Primarily checks no exceptions plus a few side effects, not benchmark correctness/performance metrics.
- Benchmark "all" can be broad and sensitive to unrelated benchmark operation changes.
- Cleanup deletes contents of the shared mini-cluster base directory.

## Test Signals
- Good smoke signal that benchmark entry points remain runnable across local/remote modes and important CLI options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNNThroughputBenchmark.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNNUpdateStorageVersionWhenInterrupt.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNNUpdateStorageVersionWhenInterrupt.java

## Purpose
Regression test for `NNStorage.writeAll` when interrupted while writing VERSION files. It verifies an interrupt-induced `ClosedByInterruptException` is logged but the storage directory remains registered.

## Important APIs, Types, and Functions
- Constructs `NNStorage` from file URIs for name and edits dirs.
- Uses `StorageDirectory.getVersionFile`, Java NIO `Files.createDirectories/createFile`, and `GenericTestUtils.LogCapturer.captureLogs(NNStorage.LOG)`.
- `UpdateVersionFileThread` calls `nnStorage.writeAll()` and ignores IOExceptions.

## Control Flow
- `BeforeAll` creates one storage dir and an empty VERSION file, then starts capturing `NNStorage` logs.
- Test asserts there is one storage dir, starts the writer thread, interrupts it, waits until captured logs include `ClosedByInterruptException`, and asserts the storage dir count is still one.

## State and Persistence Behavior
- Operates on a real temporary NameNode storage directory under `GenericTestUtils.getTestDir("dfs")`.
- The important invariant is that an interrupted write does not drop the storage directory from `NNStorage`.

## Dependencies and Integration Points
- Integrates low-level storage writing, Java interrupt behavior, and logging.
- Does not start a NameNode or cluster.

## Risks and Edge Cases
- Timing-sensitive because interrupt must hit during write; wait loop depends on log output.
- The worker thread is not joined, though wait-for-log implies the write path observed interruption.
- Static storage/log capture can share state across repeated JVM runs.

## Test Signals
- Focused signal for storage robustness under thread interruption and for preserving directory membership after failed VERSION writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNNUpdateStorageVersionWhenInterrupt.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameCache.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameCache.java

## Purpose
Unit test for `NameCache` dictionary promotion, lookup reuse, lookup count accounting, initialization, and reset behavior.

## Important APIs, Types, and Functions
- Uses `NameCache<String>` with use threshold 2.
- Exercises `put`, `initialized`, `size`, `reset`, and `getLookupCount`.
- Helper `verifyNameReuse` checks whether a later `put` returns an interned cached value or `null`.

## Control Flow
- Adds "matching" names twice so they reach the threshold and are promoted.
- Adds "notMatching" names once so they remain below threshold.
- Calls `initialized`, verifies promoted names are reused and dictionary size matches, then verifies below-threshold names are not reused.
- Resets, reinitializes, and verifies none of the names are reused.

## State and Persistence Behavior
- Pure in-memory dictionary/cache state.
- `lookupCount` increments only when an initialized dictionary hit occurs.

## Dependencies and Integration Points
- Tests only `NameCache`; no NameNode or filesystem integration.

## Risks and Edge Cases
- Uses object identity (`s == cache.put(s)`) to assert reuse during threshold promotion.
- Does not test concurrency, non-string keys, or memory pressure behavior.

## Test Signals
- Clear unit signal for promotion threshold, initialized lookup semantics, cache size, and reset clearing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameCache.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameEditsConfigs.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameEditsConfigs.java

## Purpose
Integration tests for combinations of NameNode image directories, edits directories, checkpoint directories, required edits dirs, and failure scenarios. The suite validates that NameNode and SecondaryNameNode can migrate between shared and separate storage layouts without reading stale metadata.

## Important APIs, Types, and Functions
- Configures `DFS_NAMENODE_NAME_DIR_KEY`, `DFS_NAMENODE_EDITS_DIR_KEY`, `DFS_NAMENODE_CHECKPOINT_DIR_KEY`, `DFS_NAMENODE_CHECKPOINT_EDITS_DIR_KEY`, and `DFS_NAMENODE_EDITS_DIR_REQUIRED_KEY`.
- Uses `MiniDFSCluster.Builder.manageNameDfsDirs(false)`, `format(false)`, `SecondaryNameNode`, `doCheckpoint`, and `DFSTestUtil.createFile`.
- Inspects storage with `FSImageTestUtil.inspectStorageDirectory`, `assertParallelFilesAreIdentical`, `assertSameNewestImage`, `FSImageTransactionalStorageInspector`, and `FileJournalManager.matchEditLogs`.
- Helpers `checkFile`, `cleanupFile`, and `checkImageAndEditsFilesExistence` validate namespace content and storage files.

## Control Flow
- `testNameEditsConfigs` starts with a shared name+edits dir, checkpoints, adds separate name and edits dirs, checkpoints again, removes shared dirs, then reintroduces them after deleting stale current dirs and verifies only latest metadata is used.
- `testNameEditsRequiredConfigs` verifies a required edits dir not present in edits dirs fails, while required-and-present and optional edits dirs succeed.
- `testNameEditsConfigsFailure` simulates shared-to-split migration, then verifies startup fails when latest edits are missing but succeeds when latest edits can replay from an older shared image.
- `testCheckPointDirsAreTrimmed` supplies whitespace-padded checkpoint dir values and verifies directories are created after checkpoint.

## State and Persistence Behavior
- Heavily validates real on-disk NameNode and SecondaryNameNode storage under a test `dfs` directory.
- File existence across restarts proves fsimage/edit-log replay selected the correct directories.
- Checkpointing propagates images/edits to secondary storage dirs.
- Storage current dirs are deleted/recreated to prevent stale metadata reads.

## Dependencies and Integration Points
- Integrates NameNode startup/restart, storage directory role classification, edit-log replay, SecondaryNameNode checkpointing, file namespace operations, and storage inspection utilities.

## Risks and Edge Cases
- Multi-stage tests are long and stateful; failures can cascade if a prior cluster shutdown/cleanup fails.
- Exact expectations depend on storage file naming and checkpoint behavior.
- `fileSys.close`, `cluster.shutdown`, and `secondary.shutdown` are called in many finally blocks and assume successful initialization.

## Test Signals
- Strong signal for metadata directory migration, required edits validation, stale storage avoidance, checkpoint dir trimming, and replay correctness across name/edit dir layout changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameEditsConfigs.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameNodeAcl.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameNodeAcl.java

## Purpose
NameNode-specific ACL integration test class that inherits the full ACL API test suite from `FSAclBaseTest` and starts an HDFS cluster for NameNode interaction coverage.

## Important APIs, Types, and Functions
- Extends `FSAclBaseTest`.
- `BeforeAll init` assigns a new `Configuration` to inherited `conf` and calls inherited `startCluster()`.

## Control Flow
- This class defines no test methods directly; inherited tests execute against the cluster initialized here.
- The inherited suite covers ACL modification APIs and interaction between `setPermission` and inodes with ACLs.

## State and Persistence Behavior
- Cluster and filesystem state are managed by `FSAclBaseTest`.
- ACL changes are expected to be applied to NameNode inode metadata through the normal filesystem API.

## Dependencies and Integration Points
- Integrates inherited ACL tests with NameNode-backed HDFS rather than another filesystem implementation.
- Depends on inherited lifecycle and cleanup behavior.

## Risks and Edge Cases
- Local file is small, so most behavior is implicit in the base class; changes to `FSAclBaseTest` alter this class's coverage.
- Static inherited configuration/cluster setup can affect test isolation if base class state changes.

## Test Signals
- Delegated but important signal that NameNode supports the standard ACL API contract and permission interactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameNodeAcl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameNodeConfiguration.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameNodeConfiguration.java

## Purpose
Unit guard that `NameNode.NAMENODE_SPECIFIC_KEYS` contains no duplicate configuration keys.

## Important APIs, Types, and Functions
- Iterates `NameNode.NAMENODE_SPECIFIC_KEYS`.
- Uses a `HashSet<String>` and JUnit `assertTrue(keySet.add(key), message)`.

## Control Flow
- Single test inserts each key into a set and fails immediately with the duplicate key name if an insertion returns false.

## State and Persistence Behavior
- Pure in-memory validation; no cluster or persistent state.

## Dependencies and Integration Points
- Protects NameNode-specific configuration override logic from duplicate key declarations.

## Risks and Edge Cases
- Does not validate key correctness, scope, or missing keys; only uniqueness.

## Test Signals
- Simple, fast signal for accidental duplicate entries in a static NameNode config-key list.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameNodeConfiguration.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameNodeHttpServer.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameNodeHttpServer.java

## Purpose
Parameterized tests for `NameNodeHttpServer` honoring HTTP policy modes: HTTP only, HTTPS only, and both HTTP/HTTPS.

## Important APIs, Types, and Functions
- JUnit parameterized class with method source `policy()` returning `HttpConfig.Policy` values.
- Uses `KeyStoreTestUtil.setupSSLConfig`, `URLConnectionFactory.newDefaultURLConnectionFactory`, and DFS SSL resource keys.
- Starts `NameNodeHttpServer(conf, null, addr)` and verifies `getHttpAddress`, `getHttpsAddress`, and reachability through `URLConnection`.

## Control Flow
- `BeforeAll` creates a temp base dir, SSL keystore/conf files, connection factory, and DFS client/server keystore resource settings.
- For each policy, `testHttpPolicy` sets `DFS_HTTP_POLICY_KEY`, binds HTTPS address to `localhost:0`, starts a server, and checks enabled schemes are reachable while disabled schemes have null addresses.
- `tearDown` deletes temp dirs and SSL config.

## State and Persistence Behavior
- Persists temporary SSL config/keystore files under the test base directory and classpath SSL config dir.
- HTTP server bind addresses are ephemeral ports.

## Dependencies and Integration Points
- Integrates NameNode HTTP server construction, Hadoop HTTP policy config, SSL setup, URL connection factory, and NetUtils host:port formatting.

## Risks and Edge Cases
- `canAccess` catches all exceptions and returns false, so failures require policy assertions to identify reachability issues.
- Network bind/reachability can be environment-sensitive.
- Static shared `Configuration` is mutated per parameterized instance.

## Test Signals
- Good signal that configured HTTP/HTTPS endpoints are enabled or disabled consistently with policy and are actually reachable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameNodeHttpServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameNodeHttpServerXFrame.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameNodeHttpServerXFrame.java

## Purpose
Tests X-Frame-Options header behavior for NameNode and SecondaryNameNode HTTP servers, covering enabled, disabled, illegal option, and secondary server defaults.

## Important APIs, Types, and Functions
- Uses `NameNodeHttpServer`, `HttpServer2.XFrameOption.SAMEORIGIN`, `DFS_XFRAME_OPTION_ENABLED`, and `DFS_XFRAME_OPTION_VALUE`.
- `getServerURL` derives server URL from `HttpServer2.getConnectorAddress(0)`.
- Uses `SecondaryNameNode.startInfoServer` and `SecondaryNameNode.getHttpAddress`.

## Control Flow
- `testNameNodeXFrameOptionsEnabled` starts a server with XFrame enabled and asserts header exists and ends with `SAMEORIGIN`.
- `testNameNodeXFrameOptionsDisabled` asserts the header is absent when disabled.
- `testNameNodeXFrameOptionsIllegalOption` expects `IllegalArgumentException` for invalid value `hadoop`.
- `testSecondaryNameNodeXFrame` starts SecondaryNameNode info server and verifies default `SAMEORIGIN` header.

## State and Persistence Behavior
- No metadata persistence is tested; state is HTTP server configuration and response headers.
- Helper starts a `NameNodeHttpServer` but does not stop it, so tests rely on ephemeral ports and JVM cleanup.

## Dependencies and Integration Points
- Integrates NameNode/SecondaryNameNode HTTP server config with Hadoop `HttpServer2` X-Frame option enforcement.
- Uses real `HttpURLConnection` to inspect headers.

## Risks and Edge Cases
- `createServerwithXFrame` leaks server instances because it does not call `stop`.
- Header comparison uses `endsWith`, allowing prefixed values.
- SecondaryNameNode is started without explicit shutdown in the test body.

## Test Signals
- Focused signal for clickjacking header defaults and validation across NameNode HTTP surfaces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameNodeHttpServerXFrame.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameNodeMXBean.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameNodeMXBean.java

## Purpose
Large integration suite for NameNode JMX/MXBean attributes exposed by `NameNodeMXBean`, `FSNamesystem`, `FSNamesystemState`, replicated block state, and EC block group state. It validates JSON payloads, DataNode admin states, top users, directory-size metrics, erasure coding policy/health metrics, total block counts, and dead-node details.

## Important APIs, Types, and Functions
- Uses platform `MBeanServer` and `ObjectName` values such as `Hadoop:service=NameNode,name=NameNodeInfo`, `FSNamesystem`, `FSNamesystemState`, `ReplicatedBlocksState`, and `ECBlockGroupsState`.
- Parses JSON with Jetty `JSON.parse` and Jackson `ObjectMapper`.
- Cluster operations use `MiniDFSCluster`, HA topologies, `HATestUtil`, `HostsFileWriter`, `CombinedHostFileManager`, `DatanodeManager`, `DatanodeDescriptor`, and DataNode admin transitions.
- EC tests use `StripedFileTestUtil`, `ErasureCodingPolicy`, `LocatedStripedBlock`, `StripedBlockUtil.parseStripedBlockGroup`, and corrupted replicas.
- Storage/metrics tests use `FileUtil.chmod`, `FileUtils.sizeOfDirectory`, `NameNodeRpc.rollEditLog`, and `saveNamespace`.

## Control Flow
- `testNameNodeMXBeanInfo` starts four DataNodes, sets upgrade domain and maintenance/decommission states, reads many NameNodeInfo attributes, verifies live/dead node JSON fields, name dir status before/after chmod-induced rollEditLog failure, cache metrics, and rolling upgrade status.
- `testLastContactTime`, `testDecommissioningNodes`, `testInServiceNodes`, and `testMaintenanceNodes` use host include/exclude/out-of-service files and refreshNodes to verify live/dead/decommission/maintenance JMX JSON and FSNamesystem counters.
- `testTopUsers`, `testTopUsersDisabled`, and `testTopUsersNoPeriods` exercise `TopUserOpCounts` under enabled, disabled, and no-window configs after repeated filesystem operations.
- `testQueueLength` reads `LockQueueLength`.
- `testNNDirectorySize` starts HA NameNodes with explicit IPC ports, rolls/tails edits, saves namespace, and compares reported per-directory sizes to actual disk usage.
- `testEnabledEcPoliciesMetric`, `testVerifyMissingBlockGroupsMetrics`, and `testTotalBlocksMetrics` validate EC policies, missing/corrupt EC block group metrics, total replicated versus EC block counts, and topology verification message.
- `testDeadNodesInNameNodeMXBean` adds an included but absent mock DataNode and verifies dead-node JSON includes blank UUID.

## State and Persistence Behavior
- Many tests depend on live cluster state, DataNode heartbeats, host include/exclude files, admin-state transitions, and MBean registration.
- Storage status and directory-size tests inspect real NameNode directories and permission-induced failure states.
- EC tests create replicated and striped files, corrupt replicas, disable heartbeats to retain corrupt-block records, and delete files while waiting for delete queues.
- HA total-block test compares active and standby metrics after namespace changes and deletion queues.

## Dependencies and Integration Points
- Broad integration across NameNode JMX, FSNamesystem metrics, block manager, DataNode manager, host config providers, HA, EC, storage directories, nntop, and native IO cache manipulation.
- Uses `@TempDir baseDir` for cluster roots and static `NativeIO.POSIX.setCacheManipulator(new NoMlockCacheManipulator())`.

## Risks and Edge Cases
- Timing-sensitive waits around heartbeats, admin-state transitions, corrupt-block discovery, HA startup ports, and standby catch-up.
- JSON payload structure is asserted directly; field rename/type changes will break tests.
- Some tests intentionally chmod storage dirs and must restore permissions in finally.
- EC topology verification assumes one rack and specific default EC policy requirements.
- Large breadth makes failures useful but sometimes expensive to diagnose.

## Test Signals
- Very high signal for NameNode observability compatibility: JMX attribute values must match internal `FSNamesystem` methods, node-state JSON must include expected fields, EC/replicated counters must add up, and storage/HTTP/top-user metrics must remain stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameNodeMXBean.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameNodeMetadataConsistency.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameNodeMetadataConsistency.java

## Purpose
Integration tests for NameNode behavior when DataNodes report blocks with generation stamps in the future. It verifies the special handling applies during startup safe mode and not during normal operation.

## Important APIs, Types, and Functions
- Uses `MiniDFSCluster.changeGenStampOfBlock`, `DFSTestUtil.getFirstBlock`, `DataNodeTestUtils.runDirectoryScanner`, `cluster.stopDataNode/restartDataNode`, and `cluster.restartNameNode`.
- Mutates block manager state using `BlockInfo.delete` and `BlockManager.removeBlock` under `FSNamesystem.writeLock(RwLockMode.BM)`.
- Uses `BlockManagerTestUtil.setStartupSafeModeForTest` and `cluster.triggerBlockReports`.
- Checks `NameNode.getBytesWithFutureGenerationStamps` and `FSNamesystem.getSafeModeTip`.

## Control Flow
- `InitTest` starts a one-DataNode cluster with directory scan interval 1.
- `testGenerationStampInFuture` writes a file, increments its on-disk block generation stamp, runs scanner, stops DataNode, restarts NameNode, removes the stored block from NameNode memory, marks block manager as startup safe mode, restarts DataNode, waits for bytes-with-future-gen-stamps to equal file length, and checks safemode reason.
- `testEnsureGenStampsIsStartupOnly` performs a similar future-generation-stamp setup without setting startup safe mode and expects the future-byte count to remain zero.
- `waitForNumBytes` repeatedly triggers block reports until the expected count appears.

## State and Persistence Behavior
- Directly manipulates DataNode on-disk block metadata generation stamp and NameNode in-memory block map.
- Restart and startup-safe-mode flags determine whether the future-generation report contributes to special metrics/safemode.

## Dependencies and Integration Points
- Integrates DataNode scanner/block reports, block manager metadata consistency checks, NameNode safemode logic, and mini-cluster restart controls.

## Risks and Edge Cases
- Invasive block-manager mutation requires correct BM write lock handling.
- Timing-sensitive around scanners and block reports.
- Assumes future generation stamp change survives DataNode restart/report.

## Test Signals
- Strong targeted signal for metadata consistency protection during startup and for avoiding false positives during non-startup operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameNodeMetadataConsistency.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameNodeMetricsLogger.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameNodeMetricsLogger.java

## Purpose
Tests periodic NameNode metrics logging configuration, async appender setup, and actual logging of Hadoop-domain MBeans.

## Important APIs, Types, and Functions
- Creates a custom `TestNameNode` subclass that overrides `loadNamesystem` with a mocked `FSNamesystem`.
- Configures `DFS_NAMENODE_METRICS_LOGGER_PERIOD_SECONDS_KEY`, `FS_DEFAULT_NAME_KEY`, and `DFS_NAMENODE_HTTP_ADDRESS_KEY`.
- Inspects log4j logger `NameNode.METRICS_LOG_NAME` and asserts first appender is `AsyncAppender`.
- Registers `TestFakeMetric` via `MBeans.register` and waits for a `PatternMatchingAppender` to match output.

## Control Flow
- `testMetricsLoggerOnByDefault` builds a NameNode with period 1 and expects `metricsLoggerTimer` non-null.
- `testDisableMetricsLogger` sets period 0 and expects timer null.
- `testMetricsLoggerIsAsync` builds enabled NameNode and checks appender type.
- `testMetricsLogOutput` registers fake MXBean metric, starts metrics logger, fetches the test pattern appender by name, and waits until it observes the metric output.

## State and Persistence Behavior
- Runtime-only logger/timer/MBean state; no HDFS namespace is loaded because namesystem is mocked.
- Uses random ports through `hdfs://localhost:0` and `0.0.0.0:0`.

## Dependencies and Integration Points
- Integrates NameNode initialization, metrics logger timer, log4j async appenders, Hadoop `MBeans`, and test logging appender configuration.

## Risks and Edge Cases
- Depends on log4j appender ordering and presence of `PATTERNMATCHERAPPENDER`.
- Fake MBean registration may conflict if not unregistered across repeated runs.
- Uses a partially initialized NameNode with mocked namesystem; not a full cluster signal.

## Test Signals
- Focused signal for metrics logger enable/disable behavior, async logging path, and ability to include Hadoop MBean metrics in periodic output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameNodeMetricsLogger.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameNodeOptionParsing.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameNodeOptionParsing.java

## Purpose
Unit tests for `NameNode.parseArguments` startup option parsing, covering upgrade options, reserved path rename mappings, rolling upgrade modes, and format interactivity/force flags.

## Important APIs, Types, and Functions
- Exercises `NameNode.parseArguments`.
- Validates `HdfsServerConstants.StartupOption` values and `RollingUpgradeStartupOption`.
- Inspects `StartupOption.getClusterId`, `getRollingUpgradeStartupOption`, `getInteractiveFormat`, and `getForceFormat`.
- Checks `FSImageFormat.renameReservedMap` for `-renameReserved` behavior.

## Control Flow
- `testUpgrade` parses `-upgrade` alone, with `-clusterid`, with explicit `-renameReserved`, in alternate argument order, and with default rename values based on layout version. It then asserts error messages for unknown reserved paths and invalid rename targets, and null for `-cid`.
- `testRollingUpgrade` expects null for missing subcommand, correct options for `started` and `rollback`, and `IllegalArgumentException` for unknown subcommand.
- `testFormat` verifies default interactive format, non-interactive mode, force mode, and invalid lone `-nonInteractive`.

## State and Persistence Behavior
- Pure parser state, except static `FSImageFormat.renameReservedMap` is populated and manually cleared in part of the upgrade test.

## Dependencies and Integration Points
- Protects NameNode CLI startup option semantics used by real NameNode process startup and upgrades.

## Risks and Edge Cases
- Static `renameReservedMap` can leak entries if a failing assertion interrupts before clear points.
- Some exception branches catch expected exceptions but do not fail if no exception is thrown for two upgrade invalid cases unless later behavior exposes it.

## Test Signals
- Fast parser-level signal for upgrade, rolling upgrade, and format CLI compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameNodeOptionParsing.java -->
