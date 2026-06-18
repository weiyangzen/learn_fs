<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/moving/MovingFileInsertMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/moving/MovingFileInsertMsgEx.cpp

## Purpose
Handles destination-side insertion of a file during a remote rename, including overwrite handling and optional xattr streaming for inlined files.

## Important APIs, Types, and Functions
`lock()` skips local generated requests, locks destination directory/name, deserializes the incoming file inode metadata to identify the new inode, checks an existing destination file, and locks new/overwritten inode IDs in lexicographic order. `executeLocally()` references the destination directory, calls `MetaStore::moveRemoteFileInsert()`, reads streamed xattrs with `MsgHelperXAttr::StreamXAttrState::readNextXAttr()`, records xattr names for secondary forwarding, serializes any overwritten inlined inode into the response, fixes timestamps, and rolls back the inserted metadata on xattr failure.

## Control Flow, State, and Persistence
The destination directory gains the moved file dentry/inode state. If a destination file is overwritten, the response may carry serialized inode metadata so the source side can delete old chunks. Xattrs are streamed after the main insert and applied to `newFileInfo`; failure unlinks the inserted metadata but cannot necessarily undo all side effects outside metadata.

## Dependencies and Integration Points
Depends on `MetaStore::moveRemoteFileInsert()`, `FileInode` serialization, `MovingFileInsertMsg/RespMsg`, `MsgHelperXAttr`, `MsgHelperUnlink`, `MirroredMessage`, and `RenameV2MsgEx::remoteFileInsertAndUnlink()`.

## Risks and Test Signals
Risks include response serialization omitting `overWrittenEntryInfo` in `serializeContents()` even though deserialization expects it, xattr streaming failures after insert, lock ordering with existing target, and memory allocation failure leaking chunks. Tests should cover overwrite inlined/non-inlined targets, xattr success/failure, secondary forwarding of xattrs, serialized response round trip, and destination parent missing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/moving/MovingFileInsertMsgEx.cpp -->
