<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/HardlinkMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/HardlinkMsgEx.cpp

Purpose: Implements the HardlinkMsgEx server-side message extension: mirrored hardlink creation handler coordinating source inode link counts and destination dentry insertion.

Important APIs/types/functions: Implemented entry points: std::tuple<FileIDLock, ParentNameLock, ParentNameLock, FileIDLock> HardlinkMsgEx::lock( EntryLockStore& store); bool HardlinkMsgEx::processIncoming(ResponseContext& ctx); std::unique_ptr<MirroredMessageResponseState> HardlinkMsgEx::executeLocally(ResponseContext& ctx, bool isSecondary); FhgfsOpsErr HardlinkMsgEx::incDecRemoteLinkCount(NumNodeID const& ownerNodeID, bool increment); void HardlinkMsgEx::forwardToSecondary(ResponseContext& ctx).

Control flow: Control flow enters processIncoming(), delegates to BaseType/MirroredMessage, obtains the declared locks, executes the local primary or secondary branch, serializes a ResponseState, and forwards the same operation to the secondary when the entry is mirrored.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <program/Program.h>, <common/net/message/storage/creating/HardlinkRespMsg.h>, <common/net/message/storage/creating/MoveFileInodeMsg.h>, <common/net/message/storage/creating/MoveFileInodeRespMsg.h>, <common/net/message/storage/attribs/SetAttrMsg.h>, <common/net/message/storage/attribs/SetAttrRespMsg.h>, <common/toolkit/MessagingTk.h>, <components/FileEventLogger.h>, "HardlinkMsgEx.h". Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics; integrates with MetaStore/DirInode/FileInode persistence; uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage; emits file/modification events when enabled.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary referenced metadata objects must be released on every error path Link-count changes and destination dentry creation must be compensated on partial failure, especially when the source owner is remote.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/HardlinkMsgEx.cpp -->
