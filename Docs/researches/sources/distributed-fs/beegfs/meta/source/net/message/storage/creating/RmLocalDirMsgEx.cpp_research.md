<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/RmLocalDirMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/RmLocalDirMsgEx.cpp

Purpose: Implements the RmLocalDirMsgEx server-side message extension: mirrored helper handler that removes a locally owned directory inode.

Important APIs/types/functions: Implemented entry points: std::tuple<HashDirLock, FileIDLock> RmLocalDirMsgEx::lock(EntryLockStore& store); bool RmLocalDirMsgEx::processIncoming(ResponseContext& ctx); std::unique_ptr<MirroredMessageResponseState> RmLocalDirMsgEx::executeLocally(ResponseContext& ctx, bool isSecondary); std::unique_ptr<RmLocalDirMsgEx::ResponseState> RmLocalDirMsgEx::rmDir(); void RmLocalDirMsgEx::forwardToSecondary(ResponseContext& ctx).

Control flow: Control flow enters processIncoming(), delegates to BaseType/MirroredMessage, obtains the declared locks, executes the local primary or secondary branch, serializes a ResponseState, and forwards the same operation to the secondary when the entry is mirrored.

State and persistence behavior: persists metadata through MetaStore, inode objects, dentries, xattrs, or stripe-pattern updates.

Dependencies and integration points: Direct includes: <program/Program.h>, <common/net/message/storage/creating/RmLocalDirRespMsg.h>, <common/toolkit/MetaStorageTk.h>, "RmLocalDirMsgEx.h". Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics; integrates with MetaStore/DirInode/FileInode persistence; uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/RmLocalDirMsgEx.cpp -->
