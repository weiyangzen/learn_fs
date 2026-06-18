<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-space-map-disk.c -->
# sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-space-map-disk.c

## Purpose
Implements the public `dm_space_map` wrapper for general disk/data space. It builds on the shared low-level space-map engine and preserves rollback safety by allocating only blocks that are free in both the previous committed map and the current transaction map.

## Important APIs, Types, And Functions
`struct sm_disk` embeds `struct dm_space_map`, current `ll`, committed snapshot `old_ll`, allocation search cursor `begin`, and `nr_allocated_this_transaction`. Its operation table implements destroy, extend, count lookup, set/inc/dec, new block, commit, root size/copy, and no threshold callback.

Public constructors are `dm_sm_disk_create()` and `dm_sm_disk_open()`. Internal operation methods include `sm_disk_get_nr_blocks()`, `sm_disk_get_nr_free()`, `sm_disk_set_count()`, `sm_disk_inc_blocks()`, `sm_disk_dec_blocks()`, `sm_disk_new_block()`, and `sm_disk_commit()`.

## Control Flow
Create initializes an empty low-level disk map, extends it to the requested block count, then commits to seed `old_ll`. Open loads a root and commits the current state into `old_ll`. Increment, decrement, and set operations delegate to low-level functions and accumulate net allocations in `nr_allocated_this_transaction`.

`sm_disk_new_block()` searches from `begin` to the end, then wraps to the beginning, using `sm_ll_find_common_free_block()` so a block must be free in both `old_ll` and `ll`. Once found, it advances `begin`, increments the block's count in the current map, and tracks the allocation. Commit writes low-level index state, copies `ll` into `old_ll`, and resets transaction allocation accounting.

## State And Persistence
Persistent root data is `disk_sm_root`. Runtime state maintains both current and committed snapshots so free space semantics exclude blocks freed only in the current transaction. `get_nr_blocks()` reports committed block count, while extensions are not visible there until commit, matching the `dm_space_map` contract.

## Dependencies And Integration Points
This file depends on `dm-space-map-common`, `dm-space-map`, transaction manager, Linux slab/list/export helpers, and device-mapper logging. It is used by metadata formats that need a space map for provisioned data blocks or other non-self-hosted allocation domains.

## Risks
The rollback-safety rule is critical. Allocating a block freed earlier in the same transaction could make rollback impossible or expose stale metadata/data. `nr_allocated_this_transaction` must be updated for all set/inc/dec/new paths or free-space reporting becomes wrong. `memcpy(&old_ll, &ll, sizeof(...))` copies cache state, so low-level structures must remain safe for value copying.

## Test Signals
Tests should allocate after freeing within the same transaction and verify the freed block is not reused until commit. Other signals include wraparound search behavior, root copy/open round trips, extend visibility only after commit, free-space accounting, and overflow count transitions through the common layer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-space-map-disk.c -->
