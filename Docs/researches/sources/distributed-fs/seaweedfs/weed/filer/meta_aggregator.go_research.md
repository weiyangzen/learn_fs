# sources/distributed-fs/seaweedfs/weed/filer/meta_aggregator.go

## Purpose

`meta_aggregator.go` implements live metadata aggregation among filer peers. It subscribes to remote filer local metadata streams, stores received events in an in-memory aggregate log buffer for clients, optionally replays changes into the local store when filers do not share the same store signature, and persists per-peer offsets in the filer KV store.

## Important APIs, Types, and Functions

`MetaAggregator` holds the local filer, self address, gRPC dial option, aggregate `LogBuffer`, peer subscription stop channels, and listener condition state. Key methods are `NewMetaAggregator`, `OnPeerUpdate`, `HasRemotePeers`, `HasPeer`, `loopSubscribeToOneFiler`, `doSubscribeToOneFiler`, `traversePeerMetadata`, `readFilerStoreSignature`, `readOffset`, and `updateOffset`. `GetPeerMetaOffsetKey` formats KV keys for peer signatures, and `filerClient` adapts a gRPC client to lookup functions.

## Control Flow

Peer updates add or remove subscription goroutines. Each subscription loop reconnects from the last timestamp and sleeps between failures. On first contact with a peer with a different store signature, the aggregator reads the saved offset; if absent, it performs a full BFS metadata traversal excluding system logs, inserts newer peer entries, then starts streaming from one minute before the traversal start to cover clock skew and concurrent changes.

During streaming, the code subscribes with batching and metadata chunk support, accumulates `LogFileRefs`, decodes referenced persisted logs via `pb.ReadLogFileRefs`, processes direct and batched events, writes every event to `MetaLogBuffer`, calls `Replay` when replication is needed, notifies local filer listeners, and periodically persists offsets.

## State and Persistence Behavior

The aggregate log buffer is in-memory and not re-persisted to disk. Durable state is the per-peer last timestamp stored via `FilerStore.KvPut` under a key derived from peer store signature. Replicated metadata is persisted through the local filer store. Peer subscription state and listener wait counts are process-local.

## Dependencies and Integration Points

The file depends on SeaweedFS master cluster updates, filer gRPC clients, protobuf metadata events, log buffers, metadata replay, persisted log refs, chunk stream readers, and the filer store KV API. It is central to multi-filer metadata convergence and client metadata subscriptions.

## Risks and Edge Cases

Offset keys are based only on peer signature, so signature uniqueness matters. Bootstrap traversal uses entry mtime to resolve insert conflicts but stream timestamps to resume, which is deliberate but easy to confuse. Replaying events can duplicate work, relying on upsert/delete idempotence. Subscription errors loop forever. Listener broadcast only happens when waiters exist. A peer with the same store signature is aggregated for clients but not replayed into the same shared store.

## Test Signals

Tests should cover peer add/remove cancellation, `HasPeer`, first-sync traversal and offset write, offset resume, persisted log refs plus batched events, duplicate local subscription handling, same-signature no-replay behavior, and replay idempotence with duplicate overlap events.
