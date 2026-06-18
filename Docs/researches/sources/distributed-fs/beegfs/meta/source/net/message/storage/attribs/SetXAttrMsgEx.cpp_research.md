<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/SetXAttrMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/SetXAttrMsgEx.cpp

Purpose: Implements the SetXAttrMsgEx server-side message extension: mirrored extended-attribute write handler.

Important APIs/types/functions: Implemented entry points: std::tuple<FileIDLock, FileIDLock> SetXAttrMsgEx::lock(EntryLockStore& store); bool SetXAttrMsgEx::processIncoming(ResponseContext& ctx); std::unique_ptr<MirroredMessageResponseState> SetXAttrMsgEx::executeLocally(ResponseContext& ctx, bool isSecondary); void SetXAttrMsgEx::forwardToSecondary(ResponseContext& ctx).

Control flow: Control flow enters processIncoming(), delegates to BaseType/MirroredMessage, obtains the declared locks, executes the local primary or secondary branch, serializes a ResponseState, and forwards the same operation to the secondary when the entry is mirrored.

State and persistence behavior: persists metadata through MetaStore, inode objects, dentries, xattrs, or stripe-pattern updates.

Dependencies and integration points: Direct includes: <program/Program.h>, <common/net/message/storage/attribs/SetXAttrRespMsg.h>, <net/msghelpers/MsgHelperXAttr.h>, <session/EntryLock.h>, "SetXAttrMsgEx.h". Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics; integrates with MetaStore/DirInode/FileInode persistence; uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage; delegates protocol-specific work to BeeGFS MsgHelper utilities.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary referenced metadata objects must be released on every error path Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/SetXAttrMsgEx.cpp -->
