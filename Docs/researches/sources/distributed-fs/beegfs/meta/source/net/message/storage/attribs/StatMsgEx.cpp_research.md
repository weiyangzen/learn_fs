<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/StatMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/StatMsgEx.cpp

Purpose: Implements the StatMsgEx server-side message extension: mirrored stat handler for regular metadata entries and the root directory special case.

Important APIs/types/functions: Implemented entry points: bool StatMsgEx::processIncoming(ResponseContext& ctx); FileIDLock StatMsgEx::lock(EntryLockStore& store); std::unique_ptr<MirroredMessageResponseState> StatMsgEx::executeLocally(ResponseContext& ctx, bool isSecondary); FhgfsOpsErr StatMsgEx::statRoot(StatData& outStatData).

Control flow: Control flow enters processIncoming(), delegates to BaseType/MirroredMessage, obtains the declared locks, executes the local primary or secondary branch, serializes a ResponseState, and forwards the same operation to the secondary when the entry is mirrored.

State and persistence behavior: persists metadata through MetaStore, inode objects, dentries, xattrs, or stripe-pattern updates.

Dependencies and integration points: Direct includes: <program/Program.h>, <common/net/message/storage/attribs/StatRespMsg.h>, <common/toolkit/MessagingTk.h>, <net/msghelpers/MsgHelperStat.h>, "StatMsgEx.h". Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics; uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage; delegates protocol-specific work to BeeGFS MsgHelper utilities.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary root-directory special cases need explicit coverage because they bypass normal parent/name lookup Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/StatMsgEx.cpp -->
