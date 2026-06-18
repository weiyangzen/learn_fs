# sources/distributed-fs/beegfs/common/source/common/nodes/StoragePoolStore.h

## Purpose
Declares the storage-pool registry and its serialization hooks.

## Important APIs, Types, And Functions
Static IDs define default and invalid pools. Public APIs create pools, move targets/buddy groups, set descriptions, add/remove/query items, sync from vectors, and export pool vectors. Protected hooks include `makePool()` for subclasses and map-value serialization/deserialization.

## Control Flow
The serialization helpers write only pool values and rebuild keys from each pool ID during deserialization, using virtual `initFromDesBuf()` so derived pool types can participate.

## State, Persistence, And Dependencies
`storagePools` is protected by `RWLock`. Pointers to buddy and target mappers are non-owning integration hooks. Serialized state includes pool contents and capacity-pool data via `StoragePool`.

## Integration Points
The store sits between target mapping, mirror buddy mapping, capacity-pool selection, and management pool operations.

## Risks
Non-owning mapper pointers must outlive the store. No explicit default-pool invariant check exists after `syncFromVector()` or deserialization.

## Test Signals
Subclass serialization, missing default pool after sync, non-owning pointer lifetime in fixtures, and pool ID key reconstruction should be tested.
