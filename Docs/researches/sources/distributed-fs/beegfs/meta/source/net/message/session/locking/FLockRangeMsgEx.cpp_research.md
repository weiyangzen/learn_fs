<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/session/locking/FLockRangeMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/session/locking/FLockRangeMsgEx.cpp

Purpose: Implements the FLockRangeMsgEx server-side message extension: mirrored byte-range flock handler for session-scoped range locks.

Important APIs/types/functions: Implemented entry points: bool FLockRangeMsgEx::processIncoming(ResponseContext& ctx); FileIDLock FLockRangeMsgEx::lock(EntryLockStore& store); std::unique_ptr<MirroredMessageResponseState> FLockRangeMsgEx::executeLocally(ResponseContext& ctx, bool isSecondary); void FLockRangeMsgEx::forwardToSecondary(ResponseContext& ctx).

Control flow: Control flow enters processIncoming(), delegates to BaseType/MirroredMessage, obtains the declared locks, executes the local primary or secondary branch, serializes a ResponseState, and forwards the same operation to the secondary when the entry is mirrored.

State and persistence behavior: updates or reads session-scoped open-file, lock, or version state.

Dependencies and integration points: Direct includes: <common/net/message/session/locking/FLockRangeRespMsg.h>, <common/toolkit/MessagingTk.h>, <common/toolkit/SessionTk.h>, <net/msghelpers/MsgHelperLocking.h>, <program/Program.h>, <session/SessionStore.h>, <storage/MetaStore.h>, "FLockRangeMsgEx.h". Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics; integrates with MetaStore/DirInode/FileInode persistence; uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage; delegates protocol-specific work to BeeGFS MsgHelper utilities.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary referenced metadata objects must be released on every error path Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/session/locking/FLockRangeMsgEx.cpp -->
