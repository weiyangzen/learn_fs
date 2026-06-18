# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/physical-zone.c

## Purpose
`physical-zone.c` manages physical zones, PBN locks, and block allocation. It serializes in-flight operations by physical block number, pools lock objects, handles read/write/block-map write lock semantics, manages provisional references, and rotates allocation attempts across zones or waits for slab scrubbing.

## Important APIs, Types, and Functions
Public functions include `vdo_is_pbn_read_lock()`, `vdo_downgrade_pbn_write_lock()`, `vdo_claim_pbn_lock_increment()`, `vdo_assign_pbn_lock_provisional_reference()`, `vdo_unassign_pbn_lock_provisional_reference()`, `vdo_make_physical_zones()`, `vdo_free_physical_zones()`, `vdo_get_physical_zone_pbn_lock()`, `vdo_attempt_physical_zone_pbn_lock()`, `vdo_allocate_block_in_zone()`, `vdo_release_physical_zone_pbn_lock()`, and `vdo_dump_physical_zone()`. Internal structures include `pbn_lock_implementation`, `idle_pbn_lock`, and `pbn_lock_pool`.

## Control Flow
Zone initialization creates an `int_map` for active PBN operations, a fixed lock pool sized for user VIOs, links the zone to a block allocator and next zone, and creates the zone thread. Lock acquisition borrows a lock before insertion to avoid double map access; insertion with `update=false` either installs the new lock or returns an existing lock and returns the spare to the pool. Allocation obtains a block from the current zone allocator, locks it, marks a provisional reference, and returns to the caller. On no-space, the data VIO may cycle through zones or enqueue as a clean-slab waiter before retrying. Release decrements holder count, removes the map entry when last holder exits, releases provisional references, and returns the lock to the pool.

## State and Persistence Behavior
Runtime state includes per-zone active lock map, fixed lock pool, allocator pointer, and next-zone ring. Persistent effects are indirect through block allocator/reference-count changes. Provisional references represent on-disk reference accounting obligations that must be released if a lock is abandoned.

## Dependencies and Integration Points
The file integrates with block allocator/slab depot, data VIO allocation state, wait queues, completions, dedupe/reference update paths, physical thread configuration, `int-map`, VDO constants/status codes, and logging/allocation/assertion helpers.

## Risks and Edge Cases
Lock pool exhaustion is treated as a serious lock error; sizing assumes at most two locks per user VIO. `vdo_attempt_physical_zone_pbn_lock()` contains unreachable assertion code after returning the spare lock, so diagnostics for an existing lock's holder count may not run. Increment claims on read locks are atomic because compressed-block dedupe can involve multiple hash-zone threads. Allocation retry must avoid touching a VIO after it has been dispatched to another zone or waiter. Releasing provisional references on error is critical to avoid reference leaks.

## Test Signals
Test lock acquire existing/new cases, holder-count sharing/release, write-to-read downgrade, increment claim limits, provisional reference assign/release, pool exhaustion fault injection, allocation success/no-space/wait-for-scrub cycling, multi-zone rotation, and cleanup with all locks returned.
