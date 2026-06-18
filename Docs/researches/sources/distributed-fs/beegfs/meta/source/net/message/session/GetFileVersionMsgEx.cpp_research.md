<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/session/GetFileVersionMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/session/GetFileVersionMsgEx.cpp

Purpose: Implements the GetFileVersionMsgEx server-side message extension: mirrored read handler that returns the current version counter for a file inode.

Important APIs/types/functions: Implemented entry points: bool GetFileVersionMsgEx::processIncoming(ResponseContext& ctx); FileIDLock GetFileVersionMsgEx::lock(EntryLockStore& store); std::unique_ptr<MirroredMessageResponseState> GetFileVersionMsgEx::executeLocally(ResponseContext& ctx, bool isSecondary).

Control flow: Control flow enters processIncoming(), delegates to BaseType/MirroredMessage, obtains the declared locks, executes the local primary or secondary branch, serializes a ResponseState, and forwards the same operation to the secondary when the entry is mirrored.

State and persistence behavior: updates or reads session-scoped open-file, lock, or version state.

Dependencies and integration points: Direct includes: "GetFileVersionMsgEx.h", <program/Program.h>. Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics; integrates with MetaStore/DirInode/FileInode persistence; uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary referenced metadata objects must be released on every error path Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/session/GetFileVersionMsgEx.cpp -->
