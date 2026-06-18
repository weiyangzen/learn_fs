<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/session/AckNotifyMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/session/AckNotifyMsgEx.h

Purpose: Declares the AckNotifiyMsgEx server-side message extension: mirrored acknowledgement-notification wrapper; the spelling follows the BeeGFS message class name.

Important APIs/types/functions: Declarations/types: class AckNotifiyMsgEx : public MirroredMessage<AckNotifiyMsg, std::tuple<>>; typedef ErrorCodeResponseState< AckNotifiyRespMsg, NETMSGTYPE_AckNotify> ResponseState;.

Control flow: The header wires this message into the mirrored-message template, names its response-state type, exposes lock(), executeLocally(), isMirrored(), and forward-to-secondary hooks where needed.

State and persistence behavior: updates or reads session-scoped open-file, lock, or version state.

Dependencies and integration points: Direct includes: <common/net/message/session/AckNotifyMsg.h>, <common/net/message/session/AckNotifyRespMsg.h>, <net/message/MirroredMessage.h>, <session/MirrorMessageResponseState.h>. Integration dependencies: uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/session/AckNotifyMsgEx.h -->
