# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/snapshot/DirectoryWithSnapshotFeature.java

## Purpose

`DirectoryWithSnapshotFeature` stores and applies directory snapshot diffs for any directory participating in snapshots. It records child create/delete/modify deltas, reconstructs historical child lists, manages snapshot cleanup and block reclamation for directory subtrees, and computes directory-level changes between snapshots.

## Important APIs, Types, And Functions

`ChildrenDiff` extends `Diff<byte[], INode>` for child-list changes and adds FSImage serialization helpers, created/deleted destruction, and replacement/removal utilities. `DirectoryDiff` extends `AbstractINodeDiff` and stores `childrenSize`, a `ChildrenDiff`, and `isSnapshotRoot`. `DirectoryDiffList` extends `AbstractINodeDiffList` and creates directory diffs/snapshot copies. Top-level APIs include `addChild`, `removeChild`, `getChildrenList`, `getChild`, `saveChild2Snapshot`, `clear`, quota/content summary methods, `computeDiffBetweenSnapshots`, `cleanDirectory`, `destroyDstSubtree`, and `cleanDeletedINode`.

## Control Flow

Mutations call `diffs.checkAndAddLatestSnapshotDiff` for the latest snapshot ID, update the `ChildrenDiff`, then apply the live children-list change with undo if the live operation fails. Historical reads find the diff for a snapshot and combine posterior diffs from that point to current state, reverse-applying them to current children. Snapshot deletion updates the prior snapshot, deletes the target diff, cleans recursive subtrees, destroys nodes created only in removed intervals, and handles renamed/reference nodes through specialized cleanup paths.

## State And Persistence Behavior

The durable state is the chronological `DirectoryDiffList`; each diff records child count, optional directory attribute copy or snapshot root, and created/deleted child lists. Created list entries persist by local name, while deleted list entries persist full inode data or references. Cleanup mutates diff lists and records quota/block reclamation in `INode.ReclaimContext`. ACL references attached to snapshot copies are released during destruction.

## Dependencies And Integration Points

The class depends on `AbstractINodeDiffList`, `Diff`, `INodeDirectory`, `INodeFile`, `INodeReference`, quota/content-summary infrastructure, ACL storage, `SnapshotFSImageFormat.ReferenceMap`, and `SnapshotManager.isDeletionOrdered`. It is used by `INodeDirectory` mutation paths, snapshot diff reports, FSImage save/load, rename handling, and block/quota reclamation.

## Risks And Edge Cases

Cleanup is lifecycle-sensitive: created nodes, deleted nodes, renamed reference nodes, and posterior diffs must be combined or destroyed exactly once. Ordered deletion forbids posterior combination in `DirectoryDiff.combinePosteriorAndCollectBlocks`. Historical child reconstruction assumes diff lists are sorted and `ChildrenDiff` operations are correct. Quota deltas are computed from before/after reclaim context counts and must be added for quota-bearing directories. Many methods depend on caller-held NameNode/FSDirectory locks.

## Test Signals

Strong tests include creating/removing children across multiple snapshots, reconstructing child lists for each snapshot, deleting current directories with snapshots, deleting snapshots with prior/posterior diffs, rename scenarios with `WithName`/`DstReference`, quota and content summary updates, ACL release behavior, and comparing skip-list versus array-list diff reconstruction.
