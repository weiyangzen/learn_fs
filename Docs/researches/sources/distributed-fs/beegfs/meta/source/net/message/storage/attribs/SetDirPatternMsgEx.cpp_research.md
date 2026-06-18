<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/SetDirPatternMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/SetDirPatternMsgEx.cpp

Purpose: Implements the SetDirPatternMsgEx server-side message extension: mirrored directory stripe-pattern update handler.

Important APIs/types/functions: Implemented entry points: bool SetDirPatternMsgEx::processIncoming(ResponseContext& ctx); std::unique_ptr<MirroredMessageResponseState> SetDirPatternMsgEx::executeLocally( ResponseContext& ctx, bool isSecondary); void SetDirPatternMsgEx::forwardToSecondary(ResponseContext& ctx).

Control flow: Control flow enters processIncoming(), delegates to BaseType/MirroredMessage, obtains the declared locks, executes the local primary or secondary branch, serializes a ResponseState, and forwards the same operation to the secondary when the entry is mirrored.

State and persistence behavior: persists metadata through MetaStore, inode objects, dentries, xattrs, or stripe-pattern updates.

Dependencies and integration points: Direct includes: <common/net/message/storage/attribs/SetDirPatternRespMsg.h>, <common/storage/striping/Raid0Pattern.h>, <common/toolkit/MessagingTk.h>, <program/Program.h>, <session/EntryLock.h>, <storage/DirInode.h>, <storage/MetaStore.h>, "SetDirPatternMsgEx.h". Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics; integrates with MetaStore/DirInode/FileInode persistence; uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary referenced metadata objects must be released on every error path root-directory special cases need explicit coverage because they bypass normal parent/name lookup Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/SetDirPatternMsgEx.cpp -->
