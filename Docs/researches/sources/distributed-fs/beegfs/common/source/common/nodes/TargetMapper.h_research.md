# sources/distributed-fs/beegfs/common/source/common/nodes/TargetMapper.h

## Purpose
Declares the target-to-node mapping service and its side-store attachment hooks.

## Important APIs, Types, And Functions
Public APIs map/unmap/sync/query targets and attach target-state, storage-pool, and quota stores. Inline getters provide node lookup, size, existence, and full mapping copy.

## Control Flow
The API promises `NumNodeID{}` for unknown targets and `std::pair<FhgfsOpsErr,bool>` for mapping outcomes.

## State, Persistence, And Dependencies
`targets` is protected by `RWLock`. Attached store pointers are non-owning. Depends on `StoragePoolStore`, `TargetCapacityPools` type aliases, `TargetStateStore`, and quota stores.

## Integration Points
Central integration point for target routing, state initialization, pool membership, and quota tracking.

## Risks
Non-owning side stores must outlive the mapper. Copying full mappings can be expensive for large clusters.

## Test Signals
Verify unknown target zero semantics, map copy consistency under concurrent mutation, and side-store attachment sequencing.
