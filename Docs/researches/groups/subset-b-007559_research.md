# Research: subset-b-007559

Grouped research for Hadoop HDFS NameNode snapshot tests under `sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/SnapshotTestHelper.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/SnapshotTestHelper.java

Purpose: Shared test utility for snapshot-related HDFS tests. It centralizes noisy log suppression, snapshot path construction, snapshot creation checks, FSDirectory tree dumping/comparison, and small test harnesses used by trash and randomized snapshot scenarios.

Important APIs/types/functions: `disableLogs()` disables common Hadoop and Jetty loggers. `MyCluster` wraps `MiniDFSCluster`, `FSNamesystem`, `FSDirectory`, `DistributedFileSystem`, and `FsShell`, exposing `createSnapshot`, `deleteSnapshot`, `rename`, `moveToTrash`, `mkdirs`, `createFile`, `getTrashPath`, and diagnostic `printFs`. `Log4jRecorder` captures Log4j output from an SLF4J logger to discover trash destinations. Static helpers include `getSnapshotRoot`, `getSnapshotPath`, `createSnapshot`, `checkSnapshotCreation`, `compareDumpedTreeInFile`, `dumpTree2File`, and `getSnapshotFile`. `TestDirectoryTree` builds a binary directory tree with `Node` instances and per-node file/non-snapshot-child state.

Control flow: test code calls `createSnapshot`, which asserts the root exists, enables snapshots, creates the named snapshot, and sets high namespace/storage quotas for count tests. Tree comparison normalizes object identity, snapshot file class names, under-construction replica fields, and optionally quota text before asserting line-by-line equality.

State and persistence behavior: utilities expose NameNode in-memory state via dump-tree snapshots and compare before/after restart images. `MyCluster` maintains counters for snapshot names, trash operations, and printed trees.

Dependencies and integration points: heavily integrated with `MiniDFSCluster`, `DFSTestUtil`, `FSDirectory`, `INode`, `TrashPolicyDefault`, `FsShell`, and NameNode logging classes.

Risks and test signals: broad log suppression can hide diagnostics during failures. Dump comparisons intentionally ignore unstable fields, so they are good persistence signals for namespace topology but not for exact object identity. `Log4jRecorder.stop()` is not used by `MyCluster.moveToTrash`, so repeated calls can accumulate appenders during long stress tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/SnapshotTestHelper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestAclWithSnapshot.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestAclWithSnapshot.java

Purpose: Verifies ACL behavior across HDFS snapshots, including immutable snapshot ACLs, permission enforcement, restart/checkpoint persistence, snapshot-path mutation rejection, quota edge cases, and `AclFeature` deduplication/reference counting.

Important APIs/types/functions: static users `BRUCE` and `DIANA` drive authorization checks through `DFSTestUtil.getFileSystemAs`. Tests use `hdfs.setAcl`, `modifyAclEntries`, `removeAcl`, `removeAclEntries`, `removeDefaultAcl`, `getAclStatus`, and `AclTestHelpers.assertPermission`. `FSAclBaseTest.getAclFeature`, `AclStorage.getUniqueAclFeatures`, and `AclFeature.getRefCount` inspect internal ACL feature sharing. `restart(boolean checkpoint)` optionally invokes `NameNodeAdapter.enterSafeMode` and `saveNamespace`.

Control flow: each test creates a unique `/pN` and snapshot name. Root/content ACL tests set initial ACLs, create a snapshot, mutate or remove ACLs on the live inode, then assert the live path reflects the new ACL while `.snapshot/name` retains old entries and access results. Assertions are repeated after edit-log restart and checkpoint reload. Mutation-on-snapshot tests expect `SnapshotAccessControlException`.

State and persistence behavior: ACL state is checked before restart, after restart without checkpoint, and after saved namespace reload. Deduplication tests verify snapshot roots can share the same `AclFeature`, mutations create new features for live inodes, and deletion/removal eventually drops reference counts and unique feature entries.

Dependencies and integration points: integrates HDFS ACL config (`DFS_NAMENODE_ACLS_ENABLED_KEY`), NameNode saveNamespace, internal `AclStorage`, and user impersonation.

Risks and test signals: strong regression coverage for immutable snapshot metadata and ACL persistence. Some quota tests only assert that ACL changes/removals succeed under tight namespace quota; they do not assert quota counters directly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestAclWithSnapshot.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestCheckpointsWithSnapshots.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestCheckpointsWithSnapshots.java

Purpose: Regression test for HDFS-5433, ensuring SecondaryNameNode checkpoint reload clears stale snapshottable-directory state when the primary NameNode image no longer contains snapshots or snapshottable directories.

Important APIs/types/functions: `MiniDFSCluster`, `SecondaryNameNode`, `HdfsAdmin.allowSnapshot/disallowSnapshot`, `SnapshotManager.getNumSnapshots`, `SnapshotManager.getNumSnapshottableDirs`, and `NameNodeAdapter.saveNamespace`.

Control flow: setup deletes the MiniDFSCluster base directory. The test starts a primary NameNode and a 2NN, creates `/foo`, marks it snapshottable, creates one snapshot, and checkpoints to load that state into the 2NN. It then deletes the snapshot, disallows snapshots on `/foo`, saves a fresh namespace on the primary, and triggers another 2NN checkpoint.

State and persistence behavior: before any operations both SnapshotManagers report zero snapshots/directories. After snapshot creation primary state reports one of each, and after the first checkpoint the secondary matches. After deletion/disallow and a saved namespace, the second checkpoint must leave the secondary with zero snapshots and zero snapshottable dirs, proving reload reset both image tree and manager-side lists.

Dependencies and integration points: exercises image transfer/reload between `NameNode` and `SecondaryNameNode`, admin snapshot APIs, and snapshot manager counters.

Risks and test signals: the final counter assertions are a targeted signal for stale manager entries that could otherwise serialize invalid fsimages. It does not restart the primary from the 2NN output in this test, relying on counters as the failure proxy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestCheckpointsWithSnapshots.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestDiffListBySkipList.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestDiffListBySkipList.java

Purpose: Tests `DiffListBySkipList`, the skip-list implementation of directory snapshot diffs, against `DiffListByArrayList` and real HDFS directory snapshot behavior.

Important APIs/types/functions: `newDiffListBySkipList()` initializes `DirectoryDiffListFactory` with interval 3 and `MAX_LEVEL`. Helpers include `verifyChildrenList`, `getCombined`, `getChildrenList`, `addDiff`, `remove`, `assertDirectoryDiff`, `assertSkipList`, and `assertSkipListNode`. It directly uses `DirectoryWithSnapshotFeature.DirectoryDiff`, `ChildrenDiff`, `DiffList`, `DiffListByArrayList`, and `SkipListNode`.

Control flow: tests create zero-datanode clusters, make snapshottable roots, then create/delete child directories between 100 snapshots. `testAddLast` adds diffs in chronological order; `testAddFirst` adds reverse-ordered diffs; removal tests delete from tail, head, random positions, lower skip-list levels, and upper levels. After each mutation, the skip list is compared with array-list behavior and HDFS `INodeDirectory.getChildrenList`.

State and persistence behavior: this is in-memory structural testing, not fsimage persistence. Snapshot diffs are generated from live NameNode state, and deletion calls `hdfs.deleteSnapshot` to keep the backing directory diffs aligned with test removals.

Dependencies and integration points: integrates `FSDirectory`, `INodeDirectory`, snapshot diff internals, `ReadOnlyList`, and HDFS snapshot creation/deletion.

Risks and test signals: verifies both semantic output (children lists for ranges) and structural invariants (skip node targets and combined diffs). Random removal adds coverage but can make reproduction require logs/seed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestDiffListBySkipList.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestDisallowModifyROSnapshot.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestDisallowModifyROSnapshot.java

Purpose: Verifies that paths inside read-only HDFS snapshots reject mutating filesystem operations with `SnapshotAccessControlException`.

Important APIs/types/functions: class-level setup creates `/TestSnapshot/sub1/dir1`, `/TestSnapshot/sub2/dir2`, snapshots `sub1` as `testSnapshot`, and stores the snapshot path to `dir1`. Tests call `DistributedFileSystem` methods such as `setReplication`, `setPermission`, `setOwner`, `rename`, `delete`, `setQuota`, `setTimes`, `append`, and `mkdirs`, plus deprecated `DFSClient.create` and `createSymlink`.

Control flow: each test attempts one mutation against `objInSnapshot` or an operation whose destination is inside `.snapshot`. Most use `assertThrows(SnapshotAccessControlException.class)`. `testRename` covers source-in-snapshot, destination-in-snapshot, and `rename` with `Options.Rename`.

State and persistence behavior: no restart path is covered. The shared static cluster persists for the class, with one snapshot object reused across all mutation tests.

Dependencies and integration points: exercises the filesystem API and lower-level `DFSClient` entry points to ensure snapshot read-only enforcement is not bypassed outside `DistributedFileSystem`.

Risks and test signals: good API surface coverage for mutation rejection. Since it reuses static state, a setup failure affects every test. The symlink case targets `"/TestSnapshot/sub1/.snapshot"` rather than the exact saved object path, covering mutation under the reserved snapshot directory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestDisallowModifyROSnapshot.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestFSImageWithOrderedSnapshotDeletion.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestFSImageWithOrderedSnapshotDeletion.java

Purpose: Tests fsimage correctness when ordered snapshot deletion is enabled and snapshots interact with complex rename/delete histories.

Important APIs/types/functions: enables `DFS_NAMENODE_SNAPSHOT_DELETION_ORDERED`. Helpers wrap `rename`, `createFile`, `appendFile`, `deleteSnapshot`, `restartCluster`, `dumpTree2File`, and `printTree`. `restartCluster()` enters safe mode, saves namespace, restarts without formatting, dumps FSDirectory before/after, and uses `SnapshotTestHelper.compareDumpedTreeInFile`.

Control flow: tests build directories under snapshottable roots, create snapshots at several points, rename directories across parents or out of snapshottable areas, append/create files, delete current directories/files, delete snapshots out of order, then restart. Cases include double renames, nested rename chains, deleting snapshots `s1/s3` while later snapshots must retain files, and deleting the newest/older snapshots around renamed directories.

State and persistence behavior: the core signal is fsimage round-trip equality and successful NameNode restart. `printTree` also compares classic `dumpTreeRecursively` output with `NamespacePrintVisitor.print2Sting`, catching visitor-format divergence.

Dependencies and integration points: integrates snapshot deletion ordering, safe-mode saveNamespace, fsimage reload, `INode` dump state, `NamespacePrintVisitor`, and `DFSTestUtil` file creation/appends.

Risks and test signals: strong coverage for rename history serialized into fsimage. Most tests assert restart success and selective existence, but many do not inspect every surviving snapshot path after reload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestFSImageWithOrderedSnapshotDeletion.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestFileContextSnapshot.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestFileContextSnapshot.java

Purpose: Verifies snapshot operations exposed through `FileContext` rather than `DistributedFileSystem`.

Important APIs/types/functions: setup creates a `MiniDFSCluster` with block size 1024 and replication 3, obtains `FileContext.getFileContext(conf)` and a `DistributedFileSystem`, and creates `/snapshot`. Tests call `fileContext.createSnapshot`, `deleteSnapshot`, and `renameSnapshot`; `DistributedFileSystem` is used for setup and status assertions.

Control flow: `testCreateAndDeleteSnapshot` creates a file, disallows snapshots, expects `FileContext.createSnapshot` to throw `SnapshotException` containing "Directory is not a snapshottable directory", then allows snapshots, creates `s1`, verifies the snapshot path exists, deletes it, and verifies removal. `testRenameSnapshot` records `FileStatus` for `.snapshot/s1/file1`, renames `s1` to `s2`, verifies old path gone/new path present, then checks status equality after normalizing the path.

State and persistence behavior: no restart or fsimage persistence. It validates API-layer path/status behavior during a live NameNode session.

Dependencies and integration points: covers `FileContext` bindings to HDFS snapshot APIs, `SnapshotTestHelper.getSnapshotRoot`, and `FileStatus` equality semantics.

Risks and test signals: focused API smoke test. It intentionally compares status string after path normalization to ensure snapshot rename changes only the path, but it does not verify block/checksum identity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestFileContextSnapshot.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestFileWithSnapshotFeature.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestFileWithSnapshotFeature.java

Purpose: Unit-tests `FileWithSnapshotFeature.updateQuotaAndCollectBlocks` quota/block accounting without running a cluster.

Important APIs/types/functions: uses `FileDiffList`, `FileWithSnapshotFeature`, `FileDiff`, `INodeFile`, `INode.ReclaimContext`, `QuotaCounts`, `BlockInfoContiguous`, `BlockStoragePolicySuite`, `BlockStoragePolicy`, Mockito spies/mocks, and `Whitebox.setInternalState` to set replication encoded in inode headers.

Control flow: `testUpdateQuotaAndCollectBlocks` first checks a no-snapshot case where quota delta remains zero. It then injects a snapshot inode with replication 3 while the live file prefers replication 1 and mocks storage policy choices of SSD vs DISK; updating quota should account for the replication/storage-type delta. `testUpdateQuotaDistinctBlocks` tests whether removed file-diff blocks are charged only when distinct from current file blocks and remaining diffs.

State and persistence behavior: purely in-memory; state is mocked or constructed. No fsimage/edit-log path is involved.

Dependencies and integration points: targets block management, storage policy selection, namespace quota delta accumulation, and snapshot file-diff internals.

Risks and test signals: precise for quota arithmetic and duplicate-block avoidance. Mocking internal headers/storage policies can diverge from production construction paths, so this complements but does not replace integration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestFileWithSnapshotFeature.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestFsShellMoveToTrashWithSnapshots.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestFsShellMoveToTrashWithSnapshots.java

Purpose: Stress-tests FsShell move-to-trash behavior while snapshots, snapshot deletions, and many renames reshape paths.

Important APIs/types/functions: uses `SnapshotTestHelper.MyCluster` with trash enabled by `fs.trash.interval`. `MyDirs` tracks a renameable nested path with `TO_BE_REMOVED` segments. `MyFile` tracks temp, destination, and trash paths. Operation classes `MoveToTrashOp` and `DeleteSnapshotOp` are shuffled and executed once through `Op.execute`.

Control flow: `runTestMoveToTrashWithShell` creates db/tmp dirs, swaps nested directories through snapshot-protected renames, creates temp bucket files, moves older temp files into destination dirs, performs more nested renames, queues a move-to-trash for the database directory, and interleaves snapshot deletion operations in random order. Multi-task tests run many scenarios concurrently with a fixed thread pool, then assert all bucket files exist at normalized trash/current paths.

State and persistence behavior: no NameNode restart. State stress is live namespace state plus snapshot diffs and FsShell trash rename behavior. `updateTrashPath` compensates for trash root prefixes chosen by shell output.

Dependencies and integration points: integrates `FsShell -rm -r`, `TrashPolicyDefault` logging, snapshot creation/deletion, rename semantics, concurrency utilities, and HDFS path resolution.

Risks and test signals: high-value stress for race/order interactions and path rewrite correctness. Random shuffling and sleeps broaden coverage but complicate reproducibility; assertions mostly prove file reachability, not exact trash tree shape.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestFsShellMoveToTrashWithSnapshots.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestGetContentSummaryWithSnapshot.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestGetContentSummaryWithSnapshot.java

Purpose: Verifies `getContentSummary` reports correct live and snapshot counts/lengths for paths with snapshots and for direct snapshot paths.

Important APIs/types/functions: uses `cluster.getNameNodeRpc().getContentSummary`, `ContentSummary` fields `getDirectoryCount`, `getFileCount`, `getLength`, `getSnapshotDirectoryCount`, `getSnapshotFileCount`, and `getSnapshotLength`, plus `SnapshotTestHelper.getSnapshotRoot/getSnapshotPath`.

Control flow: the test creates `/foo/bar` and `/temp`, snapshots `/foo` as `s1`, creates two 10-byte files under `bar`, and compares live `/foo`/`bar` with snapshot `/foo/.snapshot/s1`/`bar`. It then creates snapshot `s2`, appends 10 bytes to one file, verifies `s2` retains pre-append length, deletes one file, checks snapshot length/count contribution in live `/foo`, verifies a non-existent snapshot path throws `FileNotFoundException`, renames the remaining file out to `/temp`, and rechecks snapshot counters.

State and persistence behavior: live namespace and snapshot diff accounting only; no restart path.

Dependencies and integration points: exercises NameNode RPC content summary, snapshot diff accounting for deleted/renamed files, and block length aggregation.

Risks and test signals: strong focused signal for summary counters and lengths. It uses exact small file lengths, making failures easy to localize. It does not cover quotas, erasure coding, or storage-type summaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestGetContentSummaryWithSnapshot.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestINodeFileUnderConstructionWithSnapshot.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestINodeFileUnderConstructionWithSnapshot.java

Purpose: Tests snapshot behavior for files being appended or under construction, including snapshot file sizes, block locations, and lease recovery interactions.

Important APIs/types/functions: helpers include `appendFileWithoutClosing` and tests use `HdfsDataOutputStream.hsync(UPDATE_LENGTH)`, `INodeFile.computeFileSize`, `DirectoryDiff`, `DFSClientAdapter.callGetBlockLocations`, `LocatedBlocks`, and `NameNodeAdapter.getLeaseManager/runLeaseChecks`.

Control flow: `testSnapshotAfterAppending` snapshots before/after append and replication changes, checking live inode replication and size. `testSnapshotWhileAppending` snapshots while append streams are open, closes streams later, and verifies snapshot-specific file sizes in directory diffs remain frozen. `testGetBlockLocations` snapshots files before/after appends and verifies snapshot block listings are bounded by captured file length and not marked under construction, while the live file is under construction. `testLease` deletes a directory containing an open file captured by a snapshot and runs lease checks under FSNamesystem write lock.

State and persistence behavior: no restart, but it inspects NameNode in-memory inode/diff state and lease manager behavior. Snapshot state captures open-file length at hsync points.

Dependencies and integration points: integrates append pipeline, block location RPC, snapshot diff internals, leases, FSDirectory, and NameNode locking (`RwLockMode.GLOBAL`).

Risks and test signals: good coverage of open-file snapshot size isolation and block-range correctness. Lease test mostly asserts absence of exception/deadlock, so failure signal is coarse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestINodeFileUnderConstructionWithSnapshot.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestListSnapshot.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestListSnapshot.java

Purpose: Tests listing snapshottable directories and snapshots, with ordered snapshot deletion enabled.

Important APIs/types/functions: uses `hdfs.getSnapshottableDirListing`, `hdfs.getSnapshotListing`, `SnapshotStatus`, `SnapshottableDirectoryStatus`, and `SnapshotManager.setAllowNestedSnapshots(true)`. It expects `SnapshotException` through `LambdaTestUtils.intercept` when listing snapshots on a non-snapshottable directory.

Control flow: the test first asserts no snapshottable dirs exist and `getSnapshotListing(dir1)` fails. It allows snapshots on `/`, verifies root listing and empty snapshot listing, disallows root snapshots, and checks listings again. It then allows snapshots on `/TestSnapshot1`, creates `s0`, `s1`, `s2`, verifies names, full paths, and first snapshot ID, deletes `s2`, verifies listing still contains three entries with the last marked deleted, then deletes `s0` and expects only two entries.

State and persistence behavior: live manager/listing behavior only; no restart. Ordered deletion creates an intermediate deleted snapshot visible in listing until earlier snapshots allow cleanup.

Dependencies and integration points: integrates public HDFS snapshot listing APIs, ordered deletion status flags, and snapshottable-directory listing.

Risks and test signals: targeted validation of user-visible listing semantics under ordered deletion. It does not validate pagination, permissions, or persistence of deleted flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestListSnapshot.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestNestedSnapshots.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestNestedSnapshots.java

Purpose: Tests nested snapshottable directory behavior, snapshot limits/default names, snapshot comparator semantics, and disallowing nested snapshottable directories while retaining snapshot features.

Important APIs/types/functions: configures `DFS_NAMENODE_SNAPSHOT_MAX_LIMIT`, uses `SnapshotManager.setAllowNestedSnapshots`, `SnapshotTestHelper.dumpTree`, `SnapshotTestHelper.getSnapshotRoot/getSnapshotPath`, `Snapshot.ID_COMPARATOR`, and internal `INodeDirectory` construction.

Control flow: `testNestedSnapshots` allows nested snapshots, snapshots `/testNestedSnapshots/foo` and nested `bar`, creates files before/after snapshots, and checks file visibility in live/foo snapshot/bar snapshot. It then allows/deletes root snapshot, disallows `foo`, disables nested snapshots, and verifies allowing snapshots on ancestor/descendant paths fails with messages containing "subdirectory" or "ancestor". `testSnapshotLimit` creates exactly 100 snapshots and expects the next to fail, while checking historical file visibility. `testSnapshotName` verifies default generated name pattern under quota. `testIdCmp` checks null and same/different snapshot ordering. `testDisallowNestedSnapshottableDir` verifies a nested snapshottable directory reverts to `isWithSnapshot` after disallow.

State and persistence behavior: no restart; state focus is live snapshot manager constraints and inode feature transitions.

Dependencies and integration points: integrates snapshot policy config, quota, edit-log fsync test optimization, DFSUtil byte conversion, and internal inode/snapshot classes.

Risks and test signals: broad semantic coverage for nested snapshots. Static `Random` with seed 0 makes limit visibility checks deterministic. No persistence path for nested state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestNestedSnapshots.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestOpenFilesWithSnapshot.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestOpenFilesWithSnapshot.java

Purpose: Slow integration suite for snapshot capture of open files, including aborted streams, deletion, rename, checksum stability, mixed capture-open-files config, and NameNode restart/checkpoint behavior.

Important APIs/types/functions: enables `DFS_NAMENODE_SNAPSHOT_CAPTURE_OPENFILES`. Helpers include `doWriteAndAbort`, `createFile`, `writeToStream` with `hsync(UPDATE_LENGTH)`, `createSnapshot`, `verifyFileSize`, and `restartNameNode` that triggers block reports, saves namespace, and restarts. Uses `DFSOutputStream`, `HdfsDataOutputStream`, `NamenodeProtocols.addBlock`, `FileChecksum`, and `SubjectInheritingThread`.

Control flow: early tests create under-construction files, abort streams, snapshot, delete files/parents, and restart/read snapshot files. Multiple-snapshot tests delete newer snapshots and restart with/without checkpoint. Point-in-time tests keep several files open under and outside snap roots, write between snapshots, and verify snapshot lengths freeze only when configured. Deletion tests delete open live files and snapshots in different orders while preserving remaining snapshot references. A writer-thread stress test deletes snapshots while appending. Checksum test proves old snapshot checksums survive truncate/append of current file. Mixed-config test toggles capture behavior and verifies old/new snapshot length semantics.

State and persistence behavior: strong persistence coverage through saveNamespace and NameNode restarts. Open file state is captured at hsync/update-length boundaries and represented as immutable snapshot copies when capture is enabled.

Dependencies and integration points: integrates append pipeline, block reports, leases/open file capture, snapshot deletion, truncation, checksums, NameNode RPC, and thread subject inheritance.

Risks and test signals: excellent regression coverage but slow and sometimes coarse where success is "restart does not fail". The writer stress loop is timing-sensitive and can be expensive.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestOpenFilesWithSnapshot.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestOrderedSnapshotDeletion.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestOrderedSnapshotDeletion.java

Purpose: Tests ordered snapshot deletion marking, hidden system xattr behavior, persistence, and behavior when xattrs are disabled or pre-existing user xattrs exist.

Important APIs/types/functions: enables `DFS_NAMENODE_SNAPSHOT_DELETION_ORDERED`. Static helpers `assertMarkedAsDeleted`, `assertNotMarkedAsDeleted`, and `getDeletedSnapshotName` inspect `Snapshot.Root.isMarkedAsDeleted`, `XAttrFeature`, `XATTR_SNAPSHOT_DELETED`, and `hdfs.getSnapshotListing`. `assertXAttrSet` deletes a snapshot by its active/deleted listing name and validates internal and user-visible xattrs.

Control flow: `testOrderedSnapshotDeletion` creates `s0/s1/s2`, deletes later snapshots first, verifies they are marked deleted/renamed rather than immediately removed, then deletes remaining names. Persistence tests repeat deletion, restart NameNodes, or saveNamespace before restart. Disabling-xattr test toggles `dfs.namenode.xattrs.enabled` false after marking and verifies internal deletion xattr still works while user xattr operations fail. Pre-existing xattr test ensures user xattrs remain visible while system deletion marker is hidden.

State and persistence behavior: ordered deletion stores state as renamed snapshot roots with system xattr and `Snapshot.Root` deleted flag; tests check survival across restart and fsimage save.

Dependencies and integration points: integrates snapshot listing, xattr subsystem, fsimage restart, and ordered snapshot deletion config.

Risks and test signals: strong internal/external visibility checks. `getDeletedSnapshotName` assumes a listing entry starts with the requested base name and will fail if listing semantics change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestOrderedSnapshotDeletion.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestOrderedSnapshotDeletionGc.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestOrderedSnapshotDeletionGc.java

Purpose: Tests `SnapshotDeletionGc`, the background cleanup path for ordered snapshot deletion.

Important APIs/types/functions: enables ordered deletion and sets `DFS_NAMENODE_SNAPSHOT_DELETION_ORDERED_GC_PERIOD_MS` to 10 ms. Helpers include `exist`, `waitForGc`, `createSnapshots`, and `doEditLogValidation`, which counts `OP_DELETE_SNAPSHOT` edit-log records using `FSImageTestUtil.countEditLogOpTypes`.

Control flow: `testSingleDir` creates snapshots `s0/s1/s2`, deletes `s2` and `s1` out of order, verifies they are marked deleted and renamed, sleeps to confirm they are not GCed while `s0` remains, then deletes `s0` and waits for GC to remove the marked snapshots. It validates five delete-snapshot edit-log ops: three user deletes plus two GC deletes. `testMultipleDirs` creates 10 snapshottable dirs with random snapshot counts, shuffles all snapshot paths, deletes them, waits for GC, and validates restart/replay without fixed op count.

State and persistence behavior: after edit-log validation the cluster restarts with GC delayed for a long period, ensuring replayed edits alone leave snapshot count zero.

Dependencies and integration points: integrates ordered deletion marker assertions from `TestOrderedSnapshotDeletion`, FSImage/NNStorage edit files, edit-log op counting, and background GC scheduling.

Risks and test signals: strong coverage of delayed deletion ordering and edit-log persistence. Random multi-dir case broadens coverage but intentionally avoids deterministic edit count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestOrderedSnapshotDeletionGc.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestRandomOpsWithSnapshots.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestRandomOpsWithSnapshots.java

Purpose: Slow randomized integration test that interleaves filesystem operations with snapshot create/delete/rename operations and verifies cluster health across checkpoint/restart cycles.

Important APIs/types/functions: weighted `Operations` enum chooses file/dir create/delete/rename and snapshot create/delete/rename. State is tracked in `snapshottableDirectories`, `pathToSnapshotsMap`, counters, and a random generator seeded with current time. Helpers include `createFiles`, `createTestDir`, `deleteTestDir`, `renameTestDir`, `createSnapshot`, `deleteSnapshot`, `renameSnapshot`, file operation counterparts, and `checkClusterHealth`.

Control flow: setup creates `/testDir` and `/WITNESSDIR`. The test creates 250 random-depth files in both trees, randomly enables snapshots on some parents, ensures at least one snapshottable dir, chooses iteration/operation counts, then applies batches of filesystem operations and snapshot operations. Filesystem operations are mirrored into the witness tree when possible; snapshot operations only affect test tree. After each iteration, `checkClusterHealth` compares top-level test/witness `FileStatus` metadata, optionally saves namespace, restarts NameNodes, waits out safe mode, and asserts cluster/DN activity.

State and persistence behavior: persistence signal is repeated optional checkpoint plus restart after random namespace/snapshot mutations. Snapshot bookkeeping prevents deletion/rename of directories that currently own snapshots.

Dependencies and integration points: integrates snapshots with common HDFS operations, NameNode restart, safe mode, `GenericTestUtils.waitFor`, and `Options.Rename.OVERWRITE`.

Risks and test signals: valuable broad fuzz coverage but uses current-time seed, so reproduction depends on logs. Static lists/maps are not cleared in setup, which could matter if the same JVM reuses the class in unusual ways.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestRandomOpsWithSnapshots.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestRenameWithOrderedSnapshotDeletion.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestRenameWithOrderedSnapshotDeletion.java

Purpose: Tests rename restrictions when ordered snapshot deletion and snapshot trash root support are enabled.

Important APIs/types/functions: configures `DFS_NAMENODE_SNAPSHOT_DELETION_ORDERED` and `DFS_NAMENODE_SNAPSHOT_TRASHROOT_ENABLED`. Uses `DistributedFileSystem.rename`, `allowSnapshot`, `createSnapshot`, and `DFSTestUtil.createFile`. `validateRename` asserts an `IOException` message contains "are not under the same snapshot root."

Control flow: the test creates a snapshottable directory, normal directories `/dir1` and `/dir2`, files inside `/dir1` and the snapshottable subtree, then checks forbidden and allowed rename cases. Moving a file from non-snapshottable into snapshottable root fails before and after creating snapshot `s0`; moving across non-snapshottable dirs succeeds. Moving out of the snapshottable root fails, while moving within the root succeeds. Directory rename cases similarly allow outside-to-outside and within-root renames, while rejecting crossing the snapshot root boundary.

State and persistence behavior: no restart/persistence path. The state focus is live validation of rename boundary rules under ordered deletion/trashroot mode.

Dependencies and integration points: integrates FSNamesystem snapshot trashroot config, ordered deletion config, and rename precondition logic.

Risks and test signals: clear boundary-condition coverage for same-snapshot-root enforcement. It validates exception text rather than type, so message changes can break the test even if behavior remains correct.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestRenameWithOrderedSnapshotDeletion.java -->
