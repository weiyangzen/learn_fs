<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/MoveFileInodeMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/MoveFileInodeMsgEx.cpp

Purpose: Implements the MoveFileInodeMsgEx server-side message extension: mirrored handler that verifies and moves file inode placement/mode metadata for hardlink-capable files.

Important APIs/types/functions: Implemented entry points: std::tuple<FileIDLock, ParentNameLock, FileIDLock> MoveFileInodeMsgEx::lock(EntryLockStore& store); bool MoveFileInodeMsgEx::processIncoming(ResponseContext& ctx); std::unique_ptr<MirroredMessageResponseState> MoveFileInodeMsgEx::executeLocally(ResponseContext& ctx, bool isSecondary); void MoveFileInodeMsgEx::forwardToSecondary(ResponseContext& ctx).

Control flow: Control flow enters processIncoming(), delegates to BaseType/MirroredMessage, obtains the declared locks, executes the local primary or secondary branch, serializes a ResponseState, and forwards the same operation to the secondary when the entry is mirrored.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <common/net/message/storage/creating/MoveFileInodeRespMsg.h>, "MoveFileInodeMsgEx.h". Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics; integrates with MetaStore/DirInode/FileInode persistence; uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary referenced metadata objects must be released on every error path Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/MoveFileInodeMsgEx.cpp -->
