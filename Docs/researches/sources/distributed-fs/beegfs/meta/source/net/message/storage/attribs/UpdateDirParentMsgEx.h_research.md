<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/UpdateDirParentMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/UpdateDirParentMsgEx.h

Purpose: Declares the UpdateDirParentMsgEx server-side message extension: mirrored handler that updates a directory inode parent pointer.

Important APIs/types/functions: Declarations/types: class UpdateDirParentMsgEx : public MirroredMessage<UpdateDirParentMsg, FileIDLock>; typedef ErrorCodeResponseState<UpdateDirParentRespMsg, NETMSGTYPE_UpdateDirParent> ResponseState;.

Control flow: The header wires this message into the mirrored-message template, names its response-state type, exposes lock(), executeLocally(), isMirrored(), and forward-to-secondary hooks where needed.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <storage/MetaStore.h>, <common/storage/StorageErrors.h>, <common/net/message/storage/attribs/UpdateDirParentMsg.h>, <common/net/message/storage/attribs/UpdateDirParentRespMsg.h>, <net/message/MirroredMessage.h>. Integration dependencies: integrates with MetaStore/DirInode/FileInode persistence; uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/UpdateDirParentMsgEx.h -->
