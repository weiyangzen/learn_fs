<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/chunkbalancing/StartChunkBalanceMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/chunkbalancing/StartChunkBalanceMsgEx.cpp

Purpose: Implements the StartChunkBalanceMsgEx server-side message extension: mirrored handler that creates or reuses a chunk-balancing job for an entry.

Important APIs/types/functions: Implemented entry points: FileIDLock StartChunkBalanceMsgEx::lock(EntryLockStore& store); bool StartChunkBalanceMsgEx::processIncoming(ResponseContext& ctx); std::unique_ptr<MirroredMessageResponseState> StartChunkBalanceMsgEx::executeLocally(ResponseContext& ctx, bool isSecondary); ChunkBalancerJob* StartChunkBalanceMsgEx::addChunkBalanceJob(bool& outIsNew).

Control flow: Control flow enters processIncoming(), delegates to BaseType/MirroredMessage, obtains the declared locks, executes the local primary or secondary branch, serializes a ResponseState, and forwards the same operation to the secondary when the entry is mirrored.

State and persistence behavior: uses in-memory chunk-balancer job state and may persist resulting stripe-pattern metadata.

Dependencies and integration points: Direct includes: <toolkit/StorageTkEx.h>, <program/Program.h>, "StartChunkBalanceMsgEx.h". Integration dependencies: uses the global App singleton to reach MetaStore, node stores, syncers, sessions, or statistics; uses EntryLockStore locks to serialize metadata mutation or query with writers; participates in buddy-mirror primary/secondary replay through MirroredMessage.

Risks and test signals: mirror replay must preserve lock order, response semantics, and idempotence between primary and secondary Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/chunkbalancing/StartChunkBalanceMsgEx.cpp -->
