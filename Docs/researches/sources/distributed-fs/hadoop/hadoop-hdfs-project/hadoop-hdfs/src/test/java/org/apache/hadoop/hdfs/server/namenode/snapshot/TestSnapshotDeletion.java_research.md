# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/snapshot/TestSnapshotDeletion.java

## Purpose

`TestSnapshotDeletion` is the broad regression suite for deleting snapshots and snapshot-protected current namespace entries. It validates deletion refusal rules, edit-log replay, quota accounting, block cleanup, diff-list combination, permission-disabled deletion, HA restart, fsimage corruption regressions, rename/delete cleanup, concat interactions, and snapshot diff reports after concat.

## Important APIs, types, and helpers

- Public APIs under test: `delete`, `deleteSnapshot`, `createSnapshot`, `allowSnapshot`, `setQuota`, `setReplication`, `setOwner`, `rename`, `concat`, `getSnapshotDiffReport`, `saveNamespace`, and `FsShell -deleteSnapshot`.
- Internal APIs: `FSDirectory`, `INodeDirectory`, `INodeFile`, `DirectoryDiffList`, `QuotaCounts`, `BlockInfo`, `BlockManager`, `BlockManagerTestUtil`, and inode-map lookups by ID.
- Helpers: `getDir`, `checkQuotaUsageComputation`, `SnapshotTestHelper.createSnapshot`, `getSnapshotPath`, and `TestSnapshotBlocksMap.assertBlockCollection`.
- HA/persistence tools: `MiniDFSNNTopology.simpleHATopology`, `HATestUtil.configureFailoverFs`, `NameNodeAdapter.abortEditLogs`, `rollEditLog`, safe mode, and namespace save/restart.

## Control flow

The fixture starts a formatted three-datanode cluster and records namespace and block manager handles. Many tests create `/TestSnapshot/sub1/subsub1` as the base tree.

Deletion guard tests assert that deleting a snapshottable directory with snapshots, or an ancestor of a snapshottable descendant with snapshots, fails with a clear `RemoteException`. `testApplyEditLogForDeletion` verifies that deleting snapshottable directories without snapshots updates the snapshot manager list after edit-log replay and after fsimage save/load.

`testDeleteCurrentFileDirectory` is the largest current-tree deletion scenario. It deletes normal files/directories before snapshots, deletes created-after-snapshot content, creates multiple snapshots, changes replication, deletes subtrees, then verifies quota, block invalidation, snapshot subtree shape, parent pointers, child lists for different snapshot IDs, and file replication in snapshot copies.

Earliest snapshot deletion tests cover deleting nonexistent snapshots, deleting and recreating snapshot names, preserving later snapshot file status, combining the first directory and file diffs, cleaning deleted-file blocks, and removing obsolete diffs while keeping no-change nodes in the current tree.

Diff-combination tests create sequences where files are deleted, recreated, modified, or created between snapshots `s1`, `s2`, and `s3`. Deleting middle snapshots must merge or destroy entries correctly, preserve status in older snapshots, drop created-after-prior files, and update quota/storage-space counts. Variants place modifications at the root of the snapshot and deeper in the subtree.

Later tests cover directory metadata diffs, deleting snapshots when permissions are disabled via a different user, renaming a snapshot diff to its previous snapshot under nested snapshots, illegal `FsShell -deleteSnapshot` arguments, HA NameNode restart after `OP_DELETE_SNAPSHOT`, zero-block totals after restart, HDFS-9697 fsimage corruption, moving a snapshot-protected file outside the snapshottable tree and deleting it, and concat behavior.

Concat tests assert that concat fails when a source is in a snapshot, that repeated concat plus snapshot deletion survives save/restart, and that snapshot diff reports show a single `MODIFY` entry on the concat destination.

## State and persistence behavior

This file repeatedly checks three state planes:

- Namespace state: current inodes, snapshot copies, directory diff lists, metadata copies, parent/child relationships, and inode-map cleanup.
- Quota and block state: namespace/storage-space counts from both stored quota features and recomputation, block collection invalidation, block totals after restart, and marked-delete queue draining.
- Persistence state: edit-log replay after deletion, fsimage save/load, HA active restart after aborted edit logs, and fsimage corruption regressions.

`checkQuotaUsageComputation` is central: it compares stored `DirectoryWithQuotaFeature` usage with freshly computed quota usage and emits dump-tree context on mismatch.

## Dependencies and integration points

The suite integrates snapshot deletion with NameNode snapshot manager lists, directory/file diff algorithms, block manager cleanup, quota accounting, command-line `FsShell`, permissions, HA failover plumbing, concat semantics, snapshot diff reports, and fsimage/edit-log persistence.

## Risks and maintenance notes

- Many tests assert exact quota numbers and diff-list sizes. These are strong regression signals but can be brittle during internal accounting refactors.
- Some tests rely on exact exception message fragments and shell output text.
- HA and restart tests are slow and can expose timing sensitivity; one test waits for asynchronous block deletion.
- The concat scenarios use randomized file seeds and repeated recreate/concat cycles to stress diff state.
- Permission-disabled deletion uses `UserGroupInformation.doAs` and expects no authorization failure when permissions are globally disabled.

## Test signals

High-value signals include deletion refusal messages, snapshot manager counts after restart, quota stored-vs-computed equality, block collection IDs becoming invalid only when safe, snapshot path presence/absence, metadata owner/group and replication values in snapshots, diff-list snapshot IDs, inode-map cleanup after rename/delete, zero total blocks after restart, successful fsimage save/restart, shell argument errors, HA restart completion, and concat diff-report contents.
