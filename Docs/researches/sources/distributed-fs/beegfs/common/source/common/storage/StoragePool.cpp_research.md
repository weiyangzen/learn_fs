# sources/distributed-fs/beegfs/common/source/common/storage/StoragePool.cpp

## Purpose
Implements a single storage pool's membership and capacity-pool side effects for targets and buddy groups.

## Important APIs, Types, And Functions
Implements target add/remove/has/get/get-and-remove, buddy-group add/remove/has/get/get-and-remove, description getter/setter, and ID getter.

## Control Flow
Public mutators lock `mutex` and call unlocked helpers. Adding a new target inserts into `members.targets` and adds it to `targetsCapacityPools` as low capacity. Removing a target removes it from both members and capacity pools. Buddy group operations mirror this with `buddyCapacityPools`. Bulk get-and-remove swaps the member set out and removes each ID from the corresponding capacity pool.

## State, Persistence, And Dependencies
State is `id`, `description`, member target/buddy sets, and owned target/buddy capacity pool objects declared in the header. No disk I/O here; serialization is in the header.

## Integration Points
Owned by `StoragePoolStore`; target and buddy mapping changes use this object to keep placement pools aligned.

## Risks
New targets/buddy groups default to `CapacityPool_LOW` until dynamic capacity updates move them. Unlocked helpers require external locking, especially when moving buddy groups and associated targets between pools.

## Test Signals
Test duplicate add idempotence, capacity-pool side effects, bulk removal, description locking, and move helpers through `StoragePoolStore`.
