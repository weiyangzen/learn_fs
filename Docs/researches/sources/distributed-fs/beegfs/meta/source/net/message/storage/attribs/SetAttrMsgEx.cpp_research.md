<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/SetAttrMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/SetAttrMsgEx.cpp

Purpose: Implements the SetAttrMsgEx server-side message extension: mirrored setattr handler for metadata stat fields and optional chunk-file attribute updates.

Important APIs/types/functions: Implemented entry points: bool SetAttrMsgEx::processIncoming(ResponseContext& ctx); std::tuple<FileIDLock, FileIDLock> SetAttrMsgEx::lock(EntryLockStore& store); std::unique_ptr<MirroredMessageResponseState> SetAttrMsgEx::executeLocally(ResponseContext& ctx, bool isSecondary); void SetAttrMsgEx::forwardToSecondary(ResponseContext& ctx); FhgfsOpsErr SetAttrMsgEx::setAttrRoot(); FhgfsOpsErr SetAttrMsgEx::setChunkFileAttribs(FileInode& file, bool requestDynamicAttribs); FhgfsOpsErr SetAttrMsgEx::setChunkFileAttribsSequential(FileInode& inode, bool requestDynamicAttribs); FhgfsOpsErr SetAttrMsgEx::setChunkFileAttribsParallel(FileInode& inode, bool requestDynamicAttribs).

Control flow: Control flow enters processIncoming(), delegates to BaseType/MirroredMessage, obtains the declared locks, executes the local primary or secondary branch, serializes a ResponseState, and forwards the same operation to the secondary when the entry is mirrored.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <common/components/streamlistenerv2/IncomingPreprocessedMsgWork.h>, <common/net/message/control/GenericResponseMsg.h>, <common/net/message/storage/attribs/SetAttrRespMsg.h>, <common/net/message/storage/attribs/SetLocalAttrMsg.h>, <common/net/message/storage/attribs/SetLocalAttrRespMsg.h>, <common/toolkit/MessagingTk.h>, <components/FileEventLogger.h>, <components/worker/SetChunkFileAttribsWork.h>, <program/Program.h>, <session/EntryLock.h>, ... Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics; integrates with MetaStore/DirInode/FileInode persistence; uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage; emits file/modification events when enabled.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary referenced metadata objects must be released on every error path root-directory special cases need explicit coverage because they bypass normal parent/name lookup Chunk attribute updates can run sequentially or in parallel; dynamic-attribute refresh failures must not leave stat data inconsistent with storage targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/attribs/SetAttrMsgEx.cpp -->
