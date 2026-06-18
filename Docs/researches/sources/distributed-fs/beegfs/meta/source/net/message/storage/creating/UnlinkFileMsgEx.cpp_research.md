<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/UnlinkFileMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/UnlinkFileMsgEx.cpp

## Purpose
Implements the metadata-server side of `UnlinkFileMsg` for BeeGFS file dentries, including buddy-mirrored forwarding, local versus remote inode ownership, hardlink-aware inode removal, chunk cleanup, timestamp repair, and file-event logging.

## Important APIs, Types, and Functions
`UnlinkFileMsgEx::lock()` preloads the target dentry, captures `fileInfo`, locks the parent directory ID, parent/name tuple, target inode ID, and, during resync for non-inlined inodes, the inode hash directory. `processIncoming()` records `MetaOpCounter_UNLINK` before delegating to `MirroredMessage`. `executeLocally()` references the parent `DirInode`, validates the dentry and mirrored entry ID, chooses same-owner local handling or remote `UnlinkLocalFileInodeMsg`, and returns `ResponseState`. `executePrimary()` performs metadata unlink, optional early response, storage chunk removal, timestamp fixes, and event logging. `executeSecondary()` mirrors only metadata effects.

## Control Flow, State, and Persistence
The handler first removes or updates metadata in `MetaStore` through `DirInode`/`MsgHelperUnlink`. If the file inode owner is remote, it removes only the local dentry and asks the owner metadata node or buddy group to unlink the inode; remote failure is logged but does not overwrite successful dentry removal for the user path. If the local primary removes the last inode reference, chunk files are deleted or deferred to disposal by `MsgHelperUnlink`. Timestamp fixup persists through inode/dir helpers when mirrored replay needs deterministic times.

## Dependencies and Integration Points
Depends on `Program::getApp()`, `MetaStore`, `DirInode`, `DirEntry`, `MetaStorageTk`, `MessagingTk`, `RequestResponseNode`, buddy group mapping, `MsgHelperUnlink`, `UnlinkLocalFileInodeMsg`, `MirroredMessage`, `FileEventLogger`, and op counters.

## Risks and Test Signals
High-risk areas are lock-time dentry lookup races, remote inode unlink failure after local dentry removal, early-response behavior that hides later chunk cleanup failures, mirrored entry-ID validation, and correct hardlink counts in events. Tests should cover local inlined and non-inlined unlink, hardlinks, open-file disposal, remote-owner inode unlink, buddy primary/secondary replay, resync-running hash locks, timestamp repair, and remote communication failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/UnlinkFileMsgEx.cpp -->
