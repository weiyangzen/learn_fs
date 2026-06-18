<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/MkFileWithPatternMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/MkFileWithPatternMsgEx.h

Purpose: Declares the MkFileWithPatternMsgEx server-side message extension: mirrored file creation handler that honors an explicit caller-provided stripe pattern.

Important APIs/types/functions: Declarations/types: class MkFileWithPatternMsgEx : public MirroredMessage<MkFileWithPatternMsg,; typedef ErrorAndEntryResponseState<MkFileWithPatternRespMsg, NETMSGTYPE_MkFileWithPattern> ResponseState;.

Control flow: The header wires this message into the mirrored-message template, names its response-state type, exposes lock(), executeLocally(), isMirrored(), and forward-to-secondary hooks where needed.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <common/net/message/storage/creating/MkFileRespMsg.h>, <common/net/message/storage/creating/MkFileWithPatternMsg.h>, <common/net/message/storage/creating/MkFileWithPatternRespMsg.h>, <common/storage/StorageErrors.h>, <net/message/MirroredMessage.h>, <session/EntryLock.h>, <storage/MetaStore.h>. Integration dependencies: integrates with MetaStore/DirInode/FileInode persistence; uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage; delegates protocol-specific work to BeeGFS MsgHelper utilities.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary Explicit patterns need validation for target existence, buddy-group primary mapping, minimum targets, and power-of-two chunk size.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/creating/MkFileWithPatternMsgEx.h -->
