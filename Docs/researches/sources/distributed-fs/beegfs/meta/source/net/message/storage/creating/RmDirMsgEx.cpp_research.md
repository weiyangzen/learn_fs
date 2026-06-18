<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/RmDirMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/RmDirMsgEx.cpp

Purpose: Implements the RmDirMsgEx server-side message extension: mirrored rmdir handler that removes a child directory dentry and coordinates local or remote inode deletion.

Important APIs/types/functions: Implemented entry points: bool RmDirMsgEx::processIncoming(ResponseContext& ctx); std::tuple<HashDirLock, FileIDLock, FileIDLock, ParentNameLock> RmDirMsgEx::lock(EntryLockStore& store); std::unique_ptr<RmDirMsgEx::ResponseState> RmDirMsgEx::rmDir(ResponseContext& ctx, const bool isSecondary); FhgfsOpsErr RmDirMsgEx::rmRemoteDirInode(EntryInfo* delEntryInfo); void RmDirMsgEx::forwardToSecondary(ResponseContext& ctx).

Control flow: Control flow enters processIncoming(), delegates to BaseType/MirroredMessage, obtains the declared locks, executes the local primary or secondary branch, serializes a ResponseState, and forwards the same operation to the secondary when the entry is mirrored.

State and persistence behavior: persists metadata through MetaStore, inode objects, dentries, xattrs, or stripe-pattern updates.

Dependencies and integration points: Direct includes: <common/components/streamlistenerv2/IncomingPreprocessedMsgWork.h>, <common/net/message/control/GenericResponseMsg.h>, <common/net/message/storage/creating/RmDirRespMsg.h>, <common/net/message/storage/creating/RmLocalDirMsg.h>, <common/net/message/storage/creating/RmLocalDirRespMsg.h>, <common/toolkit/MessagingTk.h>, <components/FileEventLogger.h>, <components/ModificationEventFlusher.h>, <program/Program.h>, <session/EntryLock.h>, ... Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics; integrates with MetaStore/DirInode/FileInode persistence; uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage; emits file/modification events when enabled.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary referenced metadata objects must be released on every error path Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/RmDirMsgEx.cpp -->
