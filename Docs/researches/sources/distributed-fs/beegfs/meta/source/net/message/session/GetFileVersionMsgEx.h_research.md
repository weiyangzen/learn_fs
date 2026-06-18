<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/session/GetFileVersionMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/session/GetFileVersionMsgEx.h

Purpose: Declares the GetFileVersionMsgEx server-side message extension: mirrored read handler that returns the current version counter for a file inode.

Important APIs/types/functions: Declarations/types: class GetFileVersionMsgResponseState : public MirroredMessageResponseState; class GetFileVersionMsgEx : public MirroredMessage<GetFileVersionMsg, FileIDLock>; typedef GetFileVersionMsgResponseState ResponseState;.

Control flow: The header wires this message into the mirrored-message template, names its response-state type, exposes lock(), executeLocally(), isMirrored(), and forward-to-secondary hooks where needed.

State and persistence behavior: updates or reads session-scoped open-file, lock, or version state.

Dependencies and integration points: Direct includes: <common/net/message/session/GetFileVersionMsg.h>, <common/net/message/session/GetFileVersionRespMsg.h>, <common/net/message/session/GetFileVersionRespMsg.h>, <net/message/MirroredMessage.h>. Integration dependencies: uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/session/GetFileVersionMsgEx.h -->
