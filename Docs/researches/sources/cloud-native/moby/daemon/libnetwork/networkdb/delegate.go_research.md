# sources/cloud-native/moby/daemon/libnetwork/networkdb/delegate.go

## Purpose
Memberlist delegate implementation for NetworkDB message handling, push/pull state exchange, and event rebroadcast decisions.

## Important APIs, Types, And Functions
`delegate` implements `NodeMeta`, `NotifyMsg`, `GetBroadcasts`, `LocalState`, and `MergeRemoteState`. NetworkDB handlers include `handleNodeEvent`, `handleNetworkEvent`, `handleTableEvent`, `handleCompound`, `handleTableMessage`, `handleNodeMessage`, `handleNetworkMessage`, `handleBulkSync`, and `handleMessage`.

## Control Flow
Incoming gossip is decoded by `handleMessage` and dispatched by message type. Node/network events witness Lamport clocks, reject stale data, update membership/network maps, and rebroadcast fresh state. Table events are accepted only for locally joined, non-leaving networks where the owner is still a network participant; stale Lamport times are ignored. Watch events are synthesized from actual local state transitions rather than raw CREATE/UPDATE/DELETE type alone. Bulk sync handles compound payloads, closes ACK channels for responses, and replies to unsolicited syncs.

## State And Persistence
Mutates in-memory NetworkDB maps, radix indexes, Lamport clocks, broadcast queues, bulk sync ACK table, and local watcher broadcaster. No disk persistence.

## Dependencies And Integration Points
Integrates memberlist delegate hooks with protobuf message types, cluster bulk sync, node management helpers, and upper-layer watchers receiving `WatchEvent`.

## Risks
This is a convergence-critical path. Wrong stale checks can resurrect deleted entries or drop valid updates. Unknown delete handling is deliberately conservative and only rebroadcasts certain bulk-sync tombstones. Holding locks through watcher writes is intentional to avoid duplicate synthesized events, but any broadcaster blocking behavior would be risky. Mixed-version clusters with zero residual reap time are handled with warnings and default reap intervals.

## Test Signals
No direct tests in this subset; behavior is indirectly covered by broader NetworkDB tests outside this item.
