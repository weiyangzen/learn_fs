<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/session/BumpFileVersionMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/session/BumpFileVersionMsgEx.cpp

Purpose: Implements the BumpFileVersionMsgEx server-side message extension: mirrored session handler that increments a file inode version and optionally emits file-event context.

Important APIs/types/functions: Implemented entry points: bool BumpFileVersionMsgEx::processIncoming(ResponseContext& ctx); FileIDLock BumpFileVersionMsgEx::lock(EntryLockStore& store); std::unique_ptr<MirroredMessageResponseState> BumpFileVersionMsgEx::executeLocally( ResponseContext& ctx, bool isSecondary); void BumpFileVersionMsgEx::forwardToSecondary(ResponseContext& ctx).

Control flow: Control flow enters processIncoming(), delegates to BaseType/MirroredMessage, obtains the declared locks, executes the local primary or secondary branch, serializes a ResponseState, and forwards the same operation to the secondary when the entry is mirrored.

State and persistence behavior: updates or reads session-scoped open-file, lock, or version state.

Dependencies and integration points: Direct includes: "BumpFileVersionMsgEx.h", <components/FileEventLogger.h>, <program/Program.h>. Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics; integrates with MetaStore/DirInode/FileInode persistence; uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage; emits file/modification events when enabled.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary referenced metadata objects must be released on every error path Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/session/BumpFileVersionMsgEx.cpp -->
