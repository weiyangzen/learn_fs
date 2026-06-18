<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/moving/MovingDirInsertMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/moving/MovingDirInsertMsgEx.cpp

## Purpose
Handles the destination-side insertion phase of a cross-directory or cross-node directory rename.

## Important APIs, Types, and Functions
`processIncoming()` stores `ResponseContext` for lock logic and delegates to `BaseType`. `executeLocally()` references the destination parent, deserializes a `DirEntry` from the supplied metadata buffer, rejects attempts to insert a directory into itself, calls `DirInode::makeDirEntry()`, optionally fixes destination directory timestamps, releases the parent, and returns `MovingDirInsertRespMsg` through `ResponseState`. `forwardToSecondary()` mirrors the insert to the secondary.

## Control Flow, State, and Persistence
The operation persists a new directory dentry in the destination directory. It does not update the moved directory inode’s parent info; the source-side rename handler performs that through `UpdateDirParentMsg` after local removal.

## Dependencies and Integration Points
Depends on `MirroredMessage`, destination `MetaStore`, serialized `DirEntry`, `MovingDirInsertMsg/RespMsg`, timestamp repair, and `RenameV2MsgEx::remoteDirInsert()`.

## Risks and Test Signals
Risks include metadata buffer version mismatch, accepting duplicate destination names, self-move detection, and partial remote insert before source-side cleanup. Tests should cover bad deserialization, existing target, self insert, mirrored secondary replay, timestamp fixup, and destination parent missing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/moving/MovingDirInsertMsgEx.cpp -->
