# Research: subset-b-007561

Grouped research report for Hadoop HDFS NameNode snapshot, SPS, startup progress, top-window, and WebHDFS test sources. Each section is delimited for reconciliation into the source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestSnapshotDiffReport.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestSnapshotDiffReport.java

## Purpose
`TestSnapshotDiffReport` is the main integration-style test suite for HDFS snapshot diff reporting. It builds `MiniDFSCluster` instances with open-file snapshot capture, low access-time precision, access-time-only elision, descendant diff support, and a small diff listing RPC limit. The suite verifies `DistributedFileSystem#getSnapshotDiffReport`, `snapshotDiffReportListingRemoteIterator`, descendant-root diff behavior, rename/delete/create/modify normalization, open-file length capture, and persistence across NameNode restart.

## Important APIs, Types, and Functions
Key external APIs are `DistributedFileSystem.allowSnapshot/createSnapshot/deleteSnapshot/getSnapshotDiffReport/snapshotDiffReportListingRemoteIterator`, `SnapshotDiffReport`, `SnapshotDiffReport.DiffReportEntry`, `DiffType`, `SnapshotDiffReportListing`, `SnapshotDiffReportGenerator`, `SnapshotStatus`, and `SnapshottableDirectoryStatus`. Internal assertions use `DFSTestUtil.verifySnapshotDiffReport`, `SnapshotTestHelper`, `INodeDirectory`, `Snapshot`, `SnapshotDiffInfo`, `NameNodeAdapter`, and `DFSUtil.string2Bytes`.

Important helpers include `genSnapshotName`, `modifyAndCreateSnapshot`, `verifyDiffReport`, `verifyDescendantDiffReports`, `restartNameNode`, `writeToStream`, access-time helpers, `verifyDiffReportForGivenReport`, `assertDiff`, and `diff`. `modifyAndCreateSnapshot` is the shared mutation generator: it creates files and symlinks, snapshots configured roots, then applies delete, replication-change, recreate, symlink, and post-snapshot changes to produce expected diff entries.

## Control Flow
Most tests follow the same flow: create a directory tree, mark a snapshot root, take snapshots around a known mutation sequence, then compare the returned diff list against explicit ordered `DiffReportEntry` expectations. The descendant tests enable diff calculation from paths below the snapshot root and assert that identical mutations are rendered relative to each requested path. Rename tests exercise moves inside the root, out of the root, into the root, overwrite rename, ancestor deletion, and nested rename after snapshot deletion. RPC-limit and remote-iterator tests force pagination by setting `DFS_NAMENODE_SNAPSHOT_DIFF_LISTING_LIMIT` to 3, then reconstruct the final report from listing pages.

## State and Persistence Behavior
The tests depend on persistent NameNode namespace state: snapshots preserve point-in-time trees, snapshot IDs remain ordered, open-file snapshots freeze file lengths at capture time, access-time-only changes may intentionally not create snapshot copies, and edit-log/fsimage replay must preserve those relationships. `testDiffReportWithOpenFiles` saves the namespace and restarts the NameNode after block reports. `testDontCaptureAccessTimeOnlyChangeReport` restarts NameNodes after multiple snapshot atime transitions to ensure edit loading does not materialize skipped atime-only diffs.

## Dependencies and Integration Points
This file integrates the HDFS client, NameNode snapshot manager, FSDirectory inode layer, diff report protocol objects, Web/RPC pagination-facing remote iterators, block report and safe-mode namespace save code, and test utilities. It also depends on `TreeList` and `ChunkedArrayList` for accumulating paged diff entries.

## Risks and Edge Cases
The file targets high-risk snapshot edge cases: null/invalid snapshot names, qualified paths, descendant paths under snapshot roots, non-snapshot descendants, symlink deletion/recreation, duplicate delete/create names, rename interpretation relative to the requested diff scope, quota-bearing snapshot roots, open files under construction, atime-only changes, reversed diff semantics, pagination boundaries, and iterator exhaustion errors. The suite is timing-sensitive where it sleeps for access-time precision and asynchronous cluster restart behavior.

## Test Signals
Strong signals include exact diff-entry assertions, inverse report checks for create/delete reversal, remote iterator reconstruction matching the non-iterator report, explicit exception message checks, snapshot listing/ID assertions in `testSubtrees`, and restart-based persistence checks. The large scope makes this a regression anchor for diff semantics rather than a narrow unit test.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestSnapshotDiffReport.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestSnapshotFileLength.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestSnapshotFileLength.java

## Purpose
`TestSnapshotFileLength` verifies that a file read through a snapshot path is capped at the file length captured when the snapshot was taken, even if the live file is later appended or opened for append. It also verifies that shell-level `-cat` observes the same snapshot length boundary.

## Important APIs, Types, and Functions
The test uses `MiniDFSCluster`, `DistributedFileSystem`, `DFSTestUtil`, `AppendTestUtil`, `FSDataInputStream`, `FSDataOutputStream`, `FileStatus`, `FileChecksum`, `FsShell`, and `ToolRunner`. Snapshot paths are built with `SnapshotTestHelper.getSnapshotPath`. Configuration sets `DFS_NAMENODE_MIN_BLOCK_SIZE_KEY` and `DFS_BYTES_PER_CHECKSUM_KEY` to the test block size so checksum and read-length expectations are deterministic.

## Control Flow
`testSnapshotfileLength` creates a file, appends enough data to make an original length, snapshots the parent, records the snapshot checksum, opens the live file for append, validates that live checksums fail while the file is under construction, writes and flushes additional bytes, then confirms the snapshot still reads only the original length and retains the original checksum. After closing the append stream, the live file checksum diverges while the snapshot checksum remains unchanged. `testSnapshotFileLengthWithCatCommand` repeats the length check through `FsShell -cat`, redirecting stdout/stderr into a byte buffer and asserting the emitted byte count equals the snapshot length.

## State and Persistence Behavior
The tests are about snapshot inode state rather than NameNode restarts. They confirm that snapshot file metadata stores length and checksum-relevant block state independently from subsequent live-file appends and under-construction block state.

## Dependencies and Integration Points
Coverage crosses client read paths, checksum retrieval, append/hflush behavior, snapshot namespace resolution, `FsShell` command execution, and NameNode block/checksum behavior for files under construction.

## Risks and Edge Cases
Important risks include clients reading beyond snapshot length, snapshot checksums accidentally tracking the live file, checksum calls on under-construction files succeeding when they should fail, and command-line tools bypassing snapshot length checks. The test relies on byte counts captured from process-global `System.out` and `System.err`, so the finally block restoring streams is important.

## Test Signals
Assertions cover live versus snapshot `FileStatus` lengths, positioned reads, whole-file buffer reads, checksum equality/inequality before and after append close, expected under-construction checksum failure text, and shell output byte count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestSnapshotFileLength.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestSnapshotListing.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestSnapshotListing.java

## Purpose
`TestSnapshotListing` verifies `.snapshot` directory listing semantics for a snapshottable directory. It ensures root snapshot listing behaves specially, non-snapshottable directories reject `.snapshot` listing, empty snapshottable directories list no snapshots, and snapshot create/delete operations are reflected in sorted listing results.

## Important APIs, Types, and Functions
The suite uses `MiniDFSCluster`, `DistributedFileSystem`, `FileStatus`, `Path`, `FSNamesystem`, and `GenericTestUtils.assertExceptionContains`. The sole test method is `testListSnapshots`.

## Control Flow
The setup creates `/test.snapshot/dir`. The test first lists `/.snapshot` and expects an empty result because root has zero snapshot quota by default. It then attempts to list `<dir>/.snapshot` before `allowSnapshot` and expects a `SnapshotException` surfaced as `IOException`. After enabling snapshots, it checks the empty listing, creates five snapshots `s_0` through `s_4`, verifying the listing length and names after each creation, then deletes snapshots in reverse order and verifies the listing shrinks while retaining the remaining names. Finally it deletes the last snapshot and expects an empty listing.

## State and Persistence Behavior
This file does not restart the NameNode. State is the in-memory and namespace-backed snapshot list of a single snapshottable directory. The expected order is stable by snapshot name/creation sequence used by the directory listing API.

## Dependencies and Integration Points
It integrates filesystem path resolution of the reserved `.snapshot` component with snapshot manager state and `FileSystem#listStatus` behavior.

## Risks and Edge Cases
Risks covered include exposing `.snapshot` on non-snapshottable directories, incorrectly reporting root snapshots, stale list entries after deletion, and unstable ordering while snapshots are added and removed.

## Test Signals
The test gives direct signals through list length checks, entry-name assertions after each mutation, and the exact non-snapshottable error substring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestSnapshotListing.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestSnapshotManager.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestSnapshotManager.java

## Purpose
`TestSnapshotManager` covers snapshot manager limits and restart handling. It verifies global snapshot ID rollover, configured file-system and per-directory snapshot limits, the relationship between maximum snapshot ID and `Snapshot.CURRENT_STATE_ID`, and replay behavior when the configured limit is lowered after snapshots already exist.

## Important APIs, Types, and Functions
The file uses `SnapshotManager`, `Snapshot`, `SnapshotException`, `FSDirectory`, `INodeDirectory`, `INodesInPath`, `LeaseManager`, `INode.ReclaimContext`, `MiniDFSCluster`, `DistributedFileSystem`, `DFSConfigKeys.DFS_NAMENODE_SNAPSHOT_FILESYSTEM_LIMIT`, and `DFS_NAMENODE_SNAPSHOT_MAX_LIMIT`. Mockito spies/mocks isolate `SnapshotManager#createSnapshot` and `deleteSnapshot`; `LambdaTestUtils.intercept` validates live cluster exceptions.

## Control Flow
`testSnapshotIDLimits` and `testMaxSnapshotLimit` delegate into `testMaxSnapshotLimit`, which constructs a spied `SnapshotManager`, stubs the snapshottable root and max snapshot ID, creates up to the configured limit, then verifies the next create fails with the expected lower-case message. It deletes a snapshot and attempts another create to distinguish count-limit behavior from irreversible ID rollover behavior. `testValidateSnapshotIDWidth` checks the max ID remains below the current-state sentinel. `testSnapshotLimitOnRestart` creates five snapshots, lowers the configured directory limit before restart, verifies all five prior snapshots are replayed, then lowers the file-system limit and checks replay still preserves the existing count while blocking new creation.

## State and Persistence Behavior
The mock-based tests focus on manager counters and max-ID state. The restart test validates edit-log replay under stricter new limits: existing snapshots are preserved even when current configuration would no longer allow that many, but future creation is denied.

## Dependencies and Integration Points
The class straddles internal unit-style manager tests and live NameNode integration. It depends on FSDirectory image-loaded checks, lease manager handoff during snapshot creation, and cluster restart propagation of NameNode configuration into the snapshot manager.

## Risks and Edge Cases
The major risk is confusing reusable snapshot quota slots with non-reusable snapshot ID space. A deleted snapshot may free a configured count slot but cannot roll back max ID allocation. Another risk is restart rejecting or truncating existing snapshots after an operator lowers limits.

## Test Signals
Signals include expected `SnapshotException` message substrings, `getMaxSnapshotID() < CURRENT_STATE_ID`, preserved `getNumSnapshots()` after restart, and updated `getMaxSnapshotLimit()` values after configuration changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestSnapshotManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestSnapshotMetrics.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestSnapshotMetrics.java

## Purpose
`TestSnapshotMetrics` verifies metrics emitted for snapshot operations and snapshot state. It checks FSNamesystem gauges for counts and NameNodeActivity counters for operation calls across allow, disallow, list, create, delete, rename, and diff report operations.

## Important APIs, Types, and Functions
The suite uses `MetricsAsserts.getMetrics`, `assertGauge`, `assertCounter`, `MiniDFSCluster`, `DistributedFileSystem`, `DFSTestUtil`, and `SnapshottableDirectoryStatus`. It reads metrics records named `NameNodeActivity` and `FSNamesystem`.

## Control Flow
`setUp` creates two files under `/TestSnapshot/sub1`. `testSnapshottableDirs` enables nested snapshots, checks zero metrics, allows snapshots on multiple directories, confirms gauges and counters, repeats `allowSnapshot` on an existing snapshottable directory to verify the operation counter increments while the gauge does not, disallows/deletes snapshottable directories, and verifies listing increments `ListSnapshottableDirOps`. `testSnapshots` checks create snapshot metrics, including a failed create attempt on a non-snapshottable directory that still increments the operation counter, then validates snapshot gauge changes for create/delete and operation counters for diff and rename.

## State and Persistence Behavior
Metrics are in-process runtime state in the `MiniDFSCluster`. The tests do not restart or persist metrics, but they tie gauges to namespace state and counters to attempted operations.

## Dependencies and Integration Points
This file integrates snapshot APIs with Hadoop metrics2 exposure. It also depends on nested snapshot allowance in `SnapshotManager` to create nested snapshottable directories for metric coverage.

## Risks and Edge Cases
The suite covers a common metrics ambiguity: counters should track attempted operations, including failures or idempotent calls, while gauges should track actual current namespace state. It also verifies delete of a snapshottable subtree decrements the snapshottable directory gauge.

## Test Signals
Signals are exact metric values after each operation sequence and an assertion that `getSnapshottableDirListing` returns the expected single surviving directory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestSnapshotMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestSnapshotNameWithInvalidCharacters.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestSnapshotNameWithInvalidCharacters.java

## Purpose
`TestSnapshotNameWithInvalidCharacters` exercises snapshot creation attempts with invalid snapshot names containing colon-separated and slash-separated path components. It is intended to verify that invalid names are rejected by the NameNode rather than creating malformed snapshot paths.

## Important APIs, Types, and Functions
The test uses `MiniDFSCluster`, `DistributedFileSystem`, `DFSTestUtil.createFile`, `allowSnapshot`, and `createSnapshot`. It catches `RemoteException` from the RPC layer.

## Control Flow
Each test starts a one-DataNode cluster, creates `/file1`, allows snapshots on root `/`, and attempts to create a snapshot named either `a:b:c` or `a/b/c`. The exception is caught and ignored.

## State and Persistence Behavior
No persistence or restart behavior is tested. State is limited to a fresh cluster per test and root being made snapshottable.

## Dependencies and Integration Points
The relevant integration point is the snapshot name validation path from `DistributedFileSystem#createSnapshot` through NameNode RPC validation and remote exception wrapping.

## Risks and Edge Cases
The intended edge cases are invalid characters in snapshot names. A notable test-quality risk is that the catch blocks do not assert an exception was thrown, so a regression that allows these names might pass silently. The tests also do not inspect the exception message.

## Test Signals
The current signal is weak: absence of uncaught failures. Stronger future checks would assert `RemoteException` with a specific validation message and verify no snapshot was created.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestSnapshotNameWithInvalidCharacters.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestSnapshotRename.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestSnapshotRename.java

## Purpose
`TestSnapshotRename` verifies snapshot rename behavior and interactions with snapshot lists, snapshot file status, invalid names, shell argument validation, and quota accounting for file renames in or around snapshotted directories.

## Important APIs, Types, and Functions
Important APIs include `DistributedFileSystem.renameSnapshot`, `SnapshotTestHelper.createSnapshot/getSnapshotRoot`, `FsShell -renameSnapshot`, `FSDirectory`, `INodeDirectory`, `DirectoryWithSnapshotFeature.DirectoryDiff`, `DiffList`, `ReadOnlyList`, `NSQuotaExceededException`, `SnapshotException`, `RemoteException`, and `LambdaTestUtils.intercept`. `checkSnapshotList` inspects internal snapshot lists sorted by name and directory diffs ordered by creation time.

## Control Flow
Snapshot list tests create three snapshots and rename them to values that change lexical order, asserting both sorted-name and time-order lists. File status tests compare snapshot file metadata before and after rename, allowing only the path to differ. Exception tests verify renaming non-existing snapshots, renaming to an existing name, reserved `.snapshot` names, slash-containing names, and wrong shell argument counts. Quota tests create snapshotted directories under tight namespace quotas and verify when create/rename operations should fail or still succeed across same-directory, cross-directory, and snapshottable-source scenarios.

## State and Persistence Behavior
The suite does not restart, but it inspects mutable namespace state through FSDirectory internals. Snapshot rename updates visible `.snapshot/<name>` path resolution and metadata while retaining underlying snapshot contents and creation-time diff ordering.

## Dependencies and Integration Points
Coverage integrates NameNode snapshot manager RPCs, FSDirectory internal inode/diff structures, HDFS shell command validation, quota enforcement, and general filesystem rename semantics under snapshot retention.

## Risks and Edge Cases
High-risk areas are maintaining two snapshot orderings, rejecting illegal target names, preserving snapshot file metadata under path rename, and quota calculations where snapshots retain deleted or renamed inodes. The quota tests particularly protect against double-counting or under-counting namespace space during rename operations involving snapshotted parents.

## Test Signals
Signals include exact snapshot list order, `FileStatus` string comparison after path normalization, exception type/message checks, shell return code and output checks, and successful/failed rename behavior under quota pressure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestSnapshotRename.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestSnapshotReplication.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestSnapshotReplication.java

## Purpose
`TestSnapshotReplication` verifies how replication factors are represented for live files, snapshot file inodes, and shared block metadata. It ensures block preferred replication reflects the maximum required replication across live and retained snapshot states.

## Important APIs, Types, and Functions
The suite uses `DistributedFileSystem.setReplication`, `DFSTestUtil.createFile`, `SnapshotTestHelper.createSnapshot`, `FSDirectory.getINode`, `INodeFile`, `BlockInfo`, `INodesInPath`, and `FSDirectory.DirOp.READ`. Helpers are `checkFileReplication`, `getINodeFile`, and `checkSnapshotFileReplication`.

## Control Flow
`testReplicationWithoutSnapshot` creates a normal file and verifies both `FileStatus` replication and block replication change when the live replication factor changes. `testReplicationWithSnapshot` creates a file with replication 1, takes snapshots between incremental replication increases up to the number of DataNodes, records expected snapshot inode replication, and verifies each shared block reports the highest needed replication. It then lowers live replication to 3 and expects block replication to remain at 4 due to prior snapshots. `testReplicationAfterDeletion` snapshots a file three times, deletes the live file, and verifies snapshot inodes and blocks still retain the expected replication.

## State and Persistence Behavior
There is no restart, but the tests inspect snapshot-retained inode state after live metadata changes and live deletion. The key state behavior is shared block metadata preserving enough replication for all snapshot references.

## Dependencies and Integration Points
The file bridges client-level replication APIs and internal NameNode block/inode state. It relies on snapshot inode lookup through snapshot paths and `getPathSnapshotId` to compute per-snapshot file replication.

## Risks and Edge Cases
The risk is lowering live replication incorrectly reducing block replication needed by snapshots, or deleting the live file losing snapshot replication state. Another subtle risk is `checkFileReplication(Path file, ...)` ignores its `file` parameter and always checks `file1`, which is harmless in current tests but weakens helper generality.

## Test Signals
Signals are exact assertions on `FileStatus.getReplication`, `INodeFile.getFileReplication`, `INodeFile.getFileReplication(snapshotId)`, and `BlockInfo.getReplication` across live, snapshot, changed, and deleted states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestSnapshotReplication.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestSnapshotStatsMXBean.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestSnapshotStatsMXBean.java

## Purpose
`TestSnapshotStatsMXBean` verifies that the NameNode JMX/MXBean snapshot information agrees with `SnapshotManager` counts and includes the expected path information for snapshottable directories and snapshots.

## Important APIs, Types, and Functions
The test uses `MiniDFSCluster`, `DistributedFileSystem`, `SnapshotManager`, platform `MBeanServer`, `ObjectName` `Hadoop:service=NameNode,name=SnapshotInfo`, and OpenMBean `CompositeData` arrays exposed as `SnapshottableDirectories` and `Snapshots`.

## Control Flow
The test starts a cluster, creates `/snapshot`, allows snapshots, creates one snapshot, obtains the platform MBean server, reads the two snapshot attributes, compares array lengths with `SnapshotManager#getNumSnapshottableDirs` and `getNumSnapshots`, then inspects the first composite records for path fields containing `/snapshot`.

## State and Persistence Behavior
No restart is involved. The state under test is the live NameNode snapshot manager exposed through JMX at runtime.

## Dependencies and Integration Points
This is an observability integration test between HDFS snapshot namespace state and the NameNode management interface. It relies on the MXBean registration name and composite field names `path` and `snapshotDirectory`.

## Risks and Edge Cases
Risks include stale or unregistered MXBean data, mismatched counts, field-name changes, or paths missing from serialized composite data. The test only creates one directory and one snapshot, so it does not validate multi-entry ordering or multiple records.

## Test Signals
Signals are count equality between JMX arrays and `SnapshotManager`, plus substring checks for expected path content in the first records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestSnapshotStatsMXBean.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestSnapshottableDirListing.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestSnapshottableDirListing.java

## Purpose
`TestSnapshottableDirListing` verifies `getSnapshottableDirListing` results for root, normal directories, nested snapshottable directories, deletion/rename effects, snapshot counts, and user-based filtering.

## Important APIs, Types, and Functions
The file uses `DistributedFileSystem.getSnapshottableDirListing`, `allowSnapshot`, `disallowSnapshot`, `createSnapshot`, `rename` with `Rename.OVERWRITE`, `SnapshottableDirectoryStatus`, `UserGroupInformation`, `DFSTestUtil.getFileSystemAs`, `FsPermission`, and superuser group configuration keys.

## Control Flow
`testListSnapshottableDir` enables nested snapshots, starts with no listing, allows/disallows root, allows `dir1` and `dir2`, verifies status local names/full paths/snapshot counts, overwrites `dir2` to ensure its snapshottable status is removed, re-enables and creates two snapshots on `dir2`, creates nested snapshottable subdirectories under `dir1`, disallows one, and finally deletes `dir1` to ensure descendant snapshottable entries disappear. `testListWithDifferentUser` creates snapshottable directories as user1 and user2, then verifies the superuser sees all six while each normal user sees only owned directories.

## State and Persistence Behavior
The test manipulates live namespace state without restart. It verifies that snapshottable status follows inode lifecycle, not just path strings, and that listing authorization filters reflect owner/superuser state.

## Dependencies and Integration Points
It integrates snapshot manager listing, permission/UGI handling, root permissions, nested snapshot configuration, and rename/delete namespace operations.

## Risks and Edge Cases
Risks include returning null versus empty arrays inconsistently, stale snapshottable entries after overwrite/delete, wrong full paths after mutations, incorrect snapshot counts, and leaking other users' snapshottable directories to non-superusers.

## Test Signals
Signals are exact null/length checks, ordered full-path assertions, snapshot-number assertions, and user-specific visibility counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestSnapshottableDirListing.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestUpdatePipelineWithSnapshots.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestUpdatePipelineWithSnapshots.java

## Purpose
`TestUpdatePipelineWithSnapshots` is a regression test for HDFS-6647. It verifies that edit logs containing a delete of a live file retained by a snapshot and a later failed pipeline update for the same block do not prevent NameNode restart.

## Important APIs, Types, and Functions
The test uses `MiniDFSCluster`, `FileSystem`, `DistributedFileSystem`, `DFSOutputStream`, `FSDataInputStream`, `NamenodeProtocols.updateBlockForPipeline`, `updatePipeline`, `ExtendedBlock`, `LocatedBlock`, `DFSTestUtil.getAllBlocks`, `SnapshotTestHelper.createSnapshot`, and `GenericTestUtils.assertExceptionContains`.

## Control Flow
The test creates `/test-file`, writes and flushes one byte to allocate a block, snapshots root, reads the old block ID, calls `updateBlockForPipeline` to allocate a new generation stamp, deletes the live file while it remains in the snapshot, then calls `updatePipeline` to simulate recovery. The update is expected to throw because the file is no longer under construction. Finally the cluster restarts the NameNode from the resulting edit logs.

## State and Persistence Behavior
The core persistence signal is successful NameNode restart after a sequence of snapshot retention, delete logging, and attempted block update logging. It protects edit-log replay around deleted-under-current but retained-in-snapshot files.

## Dependencies and Integration Points
This integrates HDFS client output streams, NameNode block recovery RPCs, snapshot retention of deleted files, edit logging, and NameNode restart/replay.

## Risks and Edge Cases
The risk is edit-log replay or pipeline update code confusing the deleted live inode with the snapshot-retained inode. Another risk is generating `OP_UPDATE_BLOCKS` or related state for an inode that should not accept it.

## Test Signals
Signals are the expected exception message during simulated pipeline recovery and, more importantly, `cluster.restartNameNode(true)` completing without replay failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestUpdatePipelineWithSnapshots.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestXAttrWithSnapshot.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestXAttrWithSnapshot.java

## Purpose
`TestXAttrWithSnapshot` verifies extended attribute behavior for snapshot roots and snapshot paths. It ensures snapshots preserve xattr point-in-time values, live changes read current state, snapshot paths are read-only for xattr mutation, xattrs survive edit-log and checkpoint restarts, and shell copy with `-px` preserves snapshot xattrs.

## Important APIs, Types, and Functions
The file uses `DistributedFileSystem.setXAttr/getXAttrs/removeXAttr`, `XAttrSetFlag`, `SnapshotTestHelper.createSnapshot`, `SnapshotAccessControlException`, `SnapshotDiffReport`, `SafeModeAction`, `NameNodeAdapter.saveNamespace`, `FsShell`, `ToolRunner`, and `DFS_NAMENODE_XATTRS_ENABLED_KEY`. Shared helpers include `doSnapshotRootChangeAssertions`, `doSnapshotRootRemovalAssertions`, `initCluster`, and `restart`.

## Control Flow
The class starts one static cluster with xattrs enabled and allocates a unique `/pN` path per test. It tests xattrs added after snapshot creation do not appear in the earlier snapshot, modified/removed live xattrs do not mutate captured snapshot values, restart with and without checkpoint preserves divergent live/snapshot xattr state, successive snapshots capture each version independently and deleting one snapshot does not corrupt others, snapshot paths reject `setXAttr` and `removeXAttr`, and `FsShell -cp -px` copies snapshot xattrs to a new live path.

## State and Persistence Behavior
This suite strongly covers persisted namespace state. `restart(false)` replays edits, while `restart(true)` saves namespace before cluster restart. `testXattrWithSnapshotAndNNRestart` explicitly enters safe mode, saves namespace, restarts, and verifies snapshot diff remains empty after xattrs set before snapshot creation.

## Dependencies and Integration Points
It integrates xattr storage, snapshot copy-on-write metadata, snapshot diff calculation, safe-mode namespace save, NameNode restart, snapshot access control, and shell copy preservation flags.

## Risks and Edge Cases
Risks include xattr changes accidentally modifying snapshot roots, snapshot xattrs not surviving fsimage/edit replay, read-only snapshot path mutation being allowed, deleted snapshots corrupting retained xattr diffs, and shell copy ignoring xattrs. Because the cluster is static, test isolation depends on unique path names and proper cluster reinitialization after restarts.

## Test Signals
Signals are exact xattr map sizes and byte-array values, expected `SnapshotAccessControlException`, empty snapshot diff assertions, successful shell return code, and repeated assertions after both edit-log and checkpoint restarts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestXAttrWithSnapshot.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/sps/TestBlockStorageMovementAttemptedItems.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/sps/TestBlockStorageMovementAttemptedItems.java

## Purpose
`TestBlockStorageMovementAttemptedItems` verifies the SPS attempted-items monitor that tracks block storage movement attempts, DataNode reports, and retry scheduling for partial or timed-out movements.

## Important APIs, Types, and Functions
The test uses `BlockStorageMovementAttemptedItems`, `BlockStorageMovementNeeded`, `StoragePolicySatisfier`, `ExternalSPSContext`, `ItemInfo`, `Block`, `DatanodeInfo`, `StorageType`, and `StoragePolicySatisfier.StorageTypeNodePair`. Mockito stubs the `Context` as running, not in safe mode, and with files existing. `checkItemMovedForRetry` polls the needed queue until an item is requeued.

## Control Flow
Setup constructs a real `StoragePolicySatisfier` and attempted/needed queues around a mocked external context. Tests add attempted block maps, optionally notify finished movement reports, and then check finished-report queue counts, attempted item counts, or retry movement into `BlockStorageMovementNeeded`. One test starts the monitor thread so reported and unreported checks run asynchronously; another invokes `blocksStorageMovementUnReportedItemsCheck` and `blockStorageMovementReportedItemsCheck` manually after timeout ordering; the final test verifies a reported block alone does not requeue when the attempted queue is not processed.

## State and Persistence Behavior
The state is in-memory queue/monitor state: attempted item lists, movement finished block reports, and retry queue entries. There is no disk persistence.

## Dependencies and Integration Points
This tests SPS internal coordination between attempted movement tracking and the needed queue that schedules future work. It depends on monotonic time, self-retry timeouts, and DataNode/storage-type matching.

## Risks and Edge Cases
Risks include partial movement being treated as complete, reports being dropped, items never requeued after timeout, race/order differences between reported-check and unreported-check paths, and monitor threads leaking across tests. Teardown stops the monitor both normally and gracefully.

## Test Signals
Signals are movement finished block counts, attempted item counts, and successful/unsuccessful polling for a requeued `ItemInfo` in `BlockStorageMovementNeeded`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/sps/TestBlockStorageMovementAttemptedItems.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/sps/TestStoragePolicySatisfierWithStripedFile.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/sps/TestStoragePolicySatisfierWithStripedFile.java

## Purpose
`TestStoragePolicySatisfierWithStripedFile` is a slow integration suite for external Storage Policy Satisfier behavior on erasure-coded striped files. It verifies block movement from `DISK` to `ARCHIVE` for full stripes, partial target availability, low-redundancy restart scenarios, and no-target scenarios.

## Important APIs, Types, and Functions
The file uses `MiniDFSCluster` with multi-storage DataNodes, `StoragePolicySatisfier`, `ExternalSPSContext`, `NameNodeConnector`, `HdfsAdmin.satisfyStoragePolicy`, `ClientProtocol`, `ErasureCodingPolicy`, `StripedFileTestUtil`, `LocatedBlocks`, `LocatedBlock`, `StorageType`, and storage policy constants such as `HOT` and `COLD`. Helpers are `startSPS`, `initConfWithStripe`, `waitExpectedStorageType`, and `waitForAttemptedItems`.

## Control Flow
`init` configures external SPS mode, short DataNode cache refresh, high retry attempts, and a stripe block size based on default EC policy. The full-stripe test starts DataNodes with enough ARCHIVE targets, writes an EC file under a HOT policy, starts additional archive-only DataNodes, switches to COLD, calls `satisfyStoragePolicy`, and waits until all data/parity blocks report ARCHIVE storage. Partial-target tests use limited ARCHIVE availability, expect some attempted items to remain, and verify only reachable blocks move. The low-redundancy test stops all DataNodes, restarts the NameNode and only part of the DataNodes, starts movement, then restarts the rest and waits for full placement. The no-target test keeps only DISK storage and verifies SPS attempts but block storage remains DISK.

## State and Persistence Behavior
State includes NameNode storage policy xattrs, EC block groups, DataNode storage reports, SPS queues, attempted item monitor state, and cluster restart state in the low-redundancy case. It does not persist across full cluster shutdown beyond the test scenario restart.

## Dependencies and Integration Points
This is broad HDFS integration: EC file creation, block placement, DataNode storage types/capacities, heartbeats, external SPS service startup, NameNodeConnector mover identity, and HdfsAdmin/client protocol operations.

## Risks and Edge Cases
Risks include SPS choosing an invalid target for striped parity/data blocks, local movement not being preferred when an existing DataNode has the target storage type, low-redundancy files stalling movement until DataNodes return, no-target loops, and asynchronous heartbeat/cache timing flakiness. The tests use polling with timeouts and explicit heartbeat triggers.

## Test Signals
Signals include initial `LocatedBlocks` storage-type assertions, `StripedFileTestUtil.verifyLocatedStripedBlocks`, exact expected ARCHIVE/DISK counts, expected block-location counts, and attempted item count waits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/sps/TestStoragePolicySatisfierWithStripedFile.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/startupprogress/StartupProgressTestHelper.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/startupprogress/StartupProgressTestHelper.java

## Purpose
`StartupProgressTestHelper` provides shared helper methods for startup progress tests. It creates repeatable running and final progress states and supplies a counter increment helper.

## Important APIs, Types, and Functions
The helper uses `StartupProgress`, `StartupProgress.Counter`, `Phase`, `Step`, and `StepType` constants. Public methods are `incrementCounter`, `setStartupProgressForRunningState`, and `setStartupProgressForFinalState`.

## Control Flow
`incrementCounter` obtains the counter for a phase/step and calls `increment` `delta` times. `setStartupProgressForRunningState` completes `LOADING_FSIMAGE` with an `INODES` step at 100/100, then starts `LOADING_EDITS` for a file step with total 200 and count 100, leaving that phase running. `setStartupProgressForFinalState` completes all four startup phases: loading fsimage, loading edits, saving checkpoint, and safemode, each with a deterministic count/total.

## State and Persistence Behavior
The helper mutates only in-memory `StartupProgress` state. There is no external persistence.

## Dependencies and Integration Points
It is used by `TestStartupProgress` and `TestStartupProgressMetrics` to avoid duplicating long setup sequences and to keep expected counts/percentages consistent.

## Risks and Edge Cases
Because it increments counters one by one, large deltas can be slower than direct setting, but current deltas are small. The helper encodes expected phase totals that metrics tests depend on, so changes here affect percentage expectations.

## Test Signals
The helper itself has no assertions. Its signal is indirect through tests that consume the generated running/final states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/startupprogress/StartupProgressTestHelper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/startupprogress/TestStartupProgress.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/startupprogress/TestStartupProgress.java

## Purpose
`TestStartupProgress` is the core unit test suite for the NameNode startup progress model. It verifies counters, elapsed time, immutable views, completion freezing, initial/default values, percent completion calculations, statuses, step ordering, thread safety, and total handling after phase completion.

## Important APIs, Types, and Functions
The test uses `StartupProgress`, `StartupProgressView`, `StartupProgress.Counter`, `Phase`, `Status`, `Step`, `StepType`, and `StartupProgressTestHelper.incrementCounter`. It also uses Java concurrency types `ExecutorService`, `Callable`, and `TimeUnit` for thread-safety coverage.

## Control Flow
Each test creates a fresh `StartupProgress`. Counter and total tests begin phases/steps, set totals, increment counters, end phases, and assert values through `createView`. Elapsed-time tests sleep briefly to distinguish running and completed durations. `testFrozenAfterStartupCompletes` mutates completed phases and then all phases, asserting views remain unchanged once startup is complete. `testInitialState` checks all phases are pending and empty. `testPercentComplete` calculates expected weighted percentages before and after ending phases. `testStepSequence` shuffles steps and verifies sorted view order. `testThreadSafety` launches 100 concurrent mutations across two phases/two steps and checks no lost increments or corrupted file/size/total values.

## State and Persistence Behavior
All state is in-memory progress tracking. A central behavior is that `StartupProgressView` is a snapshot and must not change after creation, while completed phases and completed startup become immutable against later writes.

## Dependencies and Integration Points
This is mostly a unit suite for the startup progress package. Its downstream integration point is metrics and UI/status consumers that depend on stable views, sorted steps, status transitions, and percentage calculations.

## Risks and Edge Cases
Risks include views sharing mutable state, running elapsed times failing to advance, completed phase updates leaking in, division/weighting mistakes in percent complete, nondeterministic step ordering, and race conditions in counters. The concurrency test protects against lost increments but intentionally avoids ending phases until after concurrent operations because ending phases freezes step mutations.

## Test Signals
Signals are exact counts, totals, file and size values, elapsed time comparisons, percentage tolerances, status values, array order assertions, and aggregate counter expectations after concurrent updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/startupprogress/TestStartupProgress.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/startupprogress/TestStartupProgressMetrics.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/startupprogress/TestStartupProgressMetrics.java

## Purpose
`TestStartupProgressMetrics` verifies the Hadoop metrics projection of `StartupProgress` in initial, running, and final states.

## Important APIs, Types, and Functions
The suite uses `StartupProgress`, `StartupProgressMetrics`, `StartupProgressTestHelper.setStartupProgressForRunningState`, `setStartupProgressForFinalState`, and `MetricsAsserts` helpers including `mockMetricsSystem`, `getMetrics`, `assertCounter`, `assertGauge`, and `getLongCounter`.

## Control Flow
Setup initializes a mocked metrics system, a fresh `StartupProgress`, and a `StartupProgressMetrics` wrapper. `testInitialState` reads metrics and asserts all elapsed/count/total counters and percent gauges are zero. `testRunningState` applies the helper running state and verifies overall percent complete is 0.375, fsimage is complete, edits is half complete, and remaining phases are zero. `testFinalState` applies the helper final state and verifies overall and per-phase percent complete are 1.0 with expected counts and totals.

## State and Persistence Behavior
State is in-memory metrics sampling from the current progress view. There is no persistence or cluster interaction.

## Dependencies and Integration Points
The file integrates the startup progress model with Hadoop metrics2 naming. Metric names such as `LoadingFsImageCount`, `LoadingEditsPercentComplete`, and `SafeModeTotal` are part of the observable contract under test.

## Risks and Edge Cases
Risks include incorrect metric names, counters/gauges swapped, stale sampling, and percentage calculation drift between `StartupProgressView` and metrics serialization. The tests allow elapsed-time counters to be nonnegative rather than exact because timing is runtime-dependent.

## Test Signals
Signals are exact metric counter/gauge assertions for deterministic values and nonnegative elapsed-time checks for active/completed phases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/startupprogress/TestStartupProgressMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/top/window/TestRollingWindow.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/top/window/TestRollingWindow.java

## Purpose
`TestRollingWindow` verifies the basic bucketed rolling-sum behavior used by NameNode top metrics. It checks initial sums, recent updates, expiration as time advances, and out-of-order updates.

## Important APIs, Types, and Functions
The file tests `RollingWindow` through `incAt(time, delta)` and `getSum(time)`. Constants define a 60 second window, 10 buckets, and a 6 second bucket length.

## Control Flow
`testBasics` starts with empty sums at early and far-forward times, records value 5, records value 6 one bucket later, then advances near and beyond the window to confirm old buckets expire. `testReorderedAccess` records a current value, then records an event two buckets in the past and verifies it contributes to the current window until it ages out.

## State and Persistence Behavior
State is in-memory bucket values keyed by time bucket. There is no persistence.

## Dependencies and Integration Points
This is a unit test for the lower-level window used by `RollingWindowManager` and NameNode top user/operation statistics.

## Risks and Edge Cases
Risks include off-by-one bucket expiry, incorrect handling of time jumps, and dropping reordered events that still fall within the active window.

## Test Signals
Signals are exact rolling sums after each increment and time advance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/top/window/TestRollingWindow.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/top/window/TestRollingWindowManager.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/top/window/TestRollingWindowManager.java

## Purpose
`TestRollingWindowManager` verifies aggregation of per-user per-operation rolling windows into top-user snapshots for NameNode top metrics. It covers top-N selection, aggregate `ALL_CMDS`, window reset, totals across operations, fuzzed consistency, and aggregate top-user composition.

## Important APIs, Types, and Functions
The file uses `RollingWindowManager`, nested `TopWindow`, `Op`, and `User` types, `TopConf.ALL_CMDS`, and configuration keys `NNTOP_BUCKETS_PER_WINDOW_KEY` and `NNTOP_NUM_USERS_KEY`. Helpers are `checkValues` and `checkTotal`.

## Control Flow
Setup creates a manager with one-minute windows, ten buckets, ten top users, and twenty generated users. `testTops` records `open` and `close` counts for all users, snapshots top users, verifies top-N ordering and totals, then advances the window so `open` expires. `windowReset` checks a one-bucket window resets at the period boundary. `testTotal` interleaves operations and verifies per-op and aggregate totals as buckets reset independently. `testWithFuzzing` records 10,000 random events and repeatedly checks aggregate consistency. `testOpTotal` verifies the aggregate op includes top users from each individual operation.

## State and Persistence Behavior
State is in-memory rolling windows per operation/user. No disk persistence is involved.

## Dependencies and Integration Points
This manager feeds NameNode top metrics consumers. It depends on correct lower-level `RollingWindow` behavior and configuration-driven bucket/top-N sizing.

## Risks and Edge Cases
Risks include aggregate totals diverging from per-op totals, top-N truncation losing users in `ALL_CMDS`, bucket reset errors at exact boundaries, and nondeterministic behavior under varied operations/users. The fuzz test guards invariants across random sequences.

## Test Signals
Signals include exact operation counts, top-user list sizes and values, aggregate total equality, all-op/per-op user tally cancellation in `checkTotal`, and random-run invariant checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/top/window/TestRollingWindowManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/web/resources/TestWebHdfsCreatePermissions.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/web/resources/TestWebHdfsCreatePermissions.java

## Purpose
`TestWebHdfsCreatePermissions` verifies that WebHDFS create and mkdir operations apply the same default and explicit permissions expected from normal HDFS creation paths.

## Important APIs, Types, and Functions
The test uses `WebHdfsTestUtil.createConf`, `MiniDFSCluster.getHttpUri`, raw `HttpURLConnection`, `NamenodeProtocols.getFileInfo`, and `FsPermission`. The shared helper `testPermissions` constructs a `/webhdfs/v1` URL with `user.name`, operation, and optional `permission` parameter, sends a PUT, then reads the resulting permission through the NameNode RPC server.

## Control Flow
Each test starts a cluster, invokes `testPermissions`, and the helper shuts the cluster down in its finally block. The cases are MKDIRS with no permission expecting `rwxr-xr-x`, MKDIRS with `permission=777`, CREATE with no permission expecting `rw-r--r--`, and CREATE with `permission=666`.

## State and Persistence Behavior
State is the live HDFS namespace permission bits after WebHDFS requests. There is no restart or persistence validation.

## Dependencies and Integration Points
This file integrates the WebHDFS HTTP layer, query parameter parsing, NameNode create/mkdir implementation, and RPC metadata reads.

## Risks and Edge Cases
Risks include WebHDFS ignoring explicit permission parameters, applying directory defaults to files or vice versa, or returning HTTP success while creating metadata with wrong permission bits. A structural risk is that `testPermissions` shuts down the cluster even though `tearDown` also does, which is tolerated by the null check but unusual.

## Test Signals
Signals are HTTP status codes `200 OK` or `201 Created` and exact symbolic permission strings read back from the NameNode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/web/resources/TestWebHdfsCreatePermissions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/web/resources/TestWebHdfsDataLocality.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/web/resources/TestWebHdfsDataLocality.java

## Purpose
`TestWebHdfsDataLocality` verifies WebHDFS DataNode selection for HTTP redirects. It ensures create operations prefer a local DataNode, read/checksum/append operations choose a block replica, excluded DataNodes are avoided, invalid exclusions are harmless, and a not-yet-initialized NameNode fails with a clear error.

## Important APIs, Types, and Functions
The file uses `NamenodeWebHdfsMethods.chooseDatanode`, `MiniDFSCluster` with racks/hosts, `DistributedFileSystem`, `DatanodeManager`, `NameNodeAdapter.getBlockLocations`, `LocatedBlocks`, `LocatedBlock`, `HdfsFileStatus`, `PutOpParam.Op.CREATE`, `GetOpParam.Op.GETFILECHECKSUM/OPEN`, `PostOpParam.Op.APPEND`, and Mockito for an uninitialized `NameNode`.

## Control Flow
`testDataLocality` starts six DataNodes across three racks, verifies CREATE chooses the DataNode matching the client address, creates a one-replica file, finds its block location, and asserts GETFILECHECKSUM, OPEN, and APPEND choose that replica. `testExcludeDataNodes` creates a three-replica file with named hosts, builds an exclusion string from one then two replica transfer addresses, and checks each read-like operation avoids excluded hosts. `testExcludeWrongDataNode` excludes a non-existent host and expects no failure. `testChooseDatanodeBeforeNamesystemInit` uses a mocked NameNode with null namesystem and expects `IOException`.

## State and Persistence Behavior
State is live cluster block placement and DataNode topology. There is no persistence or restart behavior.

## Dependencies and Integration Points
This is a WebHDFS/NameNode placement integration test covering network topology, block manager DataNode lookup, file status lookup, operation-specific redirect logic, and exclusion parsing.

## Risks and Edge Cases
Risks include redirecting clients away from local or replica DataNodes, ignoring exclude lists and causing retry loops, failing when exclusions reference unknown hosts, and null-pointer failures before namesystem initialization. The first CREATE loop computes each DataNode IP but passes loopback as client host, so it depends on MiniDFSCluster/DataNodeManager local-address behavior.

## Test Signals
Signals are equality with expected DataNode IP or replica `DatanodeInfo`, inequality against excluded hosts, absence of failure for unknown exclusions, and a specific initialization error substring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/web/resources/TestWebHdfsDataLocality.java -->
