<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/moving/RenameV2MsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/moving/RenameV2MsgEx.cpp

## Purpose
Implements the main metadata rename operation for files and directories, supporting same-directory renames, cross-directory/cross-node moves, buddy mirroring, xattr transfer, overwritten target cleanup, event logging, and modification-event flushing.

## Important APIs, Types, and Functions
`lock()` references source and destination dirs, computes deterministic locks for source/destination dir IDs, parent/name pairs, directory child IDs, local source/target file inodes, and destination hash directories during resync. `processIncoming()` delegates to mirrored processing and updates `MetaOpCounter_RENAME`. `executeLocally()` gathers event context, invokes `movingPerform()`, fixes source timestamps, logs file events, and emits modification events. `movingPerform()` selects `renameInSameDir()`, `renameDir()`, or `renameFile()`. Remote helpers send `MovingFileInsertMsg`, `MovingDirInsertMsg`, `UpdateDirParentMsg`, `UnlinkLocalFileInodeMsg`, and `StatMsg`.

## Control Flow, State, and Persistence
Same-directory rename is performed in `MetaStore::renameInSameDir()` and then deletes overwritten chunks/inodes as needed. Directory moves serialize the source dentry, insert it remotely if not on mirror secondary, remove the source dentry, and update the moved directory inode parent. File moves serialize source inode/dentry state, optionally streams xattrs, inserts remotely, unlinks the source dentry, and completes the move in `MetaStore`. Overwritten destination files are cleaned either via chunk unlink for inlined inodes or remote inode unlink for non-inlined inodes.

## Dependencies and Integration Points
Depends on `MetaStore`, `DirInode`, `DirEntry`, `MessagingTk`, `MovingFileInsertMsgEx`, `MovingDirInsertMsgEx`, `UpdateDirParentMsg`, `UnlinkLocalFileInodeMsgEx`, `MsgHelperUnlink`, `MsgHelperXAttr`, `MsgHelperStat`, `FileEventLogger`, `ModificationEventFlusher`, buddy mappings, and target state stores.

## Risks and Test Signals
Rename has broad consistency risk: partial remote insert before source unlink, update-parent failure after directory move, overwritten inode cleanup failures hidden from clients, cross-node xattr streaming errors, lock-order regressions, remote-owner hardlink counts for event logging, and mirror-secondary shortcuts. Tests should cover same-directory replace, file move across owners, directory move, overwrite inlined/non-inlined targets, hardlinks, xattrs, buddy primary/secondary replay, failed remote insert, failed source unlink after remote insert, and modification/file event outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/moving/RenameV2MsgEx.cpp -->
