<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/moving/MovingDirInsertMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/moving/MovingDirInsertMsgEx.h

## Purpose
Declares the mirrored destination-side directory insertion message for rename/move.

## Important APIs, Types, and Functions
`MovingDirInsertMsgEx` inherits `MirroredMessage<MovingDirInsertMsg, std::tuple<FileIDLock, ParentNameLock>>`. It overrides `processIncoming()`, inline `lock()`, `isMirrored()`, `executeLocally()`, forwarding, secondary response extraction, and mirror log context. `lock()` skips locks for locally generated messages and otherwise locks the destination directory and destination name.

## Control Flow, State, and Persistence
The header’s lock contract protects destination directory/name creation while allowing source-side local messages to rely on already-held locks from the initiating rename.

## Dependencies and Integration Points
Includes moving request/response messages, storage errors, `MetaStore`, and `MirroredMessage`. Used by `RenameV2MsgEx` remote directory moves.

## Risks and Test Signals
The `rctx` pointer must be set before locking; tests should include locally generated and remote-generated paths to verify lock suppression does not run on an uninitialized context.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/moving/MovingDirInsertMsgEx.h -->
