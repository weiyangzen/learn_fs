<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/session/opening/OpenFileMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/session/opening/OpenFileMsgEx.cpp

Purpose: Implements the OpenFileMsgEx server-side message extension: mirrored open-file handler that references metadata, checks access, and registers the open file in the session store.

Important APIs/types/functions: Implemented entry points: FileIDLock OpenFileMsgEx::lock(EntryLockStore& store); bool OpenFileMsgEx::processIncoming(ResponseContext& ctx); std::unique_ptr<MirroredMessageResponseState> OpenFileMsgEx::executeLocally(ResponseContext& ctx, bool isSecondary); void OpenFileMsgEx::forwardToSecondary(ResponseContext& ctx).

Control flow: Control flow enters processIncoming(), delegates to BaseType/MirroredMessage, obtains the declared locks, executes the local primary or secondary branch, serializes a ResponseState, and forwards the same operation to the secondary when the entry is mirrored.

State and persistence behavior: updates or reads session-scoped open-file, lock, or version state.

Dependencies and integration points: Direct includes: <common/net/message/control/GenericResponseMsg.h>, <common/net/message/session/opening/OpenFileRespMsg.h>, <common/toolkit/SessionTk.h>, <common/storage/striping/Raid0Pattern.h>, <components/FileEventLogger.h>, <net/msghelpers/MsgHelperOpen.h>, <program/Program.h>, <session/EntryLock.h>, <session/SessionStore.h>, "OpenFileMsgEx.h". Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics; integrates with MetaStore/DirInode/FileInode persistence; uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage; delegates protocol-specific work to BeeGFS MsgHelper utilities; emits file/modification events when enabled.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary referenced metadata objects must be released on every error path Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/session/opening/OpenFileMsgEx.cpp -->
