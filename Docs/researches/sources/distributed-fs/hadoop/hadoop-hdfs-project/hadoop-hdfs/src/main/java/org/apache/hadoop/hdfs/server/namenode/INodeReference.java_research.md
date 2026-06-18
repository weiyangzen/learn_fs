<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INodeReference.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INodeReference.java

## Purpose

`INodeReference` implements the reference objects that let one inode have multiple access paths after snapshot-aware renames. It preserves historical source names and destination paths while ensuring the underlying file or directory is reclaimed only when all snapshot and current references are gone.

## Important APIs and Types

The abstract base delegates most inode operations to `referred`. Static helpers remove references and compute the prior snapshot for cleanup. `WithCount` owns the real referred inode and tracks all `WithName` references plus the optional current-parent `DstReference`. `WithName` stores an immutable historical name and `lastSnapshotId`. `DstReference` stores `dstSnapshotId`, the latest destination snapshot before rename.

## Control Flow, State, and Persistence

A rename involving snapshots creates a `WithCount`, one or more source-side `WithName` references, and a destination-side `DstReference`. Quota/content-summary calls on `WithName` compute against the snapshot timeline rather than current cached quota. Cleanup has careful branches: `WithName.cleanSubtree` may restore quota deltas when deleting older snapshots, while `DstReference.destroyAndCollectBlocks` removes the destination link and either destroys the referred subtree or cleans content created after the prior source snapshot. `removeReference` updates reference counts and only destroys blocks when the count reaches zero.

## Dependencies and Integration Points

This class is tightly coupled to snapshot diff logic in `DirectoryWithSnapshotFeature`, `FileWithSnapshotFeature`, `FileDiffList`, `Snapshot`, and `ReclaimContext`. It also integrates with permission/ACL/XAttr delegation, quota accounting, visitor traversal, debug tree dumps, and `INodeReferenceValidation`.

## Risks and Test Signals

This is high-risk namespace code. Bugs can leak blocks, double-count quota, expose wrong snapshot paths, or delete live data. Tests should cover repeated renames across one or more snapshottable directories, rename within the same snapshottable subtree, snapshot deletion ordering, reference count changes, quota updates along source and destination ancestors, and validation failures for broken `WithCount`/`WithName`/`DstReference` links.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INodeReference.java -->
