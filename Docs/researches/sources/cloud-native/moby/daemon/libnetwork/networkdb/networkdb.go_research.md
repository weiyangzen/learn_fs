# sources/cloud-native/moby/daemon/libnetwork/networkdb/networkdb.go

## Purpose
Defines the core NetworkDB data model and public API for cluster-scoped membership, per-network peer tracking, and distributed table entries used by libnetwork drivers and service discovery.

## Important APIs, Types, And Functions
Major types are `NetworkDB`, `Config`, `PeerInfo`, `PeerClusterInfo`, internal `node`, `network`, `thisNodeNetwork`, `entry`, and public `TableElem`. Public methods include `DefaultConfig`, `New`, `Join`, `Close`, `ClusterPeers`, `Peers`, `GetEntry`, `CreateEntry`, `UpdateEntry`, `GetTableByNetwork`, `DeleteEntry`, `WalkTable`, `JoinNetwork`, and `LeaveNetwork`. Internal helpers manage node/network membership and dual radix-tree entry indexes.

## Control Flow
`New` builds state and initializes memberlist. Table create/update/delete operations take the lock, validate existing state, increment Lamport table clock, update both radix indexes, unlock, and send table events. Deletes create tombstone entries with residual reap time. `JoinNetwork` increments the network clock, initializes local per-network queues, sends a network join event, records local membership, performs bulk sync with peers, and marks the network in sync. `LeaveNetwork` sends leave, removes local membership, tombstones local-owned entries, hard-deletes remote entries, broadcasts watch deletes, and marks the local network as leaving until reaped.

## State And Persistence
All state is in-memory. Entries are indexed by table path (`/table/network/key`) and network path (`/network/table/key`) in immutable radix trees. Membership is tracked in `nodes`, `failedNodes`, `leftNodes`, `networks`, `thisNodeNetworks`, and `networkNodes`. Atomic counters approximate node and per-network peer counts. Lamport clocks order node/network/table events. Tombstone `reapTime` fields control later garbage collection.

## Dependencies And Integration Points
Integrates with memberlist/serf, Docker logging, event broadcaster, immutable radix trees, string IDs, errdefs/types, and cluster/delegate files in the same package. Libnetwork `Network.Peers` uses this API for dynamic networks.

## Risks
This is concurrency-sensitive distributed state. Callers must join a network before table events are accepted. `GetEntry` intentionally panics if a nil entry exists. Path encoding uses slash-separated table/network/key strings, so keys containing slashes could confuse parsing if allowed by callers. Reap timing and Lamport comparisons must remain consistent to avoid stale resurrection or premature deletion.

## Test Signals
The subset includes random peer sampling tests; broader table, watch, and convergence behavior relies on other NetworkDB tests not listed here.
