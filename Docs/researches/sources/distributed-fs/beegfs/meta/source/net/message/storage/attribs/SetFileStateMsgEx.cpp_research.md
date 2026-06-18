<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/SetFileStateMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/SetFileStateMsgEx.cpp

Purpose: Implements the SetFileStateMsgEx server-side message extension: mirrored file state update handler.

Important APIs/types/functions: Implemented entry points: bool SetFileStateMsgEx::processIncoming(ResponseContext& ctx); FileIDLock SetFileStateMsgEx::lock(EntryLockStore& store); std::unique_ptr<MirroredMessageResponseState> SetFileStateMsgEx::executeLocally( ResponseContext& ctx, bool isSecondary); void SetFileStateMsgEx::forwardToSecondary(ResponseContext& ctx).

Control flow: Control flow enters processIncoming(), delegates to BaseType/MirroredMessage, obtains the declared locks, executes the local primary or secondary branch, serializes a ResponseState, and forwards the same operation to the secondary when the entry is mirrored.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <session/EntryLock.h>, "SetFileStateMsgEx.h". Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics; integrates with MetaStore/DirInode/FileInode persistence; uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/SetFileStateMsgEx.cpp -->
