# subset-b-005653 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/mballoc.c -->
# sources/distributed-fs/ceph-client/fs/ext4/mballoc.c

## Purpose
`mballoc.c` implements ext4's multiblock allocator: the block/cluster allocation, preallocation, free, discard/TRIM, and allocator-statistics machinery used by ext4 regular data and metadata allocation paths. It keeps an in-memory buddy view of each block group's free clusters, overlays active preallocation descriptors on top of the on-disk block bitmap, and updates persistent bitmaps and group descriptors under journal control.

This file is not just a search routine. It owns the lifecycle of allocator state (`ext4_mb_init()`/`ext4_mb_release()` and module slab caches), the public allocation/free entry points (`ext4_mb_new_blocks()`, `ext4_free_blocks()`, `ext4_group_add_blocks()`), fast-commit replay helpers, delayed post-commit freeing (`ext4_process_freed_data()`), fstrim handling (`ext4_trim_fs()`), and range query support (`ext4_mballoc_query_range()`).

## Important APIs, Types, And Functions
Allocator entry points are `ext4_mb_new_blocks()`, `ext4_free_blocks()`, `ext4_group_add_blocks()`, `ext4_trim_fs()`, `ext4_mballoc_query_range()`, `ext4_discard_preallocations()`, `ext4_process_freed_data()`, `ext4_mb_mark_bb()`, `ext4_mb_prefetch()`, `ext4_mb_prefetch_fini()`, `ext4_mb_init()`, `ext4_mb_release()`, `ext4_init_mballoc()`, and `ext4_exit_mballoc()`.

Core state comes from `mballoc.h`: `struct ext4_allocation_context` carries the original, normalized goal, best, and final extents plus scan criteria, prefetch state, flags, selected PA, locality group, and pinned buddy-cache folios. `struct ext4_buddy` binds a loaded block group's in-core bitmap, buddy bitmap, group info, folios, and superblock. `struct ext4_prealloc_space` tracks inode or locality-group preallocations. `struct ext4_free_data` records blocks freed in a still-uncommitted journal transaction.

Important internal groups are:

- Bitmap and buddy primitives: `mb_test_bit()`, `mb_set_bit()`, `mb_clear_bit()`, `mb_find_next_zero_bit()`, `mb_find_next_bit()`, `mb_set_bits()`, `mb_clear_bits()`, `mb_mark_used()`, `mb_free_blocks()`, `mb_find_extent()`, and `ext4_mb_generate_buddy()`.
- Buddy cache lifecycle: `ext4_mb_init_cache()`, `ext4_mb_init_group()`, `ext4_mb_load_buddy_gfp()`, `ext4_mb_unload_buddy()`, and `ext4_mb_generate_from_pa()`.
- Group selection: `ext4_mb_find_by_goal()`, `ext4_mb_regular_allocator()`, `ext4_mb_scan_groups()`, `ext4_mb_scan_group()`, `ext4_mb_good_group_nolock()`, `ext4_mb_good_group()`, `ext4_mb_simple_scan_group()`, `ext4_mb_complex_scan_group()`, and `ext4_mb_scan_aligned()`.
- Optimized scan structures: `mb_set_largest_free_order()`, `mb_update_avg_fragment_size()`, `ext4_mb_scan_groups_p2_aligned()`, `ext4_mb_scan_groups_goal_fast()`, and `ext4_mb_scan_groups_best_avail()`, which use xarrays hanging off `ext4_sb_info`.
- Preallocation lifecycle: `ext4_mb_use_preallocated()`, `ext4_mb_normalize_request()`, `ext4_mb_new_preallocation()`, `ext4_mb_new_inode_pa()`, `ext4_mb_new_group_pa()`, `ext4_mb_release_context()`, `ext4_mb_put_pa()`, `ext4_mb_discard_group_preallocations()`, `ext4_discard_preallocations()`, and locality-group trimming helpers.
- Persistent bitmap updates: `ext4_mb_mark_context()` marks or clears on-disk bitmap bits, updates group/flex counters and checksums, and dirties metadata buffers. `ext4_mb_mark_diskspace_used()` validates and persists a chosen allocation.

## Control Flow
`ext4_mb_new_blocks()` is the main allocation flow. It handles fast-commit replay with `ext4_mb_new_blocks_simple()`, reserves clusters and quota for normal allocations, allocates an `ext4_allocation_context`, initializes it from `struct ext4_allocation_request`, and decides whether the request should use inode preallocation, locality-group preallocation, stream allocation, or no preallocation. It first tries `ext4_mb_use_preallocated()`. If no PA satisfies the request, it normalizes the request to a larger/aligned goal, allocates a PA descriptor, and calls `ext4_mb_regular_allocator()`.

`ext4_mb_regular_allocator()` tries the exact goal first, then scans groups through increasingly permissive criteria: `CR_POWER2_ALIGNED`, `CR_GOAL_LEN_FAST`, `CR_BEST_AVAIL_LEN`, `CR_GOAL_LEN_SLOW`, and finally `CR_ANY_FREE`. Optimized scan mode consults per-order xarrays for largest-free-order and average-fragment-size groups, after an optional small linear scan for locality on rotational devices. Each candidate group is checked without loading the buddy when possible, then the buddy is loaded, the group is locked, suitability is rechecked, and the group scanner either finds a power-of-two free buddy, a stripe-aligned run, or a measured bitmap extent.

Once a best extent is selected, `ext4_mb_use_best_found()` marks it used in the in-core buddy, pins the bitmap and buddy folios to prevent reinitialization races, records stream-allocation group hints, and creates a new inode or group PA if the normalized allocation is larger than the original request. `ext4_mb_mark_diskspace_used()` then persists the selected extent by setting the on-disk bitmap and decrementing free counts. On error, `ext4_discard_allocated_blocks()` reverses the in-core allocation or restores PA accounting.

Freeing flows through `ext4_free_blocks()`. It validates the range, forgets buffers when requested, expands or shrinks partial bigalloc clusters according to flags, and calls `ext4_mb_clear_bb()`. That function clears bits on disk via `ext4_mb_mark_context()` and either delays reuse through `ext4_mb_free_metadata()` until the freeing transaction commits, or immediately discards/reinserts clusters into the buddy with `mb_free_blocks()`. `ext4_process_freed_data()` is later invoked from jbd2 commit completion to move transaction-safe freed ranges into the buddy and optionally queue asynchronous discard work.

TRIM flows from `ext4_trim_fs()` over the groups covering the requested byte range. Each group is initialized if needed, then `ext4_trim_all_free()` loads its buddy and `ext4_try_to_trim_range()` walks free extents above the minimum size. `ext4_trim_extent()` temporarily marks a free extent used under the group lock, drops the lock to issue discard, then reacquires the lock and frees the range back into the buddy.

`ext4_mballoc_query_range()` provides a callback-based iterator over free extents in a group. It loads the buddy, starts at `max(bb_first_free, first)`, optionally reports the metadata/prefix range via `meta_formatter`, and calls `formatter` for each free extent while dropping the group lock around callbacks.

## State And Persistence Behavior
The persistent state is the block bitmap, group descriptor free-cluster count, flex-group free-cluster count, metadata checksums, quota accounting, and journaled metadata buffers. `ext4_mb_mark_context()` is the central persistence primitive: it reads the group bitmap, obtains journal write access when a handle is present, clears `EXT4_BG_BLOCK_UNINIT` if necessary, sets or clears bitmap bits, adjusts group/flex counters, refreshes checksums, marks metadata dirty, and optionally syncs buffers for fast-commit replay.

The in-memory state is deliberately richer than disk. The buddy cache inode (`s_buddy_cache`) stores per-group bitmap and buddy blocks in page-cache folios and is thrown away at unmount. `struct ext4_group_info` tracks free counts, fragment count, first free cluster, buddy counters, corruption/trim/read flags, per-group PA list, and a red-black tree of post-commit-free extents. Optimized scan mode also maintains xarray indexes by largest free order and average fragment size.

Preallocation descriptors are non-persistent reservations. The file's own comments define the key invariant: in-core buddy equals on-disk bitmap plus preallocation descriptors. Active PAs are marked used in the buddy so they cannot be handed to a different allocation. Consuming a PA marks on-disk bitmap bits and then decrements `pa_free`; discarding a PA frees only still-unused bits back into the buddy. Inode PAs live in a per-inode rb-tree ordered by logical block and a per-group list; group PAs live in per-CPU locality-group bucket lists and the per-group list.

Freed data can be persistent-on-disk but not yet reusable. For journaled frees of metadata or ordered data, `ext4_mb_clear_bb()` clears the on-disk bitmap immediately but stores `struct ext4_free_data` in the group's `bb_free_root` and the superblock transaction list. The buddy folios are pinned while such extents exist so reinitialization from disk does not expose not-yet-committed freed blocks. `ext4_process_freed_data()` releases them after commit.

## Dependencies And Integration Points
The file depends on ext4 internals in `ext4.h`, `ext4_jbd2.h`, and `mballoc.h`, plus Linux folio/page-cache APIs, buffer heads, block discard, slab caches, xarrays, rb-trees, per-CPU counters, quota, tracepoints, and KUnit static stubs. It is tightly coupled to ext4 block group descriptors, flex_bg, bigalloc cluster conversion macros, metadata checksum handling, fast commit replay state, delayed allocation reservation accounting, and jbd2 transaction commit callbacks.

The public allocation API is consumed by ext4 mapping, extent, indirect-block, metadata, resize, truncate, migration, and replay paths. Sysfs/proc-facing statistics and group summaries use `ext4_mb_seq_groups_ops`, `ext4_mb_seq_structs_summary_ops`, and `ext4_seq_mb_stats_show()`. Online resize integrates through `ext4_mb_alloc_groupinfo()`, `ext4_mb_add_groupinfo()`, and `ext4_group_add_blocks()`.

## Risks And Edge Cases
The largest correctness risk is divergence among the on-disk bitmap, in-core buddy, PA descriptors, group counters, and post-commit-free rb-trees. The code addresses this with group locks, pinned folios, PA reference counts, strict ordering around PA deletion, and optional aggressive/double-check validation, but many paths intentionally relax atomicity for performance.

Concurrency is subtle. Buddy initialization copies the on-disk bitmap and overlays PAs while holding the group lock; PA consumption and deletion must avoid making a block visible as free during the window between disk bitmap update and PA unlink. Group PA list traversal uses RCU and per-locality locks; inode PA lookup uses rb-tree locks plus `pa_lock`; discard paths retry or wait when `pa_count` is nonzero.

Allocation failure and ENOSPC behavior is complex. `ext4_mb_new_blocks()` may halve requested length while reserving clusters, shrink for quota, retry after discarding PAs, and switch to strict checking if the per-CPU discard sequence changes. Bugs here can manifest as short allocation, leaked quota/reservation, or inappropriate ENOSPC under concurrent freeing.

Bigalloc and group-boundary handling are high-risk. Free paths adjust partial clusters with several flags, split cross-group frees, and use cluster-vs-block conversions throughout. Persistent bitmap marking takes cluster counts while validation often takes block counts, so off-by-one conversion errors would be severe.

Corruption handling is defensive but not fully recoverable. Bitmap/group descriptor mismatches mark block bitmaps corrupt; some paths skip corrupt groups, while allocation-over-metadata errors may mark bits to prevent reuse and return `-EFSCORRUPTED`, leaking blocks intentionally to preserve safety.

Discard/TRIM temporarily removes free ranges from allocation while issuing device discard outside the lock. Interrupt/freezer handling, `WAS_TRIMMED` caching, and discard granularity/minlen conversions are important edge cases.

Fast-commit replay uses simple idempotent bitmap mutation and bypasses normal buddy allocation. Replay can free already-free blocks and force buddy regeneration, so tests must cover replay-specific tolerance separately from normal corruption paths.

## Test Signals
Useful signals include KUnit coverage for exported test hooks: bit helpers, `mb_mark_used()`, `mb_free_blocks()`, buddy generation/load/unload, simple replay allocation, and diskspace marking. Functional tests should include exact goal allocation, power-of-two allocations, stripe-aligned allocations, optimized-scan on/off, ENOSPC with PA discard retry, inode PA reuse/discard, group PA reuse/list trimming, delayed-free commit release, fast-commit replay allocation/free idempotence, bigalloc partial-cluster frees, cross-group frees, online resize group addition, fstrim minlen/discard-granularity behavior, metadata-overlap detection, quota failure, and corrupted bitmap/group descriptor handling.

Runtime observability comes from ext4 tracepoints (`trace_ext4_request_blocks`, `trace_ext4_allocate_blocks`, `trace_ext4_mballoc_alloc`, `trace_ext4_mballoc_prealloc`, `trace_ext4_mballoc_free`, discard traces), proc/sysfs stats (`mb_groups`, `mb_structs_summary`, `mb_stats`), warning/error logs, and free-cluster counter consistency checks after mount, fsck, or stress workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/mballoc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/mballoc.h -->
# sources/distributed-fs/ceph-client/fs/ext4/mballoc.h

## Purpose
`mballoc.h` declares the data structures, defaults, debug macros, helper functions, and test-only exports used by ext4's multiblock allocator. It defines the allocator's shared vocabulary: free extents, allocation contexts, buddy views, preallocation descriptors, delayed-free descriptors, locality groups, scan tunables, and the callback signature for querying allocator ranges.

## Important APIs, Types, And Functions
Tunables include `MB_DEFAULT_MAX_TO_SCAN`, `MB_DEFAULT_MIN_TO_SCAN`, `MB_DEFAULT_STATS`, `MB_DEFAULT_STREAM_THRESHOLD`, `MB_DEFAULT_ORDER2_REQS`, `MB_DEFAULT_GROUP_PREALLOC`, `MB_DEFAULT_LINEAR_LIMIT`, `MB_DEFAULT_LINEAR_SCAN_THRESHOLD`, `MB_DEFAULT_BEST_AVAIL_TRIM_ORDER`, and `MB_NUM_ORDERS(sb)`. These seed the corresponding `ext4_sb_info` allocator fields in `ext4_mb_init()`.

`struct ext4_free_data` describes a free cluster extent that has been cleared from the on-disk bitmap but cannot be returned to the buddy until its journal transaction commits. It links into both a superblock list and a per-group rb-tree and stores group, start cluster, count, and transaction id.

`struct ext4_prealloc_space` is the shared descriptor for inode and locality-group preallocations. It has an inode rb-node or locality list node, a per-group list node, temporary/RCU linkage, `pa_lock`, reference count, deletion flag, physical/logical start, length/free counts in clusters, type, object lock pointer, and optional inode pointer.

`struct ext4_free_extent` is the allocator's compact extent form: logical start, group-relative cluster start, group number, and cluster length.

`struct ext4_locality_group` holds the per-CPU group preallocation state: a mutex serializing allocations and bucketed PA lists protected by `lg_prealloc_lock`.

`struct ext4_allocation_context` is the allocator work object. It stores original, goal, best, and final extents; scan/prefetch counters; flags; status; criteria; selected buddy, folios, PA, and locality group. `AC_STATUS_CONTINUE`, `AC_STATUS_FOUND`, and `AC_STATUS_BREAK` encode allocation progress.

`struct ext4_buddy` points to the loaded buddy and bitmap folios/data for one block group plus its `ext4_group_info` and superblock. Inline helpers include `ext4_grp_offs_to_block()`, `extent_logical_end()`, and `pa_logical_end()`.

The public declarations are `ext4_mballoc_query_range()` and `ext4_mb_mark_context()`. Under `CONFIG_EXT4_KUNIT_TESTS`, the header exposes allocator internals as test symbols.

## Control Flow
This header does not implement the allocator, but it shapes the control flow in `mballoc.c`. `ext4_mb_new_blocks()` initializes `ext4_allocation_context` from `ext4_allocation_request`, manipulates `ext4_free_extent` values through normalization and scanning, optionally attaches an `ext4_prealloc_space`, and loads groups through `ext4_buddy`.

The preallocation data model declared here determines the two PA paths. Inode PAs are found by logical range in an rb-tree and consumed without changing physical start/length until the descriptor is deleted. Group PAs are consumed from the front and bucketed by remaining free count in per-CPU locality groups.

`ext4_free_data` supports the free control flow in which bitmap clearing is journaled first and buddy reuse is deferred until jbd2 commit completion. `ext4_mballoc_query_range_fn` lets callers walk allocator ranges without embedding formatting or collection policy inside `mballoc.c`.

## State And Persistence Behavior
All structures in this header are in-memory state. They mirror or protect persistent bitmap/group-descriptor state but are not themselves stored on disk. `ext4_free_extent` lengths and starts are in clusters, not always filesystem blocks, which is central for bigalloc behavior.

`ext4_prealloc_space` describes non-persistent reserved space. Its `pa_free` count changes as blocks are consumed, `pa_deleted` prevents new users while discard/unlink completes, and `pa_count` prevents freeing while an allocator or discard path references it. `pa_inode` is used for inode PA ownership and for group discard paths that need inode context.

`ext4_free_data` persists only as long as a transaction remains unsafe for reuse. Its transaction id is the persistence boundary: once jbd2 reports the commit, `mballoc.c` can transfer the range into the in-core buddy and eventually into discard work.

## Dependencies And Integration Points
The header includes Linux filesystem, quota, buffer-head, proc, block-device, mutex, swap, and seq-file headers, and it includes `ext4_jbd2.h` and `ext4.h`. It depends on ext4 types such as `ext4_group_t`, `ext4_fsblk_t`, `ext4_lblk_t`, `ext4_grpblk_t`, `ext4_sb_info`, `handle_t`, and `ext4_allocation_request`.

`mb_debug()` integrates allocator debug output with `CONFIG_EXT4_DEBUG`. The KUnit section integrates with ext4's internal test modules by exporting otherwise-private helpers from `mballoc.c`.

## Risks And Edge Cases
The main header-level risk is unit confusion: `fe_len`, `pa_len`, `pa_free`, `efd_start_cluster`, and `efd_count` are cluster units, while logical and physical starts may be in filesystem blocks depending on the field. Callers must use `EXT4_C2B`, `EXT4_B2C`, and `EXT4_NUM_B2C` consistently.

PA lifetime fields are easy to misuse. `pa_deleted` alone does not mean the descriptor is unlinked everywhere; paths must also respect `pa_count`, the object lock stored in `pa_node_lock`, the group lock, and RCU rules for locality lists.

`extent_logical_end()` and `pa_logical_end()` intentionally return `loff_t` to avoid overflow beyond `ext4_lblk_t`; callers that cast back to narrower types or skip overflow checks risk invalid normalization around very large logical offsets.

## Test Signals
Compile-time test signals are the `CONFIG_EXT4_KUNIT_TESTS` declarations. Behavioral tests should assert structure unit handling under bigalloc, PA rb-tree ordering and non-overlap, correct logical-end calculations near `EXT_MAX_BLOCKS`, delayed-free transaction bucketing by `efd_tid`, and that debug/test exports remain synchronized with the implementations in `mballoc.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/mballoc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/migrate.c -->
# sources/distributed-fs/ceph-client/fs/ext4/migrate.c

## Purpose
`migrate.c` implements conversion between ext4's legacy indirect block mapping and extent-based mapping. `ext4_ext_migrate()` converts an indirect-mapped regular file to extents by building an equivalent extent tree in a temporary inode, swapping the original inode's `i_data`, and freeing old indirect metadata. `ext4_ind_migrate()` performs the limited reverse conversion from a simple extent file to direct `i_data[]` block pointers.

## Important APIs, Types, And Functions
`struct migrate_struct` tracks the current contiguous logical-to-physical run during indirect-tree traversal: first/current/last logical block and first/last physical block.

Forward migration helpers are `update_extent_range()`, `finish_range()`, `update_ind_extent_range()`, `update_dind_extent_range()`, and `update_tind_extent_range()`. They scan direct, single-indirect, double-indirect, and triple-indirect mappings, coalesce contiguous physical/logical runs, and insert extents into the temporary inode.

Cleanup and swap helpers include `free_dind_blocks()`, `free_tind_blocks()`, `free_ind_block()`, `ext4_ext_swap_inode_data()`, `free_ext_idx()`, and `free_ext_block()`. They free old indirect metadata after a successful swap or free temporary extent metadata after failure.

The public functions are `ext4_ext_migrate(struct inode *inode)` and `ext4_ind_migrate(struct inode *inode)`.

## Control Flow
`ext4_ext_migrate()` first rejects filesystems without extents, inodes already using extents, inline-data inodes, and fast symlinks. It takes the ext4 writepages lock, starts a migration transaction, marks fast commit ineligible, creates a hidden temporary regular inode near the source inode's group, copies the source checksum seed into the temporary inode, sets its size, clears its link count, initializes its extent tree, and stops the creation transaction.

It then sets `EXT4_STATE_EXT_MIGRATE` under `i_data_sem`. This flag lets concurrent block allocation invalidate the migration. A new transaction is started, `migrate_struct` is reset, and the code walks the original inode's direct entries, single indirect block, double indirect tree, and triple indirect tree. Sparse entries only advance `curr_block`; nonzero physical blocks are fed to `update_extent_range()`, which either extends the current run or flushes the previous run through `finish_range()`.

`finish_range()` builds an `ext4_extent`, finds the insertion path in the temporary inode, calculates needed credits, ensures journal credits, and inserts the extent under the temporary inode's `i_data_sem`. After traversal, the final run is flushed. On success, `ext4_ext_swap_inode_data()` verifies the migrate flag is still set, clears it, sets `EXT4_INODE_EXTENTS`, copies the temporary inode extent tree into the original inode, adds temporary extent metadata blocks to `i_blocks`, frees old indirect metadata, and marks the inode dirty. On failure, temporary extent index blocks are freed and the temporary inode is reset to a zero-size, empty extent inode before `iput()`.

`ext4_ind_migrate()` is intentionally narrow. It requires extents support and an extent inode, rejects bigalloc, forces delayed allocations to disk when delalloc is enabled, takes the writepages lock, starts a migration transaction, disables fast commit, locks `i_data_sem`, validates the extent tree, and only accepts depth-zero trees with at most one extent whose logical end fits in direct blocks. It clears `EXT4_INODE_EXTENTS`, zeros `i_data`, writes direct physical block numbers, marks the inode dirty, and releases locks.

## State And Persistence Behavior
Both directions are journaled with `EXT4_HT_MIGRATE` transactions and mark the filesystem fast-commit ineligible because the mapping-layout rewrite is not represented in the fast commit log.

Forward migration uses a real temporary inode as durable staging while building the extent tree. Its checksum seed is temporarily changed to the source inode's seed so newly allocated extent metadata blocks will have correct checksums after the swap. The temporary inode link count is zero so it is deleted when dropped. The source inode's `i_blocks` is increased by the temporary inode's metadata blocks before old indirect metadata is freed; quota for temporary extent metadata has already been charged to the temporary inode.

`EXT4_STATE_EXT_MIGRATE` is the race detector. It is set before scanning and checked while holding the original inode's `i_data_sem` during swap. If concurrent allocation cleared it, migration fails with `-EAGAIN` instead of installing a stale mapping.

Old indirect metadata is freed with `EXT4_FREE_BLOCKS_METADATA | EXT4_FREE_BLOCKS_FORGET`, ensuring buffer invalidation/revoke handling. Temporary extent metadata is recursively freed on failure via `free_ext_block()`.

## Dependencies And Integration Points
The file includes `ext4_jbd2.h` and `ext4_extents.h` and depends on ext4 extent APIs (`ext4_find_extent()`, `ext4_ext_insert_extent()`, `ext4_ext_tree_init()`, `ext4_ext_check_inode()`), journal credit helpers, inode creation, quota-aware allocation, block bitmap freeing through `ext4_free_blocks()`, buffer reads through `ext4_sb_bread()`, and writeback coordination through `ext4_writepages_down_write()`/`ext4_writepages_up_write()`.

It integrates with ioctl or internal migration callers that request extent enablement/disablement. It also integrates with checksum, fast commit, delayed allocation, and metadata revoke paths.

## Risks And Edge Cases
Forward migration races with mmap writes or other block allocation despite taking higher-level locks; the migrate state flag is the final guard. Any path that allocates blocks without clearing `EXT4_STATE_EXT_MIGRATE` could permit stale conversion.

Journal credit management is delicate because extent insertion and metadata freeing occur in loops and can require restarts/credit extension. Failures must leave either the original indirect mapping intact or free all temporary extent metadata.

Sparse file traversal must advance logical block numbers exactly across holes in direct, indirect, double-indirect, and triple-indirect levels. Miscounting `max_entries` offsets would map extents to the wrong logical blocks.

The temporary checksum seed swap is critical. If extent metadata is created with the temporary inode's own seed and then copied to the original inode, metadata checksum verification can fail after migration.

Reverse migration is deliberately limited to a single leaf extent fully inside direct blocks and is unsupported for bigalloc. Callers must not expect general extents-to-indirect conversion.

## Test Signals
Forward tests should cover direct-only files, sparse indirect files, contiguous and fragmented runs, single/double/triple indirect coverage, failure during extent insertion, failure during metadata free, concurrent allocation producing `-EAGAIN`, checksum-enabled filesystems, quota interactions, and cleanup of the temporary inode. Reverse tests should cover empty extent inodes, one direct-range extent, depth-nonzero rejection, multiple-extent rejection, extent ending beyond `EXT4_NDIR_BLOCKS`, bigalloc rejection, delayed allocation flushing, and fast-commit ineligibility marking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/migrate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/mmp.c -->
# sources/distributed-fs/ceph-client/fs/ext4/mmp.c

## Purpose
`mmp.c` implements ext4 Multiple Mount Protection. MMP stores a heartbeat block on disk and refuses mount if that block appears to be actively updated by another node or fsck. After mount, a kernel thread (`kmmpd`) periodically writes a changing sequence number, timestamp, nodename, device name, and checksum to the MMP block.

## Important APIs, Types, And Functions
Checksum helpers are `ext4_mmp_csum()`, `ext4_mmp_csum_verify()`, and `ext4_mmp_csum_set()`. They use the filesystem checksum seed and cover the MMP structure up to `mmp_checksum` when metadata checksums are enabled.

I/O helpers are `write_mmp_block_thawed()`, `write_mmp_block()`, and `read_mmp_block()`. Writes use synchronous metadata-priority buffer submission; reads explicitly clear the uptodate flag to force device reads and then validate magic and checksum.

Diagnostics are handled by `__dump_mmp_msg()`, which prints last update time, node, and block device.

The background heartbeat is `kmmpd()`. Lifecycle/public functions are `ext4_multi_mount_protect()` to verify/start protection and `ext4_stop_mmpd()` to stop the thread and release the MMP buffer.

`mmp_new_seq()` chooses a random sequence number bounded by `EXT4_MMP_SEQ_MAX`. Constants and `struct mmp_struct` are defined in `ext4.h`, including `EXT4_MMP_MAGIC`, `EXT4_MMP_SEQ_CLEAN`, `EXT4_MMP_SEQ_FSCK`, min/max check intervals, and the on-disk fields.

## Control Flow
`ext4_multi_mount_protect()` validates that the superblock's MMP block lies inside the filesystem, reads it from disk, derives the check interval from the superblock update interval and the block's own advertised interval, and examines `mmp_seq`. A clean sequence skips the initial active-writer wait. An fsck sequence fails with `-EBUSY`. Otherwise the mount waits for approximately two check intervals, rereads the block, and fails if the sequence changed, because another node is updating it.

After the initial check, the mount writes a new random sequence number, waits again, rereads, and verifies the same sequence remains. If it changed, the device is considered active elsewhere. If it remains stable, the buffer is stored in `s_mmp_bh`, the block device name is written into the MMP structure, and `kthread_run()` starts `kmmpd`.

`kmmpd()` initializes the timestamp, nodename, and check interval, then loops until stopped or emergency state. Each iteration increments/wraps the sequence, updates timestamp, writes the MMP block synchronously, sleeps for the configured update interval minus write time, and if a write took longer than the adaptive check interval, rereads the MMP block to confirm its sequence and nodename still match. On clean stop it writes `EXT4_MMP_SEQ_CLEAN` and the final timestamp.

`ext4_stop_mmpd()` stops the thread, releases `s_mmp_bh`, and nulls the task pointer.

## State And Persistence Behavior
The MMP block is persistent on disk and acts as a lease/heartbeat record. While mounted, `mmp_seq` is expected to change regularly and `mmp_time`, `mmp_nodename`, `mmp_bdevname`, and `mmp_check_interval` provide diagnostics and timing guidance. On clean unmount, `kmmpd()` writes `EXT4_MMP_SEQ_CLEAN`.

The in-memory state is held in `EXT4_SB(sb)->s_mmp_bh` and `s_mmp_tsk`. The same buffer head is reused by the heartbeat thread. Reads during validation use a separate buffer when needed and always force a fresh device read to avoid trusting cached heartbeat data.

Writes are protected against filesystem freezing by `write_mmp_block()` using superblock write protection, while mount/remount setup uses `write_mmp_block_thawed()` directly because the mount path already holds `s_umount` and taking freeze protection would upset lockdep.

## Dependencies And Integration Points
The file depends on Linux buffer heads, synchronous bio submission through `submit_bh()`, random number generation, UTS nodename, kthreads, jiffies/scheduling, superblock freeze guards, and ext4 checksum/feature helpers. It integrates with ext4 mount/remount setup, unmount teardown, emergency state handling, metadata checksum feature state, and administrator diagnostics.

MMP is especially important for shared block devices, clustered deployments, stale mounts, and fsck coordination. `EXT4_MMP_SEQ_FSCK` is treated as unsafe regardless of timestamp age.

## Risks And Edge Cases
False positives and false negatives are timing-sensitive. Slow storage can delay MMP writes; the adaptive `mmp_check_interval` tries to avoid declaring a live filesystem dead too aggressively. Conversely, if reads are cached or not forced from disk, a second node could miss an active writer, so `read_mmp_block()` clears uptodate and uses priority metadata reads.

Startup waits are interruptible. If interrupted, mount fails with `-ETIMEDOUT`, which is safer than proceeding without a full MMP check.

Checksum or magic failures abort MMP reads. This protects against corrupt heartbeat data but can also prevent mount until repaired.

`kmmpd()` throttles repeated write errors, but persistent write failure undermines the heartbeat and eventually causes ext4 errors. If the MMP feature is disabled while the thread is running, the thread logs and exits its active loop.

The random sequence range includes values up to `EXT4_MMP_SEQ_MAX`; correctness depends on avoiding reserved values above max and detecting any unexpected sequence change during waits.

## Test Signals
Tests should cover clean MMP mount, active sequence change rejection, fsck sequence rejection, invalid MMP block location, bad magic, bad checksum with metadata_csum, interrupted startup waits, `kthread_run()` failure, clean unmount writing `EXT4_MMP_SEQ_CLEAN`, adaptive check interval clamping, delayed-write self-check detecting another updater, write I/O error logging, and feature-disabled shutdown. Integration tests need shared-block-device or mocked block I/O scenarios that prove reads bypass cached buffer state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/mmp.c -->
