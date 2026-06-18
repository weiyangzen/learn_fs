# sources/distributed-fs/beegfs/common/source/common/nodes/NodeStoreClients.cpp

## Purpose
Implements the client-node store: a mutex-protected map from numeric client node IDs to `NodeHandle`s with add/update/delete/reference/sync operations.

## Important APIs, Types, And Functions
`addOrUpdateNode()`, `addOrUpdateNodeEx()`, `referenceNode()`, `referenceFirstNode()`, `deleteNode()`, `referenceAllNodes()`, `isNodeActive()`, `getSize()`, and `syncNodes()` are implemented.

## Control Flow
Adds generate an ID if absent via virtual `generateID()`, update existing nodes only if aliases match, update heartbeat/interface data, set client channels indirect, insert new nodes, and broadcast `newNodeCond`. `syncNodes()` assumes ordered active/master maps, computes added and removed IDs while locked, then unlocks and applies removals/adds to preserve virtual override behavior.

## State, Persistence, And Dependencies
State is the inherited store type plus `activeNodes`, `mutex`, and `newNodeCond`. It depends on `AbstractNodeStore`, `Node`, `NumNodeID`, and BeeGFS logging. No disk persistence.

## Integration Points
Used by management or server components tracking connected clients. It differs from `NodeStoreServers` by keeping alias collision rejection strict and not attaching capacity/target/state side stores.

## Risks
`generateID()` returns invalid by default, so only subclasses that implement ID generation can accept nodes without numeric IDs. `syncNodes()` relies on sorted `masterList`. Alias mismatches invalidate output ID but still return `Unchanged`, so callers must inspect `outNodeNumID` when provided.

## Test Signals
Test add, update, alias collision, generated-ID subclass behavior, delete, reference-all snapshot, sync add/remove ordering, and unsorted master-list failure modes.
