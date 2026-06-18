<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/TruncFileMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/TruncFileMsgEx.cpp

Purpose: Implements the TruncFileMsgEx server-side message extension: mirrored truncate handler that updates metadata and delegates chunk truncation through helper logic.

Important APIs/types/functions: Implemented entry points: FileIDLock TruncFileMsgEx::lock(EntryLockStore& store); bool TruncFileMsgEx::processIncoming(ResponseContext& ctx); std::unique_ptr<MirroredMessageResponseState> TruncFileMsgEx::executeLocally(ResponseContext& ctx, bool isSecondary); void TruncFileMsgEx::forwardToSecondary(ResponseContext& ctx).

Control flow: Control flow enters processIncoming(), delegates to BaseType/MirroredMessage, obtains the declared locks, executes the local primary or secondary branch, serializes a ResponseState, and forwards the same operation to the secondary when the entry is mirrored.

State and persistence behavior: persists metadata through MetaStore, inode objects, dentries, xattrs, or stripe-pattern updates.

Dependencies and integration points: Direct includes: <common/net/message/control/GenericResponseMsg.h>, <common/net/message/storage/TruncFileRespMsg.h>, <common/toolkit/MessagingTk.h>, <components/FileEventLogger.h>, <net/msghelpers/MsgHelperTrunc.h>, "TruncFileMsgEx.h", <program/Program.h>. Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics; integrates with MetaStore/DirInode/FileInode persistence; uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage; delegates protocol-specific work to BeeGFS MsgHelper utilities; emits file/modification events when enabled.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary referenced metadata objects must be released on every error path Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/TruncFileMsgEx.cpp -->
