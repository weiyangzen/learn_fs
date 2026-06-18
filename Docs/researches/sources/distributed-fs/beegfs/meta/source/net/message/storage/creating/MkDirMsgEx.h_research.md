<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/MkDirMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/MkDirMsgEx.h

Purpose: Declares the MkDirMsgEx server-side message extension: mirrored mkdir handler coordinating local or remote directory-inode creation, dentry insertion, ACLs, and event logging.

Important APIs/types/functions: Declarations/types: class MkDirMsgEx : public MirroredMessage<MkDirMsg, std::tuple<HashDirLock, FileIDLock, ParentNameLock>>; typedef ErrorAndEntryResponseState<MkDirRespMsg, NETMSGTYPE_MkDir> ResponseState;.

Control flow: The header wires this message into the mirrored-message template, names its response-state type, exposes lock(), executeLocally(), isMirrored(), and forward-to-secondary hooks where needed.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <common/storage/StorageErrors.h>, <common/net/message/storage/creating/MkDirMsg.h>, <common/net/message/storage/creating/MkDirRespMsg.h>, <session/EntryLock.h>, <storage/MetaStore.h>, <net/message/MirroredMessage.h>. Integration dependencies: integrates with MetaStore/DirInode/FileInode persistence; uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary The remote-inode compensation path is a critical failure mode; tests should cover owner selection, remote failure, duplicate names, ACL propagation, and buddy-mirrored secondary replay.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/MkDirMsgEx.h -->
