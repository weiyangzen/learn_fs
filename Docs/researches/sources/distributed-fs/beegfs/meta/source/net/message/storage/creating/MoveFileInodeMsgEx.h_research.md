<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/MoveFileInodeMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/MoveFileInodeMsgEx.h

Purpose: Declares the MoveFileInodeMsgEx server-side message extension: mirrored handler that verifies and moves file inode placement/mode metadata for hardlink-capable files.

Important APIs/types/functions: Declarations/types: class MoveFileInodeMsgResponseState : public MirroredMessageResponseState; class MoveFileInodeMsgEx : public MirroredMessage<MoveFileInodeMsg,; typedef MoveFileInodeMsgResponseState ResponseState;.

Control flow: The header wires this message into the mirrored-message template, names its response-state type, exposes lock(), executeLocally(), isMirrored(), and forward-to-secondary hooks where needed.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <common/storage/StorageErrors.h>, <common/net/message/storage/creating/MoveFileInodeMsg.h>, <common/net/message/storage/creating/MoveFileInodeRespMsg.h>, <net/message/MirroredMessage.h>, <session/EntryLock.h>, <storage/MetaStore.h>. Integration dependencies: integrates with MetaStore/DirInode/FileInode persistence; uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/MoveFileInodeMsgEx.h -->
