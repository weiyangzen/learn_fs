<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/TruncFileMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/TruncFileMsgEx.h

Purpose: Declares the TruncFileMsgEx server-side message extension: mirrored truncate handler that updates metadata and delegates chunk truncation through helper logic.

Important APIs/types/functions: Declarations/types: class TruncFileMsgEx : public MirroredMessage<TruncFileMsg, FileIDLock>; typedef ErrorCodeResponseState<TruncFileRespMsg, NETMSGTYPE_TruncFile> ResponseState;.

Control flow: The header wires this message into the mirrored-message template, names its response-state type, exposes lock(), executeLocally(), isMirrored(), and forward-to-secondary hooks where needed.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <common/net/message/storage/TruncFileMsg.h>, <common/net/message/storage/TruncFileRespMsg.h>, <net/message/MirroredMessage.h>, <storage/MetaStore.h>. Integration dependencies: integrates with MetaStore/DirInode/FileInode persistence; uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/TruncFileMsgEx.h -->
