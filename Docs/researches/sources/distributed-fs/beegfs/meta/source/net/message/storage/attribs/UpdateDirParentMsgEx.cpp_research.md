<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/UpdateDirParentMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/UpdateDirParentMsgEx.cpp

Purpose: Implements the UpdateDirParentMsgEx server-side message extension: mirrored handler that updates a directory inode parent pointer.

Important APIs/types/functions: Implemented entry points: bool UpdateDirParentMsgEx::processIncoming(ResponseContext& ctx); FileIDLock UpdateDirParentMsgEx::lock(EntryLockStore& store); std::unique_ptr<MirroredMessageResponseState> UpdateDirParentMsgEx::executeLocally( ResponseContext& ctx, bool isSecondary); void UpdateDirParentMsgEx::forwardToSecondary(ResponseContext& ctx).

Control flow: Control flow enters processIncoming(), delegates to BaseType/MirroredMessage, obtains the declared locks, executes the local primary or secondary branch, serializes a ResponseState, and forwards the same operation to the secondary when the entry is mirrored.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <program/Program.h>, <common/net/message/storage/attribs/UpdateDirParentRespMsg.h>, <common/net/message/storage/attribs/SetLocalAttrMsg.h>, <common/net/message/storage/attribs/SetLocalAttrRespMsg.h>, <common/toolkit/MessagingTk.h>, <components/worker/SetChunkFileAttribsWork.h>, <session/EntryLock.h>, "UpdateDirParentMsgEx.h". Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics; integrates with MetaStore/DirInode/FileInode persistence; uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary referenced metadata objects must be released on every error path Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/UpdateDirParentMsgEx.cpp -->
