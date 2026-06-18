# sources/distributed-fs/beegfs/common/source/common/nodes/TargetMapper.cpp

## Purpose
Implements the mapping from storage target IDs to owning node IDs and coordinates related state in storage pools, target states, and quota stores.

## Important APIs, Types, And Functions
`mapTarget()`, `unmapTarget()`, `unmapByNodeID()`, `syncTargets()`, `getMappingAsLists()`, `getTargetsByNode()`, and attachment methods are implemented.

## Control Flow
`mapTarget()` writes the mapping and detects new targets by size change. New targets are added to the storage-pool store, initial target state is created as probably-offline/good, and quota stores are initialized. If storage-pool add fails, the target mapping is rolled back. Unmap paths remove targets and cascade to attached stores. `syncTargets()` swaps a whole target map and then ensures attached state/quota stores know every target.

## State, Persistence, And Dependencies
State is `targets` under `RWLock` plus non-owning pointers to `TargetStateStore`, `StoragePoolStore`, and `ExceededQuotaPerTarget`. No disk persistence here.

## Integration Points
Node stores use `unmapByNodeID()` on server deletion. Storage-pool management uses target mappings for node association. Request routing resolves target IDs to nodes.

## Risks
Remapping an existing target to a new node does not update storage-pool membership node metadata because side-store initialization runs only for new targets. `syncTargets()` does not remove stale attached state/quota entries that are no longer present. Attached store calls happen while holding this mapper lock, so lock ordering must be consistent.

## Test Signals
Cover new map success/failure rollback, remap existing target, unmap cascade, unmap-by-node multi-remove, sync with added/removed targets, list ordering, and attached-store lock-order stress.
