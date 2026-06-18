# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSDirRenameOp.java

## Purpose
`FSDirRenameOp` implements old and POSIX-style HDFS rename semantics, including overwrite behavior, trash-specific permission checks, quota and FS-limit validation, encryption-zone move validity, snapshot/reference handling, block cleanup for overwritten destinations, leases, metrics, and edit-log replay.

## Important APIs, Types, And Functions
- Entry points are deprecated `renameToInt(FSDirectory, ..., String, String, boolean)`, POSIX `renameToInt(..., Options.Rename...)`, and `renameTo`.
- Replay paths are deprecated `renameForEditLog(String,String,long)` and current `renameForEditLog(..., Options.Rename...)`.
- `unprotectedRenameTo` has old and current variants.
- Validation helpers include `verifyQuotaForRename`, `verifyFsLimitsForRename`, `dstForRenameTo`, `validateDestination`, `validateOverwrite`, `validateRenameSource`, `validateNestSnapshot`, and `checkUnderSameSnapshottableRoot`.
- `RenameOperation` is the transaction-like helper that removes, adds, restores, cleans, and quota-adjusts source/destination inodes.

## Control Flow
The checked path resolves source as `WRITE_LINK` and destination as `CREATE_LINK`, checks protected descendants for non-empty source directories, applies write/delete permissions depending on normal rename or rename-to-trash, then under the write lock calls `unprotectedRenameTo`. The current unprotected path validates source existence/non-root/snapshots, rejects same source/destination and descendant destination moves, rejects reserved paths, checks destination root/parent/type/overwrite semantics, verifies encryption-zone move validity, nested snapshot constraints, same snapshottable root constraints when ordered snapshot deletion/trash are enabled, FS limits, and quota. It then removes source, optionally removes destination, adds the source under the destination name, updates mtimes and leases, cleans overwritten destination blocks/inodes if needed, removes deleted snapshottable directories, updates quota in source snapshot trees, and returns a `RenameResult`.

## State And Persistence Behavior
Rename mutates parent child lists, inode local names, inode references for snapshot-aware moves, parent mtimes, quotas in source and destination trees, leases, block collections for overwritten destinations, and snapshottable-directory registry. Successful checked renames log `logRename`; replay removes blocks immediately if the edit overwrote a destination. `RenameResult` carries audit status, deletion flag, and collected blocks.

## Dependencies And Integration Points
The file depends on `FSDirectory`, `INodeReference`, `SnapshotManager`, `FSDirSnapshotOp`, `FSDirDeleteOp`, `BlockStoragePolicySuite`, `BlockManager`, `LeaseManager`, `DFSUtil.checkProtectedDescendants`, `Options.Rename`, and `DistributedFileSystem` rename semantics.

## Risks And Edge Cases
Snapshot references are the most complex part: source in snapshot can be replaced by `WithName`, destination additions may need `DstReference`, and failure rollback must restore reference counts and names. Quota verification needs destination-parent storage policy and subtracts overwritten destination quota. Old rename returns null on several validation failures, while current rename throws. Edit logging currently occurs after `unprotectedRenameTo`; callers rely on exceptions to avoid logging failed current renames.

## Test Signals
Tests should cover old vs current rename behavior, overwrite flag semantics, file/directory type mismatch, non-empty destination directory rejection, source/destination root rejection, rename into descendant rejection, symlink-to-target rejection, encryption zone boundary moves, same snapshottable root enforcement, nested snapshot denial, quota and max directory item limits, rollback on add failure, overwritten destination block/lease cleanup, and edit-log replay.
