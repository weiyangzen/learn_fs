# sources/distributed-fs/beegfs/common/source/common/storage/StoragePool.h

## Purpose
Declares the storage-pool value/object that groups target IDs and mirror buddy group IDs and owns capacity-pool selectors for each.

## Important APIs, Types, And Functions
Constructors create `TargetCapacityPools` and `NodeCapacityPools`; public APIs query/mutate ID, description, targets, buddy groups, and expose capacity-pool pointers. Serialization writes ID, description, members, and both capacity pools. Shared-pointer serialization helpers and virtual `initFromDesBuf()` support derived pool types.

## Control Flow
Comparison operators compare only numeric pool IDs. Friend `StoragePoolStore` can lock and call unlocked helpers for compound moves.

## State, Persistence, And Dependencies
State includes pool ID, description, `Mutex`, member sets, and shared capacity-pool objects. Serialized state includes both explicit membership and capacity-pool snapshots.

## Integration Points
Used by `StoragePoolStore`, target placement, buddy group placement, and pool-management messages.

## Risks
Serializing both member sets and capacity pools can diverge if update paths miss a side effect. Copy construction is deleted, so containers use shared pointers or value vectors carefully.

## Test Signals
Serialization consistency between member sets and capacity pools, derived `initFromDesBuf()`, comparison by ID, and default constructor behavior should be tested.
