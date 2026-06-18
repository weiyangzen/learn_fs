<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/MkFileMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/MkFileMsgEx.cpp

Purpose: Implements the MkFileMsgEx server-side message extension: mirrored regular-file creation handler using the standard BeeGFS mkfile helper path.

Important APIs/types/functions: Implemented entry points: std::tuple<FileIDLock, ParentNameLock, FileIDLock> MkFileMsgEx::lock(EntryLockStore& store); bool MkFileMsgEx::processIncoming(ResponseContext& ctx); std::unique_ptr<MirroredMessageResponseState> MkFileMsgEx::executeLocally(ResponseContext& ctx, bool isSecondary); std::unique_ptr<MkFileMsgEx::ResponseState> MkFileMsgEx::executePrimary(); std::unique_ptr<MkFileMsgEx::ResponseState> MkFileMsgEx::executeSecondary(); void MkFileMsgEx::forwardToSecondary(ResponseContext& ctx).

Control flow: Control flow enters processIncoming(), delegates to BaseType/MirroredMessage, obtains the declared locks, executes the local primary or secondary branch, serializes a ResponseState, and forwards the same operation to the secondary when the entry is mirrored.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <common/net/message/storage/creating/MkFileRespMsg.h>, <common/net/message/control/GenericResponseMsg.h>, <common/toolkit/MessagingTk.h>, <common/storage/StatData.h>, <components/FileEventLogger.h>, <net/msghelpers/MsgHelperMkFile.h>, <program/Program.h>, "MkFileMsgEx.h". Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics; integrates with MetaStore/DirInode/FileInode persistence; uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage; delegates protocol-specific work to BeeGFS MsgHelper utilities; emits file/modification events when enabled.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary referenced metadata objects must be released on every error path Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/MkFileMsgEx.cpp -->
