# Group Research: group_743_linux_sources_os_linux_linux_fs_ext4_mballoc_c_sources_os_linux_linu_eb059c430bbe

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext4/mballoc.c -->
# File Research: sources/os/linux/linux/fs/ext4/mballoc.c

## Purpose

Implements ext4's multiblock allocator: block/cluster allocation, preallocation, buddy cache management, delayed freeing, discard/TRIM, allocator statistics, and KUnit-visible test hooks. It is the main allocator behind `ext4_mb_new_blocks()` and `ext4_free_blocks()`.

## Major Responsibilities

- Builds and maintains per-block-group in-memory buddy bitmaps from on-disk block bitmaps plus active preallocation descriptors.
- Supports inode preallocation for larger/streaming files and locality-group preallocation for small file clustering.
- Searches for free space using multiple criteria:
  - `CR_POWER2_ALIGNED`
  - `CR_GOAL_LEN_FAST`
  - `CR_BEST_AVAIL_LEN`
  - `CR_GOAL_LEN_SLOW`
  - `CR_ANY_FREE`
- Optionally accelerates group selection with xarrays keyed by largest free order and average fragment size when `MB_OPTIMIZE_SCAN` is enabled.
- Updates on-disk bitmaps, group descriptors, flex group counters, quota, and journal metadata.
- Defers reuse of journaled freed metadata/data blocks until commit via `ext4_free_data`.
- Issues discard/TRIM for freed or explicitly trimmed extents.

## Key Data and Caches

- `ext4_pspace_cachep`: slab cache for `struct ext4_prealloc_space`.
- `ext4_ac_cachep`: slab cache for `struct ext4_allocation_context`.
- `ext4_free_data_cachep`: slab cache for delayed free records.
- `ext4_groupinfo_caches[]`: block-size-specific slab caches for `struct ext4_group_info`.
- `s_buddy_cache`: synthetic inode storing buddy-cache folios, two logical blocks per block group: bitmap then buddy.
- `s_mb_largest_free_orders[]`: xarrays of groups by largest free buddy order.
- `s_mb_avg_fragment_size[]`: xarrays of groups by average free fragment order.
- Per-CPU `discard_pa_seq`: sequence signal used to decide whether allocation should retry after preallocation discard activity.

## Allocation Flow

`ext4_mb_new_blocks()` is the main entry point.

1. Handles fast commit replay with `ext4_mb_new_blocks_simple()`.
2. Claims free cluster reservations and quota unless delayed allocation already reserved space.
3. Allocates and initializes `ext4_allocation_context`.
4. Chooses inode vs group preallocation policy with `ext4_mb_group_or_file()`.
5. Attempts existing preallocation via `ext4_mb_use_preallocated()`.
6. If no PA is usable:
   - normalizes request with `ext4_mb_normalize_request()`;
   - allocates a PA descriptor;
   - searches buddy state with `ext4_mb_regular_allocator()`.
7. Marks selected clusters on disk with `ext4_mb_mark_diskspace_used()`.
8. Releases context, updates PA state, drops pinned buddy folios, unlocks locality group, and collects stats.

The allocator can retry after ENOSPC-like failure by discarding preallocations through `ext4_mb_discard_preallocations_should_retry()`.

## Buddy Cache and Group Scanning

`ext4_mb_load_buddy_gfp()` loads bitmap and buddy folios for a group, initializing them if needed through `ext4_mb_init_group()` and `ext4_mb_init_cache()`.

Buddy generation:
- Copies on-disk bitmap into the cache.
- Marks active preallocations as used via `ext4_mb_generate_from_pa()`.
- Builds higher-order buddy structures with `ext4_mb_generate_buddy()`.
- Maintains `bb_free`, `bb_fragments`, `bb_counters[]`, `bb_first_free`, largest free order, and average fragment order.

Scanning:
- `ext4_mb_find_by_goal()` first checks the goal extent.
- `ext4_mb_scan_groups()` chooses linear or optimized scan.
- `ext4_mb_scan_group()` filters groups, loads buddy state, locks the group, then scans.
- `ext4_mb_simple_scan_group()` handles power-of-two requests.
- `ext4_mb_complex_scan_group()` walks free extents in the bitmap.
- `ext4_mb_scan_aligned()` handles stripe-aligned allocation attempts.

## Preallocation Handling

Preallocation descriptors are represented by `struct ext4_prealloc_space`.

- Inode PAs are stored in an inode rbtree keyed by logical start.
- Group/locality PAs are stored in per-CPU locality group lists bucketed by free length order.
- `ext4_mb_new_inode_pa()` and `ext4_mb_new_group_pa()` create new descriptors after over-allocation.
- `ext4_mb_use_inode_pa()` and `ext4_mb_use_group_pa()` consume existing descriptors.
- `ext4_mb_put_pa()` removes and frees fully consumed descriptors.
- `ext4_discard_preallocations()` discards all inode PAs.
- `ext4_mb_discard_group_preallocations()` discards all reclaimable PAs in a block group.
- `ext4_mb_discard_lg_preallocations()` trims locality group lists when buckets grow too large.

The PA logic is highly lock-sensitive: inode PA trees use `i_prealloc_lock`, group PA lists use locality locks plus RCU, and group lists are synchronized with group locks to avoid buddy initialization races.

## Freeing and Deferred Reuse

`ext4_free_blocks()` validates and normalizes block ranges, handles buffer forgetting, cluster boundary expansion, and delegates to `ext4_mb_clear_bb()`.

`ext4_mb_clear_bb()`:
- Verifies block validity.
- Loads buddy state.
- Clears bits in the on-disk bitmap with `ext4_mb_mark_context()`.
- Either queues freed clusters in `bb_free_root`/`s_freed_data_list` until journal commit or immediately returns them to buddy state.
- Updates quota and free-cluster counters unless the caller requested special handling.

`ext4_process_freed_data()` runs after journal commit and calls `ext4_free_data_in_buddy()` to make delayed frees reusable. Optional discard work is queued afterward.

## TRIM and Range Query

- `ext4_trim_fs()` implements filesystem-wide FITRIM.
- `ext4_trim_all_free()` trims one group.
- `ext4_try_to_trim_range()` scans free extents and calls `ext4_trim_extent()`.
- `ext4_trim_extent()` temporarily marks the extent used in buddy state while issuing discard, preventing concurrent allocation.
- `ext4_mballoc_query_range()` iterates free extents in a group for metadata consumers.

## Initialization and Teardown

- `ext4_init_mballoc()` creates global slab caches.
- `ext4_mb_init()` initializes per-superblock allocator structures, xarrays, locality groups, tunables, buddy cache inode, and group info.
- `ext4_mb_release()` flushes discard work, frees group info, active PAs, buddy cache inode, xarrays, and locality groups.
- `ext4_exit_mballoc()` destroys caches after `rcu_barrier()`.

## Concurrency and Consistency

Critical synchronization:
- Block group lock protects group buddy/bitmap/group-info mutation.
- Inode `i_data_sem` serializes data block allocation paths.
- PA locks protect descriptor fields.
- Locality group mutex serializes group PA allocation.
- RCU protects group info and locality PA traversal.
- Buddy folio pinning prevents reinitialization while allocated bits have not yet reached disk.

The file includes extensive comments describing consistency between on-disk bitmap, in-core buddy, and PA descriptors.

## Error Handling and Corruption Defense

- Detects free-space count mismatches between bitmaps and group descriptors.
- Marks group block bitmaps corrupt with `EXT4_GROUP_INFO_BBITMAP_CORRUPT`.
- Validates allocation/freeing against filesystem metadata zones.
- Handles fast commit replay idempotently through simplified bitmap marking.
- Uses `AGGRESSIVE_CHECK` and `DOUBLE_CHECK` optional debug paths for buddy and bitmap consistency.
- Uses `WARN_ON`, `BUG_ON`, and `ext4_grp_locked_error()` in invariant-violation paths.

## Test Hooks

When `CONFIG_EXT4_KUNIT_TESTS` is enabled, wrappers export selected internal helpers, including bit operations, simple allocation, buddy generation/load/unload, diskspace marking, and free-block helpers.

## Research Notes

This file is central to ext4 correctness and performance. The most fragile areas are PA lifetime/race handling, buddy/on-disk bitmap synchronization, journal-delayed reuse, bigalloc cluster rounding, and optimized group xarray maintenance.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext4/mballoc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext4/mballoc.h -->
# File Research: sources/os/linux/linux/fs/ext4/mballoc.h

## Purpose

Declares ext4 multiblock allocator data structures, defaults, helper functions, query callback types, and KUnit test entry points shared by `mballoc.c` and ext4 internals.

## Key Defaults and Constants

- `MB_DEFAULT_MAX_TO_SCAN`: default maximum found extents to scan before settling.
- `MB_DEFAULT_MIN_TO_SCAN`: minimum found extents to inspect for a good fit.
- `MB_DEFAULT_STATS`: default allocator stats collection setting.
- `MB_DEFAULT_STREAM_THRESHOLD`: small-file stream/locality threshold.
- `MB_DEFAULT_ORDER2_REQS`: minimum order for buddy power-of-two search.
- `MB_DEFAULT_GROUP_PREALLOC`: default group preallocation length.
- `MB_DEFAULT_LINEAR_LIMIT`: rotational-device linear group scan limit before optimized scan.
- `MB_DEFAULT_LINEAR_SCAN_THRESHOLD`: minimum groups for scan optimization.
- `MB_DEFAULT_BEST_AVAIL_TRIM_ORDER`: max trim order for best-available allocation.
- `MB_NUM_ORDERS(sb)`: valid buddy order count derived from block size.

## Main Structures

`struct ext4_free_data`
- Tracks clusters freed by a transaction but not yet reusable.
- Linked both globally through `efd_list` and per group through `efd_node`.
- Stores group, start cluster, count, and freeing transaction id.

`struct ext4_prealloc_space`
- Represents inode or locality-group preallocation.
- Uses an rbtree node for inode PAs or list node for locality PAs.
- Also links into the block group's PA list.
- Tracks physical start, logical start, length, free count, type, deletion state, reference count, and owner lock.

`struct ext4_free_extent`
- Describes an allocator extent: logical block, group-relative cluster start, group, and cluster length.

`struct ext4_locality_group`
- Per-CPU small-file preallocation context.
- Contains a mutex and hash buckets of group PAs by remaining free length order.

`struct ext4_allocation_context`
- Per-allocation working state.
- Stores original, normalized goal, best-found, and final extents.
- Tracks scan stats, criteria, status, flags, prefetch state, PA pointer, locality group, and pinned buddy folios.

`struct ext4_buddy`
- Loaded view of one block group’s buddy and bitmap folios plus group info and superblock.

## Helpers

- `ext4_grp_offs_to_block()` converts group-relative cluster offset to physical block.
- `extent_logical_end()` computes logical end of a free extent using cluster-to-block conversion.
- `pa_logical_end()` computes logical end of a preallocation descriptor.
- `ext4_mballoc_query_range_fn` defines callbacks for free-range iteration.

## External Interfaces

- `ext4_mballoc_query_range()` iterates free extents in a group.
- `ext4_mb_mark_context()` updates block bitmap/group descriptor state and optionally reports changed clusters.
- KUnit-only declarations expose selected internal allocator primitives for ext4 tests.

## Research Notes

This header captures allocator state contracts rather than policy. The important correctness details are PA ownership/lifetime fields, cluster-unit vs block-unit conversions, and `ac_*` extent roles in `ext4_allocation_context`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext4/mballoc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext4/migrate.c -->
# File Research: sources/os/linux/linux/fs/ext4/migrate.c

## Purpose

Implements inode block mapping migration between legacy indirect block mapping and extent mapping.

It provides:
- `ext4_ext_migrate()`: converts an indirect-mapped inode to extents.
- `ext4_ind_migrate()`: converts a simple extent-mapped inode back to direct block pointers.

## Indirect to Extents

`ext4_ext_migrate()` converts a non-extent inode into extent format by building a temporary extent inode and swapping its extent tree into the original inode.

Flow:
1. Rejects unsupported cases:
   - filesystem lacks extents;
   - inode already uses extents;
   - inode has inline data;
   - fast symlink with no blocks.
2. Starts a migrate journal transaction and marks fast commit ineligible.
3. Creates a temporary hidden inode near the original inode’s group.
4. Copies checksum seed and size into the temporary inode.
5. Initializes the temp inode extent tree.
6. Sets `EXT4_STATE_EXT_MIGRATE` under `i_data_sem` to detect racing allocation.
7. Traverses original direct, indirect, double-indirect, and triple-indirect mappings.
8. Coalesces contiguous logical/physical ranges into extents with `update_extent_range()`.
9. Inserts extents into the temporary inode via `finish_range()`.
10. Swaps extent data into the original inode with `ext4_ext_swap_inode_data()`.
11. Frees old indirect metadata blocks.
12. Resets and drops the temporary inode.

## Traversal Helpers

- `update_extent_range()` maintains the currently coalesced logical/physical run.
- `finish_range()` inserts the accumulated range as an extent into the temp inode.
- `update_ind_extent_range()` scans one indirect block.
- `update_dind_extent_range()` scans a double-indirect block.
- `update_tind_extent_range()` scans a triple-indirect block.

Sparse holes advance `curr_block` without inserting extents.

## Freeing Old Metadata

- `free_ind_block()` frees indirect, double-indirect, and triple-indirect metadata roots.
- `free_dind_blocks()` frees indirect blocks beneath a double-indirect block, then the double-indirect block itself.
- `free_tind_blocks()` recursively frees double-indirect trees beneath a triple-indirect block, then the triple-indirect block.
- All metadata freeing uses journal credit extension and `ext4_free_blocks()` with metadata/forget flags.

## Swapping Data

`ext4_ext_swap_inode_data()`:
- Saves original indirect block roots.
- Takes `i_data_sem`.
- Verifies `EXT4_STATE_EXT_MIGRATE` is still set; if allocation raced, returns `-EAGAIN`.
- Sets `EXT4_INODE_EXTENTS`.
- Copies temp inode `i_data` into the original inode.
- Adds temp inode `i_blocks` for newly allocated extent metadata.
- Frees old indirect blocks and marks the inode dirty.

## Extents to Indirect

`ext4_ind_migrate()` only supports very simple extent files:
- filesystem must support extents;
- inode must currently use extents;
- bigalloc is rejected;
- delayed allocation is forced out first;
- extent tree must have depth 0 and at most one extent;
- extent must fit in direct blocks (`EXT4_NDIR_BLOCKS`).

It clears the extent flag, zeroes `i_data`, fills direct block entries from the single extent, and marks the inode dirty.

## Concurrency and Journaling

- Uses `ext4_writepages_down_write()`/`up_write()` around migrations.
- Uses `i_data_sem` to protect inode mapping mutation.
- Uses `EXT4_STATE_EXT_MIGRATE` to detect allocation races during indirect-to-extent conversion.
- Marks fast commit ineligible because mapping-layout rewrites are not represented in fast commit logs.
- Repeatedly ensures journal credits before extent insertion and metadata freeing.

## Error Handling

- On failed extent construction, frees temp extent metadata with `free_ext_block()`.
- On failed swap, frees temp extent metadata.
- Temporary inode is reset to size zero and `i_blocks = 0` before eviction.
- I/O errors from metadata block reads and journal credit failures propagate.

## Research Notes

This file is a conservative migration utility. The indirect-to-extent path handles full indirect trees, while the reverse migration intentionally supports only a shallow, single-extent direct-block-compatible case.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext4/migrate.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ext4/mmp.c -->
# File Research: sources/os/linux/linux/fs/ext4/mmp.c

## Purpose

Implements ext4 Multiple Mount Protection (MMP), which prevents the same filesystem from being mounted read-write by multiple nodes at the same time.

## Checksum Handling

- `ext4_mmp_csum()` computes checksum over the MMP structure up to `mmp_checksum`.
- `ext4_mmp_csum_verify()` validates checksums when metadata checksums are enabled.
- `ext4_mmp_csum_set()` updates checksum before writes.

## MMP Block I/O

`read_mmp_block()`:
- Forces a fresh read by clearing buffer uptodate state.
- Uses priority metadata read.
- Validates magic and checksum.
- Releases the buffer and warns on failure.

`write_mmp_block_thawed()`:
- Updates checksum.
- Submits synchronous prioritized metadata write.
- Waits for completion and returns `-EIO` if write failed.

`write_mmp_block()` wraps writes with superblock freeze protection so kmmpd does not dirty buffers on a frozen filesystem.

## Diagnostic Output

`__dump_mmp_msg()` logs the failure reason plus last update time, node name, and block device name from the MMP block. It is used when another active writer or fsck is detected.

## kmmpd Thread

`kmmpd()` is the background MMP updater.

Behavior:
1. Initializes MMP timestamp, node name, and check interval.
2. Loops until stopped or emergency state.
3. Verifies the MMP feature remains enabled.
4. Increments and writes `mmp_seq`.
5. Sleeps for the update interval.
6. If the elapsed time exceeds the check interval, rereads the MMP block and verifies that sequence and node name still match.
7. Adjusts check interval based on observed write/sleep timing.
8. On clean exit, writes `EXT4_MMP_SEQ_CLEAN`.

If it detects overwritten MMP state, it logs details, aborts the filesystem with `EBUSY`, and waits to be stopped.

## Startup Protection

`ext4_multi_mount_protect()` runs during mount.

Flow:
1. Validates the configured MMP block lies inside the filesystem.
2. Reads and validates the MMP block.
3. Computes a check interval from superblock and on-disk MMP fields.
4. Handles special states:
   - `EXT4_MMP_SEQ_CLEAN`: skip initial wait.
   - `EXT4_MMP_SEQ_FSCK`: fail with `-EBUSY`.
5. If sequence is active, waits and rereads to see whether another node updates it.
6. Writes a new random sequence.
7. Waits again and rereads to ensure the sequence remains unchanged.
8. Stores the MMP buffer in `s_mmp_bh`, records block device name, and starts `kmmpd`.

Failure releases the buffer and returns an error such as `-EINVAL`, `-EFSCORRUPTED`, `-EFSBADCRC`, `-ETIMEDOUT`, `-EBUSY`, or `-ENOMEM`.

## Shutdown

`ext4_stop_mmpd()` stops the updater thread, releases the MMP buffer, and clears `s_mmp_tsk`.

## Concurrency and Safety

- Startup writes use `write_mmp_block_thawed()` because mount/remount already protects against freezing.
- Runtime writes use `write_mmp_block()` with freeze protection.
- MMP read/write uses synchronous prioritized metadata I/O to reduce latency and avoid stale device-cache behavior.
- Random sequence generation uses `get_random_u32_below()` bounded by `EXT4_MMP_SEQ_MAX`.

## Research Notes

This file is small but safety-critical. Its correctness depends on conservative wait intervals, fresh reads, synchronous writes, checksum validation, and aborting promptly if the MMP block no longer matches the local updater’s sequence/node identity.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ext4/mmp.c -->