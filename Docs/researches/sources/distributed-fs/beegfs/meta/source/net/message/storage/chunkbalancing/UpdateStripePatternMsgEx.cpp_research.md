<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/chunkbalancing/UpdateStripePatternMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/chunkbalancing/UpdateStripePatternMsgEx.cpp

Purpose: Implements the UpdateStripePatternMsgEx server-side message extension: mirrored chunk-balancing worker handler that rewrites file stripe patterns after chunk movement checks.

Important APIs/types/functions: Implemented entry points: FileIDLock UpdateStripePatternMsgEx::lock(EntryLockStore& store); bool UpdateStripePatternMsgEx::processIncoming(ResponseContext& ctx); std::unique_ptr<MirroredMessageResponseState> UpdateStripePatternMsgEx::executeLocally(ResponseContext& ctx, bool isSecondary); bool UpdateStripePatternMsgEx::setStripePattern(EntryInfo* entryInfo, FileInode& inode, std::string& relativePath, uint16_t localTargetID, uint16_t destinationID); void UpdateStripePatternMsgEx::forwardToSecondary(ResponseContext& ctx); bool UpdateStripePatternMsgEx::checkChunkOnStorageTarget(FileInode& inode, std::string& relativePath, uint16_t targetID).

Control flow: Control flow enters processIncoming(), delegates to BaseType/MirroredMessage, obtains the declared locks, executes the local primary or secondary branch, serializes a ResponseState, and forwards the same operation to the secondary when the entry is mirrored.

State and persistence behavior: persists metadata through MetaStore, inode objects, dentries, xattrs, or stripe-pattern updates; uses in-memory chunk-balancer job state and may persist resulting stripe-pattern metadata.

Dependencies and integration points: Direct includes: <toolkit/StorageTkEx.h>, <program/Program.h>, <storage/MetaStore.h>, <components/FileEventLogger.h>, "UpdateStripePatternMsgEx.h". Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics; integrates with MetaStore/DirInode/FileInode persistence; uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage; emits file/modification events when enabled.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary Chunk-existence checks and pattern rewrites must be atomic from the metadata perspective, or balancing can strand chunks on the wrong target.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/chunkbalancing/UpdateStripePatternMsgEx.cpp -->
