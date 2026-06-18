<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/MkLocalDirMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/MkLocalDirMsgEx.cpp

Purpose: Implements the MkLocalDirMsgEx server-side message extension: mirrored helper handler that creates a directory inode on the node that owns it.

Important APIs/types/functions: Implemented entry points: HashDirLock MkLocalDirMsgEx::lock(EntryLockStore& store); bool MkLocalDirMsgEx::processIncoming(ResponseContext& ctx); std::unique_ptr<MirroredMessageResponseState> MkLocalDirMsgEx::executeLocally(ResponseContext& ctx, bool isSecondary); void MkLocalDirMsgEx::forwardToSecondary(ResponseContext& ctx).

Control flow: Control flow enters processIncoming(), delegates to BaseType/MirroredMessage, obtains the declared locks, executes the local primary or secondary branch, serializes a ResponseState, and forwards the same operation to the secondary when the entry is mirrored.

State and persistence behavior: persists metadata through MetaStore, inode objects, dentries, xattrs, or stripe-pattern updates.

Dependencies and integration points: Direct includes: <common/net/message/control/GenericResponseMsg.h>, <program/Program.h>, <common/net/message/storage/creating/MkLocalDirRespMsg.h>, "MkLocalDirMsgEx.h". Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics; integrates with MetaStore/DirInode/FileInode persistence; uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/MkLocalDirMsgEx.cpp -->
