<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/moving/MovingFileInsertMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/moving/MovingFileInsertMsgEx.h

## Purpose
Declares the mirrored destination-side file insertion message and custom response used by cross-node file rename.

## Important APIs, Types, and Functions
`MovingFileInsertResponseState` stores result, overwritten inode buffer, and overwritten entry info, sends `MovingFileInsertRespMsg`, serializes response state for mirrored replay, and reports observable change on success. `MovingFileInsertMsgEx` inherits `MirroredMessage<MovingFileInsertMsg, std::tuple<FileIDLock, FileIDLock, FileIDLock, ParentNameLock>>`, manages `xattrNames`, `newFileInfo`, and a `StreamXAttrState`, and overrides lock/execution/forwarding hooks.

## Control Flow, State, and Persistence
`prepareMirrorRequestArgs()` registers a stream-out hook when the original message has xattrs, using the xattrs just received and the new file info. This allows primary destination xattr application to be replayed to the secondary destination.

## Dependencies and Integration Points
Depends on moving wire messages, `MirroredMessage`, `MetaStore`, `MsgHelperXAttr`, and response-state serialization used by the mirror framework.

## Risks and Test Signals
Response-state serialization must include all fields needed by consumers; tests should check `overWrittenEntryInfo` survival across mirror serialization, xattr stream hook registration, and `changesObservableState()` only for successful insert.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/moving/MovingFileInsertMsgEx.h -->
