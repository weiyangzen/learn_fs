# sources/distributed-fs/beegfs/common/source/common/nodes/NodeStoreServers.cpp

## Purpose
Implements the server-node store for metadata, storage, and management nodes. It tracks active nodes, handles alias updates, synchronizes from management lists, and propagates node removals to capacity pools, target mappers, and target state stores.

## Important APIs, Types, And Functions
Core functions include `addOrUpdateNodeEx()`, `addOrUpdateNodeUnlocked()`, `referenceNode()`, `referenceFirstNode()`, `referenceNodeByTargetID()`, `deleteNode()`, `referenceAllNodes()`, `waitForFirstNode()`, `syncNodes()`, attachment setters, `retrieveNumIDFromStringID()`, and node-ID formatting helpers.

## Control Flow
Adds reject empty aliases, generate numeric IDs if a subclass supports it, update local-node alias only, update remote aliases and interfaces, enforce store/node type compatibility, set connection-pool directness, and broadcast waiters on new nodes. Deletes refuse the local node and forward removal to optional side stores. `syncNodes()` performs an ordered diff under lock, unlocks, deletes removed IDs, sets local NIC capabilities on incoming nodes, and then add/updates them.

## State, Persistence, And Dependencies
State is `activeNodes`, optional `localNode`, channel directness default, and optional pointers to `NodeCapacityPools`, `TargetMapper`, and `TargetStateStore`. It depends on `MirrorBuddyGroupMapper` only indirectly through includes, plus logging, boost formatting, mutexes, and node/network types.

## Integration Points
Storage target resolution uses `referenceNodeByTargetID()` with `TargetMapper`. Internode sync and heartbeat handling feed `addOrUpdateNodeEx()` and `syncNodes()`. Attached stores keep capacity/target/state data consistent when nodes disappear.

## Risks
`setLocalNode()` is documented as pre-threading and mutates without locking. `syncNodes()` requires an ordered master list. Alias updates from stale heartbeats can temporarily roll back aliases as noted in comments. `stateStore->removeTarget(id.val())` assumes node IDs correspond to state IDs for that store type, which is valid only for node-style state stores.

## Test Signals
Cover local-node alias update, remote alias update, empty alias rejection, type mismatch exception, target-ID reference errors, deletion side effects, wait timeout/signal behavior, sync ordering, and local node preservation during sync.
