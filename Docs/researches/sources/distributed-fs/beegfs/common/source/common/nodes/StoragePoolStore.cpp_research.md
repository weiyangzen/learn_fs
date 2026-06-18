# sources/distributed-fs/beegfs/common/source/common/nodes/StoragePoolStore.cpp

## Purpose
Implements the storage-pool registry that owns `StoragePool` objects and enforces one-pool membership for storage targets and buddy groups.

## Important APIs, Types, And Functions
Defines constants for default/invalid/max pool IDs and implements `createPool()`, `moveTarget()`, `moveBuddyGroup()`, `setPoolDescription()`, `addTarget()`, `removeTarget()`, `addBuddyGroup()`, `removeBuddyGroup()`, `findFreeID()`, pool getters, `syncFromVector()`, and `getSize()`.

## Control Flow
Construction creates the default pool unless skipped. `createPool()` chooses an ID if requested, inserts a new pool, then moves requested buddy groups and targets from the default pool only. Move operations resolve source/destination pools, remove from the old pool, and add to the new pool, moving buddy-group member targets as well when a buddy mapper is present. Adds scan all pools to prevent duplicate membership. Removal scans pools and returns the pool ID from which an item was removed.

## State, Persistence, And Dependencies
State is `storagePools` protected by `RWLock`, plus pointers to `MirrorBuddyGroupMapper` and `TargetMapper`. Serialization/deserialization is declared in the header and stores pool values. Dependencies include `StoragePool`, `FhgfsOpsErr`, buddy group mapping, target mapping, and logging.

## Integration Points
`TargetMapper` auto-adds/removes targets when mappings change. `StoragePool` capacity pools are used by placement. Management operations create/move/query pools.

## Risks
`addBuddyGroup()` returns `FhgfsOpsErr_EXISTS` after a successful new add, which looks like a bug and can make callers treat success as failure. `moveTarget()` takes only a read lock on the pool map while mutating individual pools; the pool map is stable but lock-order interactions matter. Pool creation can partially succeed and return `INVAL` after the pool has been inserted with only successful moves. Target node lookup during moves may return zero if `TargetMapper` is stale.

## Test Signals
Cover default pool creation, generated IDs, duplicate IDs, create with valid/invalid target sets, partial failure semantics, target and buddy moves, buddy target movement, duplicate add behavior, the `addBuddyGroup()` return code, serialization/deserialization, and concurrent add/move/remove.
