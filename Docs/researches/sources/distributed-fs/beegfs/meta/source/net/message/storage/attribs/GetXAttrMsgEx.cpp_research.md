<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/GetXAttrMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/GetXAttrMsgEx.cpp

Purpose: Implements the GetXAttrMsgEx server-side message extension: mirrored extended-attribute read handler.

Important APIs/types/functions: Implemented entry points: bool GetXAttrMsgEx::processIncoming(ResponseContext& ctx); FileIDLock GetXAttrMsgEx::lock(EntryLockStore& store); std::unique_ptr<MirroredMessageResponseState> GetXAttrMsgEx::executeLocally(ResponseContext& ctx, bool isSecondary).

Control flow: Control flow enters processIncoming(), delegates to BaseType/MirroredMessage, obtains the declared locks, executes the local primary or secondary branch, serializes a ResponseState, and forwards the same operation to the secondary when the entry is mirrored.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <program/Program.h>, <common/net/message/storage/attribs/GetXAttrRespMsg.h>, <net/msghelpers/MsgHelperXAttr.h>, "GetXAttrMsgEx.h". Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics; uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage; delegates protocol-specific work to BeeGFS MsgHelper utilities.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/GetXAttrMsgEx.cpp -->
