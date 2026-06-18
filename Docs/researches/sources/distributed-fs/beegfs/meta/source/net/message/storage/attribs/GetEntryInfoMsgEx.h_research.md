<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/GetEntryInfoMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/GetEntryInfoMsgEx.h

Purpose: Declares the GetEntryInfoMsgEx server-side message extension: mirrored entry-info query handler returning stripe pattern, path info, remote storage target, and session counts.

Important APIs/types/functions: Declarations/types: class GetEntryInfoMsgResponseState : public MirroredMessageResponseState; class GetEntryInfoMsgEx : public MirroredMessage<GetEntryInfoMsg, FileIDLock>; typedef GetEntryInfoMsgResponseState ResponseState;.

Control flow: The header wires this message into the mirrored-message template, names its response-state type, exposes lock(), executeLocally(), isMirrored(), and forward-to-secondary hooks where needed.

State and persistence behavior: persists metadata through MetaStore, inode objects, dentries, xattrs, or stripe-pattern updates.

Dependencies and integration points: Direct includes: <storage/DirInode.h>, <common/storage/StorageErrors.h>, <common/net/message/storage/attribs/GetEntryInfoMsg.h>, <common/net/message/storage/attribs/GetEntryInfoRespMsg.h>, <net/message/MirroredMessage.h>. Integration dependencies: uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary root-directory special cases need explicit coverage because they bypass normal parent/name lookup Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/GetEntryInfoMsgEx.h -->
