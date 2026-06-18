<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/UnlinkLocalFileInodeMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/UnlinkLocalFileInodeMsgEx.cpp

## Purpose
Implements a metadata-owner-side helper message used when another metadata node has removed a dentry but the actual file inode lives locally. It decrements hardlink state, removes the inode when appropriate, and deletes chunk files on the primary.

## Important APIs, Types, and Functions
`lock()` returns no locks for locally generated messages because callers already own the relevant locks; otherwise it should lock the inode hash during resync and the file ID. `processIncoming()` stores the response context for local-generation checks and invokes `BaseType`. `executeLocally()` copies the incoming `EntryInfo`, calls `MsgHelperUnlink::unlinkFileInode()`, fills `UnlinkLocalFileInodeResponseState`, and removes storage chunks if an inode was actually unlinked on the primary. `forwardToSecondary()` forwards the mirrored request with `NETMSGTYPE_UnlinkLocalFileInodeResp`.

## Control Flow, State, and Persistence
The metadata mutation is delegated to `MetaStore::unlinkFileInode()` through `MsgHelperUnlink`. A copied `EntryInfo` is intentionally used because unlink processing can modify parent/inlined fields; forwarding the original state to the secondary avoids primary/secondary divergence. Chunk-file deletion happens only for non-secondary execution.

## Dependencies and Integration Points
Used by `UnlinkFileMsgEx` and `RenameV2MsgEx` for remote inode cleanup. Depends on `MetaStorageTk`, `EntryLockStore`, `MirroredMessage`, `MsgHelperUnlink`, and `UnlinkLocalFileInodeRespMsg`.

## Risks and Test Signals
The `lock()` implementation contains a shadowed `HashDirLock hashLock` inside the resync branch, which appears to leave the returned hash lock empty even when resync is running. Tests should cover non-local message locking during resync, copied-entry forwarding, hardlink decrement results, chunk unlink suppression on secondary, and serialized pre-unlink hardlink count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/UnlinkLocalFileInodeMsgEx.cpp -->
