<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/chunkbalancing/UpdateStripePatternMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/chunkbalancing/UpdateStripePatternMsgEx.h

Purpose: Declares the UpdateStripePatternMsgEx server-side message extension: mirrored chunk-balancing worker handler that rewrites file stripe patterns after chunk movement checks.

Important APIs/types/functions: Declarations/types: class UpdateStripePatternMsgEx : public MirroredMessage<UpdateStripePatternMsg, FileIDLock>; typedef ErrorCodeResponseState<UpdateStripePatternRespMsg, NETMSGTYPE_UpdateStripePattern> ResponseState;.

Control flow: The header wires this message into the mirrored-message template, names its response-state type, exposes lock(), executeLocally(), isMirrored(), and forward-to-secondary hooks where needed.

State and persistence behavior: persists metadata through MetaStore, inode objects, dentries, xattrs, or stripe-pattern updates; uses in-memory chunk-balancer job state and may persist resulting stripe-pattern metadata.

Dependencies and integration points: Direct includes: <common/net/message/storage/chunkbalancing/UpdateStripePatternMsg.h>, <common/net/message/storage/chunkbalancing/UpdateStripePatternRespMsg.h>, <components/chunkbalancer/ChunkBalancerJob.h>, <net/message/MirroredMessage.h>, <app/App.h>, <session/EntryLock.h>. Integration dependencies: uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary Chunk-existence checks and pattern rewrites must be atomic from the metadata perspective, or balancing can strand chunks on the wrong target.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/chunkbalancing/UpdateStripePatternMsgEx.h -->
