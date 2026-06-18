# sources/distributed-fs/beegfs/common/source/common/nodes/NodeStoreServers.h

## Purpose
Declares the server-node store and its integration hooks for capacity pools, target mappings, and target state data.

## Important APIs, Types, And Functions
The class exposes add/update/delete/reference/sync APIs, `referenceNodeByTargetID()`, wait-for-first-node, side-store attachment, and log-format helpers. It stores `localNode`, `channelsDirectDefault`, active nodes, and optional side-store pointers.

## Control Flow
The header documents that `setLocalNode()` is intended before multithreading and inserts the local node into `activeNodes`, also adding it to attached capacity pools as low capacity.

## State, Persistence, And Dependencies
State is in memory under `Mutex` except pre-threading local-node setup. Dependencies include `Node`, `NodeCapacityPools`, `TargetMapper`, `TargetStateStore`, and `AbstractNodeStore`.

## Integration Points
Used by server registries and target resolution paths; legacy `NodeStore.h` aliases this type.

## Risks
The `generateID()` default returns invalid, so only management subclasses can assign IDs. `localNode` is owned by the app, not by the store.

## Test Signals
Subclass build tests should verify override behavior, side-store attachment ordering, and local-node insertion assumptions.
