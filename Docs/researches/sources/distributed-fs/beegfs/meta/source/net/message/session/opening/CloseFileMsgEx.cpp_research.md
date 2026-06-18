<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/session/opening/CloseFileMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/session/opening/CloseFileMsgEx.cpp

Purpose: Implements the CloseFileMsgEx server-side message extension: mirrored close-file handler that removes a session file, updates inode state, and may complete deferred unlink/disposal work.

Important APIs/types/functions: Implemented entry points: FileIDLock CloseFileMsgEx::lock(EntryLockStore& store); bool CloseFileMsgEx::processIncoming(ResponseContext& ctx); std::unique_ptr<MirroredMessageResponseState> CloseFileMsgEx::executeLocally(ResponseContext& ctx, bool isSecondary); std::unique_ptr<CloseFileMsgEx::ResponseState> CloseFileMsgEx::closeFilePrimary( ResponseContext& ctx); std::unique_ptr<CloseFileMsgEx::ResponseState> CloseFileMsgEx::closeFileSecondary( ResponseContext& ctx); FhgfsOpsErr CloseFileMsgEx::closeFileAfterEarlyResponse(MetaFileHandle inode, unsigned accessFlags, bool* outUnlinkDisposalFile, unsigned& outNumHardlinks, bool& outLastWriterClosed); void CloseFileMsgEx::forwardToSecondary(ResponseContext& ctx).

Control flow: Control flow enters processIncoming(), delegates to BaseType/MirroredMessage, obtains the declared locks, executes the local primary or secondary branch, serializes a ResponseState, and forwards the same operation to the secondary when the entry is mirrored.

State and persistence behavior: updates or reads session-scoped open-file, lock, or version state.

Dependencies and integration points: Direct includes: <common/components/streamlistenerv2/IncomingPreprocessedMsgWork.h>, <common/net/message/control/GenericResponseMsg.h>, <common/net/message/session/opening/CloseFileRespMsg.h>, <common/toolkit/MessagingTk.h>, <common/toolkit/SessionTk.h>, <components/FileEventLogger.h>, <net/msghelpers/MsgHelperClose.h>, <net/msghelpers/MsgHelperLocking.h>, <program/Program.h>, <session/EntryLock.h>, ... Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics; integrates with MetaStore/DirInode/FileInode persistence; uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage; delegates protocol-specific work to BeeGFS MsgHelper utilities; emits file/modification events when enabled.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary The early-response close path makes ordering important: session removal, write counters, inode persistence, disposal unlink, and secondary mirroring must agree even if clients disconnect.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/session/opening/CloseFileMsgEx.cpp -->
