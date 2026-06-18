<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/chunkbalancing/StartChunkBalanceMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/chunkbalancing/StartChunkBalanceMsgEx.h

Purpose: Declares the StartChunkBalanceMsgEx server-side message extension: mirrored handler that creates or reuses a chunk-balancing job for an entry.

Important APIs/types/functions: Declarations/types: class StartChunkBalanceMsgResponseState : public ErrorCodeResponseState<StartChunkBalanceRespMsg, NETMSGTYPE_StartChunkBalance>; class StartChunkBalanceMsgEx : public MirroredMessage<StartChunkBalanceMsg, FileIDLock>; typedef StartChunkBalanceMsgResponseState ResponseState;.

Control flow: The header wires this message into the mirrored-message template, names its response-state type, exposes lock(), executeLocally(), isMirrored(), and forward-to-secondary hooks where needed.

State and persistence behavior: uses in-memory chunk-balancer job state and may persist resulting stripe-pattern metadata.

Dependencies and integration points: Direct includes: <common/net/message/storage/chunkbalancing/StartChunkBalanceMsg.h>, <common/net/message/storage/chunkbalancing/StartChunkBalanceRespMsg.h>, <components/chunkbalancer/ChunkBalancerJob.h>, <net/message/MirroredMessage.h>, <session/EntryLock.h>. Integration dependencies: uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/chunkbalancing/StartChunkBalanceMsgEx.h -->
