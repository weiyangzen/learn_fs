<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/SetXAttrMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/SetXAttrMsgEx.h

Purpose: Declares the SetXAttrMsgEx server-side message extension: mirrored extended-attribute write handler.

Important APIs/types/functions: Declarations/types: class SetXAttrMsgEx : public MirroredMessage<SetXAttrMsg, std::tuple<FileIDLock, FileIDLock>>; typedef ErrorCodeResponseState<SetXAttrRespMsg, NETMSGTYPE_SetXAttr> ResponseState;.

Control flow: The header wires this message into the mirrored-message template, names its response-state type, exposes lock(), executeLocally(), isMirrored(), and forward-to-secondary hooks where needed.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <common/net/message/storage/attribs/SetXAttrMsg.h>, <common/net/message/storage/attribs/SetXAttrRespMsg.h>, <net/message/MirroredMessage.h>. Integration dependencies: uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/SetXAttrMsgEx.h -->
