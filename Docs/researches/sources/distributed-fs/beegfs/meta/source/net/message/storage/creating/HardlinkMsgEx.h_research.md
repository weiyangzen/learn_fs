<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/HardlinkMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/HardlinkMsgEx.h

Purpose: Declares the HardlinkMsgEx server-side message extension: mirrored hardlink creation handler coordinating source inode link counts and destination dentry insertion.

Important APIs/types/functions: Declarations/types: class HardlinkMsgEx : public MirroredMessage<HardlinkMsg,; typedef ErrorCodeResponseState<HardlinkRespMsg, NETMSGTYPE_Hardlink> ResponseState;.

Control flow: The header wires this message into the mirrored-message template, names its response-state type, exposes lock(), executeLocally(), isMirrored(), and forward-to-secondary hooks where needed.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <common/storage/StorageErrors.h>, <common/net/message/storage/creating/HardlinkMsg.h>, <common/net/message/storage/creating/HardlinkRespMsg.h>, <session/EntryLock.h>, <storage/DirEntry.h>, <storage/MetaStore.h>, <net/message/MirroredMessage.h>. Integration dependencies: integrates with MetaStore/DirInode/FileInode persistence; uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary Link-count changes and destination dentry creation must be compensated on partial failure, especially when the source owner is remote.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/HardlinkMsgEx.h -->
