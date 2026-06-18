# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSDirDeleteOp.java

## Purpose
`FSDirDeleteOp` owns namespace deletion for files and directories, including permission checks, recursive/protected-descendant checks, snapshot constraints, block/inode reclamation, lease cleanup, quota updates, metrics, and edit-log replay.

## Important APIs, Types, And Functions
- Client-facing `delete(FSNamesystem, FSPermissionChecker, String, boolean, boolean)` validates path and permissions.
- Internal `delete(FSDirectory, INodesInPath, BlocksMapUpdateInfo, List<INode>, List<Long>, long)` unlinks and collects reclaim work.
- `deleteInternal` coordinates edit logging, metrics, and lease/inode cleanup under the FSNamesystem write lock.
- `deleteForEditLog` is replay-only.
- `unprotectedDelete` performs the direct inode tree mutation.

## Control Flow
The checked entry point rejects exact reserved names, resolves with `WRITE_LINK`, checks delete permissions, rejects non-recursive deletion of non-empty directories, and checks protected descendants. `deleteInternal` creates block/inode/UC-file collectors, calls the lower-level delete, logs `logDelete`, increments deletion metrics, and removes leases/inodes. The locked delete path rejects missing paths and root deletion, checks snapshottable descendants through `FSDirSnapshotOp`, builds an `INode.ReclaimContext`, removes the last inode, updates parent mtime, and either destroys blocks immediately or cleans the subtree against the latest snapshot.

## State And Persistence Behavior
Deletion changes the namespace tree, inode map, parent modification time, quota counts, block replication metadata, safemode block totals, leases, and snapshottable directory registry. Client deletes persist through `logDelete`; replay deletes call `deleteForEditLog` and directly remove blocks through the block manager.

## Dependencies And Integration Points
The operation is tightly integrated with `FSNamesystem` global write locking, `FSDirectory` write locking and quota updates, `FSDirSnapshotOp` snapshot safety checks, `LeaseManager`, `BlockManager`, `NameNode` metrics, and `DFSUtil.checkProtectedDescendants`.

## Risks And Edge Cases
Root and missing paths must be non-mutating. Snapshot-held files require `cleanSubtree` rather than unconditional destruction. Large directory deletion relies on collected reclaim state, so callers must drain blocks and leases in the right lock context. Protected descendants and non-recursive directories prevent accidental destructive deletes.

## Test Signals
Tests should verify root/missing delete behavior, non-empty directory recursive flag handling, protected descendant rejection, snapshot-root rejection and snapshottable-dir cleanup, lease removal for under-construction files, quota updates, block collection/safemode total updates on replay, and edit-log retry-cache logging.
