<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/RefreshEntryInfoMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/RefreshEntryInfoMsgEx.h

Purpose: Declares the RefreshEntryInfoMsgEx server-side message extension: mirrored handler that refreshes entry information from the authoritative local inode or root metadata.

Important APIs/types/functions: Declarations/types: class RefreshEntryInfoMsgEx : public MirroredMessage<RefreshEntryInfoMsg,; typedef ErrorCodeResponseState<RefreshEntryInfoRespMsg, NETMSGTYPE_RefreshEntryInfo> ResponseState;.

Control flow: The header wires this message into the mirrored-message template, names its response-state type, exposes lock(), executeLocally(), isMirrored(), and forward-to-secondary hooks where needed.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <storage/DirInode.h>, <common/storage/StorageErrors.h>, <common/net/message/storage/attribs/RefreshEntryInfoMsg.h>, <common/net/message/storage/attribs/RefreshEntryInfoRespMsg.h>, <net/message/MirroredMessage.h>. Integration dependencies: uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary root-directory special cases need explicit coverage because they bypass normal parent/name lookup Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/RefreshEntryInfoMsgEx.h -->
