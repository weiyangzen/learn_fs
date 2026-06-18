# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSDirSnapshotOp.java

## Purpose
`FSDirSnapshotOp` owns snapshot administration and query operations for the Namenode: allowing/disallowing snapshot roots, creating/renaming/deleting snapshots, listing snapshottable directories and snapshots, producing diff reports, finding snapshot paths for a file, and enforcing snapshot delete/rename safety checks.

## Important APIs, Types, And Functions
- Mutators: `allowSnapshot`, `disallowSnapshot`, `createSnapshot`, `renameSnapshot`, and `deleteSnapshot`.
- Readers: `getSnapshottableDirListing`, `getSnapshotListing`, `getSnapshotDiffReport`, `getSnapshotDiffReportListing`, and `getSnapshotFiles`.
- Validators: `verifySnapshotName`, private recursive `checkSnapshot(INode, ...)`, and package-visible `checkSnapshot(FSDirectory, INodesInPath, ...)`.

## Control Flow
Snapshot name verification rejects path separators, invalid inode names, and overlong components. Allow/disallow set or reset snapshottable status under the write lock and then log edits. Create/rename resolve the root, require owner permissions, validate names, mutate `SnapshotManager` under the write lock with current time, and log. Listings and diffs run under read locks, with diff checking subtree read permission for both endpoints. Delete resolves and owner-checks the root, builds reclaim collectors, calls `snapshotManager.deleteSnapshot`, updates quotas, removes reclaimed inodes, updates block replication info, logs deletion, and returns collected blocks.

## State And Persistence Behavior
Snapshot state lives in `SnapshotManager`, directory snapshottable features, snapshot roots, snapshot diffs, quota deltas, inode map, and block collections. Edit-log records are `logAllowSnapshot`, `logDisallowSnapshot`, `logCreateSnapshot`, `logRenameSnapshot`, and `logDeleteSnapshot`. Delete returns blocks for later physical removal by callers.

## Dependencies And Integration Points
It integrates with `FSDirectory`, `SnapshotManager`, `DirectorySnapshottableFeature`, `LeaseManager`, `FSNamesystem.getFileInfo`, `BlockManager` replication updates, permission checking, and callers such as delete/rename that need `checkSnapshot` to prevent removal of snapshottable directories containing snapshots.

## Risks And Edge Cases
Recursive `checkSnapshot` can be expensive but is skipped when no snapshottable directories exist. Snapshot diff permissions require read access to snapshot subtrees, not only the root. Deleting a snapshot must update quotas and inode maps consistently with collected block reclamation. A log message in `deleteSnapshot` prints `snapshotName` for both snapshot and root, which is worth noticing in diagnostics.

## Test Signals
Tests should cover invalid snapshot names, owner permission enforcement, allow/disallow edit replay, create default names, rename modification time/logging, listing filtered by user/superuser, snapshot diff permission checks, deleting snapshots with removed inode/block collection, quota updates, and delete/rename rejection when a subtree contains snapshottable directories with snapshots.
