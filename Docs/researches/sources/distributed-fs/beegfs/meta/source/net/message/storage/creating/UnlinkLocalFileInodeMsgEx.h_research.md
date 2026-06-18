<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/UnlinkLocalFileInodeMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/UnlinkLocalFileInodeMsgEx.h

## Purpose
Declares the mirrored local-inode unlink message and a custom response state that carries both operation status and the pre-unlink hardlink count.

## Important APIs, Types, and Functions
`UnlinkLocalFileInodeResponseState` derives from `MirroredMessageResponseState`, serializes `result` and `preUnlinkHardlinkCount`, sends `UnlinkLocalFileInodeRespMsg`, and reports `changesObservableState() == true`. `UnlinkLocalFileInodeMsgEx` inherits `MirroredMessage<UnlinkLocalFileInodeMsg, std::tuple<HashDirLock, FileIDLock>>`, overrides `processIncoming()`, `executeLocally()`, `lock()`, `isMirrored()`, and secondary forwarding hooks.

## Control Flow, State, and Persistence
The response type makes hardlink count part of the mirrored state so remote unlink callers can log accurate post-unlink event context. `isMirrored()` follows the deleted entry info rather than a parent dentry, which matches inode-owner semantics.

## Dependencies and Integration Points
Integrates common unlink-local-inode wire messages, `EntryLock`, `MetaStore`, and `MirroredMessage`. It is a response contract consumed by remote unlink and rename paths.

## Risks and Test Signals
Serialization compatibility matters because this response is mirrored and also returned cross-node. Tests should deserialize old/new buffers, assert `changesObservableState()`, verify secondary error extraction from `getResult()`, and check response hardlink count propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/UnlinkLocalFileInodeMsgEx.h -->
