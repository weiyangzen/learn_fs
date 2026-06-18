# Group Research: group_700_linux_sources_os_linux_linux_fs_btrfs_bio_h_sources_os_linux_linux_f_470a368d9f0c

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/bio.h -->
# File Research: sources/os/linux/linux/fs/btrfs/bio.h

## Scope And Role

`bio.h` defines Btrfs' high-level wrapper around the Linux block layer `struct bio`. The central type is `struct btrfs_bio`, which embeds a `struct bio` as its final member and adds filesystem context needed by Btrfs I/O submission, checksum verification/generation, read repair, mirror selection, split I/O completion tracking, and metadata parent checks.

This is an interface/header file only. It declares allocation, initialization, submission, completion, repair, and bioset lifecycle functions implemented elsewhere.

## Main Types And Constants

`BTRFS_BIO_INLINE_CSUM_SIZE` is `64`, used for small inline checksum storage in read bios.

`btrfs_bio_end_io_t` is the completion callback type:
`void (*)(struct btrfs_bio *bbio)`.

`struct btrfs_bio` contains:

- `inode` and `file_offset`: identify the Btrfs inode and logical file offset for the I/O. Data inodes get automatic checksum verification and read repair; metadata inodes are caller-managed.
- A union of operation-specific state:
  - Data reads store checksum pointer, inline checksum buffer, and saved iterator.
  - Data writes store ordered extent, checksum sums, checksum work/completion state, saved iterator, original physical address for zone append, and original logical address for fscrypt checksum handling.
  - Metadata reads store `struct btrfs_tree_parent_check`.
- `end_io_work`: work item for internal read end-I/O handling.
- `end_io` and `private`: caller-supplied completion callback and opaque context.
- `pending_ios`: tracks split/submitted child bios.
- `mirror_num`: selected mirror.
- `status`: first error status among split bios.
- Bit flags for commit-root checksum lookup, scrub bios, remapped-copy bios, async checksum generation, and zone append use.
- Embedded `struct bio bio`, deliberately last because `bio_alloc_bioset()` allocation sizing depends on it.

## Public API

`btrfs_bio(struct bio *bio)` converts a Linux `bio` pointer back to its containing `struct btrfs_bio`.

Bioset lifecycle:
- `btrfs_bioset_init()`
- `btrfs_bioset_exit()`

Bio lifecycle:
- `btrfs_bio_init()`
- `btrfs_bio_alloc()`
- `btrfs_bio_end_io()`

Submission and repair:
- `btrfs_submit_bbio()`
- `btrfs_submit_repair_write()`
- `btrfs_repair_io_failure()`

`REQ_BTRFS_CGROUP_PUNT` aliases `REQ_FS_PRIVATE` to request submission through `blkcg_punt_bio_submit`.

## Integration Points

This header depends on Linux block APIs (`linux/bio.h`), workqueues, and Btrfs tree checking (`tree-checker.h`). It is the shared contract between Btrfs read/write paths, checksum code, scrub/repair paths, and the lower-level physical-device mapping submission machinery.

The inode comment is important: data inodes trigger automatic data integrity behavior, while metadata callers retain responsibility for validation. That split is core to how Btrfs differentiates file data I/O from btree block I/O.

## Concurrency And State Notes

`pending_ios` and `status` support split I/O completion aggregation. The design records the first failing status and delays final completion until all child bios finish.

`end_io_work`, `csum_work`, and `csum_done` show that data I/O completion and checksum generation can be asynchronous.

The struct layout invariant, with `bio` last, is a hard ABI-style implementation constraint inside the filesystem's bioset allocation logic.

## Risks And Edge Cases

The union members are context-sensitive. Misusing a `btrfs_bio` as the wrong operation type would alias unrelated fields.

Zone append and fscrypt need original physical/logical addresses preserved, so write paths must populate `orig_physical` and `orig_logical` correctly.

`is_scrub` is needed because scrub can reuse the btree inode; callers must set it to prevent metadata/data behavior confusion.

## Testing Signals

Relevant tests should exercise:
- Data read checksum verification and read repair.
- Split bio completion error aggregation.
- Async write checksum generation.
- Scrub bios using btree inode context.
- Zone append write completion.
- Remapped copy I/O paths.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/bio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/block-group.c -->
# File Research: sources/os/linux/linux/fs/btrfs/block-group.c

## Scope And Role

`block-group.c` implements Btrfs block-group lifecycle and allocation accounting. A block group is the logical chunk-level allocation unit that connects free-space state, space-info counters, chunk/device mappings, block-group items in trees, relocation/reclaim, discard, read-only transitions, zoned allocation state, and transaction commit writeback.

The file covers:

- Allocation profile selection.
- Block-group lookup and reference management.
- Free-space cache loading and block-group caching workers.
- Mount-time block-group reconstruction.
- Block-group creation and deletion.
- Dirty block-group commit/update paths.
- Chunk allocation phase orchestration.
- Reservation and used/pinned accounting.
- Reclaim and unused block-group cleanup.
- Read-only/frozen/swap-safe block-group transitions.
- Size-class optimization for data block groups.
- Fully remapped block-group handling.

## Major Data Flow

### Mount/read path

`btrfs_read_block_groups()` selects the block-group root, scans block-group items, reads each item with `read_one_block_group()`, creates in-memory `struct btrfs_block_group` objects, initializes zone/free-space state, adds them to the rb tree and `space_info`, sets available allocation bits, and initializes global reserves.

If normal block-group items cannot be read under rescue/unsupported read-only conditions, `fill_dummy_bgs()` creates full dummy block groups from the chunk mapping tree so the filesystem can still mount for recovery.

`check_chunk_block_group_mappings()` validates that every chunk map has a matching block group with identical start, length, and type flags.

### Cache loading path

`btrfs_cache_block_group()` starts a `btrfs_caching_control` worker unless the group is already cached, zoned mode bypasses caching, or a remapped group cannot allocate.

`caching_thread()` loads size-class hints, tries the old space cache if enabled, then loads free ranges from either the free-space tree or extent tree. It updates `cache->cached`, wakes waiters, frees excluded super extents, and drops references.

`load_extent_tree_free()` scans committed extent-tree items and adds gaps as free space while periodically waking allocation waiters after `CACHING_CTL_WAKE_UP`.

`btrfs_wait_block_group_cache_progress()` and `btrfs_wait_block_group_cache_done()` let allocators wait for usable progress or completion.

### Creation path

`btrfs_make_block_group()` creates a new in-memory block group for a newly allocated chunk, marks it `BLOCK_GROUP_FLAG_NEW`, initializes free space, inserts it in the rb tree and `space_info`, updates global reserves, adds it to the transaction's pending `new_bgs` list, increments delayed-ref reservation accounting, and sets available profile bits.

`btrfs_create_pending_block_groups()` is phase 2 of chunk allocation. It inserts the block-group item, chunk item if still missing, device extent items, and free-space tree records, then clears the new flag and marks unused groups for possible cleanup.

### Deletion path

`btrfs_delete_unused_bgs()` processes `fs_info->unused_bgs`, skips unsafe candidates, coordinates async discard and zoned zone finishing, marks empty groups read-only, starts a removal transaction, clears pinned extents, removes the chunk, and moves groups to transaction deleted lists when trimming must complete at commit.

`btrfs_remove_block_group()` removes a block group from all runtime structures and on-disk metadata: free-space inode/cache, rb tree, space-info lists, free-space tree, block-group item, and possibly chunk map. It carefully handles caching controls, dirty/io lists, sysfs entries, discard, frozen users, and remapped groups.

`btrfs_start_trans_remove_block_group()` calculates metadata units needed to remove a block group and starts a fallback-global-reserve transaction.

### Reclaim path

`btrfs_mark_bg_to_reclaim()` links groups into `fs_info->reclaim_bgs`.

`btrfs_reclaim_block_groups()` sorts candidates by used bytes, uses an exclusive balance operation, and relocates underused groups through `btrfs_reclaim_block_group()` until a limit is reached.

`btrfs_reclaim_block_group()` validates the group still qualifies, marks it read-only, records used/reserved bytes, relocates the chunk, updates reclaim stats, and requeues on recoverable failure.

`btrfs_reclaim_bgs()` performs periodic reclaim sweep and schedules worker execution.

### Dirty/update/commit path

`btrfs_update_block_group()` adjusts super bytes-used, block-group `used/reserved/pinned`, `space_info` counters, dirty-list membership, pinned extents, reclaim eligibility, and unused-group detection when extents are allocated or freed.

`btrfs_start_dirty_block_groups()` begins space-cache writeout and block-group item updates before the transaction critical section to reduce commit latency.

`btrfs_write_dirty_block_groups()` finishes dirty block-group updates in the commit critical section, waits for cache I/O, runs delayed refs, retries rare missing-item races, and drains `io_bgs`.

`update_block_group_item()` persists used/remap/identity-remap/flags changes back to the block-group item and rolls back last-committed snapshots on failure.

`cache_save_setup()` prepares old space-cache inode writeout, including inode lookup/creation, generation invalidation, truncation, preallocation, and cache disk state transitions.

### Chunk allocation path

`btrfs_chunk_alloc()` is phase 1 for data/metadata chunks. It decides whether allocation is needed, serializes through `space_info->chunk_alloc` and `fs_info->chunk_mutex`, rejects system chunk allocation through this path, handles mixed block groups and metadata-ratio forcing, creates the chunk, and records success/failure in `space_info`.

`do_chunk_alloc()` checks system chunk space, creates the chunk, inserts the chunk item, handles rare `-ENOSPC` by creating an extra system chunk and retrying, and releases chunk metadata reservations.

`check_system_chunk()` and `btrfs_reserve_chunk_metadata()` reserve system space for chunk-tree updates under `chunk_mutex`.

The long comment above `btrfs_chunk_alloc()` documents why chunk allocation is split into two phases: inserting extent-tree block-group items during allocation can deadlock with COW of locked extent-tree nodes.

## Key Functions

Allocation profile:
- `get_restripe_target()`
- `btrfs_reduce_alloc_profile()`
- `btrfs_get_alloc_profile()`
- `set_avail_alloc_bits()`
- `clear_avail_alloc_bits()`
- `clear_incompat_bg_bits()`

Lookup/refcount:
- `btrfs_get_block_group()`
- `btrfs_put_block_group()`
- `btrfs_lookup_first_block_group()`
- `btrfs_lookup_block_group()`
- `btrfs_next_block_group()`

NOCOW/reservation synchronization:
- `btrfs_inc_nocow_writers()`
- `btrfs_dec_nocow_writers()`
- `btrfs_wait_nocow_writers()`
- `btrfs_dec_block_group_reservations()`
- `btrfs_wait_block_group_reservations()`

Free-space/cache:
- `btrfs_add_new_free_space()`
- `load_extent_tree_free()`
- `btrfs_cache_block_group()`
- `btrfs_wait_block_group_cache_progress()`
- `btrfs_wait_block_group_cache_done()`

Read/create/remove:
- `btrfs_read_block_groups()`
- `btrfs_make_block_group()`
- `btrfs_create_pending_block_groups()`
- `btrfs_remove_block_group()`
- `btrfs_delete_unused_bgs()`

Accounting:
- `btrfs_update_block_group()`
- `btrfs_add_reserved_bytes()`
- `btrfs_free_reserved_bytes()`

Chunk metadata:
- `btrfs_chunk_alloc()`
- `btrfs_force_chunk_alloc()`
- `check_system_chunk()`
- `btrfs_reserve_chunk_metadata()`

Teardown and special states:
- `btrfs_put_block_group_cache()`
- `btrfs_free_block_groups()`
- `btrfs_freeze_block_group()`
- `btrfs_unfreeze_block_group()`
- `btrfs_inc_block_group_swap_extents()`
- `btrfs_dec_block_group_swap_extents()`

Size/remap:
- `btrfs_calc_block_group_size_class()`
- `btrfs_use_block_group_size_class()`
- `btrfs_block_group_should_use_size_class()`
- `btrfs_mark_bg_fully_remapped()`
- `btrfs_populate_fully_remapped_bgs_list()`

## Important State And Locking

`fs_info->block_group_cache_lock` protects the rb tree of block groups.

`space_info->groups_sem` protects block-group lists per raid/profile type and blocks allocator races during removal/reclaim/read-only transitions.

`space_info->lock` and `block_group->lock` protect accounting fields such as `used`, `reserved`, `pinned`, `ro`, `zone_unusable`, and `swap_extents`.

`fs_info->unused_bgs_lock` protects `unused_bgs`, `reclaim_bgs`, and `fully_remapped_bgs` list membership through `bg_list`.

`fs_info->chunk_mutex` serializes chunk-tree updates, system chunk reservation, and chunk allocation/removal.

`trans->transaction->dirty_bgs_lock` protects transaction dirty/io block-group lists.

`ro_block_group_mutex` prevents setting groups read-only after dirty block-group commit processing has begun.

`caching_control->mutex`, waitqueue, refcount, and `progress` coordinate async cache loading with allocators.

## On-Disk Integration

The file reads and writes:

- `BTRFS_BLOCK_GROUP_ITEM_KEY` in either the block-group tree or extent tree depending on `BLOCK_GROUP_TREE`.
- Chunk tree records via `btrfs_chunk_alloc_add_chunk_item()`.
- Device extent items in the device tree.
- Free-space tree records.
- Old free-space cache inodes.
- Superblock `bytes_used`.

It also cross-checks chunk map records against block-group items during mount.

## Zoned Filesystem Handling

Several paths branch on `btrfs_is_zoned()`:

- Free-space cache loading is skipped for zoned allocation.
- `has_unwritten_metadata()` checks `meta_write_pointer`.
- `read_one_block_group()` calls `btrfs_calc_zone_unusable()`.
- Read-only transitions migrate `zone_unusable` into/out of `bytes_readonly`.
- New chunks may be activated for zoned allocation.
- Empty zoned groups may be finished before removal.
- Superblock stripes are forbidden inside sequential zones.
- Size classes are disabled for zoned filesystems.

## Reflink/Remap Handling

For the remap tree feature, block-group item v2 includes `remap_bytes` and `identity_remap_count`.

Fully remapped groups are tracked by `BLOCK_GROUP_FLAG_FULLY_REMAPPED`, `BLOCK_GROUP_FLAG_STRIPE_REMOVAL_PENDING`, and `fs_info->fully_remapped_bgs`. `btrfs_populate_fully_remapped_bgs_list()` reconstructs pending fully-remapped groups after mount by comparing block-group and chunk trees.

## Error Handling And Corruption Checks

The file uses `-EUCLEAN` for structural inconsistencies such as missing block-group roots, chunk/block-group mismatches, or invalid zoned superblock placement.

Transaction-impacting failures usually call `btrfs_abort_transaction()`.

Several paths tolerate `-ENOSPC` intentionally:
- Marking block groups read-only may allocate fallback chunks.
- System chunk reservation may pre-create chunks but ignore some failures until needed.
- Space-cache setup may skip cache writeout on ENOSPC.

Warnings protect invariants around refcounted teardown, dirty/io list state, pinned/reserved accounting, swap extents, and chunk-map removal timing.

## Risks And Edge Cases

The most fragile behavior is concurrency around block-group removal. Removal must coordinate allocators, scrub, trim/discard, free-space cache I/O, frozen block groups, and transaction commit. Removing the chunk map too early can allow logical/physical ranges to be reused while trim or scrub still references them.

The two-phase chunk allocation protocol is mandatory. Collapsing it into a single insertion path can deadlock with extent-tree or chunk-tree COW.

`btrfs_update_block_group()` must load old free-space cache before freeing space if cache state is not complete, otherwise unpinning can leak space.

`space_info->full` can be set after `-ENOSPC`; later code must clear/reset allocation pressure through existing mechanisms rather than assuming permanent media exhaustion.

Size-class enforcement can return `-EAGAIN` on races for newly empty block groups. Allocator callers must retry or relax with `force_wrong_size_class`.

## Testing Signals

Important coverage areas:

- Mount with valid, missing, mismatched, and rescue block-group/chunk records.
- Empty block-group deletion with and without async discard.
- Dirty block-group update during transaction commit and pre-commit.
- Chunk allocation under degraded profiles, scrub-induced read-only groups, and discard races.
- Zoned block-group activation, finish, read-only transitions, and unwritten metadata checks.
- Reclaim threshold crossing and relocation failure requeue.
- Old space-cache setup/truncate/writeout and free-space tree mode.
- Fully remapped block groups across unmount/remount.
- Swapfile extents preventing read-only transitions.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/block-group.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/block-group.h -->
# File Research: sources/os/linux/linux/fs/btrfs/block-group.h

## Scope And Role

`block-group.h` declares the public data structures, enums, helper functions, and APIs for Btrfs block-group management. It is the interface consumed by allocation, free-space, transaction, relocation, discard, zoned, and chunk/device mapping code.

The core type is `struct btrfs_block_group`, which represents one logical chunk/block-group and stores accounting, free-space cache state, runtime flags, transaction lists, discard/reclaim state, zoned state, and allocation size-class information.

## Main Enums

`enum btrfs_disk_cache_state` tracks old space-cache write state:
- `BTRFS_DC_WRITTEN`
- `BTRFS_DC_ERROR`
- `BTRFS_DC_CLEAR`
- `BTRFS_DC_SETUP`

`enum btrfs_block_group_size_class` groups data allocations into:
- none
- small: `0 < size <= 128K`
- medium: `128K < size <= 8M`
- large: `8M < size < BG_LENGTH`

`enum btrfs_discard_state` tracks async discard passes over extent and bitmap free-space representations, plus reset/remap states.

`enum btrfs_chunk_alloc_enum` controls chunk allocation pressure:
- no force
- limited
- force
- force for extent allocation

`enum btrfs_block_group_flags` defines runtime bit positions for state such as removed, to-copy, chunk item inserted, zone active, new, fully remapped, stripe removal pending, and free-space-tree update needs.

`enum btrfs_caching_type` tracks free-space cache lifecycle:
- no caching
- started
- finished
- error

## Core Structures

`struct btrfs_caching_control` owns async free-space caching work. It has a list node, mutex, waitqueue, work item, associated block group, progress counter, and refcount.

`CACHING_CTL_WAKE_UP` is `SZ_2M`, the free-space progress threshold used to wake allocation waiters during caching.

`struct btrfs_block_group` includes:

- Identity and range: `fs_info`, `inode`, `start`, `length`, `global_root_id`.
- Accounting: `pinned`, `reserved`, `used`, `delalloc_bytes`, `bytes_super`, `remap_bytes`, `identity_remap_count`, last-committed snapshots, and bitmap thresholds.
- Profile/type: `flags`, `full_stripe_len`, `space_info`.
- State: `runtime_flags`, `ro`, `disk_cache_state`, `cached`, `caching_ctl`.
- Free-space: `free_space_ctl`, `io_ctl`, `free_space_lock`, bitmap usage booleans.
- Index/list membership: rb tree node, raid-type list, cluster list, bg list, read-only list, dirty/io lists, discard list, active-zoned list.
- Lifetime/synchronization: refcount, spinlock, data rwsem, frozen counter, reservation and nocow-writer atomics.
- Discard/reclaim: discard index/time/cursor/state and `reclaim_mark`.
- Zoned fields: allocation offset, unusable/capacity, metadata write pointer, physical map, zone finish work, last extent buffer.
- Allocation policy: `size_class`.

## Inline Helpers

`btrfs_block_group_end()` returns `start + length`.

`btrfs_is_block_group_used()` checks `used`, `reserved`, `pinned`, and `remap_bytes` under the block-group lock.

`btrfs_is_block_group_data_only()` returns true only for non-mixed data groups.

`btrfs_block_group_available_space()` returns length minus used, pinned, reserved, super bytes, and zone-unusable bytes under lock.

`btrfs_data_alloc_profile()`, `btrfs_metadata_alloc_profile()`, and `btrfs_system_alloc_profile()` wrap `btrfs_get_alloc_profile()` with the corresponding block-group type.

`btrfs_block_group_done()` uses a memory barrier and checks whether caching finished or errored.

## Public API Surface

Lookup/lifetime:
- `btrfs_lookup_first_block_group()`
- `btrfs_lookup_block_group()`
- `btrfs_next_block_group()`
- `btrfs_get_block_group()`
- `btrfs_put_block_group()`

Reservation and NOCOW synchronization:
- `btrfs_dec_block_group_reservations()`
- `btrfs_wait_block_group_reservations()`
- `btrfs_inc_nocow_writers()`
- `btrfs_dec_nocow_writers()`
- `btrfs_wait_nocow_writers()`

Caching/free-space:
- `btrfs_get_caching_control()`
- `btrfs_wait_block_group_cache_progress()`
- `btrfs_cache_block_group()`
- `btrfs_add_new_free_space()`

Lifecycle:
- `btrfs_start_trans_remove_block_group()`
- `btrfs_remove_bg_from_sinfo()`
- `btrfs_remove_block_group()`
- `btrfs_delete_unused_bgs()`
- `btrfs_mark_bg_unused()`
- `btrfs_read_block_groups()`
- `btrfs_make_block_group()`
- `btrfs_create_pending_block_groups()`
- `btrfs_put_block_group_cache()`
- `btrfs_free_block_groups()`

Reclaim:
- `btrfs_reclaim_block_groups()`
- `btrfs_reclaim_bgs_work()`
- `btrfs_reclaim_bgs()`
- `btrfs_mark_bg_to_reclaim()`

Read-only and dirty updates:
- `btrfs_inc_block_group_ro()`
- `btrfs_dec_block_group_ro()`
- `btrfs_start_dirty_block_groups()`
- `btrfs_write_dirty_block_groups()`
- `btrfs_setup_space_cache()`
- `btrfs_update_block_group()`

Allocation/chunk:
- `btrfs_add_reserved_bytes()`
- `btrfs_free_reserved_bytes()`
- `btrfs_chunk_alloc()`
- `btrfs_force_chunk_alloc()`
- `check_system_chunk()`
- `btrfs_reserve_chunk_metadata()`
- `btrfs_get_alloc_profile()`
- `btrfs_rmap_block()`

Special states:
- `btrfs_freeze_block_group()`
- `btrfs_unfreeze_block_group()`
- `btrfs_inc_block_group_swap_extents()`
- `btrfs_dec_block_group_swap_extents()`
- `btrfs_calc_block_group_size_class()`
- `btrfs_use_block_group_size_class()`
- `btrfs_block_group_should_use_size_class()`
- `btrfs_mark_bg_fully_remapped()`
- `btrfs_populate_fully_remapped_bgs_list()`

## Integration Points

This header includes `free-space-cache.h`, Linux list/rbtree/refcount/wait/rwsem primitives, and Btrfs UAPI tree definitions.

It is tightly coupled with:
- `space-info` accounting.
- Free-space cache/tree code.
- Chunk mapping and device extent code.
- Transaction dirty block-group handling.
- Discard and reclaim workers.
- Zoned block allocation.
- Relocation, scrub, and NOCOW write paths.

## Concurrency Notes

The comments document which fields are protected by which locks. `lock`, `free_space_lock`, `groups_sem`, `block_group_cache_lock`, and list-specific locks in `fs_info` are all part of the contract.

`frozen`, `reservations`, and `nocow_writers` are atomic counters used to safely coordinate removal/trim/scrub and allocation/write races.

List fields are intentionally overloaded across multiple owners, so callers must use the correct lock and helper API.

## Risks And Edge Cases

`btrfs_block_group_available_space()` assumes the block-group lock is held; callers that do not honor this can race accounting updates.

`bg_list` is shared among unused, reclaim, deleted, and new block-group lists, so incorrect list movement can corrupt lifecycle state.

`ro` is a counter, not a boolean. Read-only entry/exit must balance.

Zoned fields are meaningful only under zoned mode, but the struct stores them unconditionally.

## Testing Signals

This header's contracts are validated indirectly through:
- Allocation/free accounting tests.
- Block-group lookup and removal tests.
- Reclaim and relocation tests.
- Async discard tests.
- Zoned filesystem tests.
- Swapfile-on-Btrfs tests.
- Free-space cache/tree mount and transaction commit tests.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/block-group.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/block-rsv.c -->
# File Research: sources/os/linux/linux/fs/btrfs/block-rsv.c

## Scope And Role

`block-rsv.c` implements Btrfs metadata block reservations. A block reserve is a bucket of pre-reserved metadata space used by transactions, delayed allocation, delayed refs, chunk operations, remap, tree log, and global fallback paths.

The file explains the reserve model in detail: each reserve has a desired `size` and currently held `reserved` bytes. Reservations are charged to `space_info->bytes_may_use`, consumed when tree blocks are allocated, and released or migrated when operations finish.

## Reserve Model

Normal flow:

1. Reserve via `btrfs_block_rsv_add()` or `btrfs_block_rsv_refill()`.
2. Consume via `btrfs_use_block_rsv()`.
3. Finish via `btrfs_block_rsv_release()`.

Important reserve types described by the file:

- Transaction, delayed ops, and chunk reserves are scoped to specific operations.
- Global reserve is an overflow/fallback buffer for extent-tree and recovery-sensitive updates.
- Delalloc reserve is per-inode/file-extent/checksum oriented.
- Delayed refs reserve tracks delayed-reference metadata pressure and is preferentially refilled from excess.
- Empty reserve is a fallback for operations without a specific bucket.
- Temp reserve is used for unbounded truncate/iput-style operations, with `failfast` to force re-reservation loops.

## Key Functions

### Core accounting

`block_rsv_release_bytes()` is the internal release helper. It subtracts from reserve `size`, trims `reserved` down to `size`, optionally transfers excess to a destination reserve, frees remaining bytes from `space_info->bytes_may_use`, and returns qgroup metadata release amounts if requested.

`btrfs_block_rsv_add()` reserves metadata bytes from the reserve's `space_info` and adds them to both `reserved` and `size`.

`btrfs_block_rsv_refill()` reserves only the missing amount needed to reach `num_bytes`.

`btrfs_block_rsv_release()` sends excess from delayed refs to global reserve, or from most other reserves to delayed refs when possible, before freeing remaining bytes.

`btrfs_block_rsv_use_bytes()` subtracts bytes from a reserve if enough are available.

`btrfs_block_rsv_add_bytes()` adds bytes to a reserve and optionally grows `size`.

`btrfs_block_rsv_migrate()` consumes bytes from one reserve and adds them to another.

### Initialization and teardown

`btrfs_init_block_rsv()` zeroes and initializes a reserve.

`btrfs_init_metadata_block_rsv()` initializes a metadata reserve and binds it to metadata `space_info`.

`btrfs_alloc_block_rsv()` allocates a heap reserve.

`btrfs_free_block_rsv()` releases all bytes and frees the object.

`btrfs_init_root_block_rsv()` assigns each special tree root to the correct reserve:
- Extent/csum/free-space/block-group/raid-stripe roots use delayed refs reserve.
- Root/dev/quota roots use global reserve.
- Chunk root uses chunk reserve.
- Tree log uses treelog reserve.
- Remap tree uses remap reserve.
- Other roots default to no root reserve.

`btrfs_init_global_block_rsv()` binds global filesystem reserves to their correct `space_info`, with a dedicated treelog subgroup in zoned mode, then updates the global reserve.

`btrfs_release_global_block_rsv()` releases global reserve and warns if other global reserves still hold size/reserved bytes.

### Global reserve sizing

`btrfs_update_global_block_rsv()` computes global reserve size from used bytes in global roots, extent/csum/free-space roots, block-group and stripe roots when enabled, and a minimum unlink/delayed-ref safety budget. It caps size at `SZ_512M`, adjusts `space_info->bytes_may_use`, marks the reserve full if exact, and may force chunk allocation if reserve size exceeds current space.

### Reserve selection and use

`get_block_rsv()` chooses the reserve for a tree-block allocation:
- Shareable roots, uuid root, and checksum-tree updates while adding checksums use the transaction reserve.
- Otherwise root-specific reserve is used.
- If none exists, empty reserve is used.

`btrfs_use_block_rsv()` consumes a block from the selected reserve. If direct use fails, it may:
- Refresh the global reserve once.
- Try a no-flush metadata reservation.
- Refuse tree-log global fallback, forcing fsync to fall back to commit.
- Use global reserve if compatible.
- Try emergency flush reservation as a last resort.

`btrfs_check_trunc_cache_free_space()` checks whether a reserve has enough space for truncating free-space cache and updating an inode.

## Integration Points

The file depends on:
- `space-info` for metadata reservation and freeing.
- Root IDs and root item accounting.
- Transaction handles.
- Block-group and zoned-mode subgroup setup.
- Qgroup metadata reserve accounting.
- Tree-log behavior.

It is used by tree block allocation, transaction commit/update paths, delayed refs, inode updates, chunk-tree operations, and truncation/eviction code.

## Concurrency Notes

Every reserve has a spinlock protecting `size`, `reserved`, `full`, and qgroup reserve counters.

`btrfs_update_global_block_rsv()` locks both the space-info and reserve while changing reserve size and `bytes_may_use`.

`btrfs_block_rsv_full()` is intentionally a lockless/data-race-tolerant fast path defined in the header.

## Error Handling

Most public functions return `-ENOSPC` when reservation or use fails.

`btrfs_use_block_rsv()` returns `ERR_PTR(ret)` for allocation failure paths.

Tree-log allocation explicitly avoids consuming global reserve or emergency metadata, because log trees are optimizations and should fall back to full transaction commit.

## Risks And Edge Cases

The release path can move bytes into delayed refs or global reserve. Incorrect destination selection would skew metadata accounting or starve delayed refs.

`num_bytes == (u64)-1` has special meaning: release the full reserve size.

Global reserve sizing must track new global roots/features. Missing a root type can under-reserve for transaction-critical updates.

Zoned mode uses a special treelog `space_info` subgroup; non-zoned assumptions would break treelog reservation isolation.

## Testing Signals

Relevant coverage includes:
- Metadata ENOSPC and overcommit behavior.
- Delayed refs reserve refill from released bytes.
- Global reserve update after root usage changes.
- Tree-log allocation failure fallback.
- Truncate/iput temp reserve failfast behavior.
- Zoned treelog reservation subgroup handling.
- Qgroup metadata release accounting.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/block-rsv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/block-rsv.h -->
# File Research: sources/os/linux/linux/fs/btrfs/block-rsv.h

## Scope And Role

`block-rsv.h` defines the public interface for Btrfs metadata block reservations. It declares reserve types, the `struct btrfs_block_rsv` layout, reserve lifecycle/accounting APIs, and small inline helpers for lock-safe or lockless reserve inspection.

## Reserve Types

`enum btrfs_rsv_type` defines the reserve buckets:

- `BTRFS_BLOCK_RSV_GLOBAL`
- `BTRFS_BLOCK_RSV_DELALLOC`
- `BTRFS_BLOCK_RSV_TRANS`
- `BTRFS_BLOCK_RSV_CHUNK`
- `BTRFS_BLOCK_RSV_REMAP`
- `BTRFS_BLOCK_RSV_DELOPS`
- `BTRFS_BLOCK_RSV_DELREFS`
- `BTRFS_BLOCK_RSV_TREELOG`
- `BTRFS_BLOCK_RSV_EMPTY`
- `BTRFS_BLOCK_RSV_TEMP`

These correspond to transaction metadata, delayed allocation, chunk-tree work, remap-tree work, delayed operations, delayed references, tree logging, fallback, and temporary unbounded operations.

## Main Structure

`struct btrfs_block_rsv` contains:

- `size`: target reservation size.
- `reserved`: currently reserved bytes.
- `space_info`: backing metadata/system/remap space info.
- `lock`: protects mutable fields.
- `full`: whether `reserved >= size`.
- `failfast`: return ENOSPC quickly instead of falling back.
- `type`: reserve type.
- `qgroup_rsv_size` and `qgroup_rsv_reserved`: qgroup metadata reservation equivalents.

The qgroup comment explains that qgroup metadata reservation tracks possible quota metadata needs differently from normal metadata reservations. It cares about net extent usage changes, not checksum size or exact tree block count.

## Public API

Initialization/allocation:
- `btrfs_init_block_rsv()`
- `btrfs_init_root_block_rsv()`
- `btrfs_alloc_block_rsv()`
- `btrfs_init_metadata_block_rsv()`
- `btrfs_free_block_rsv()`

Reservation accounting:
- `btrfs_block_rsv_add()`
- `btrfs_block_rsv_check()`
- `btrfs_block_rsv_refill()`
- `btrfs_block_rsv_migrate()`
- `btrfs_block_rsv_use_bytes()`
- `btrfs_block_rsv_add_bytes()`
- `btrfs_block_rsv_release()`

Global reserve:
- `btrfs_update_global_block_rsv()`
- `btrfs_init_global_block_rsv()`
- `btrfs_release_global_block_rsv()`

Use helpers:
- `btrfs_use_block_rsv()`
- `btrfs_check_trunc_cache_free_space()`
- `btrfs_unuse_block_rsv()`

`btrfs_unuse_block_rsv()` adds bytes back to a reserve without growing its size, then releases excess.

## Inline Helpers

`btrfs_block_rsv_full()` returns `rsv->full` through `data_race()` as a fast lockless path.

`btrfs_block_rsv_reserved()` locks the reserve, reads `reserved`, and unlocks. The comment says this is for contexts where stale values are acceptable but direct lockless reads would trigger KCSAN warnings.

`btrfs_block_rsv_size()` similarly returns `size` under the spinlock.

## Integration Points

This header forwards declarations for transaction handles, roots, filesystem info, space info, and reserve flush modes. It is consumed by transaction code, inode/delalloc code, delayed refs, chunk allocation, tree-log code, qgroups, and block-group accounting.

## Concurrency Notes

The reserve lock protects exact accounting fields. The header explicitly distinguishes:
- Lockless approximate/full checks through `data_race()`.
- Locked stale-tolerant reads for KCSAN cleanliness.
- Mutation through implementation functions in `block-rsv.c`.

## Risks And Edge Cases

Callers must use the correct reserve type because release behavior and fallback logic differ by type.

Direct field access can race; helper use is expected unless the caller already holds `lock`.

Qgroup reserve fields are not equivalent to normal `size/reserved`, so they should not be mechanically updated as if they represented the same resource.

## Testing Signals

Expected coverage is mostly indirect:
- ENOSPC reservation paths.
- Delalloc metadata reservation.
- Delayed ref reservation release/refill.
- Global reserve fallback.
- Tree-log reserve failure.
- Qgroup metadata reserve accounting.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/block-rsv.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/btrfs_inode.h -->
# File Research: sources/os/linux/linux/fs/btrfs/btrfs_inode.h

## Scope And Role

`btrfs_inode.h` defines Btrfs' in-memory inode wrapper, inode runtime flags, inode helper functions, and prototypes for inode operations implemented across Btrfs. It is the main interface between VFS inodes and Btrfs-specific metadata, extent mapping, delayed allocation, fsync/logging, orphan handling, encoded I/O, checksums, and inode lifecycle management.

The central type is `struct btrfs_inode`, which embeds `struct inode vfs_inode` as the VFS-facing object and adds Btrfs state.

## Constants And Runtime Flags

`BTRFS_DIR_START_INDEX` is `2`, because directory positions `0` and `1` are reserved for `.` and `..`.

The runtime flag enum includes flags for:

- Close/writeback behavior: `BTRFS_INODE_FLUSH_ON_CLOSE`.
- Dummy/free-space/root-stub special inodes.
- Defrag and async extents.
- Full fsync/logging behavior.
- Property/xattr/capability cache state.
- Snapshot flush.
- Delalloc deadlock avoidance: `BTRFS_INODE_NO_DELALLOC_FLUSH`.
- Verity setup serialization.
- COW write error tracking.

Several comments document strict locking requirements:
- `BTRFS_INODE_NEEDS_FULL_SYNC` must be set under the VFS inode lock except during safe initialization/loading contexts.
- `BTRFS_INODE_NO_DELALLOC_FLUSH` avoids deadlock when dirty pages in a locked range need a transaction reservation.
- `BTRFS_INODE_ROOT_STUB` represents a subvolume dentry without a root reference in snapshot/subvolume nesting cases.

## Main Structure

`struct btrfs_inode` includes:

- Root and inode identity:
  - `root`
  - `objectid` on 32-bit systems
  - `generation`
  - `vfs_inode`

- Compression/defrag properties:
  - `prop_compress`
  - `defrag_compress`
  - `defrag_compress_level`

- Core locks and mapping trees:
  - `lock`
  - `extent_tree`
  - `io_tree`
  - optional `file_extent_tree`
  - `log_mutex`
  - `ordered_tree_lock`
  - `i_mmap_lock`

- Delalloc and extent accounting:
  - `outstanding_extents`
  - ordered extent rb tree and cache pointer
  - `delalloc_inodes` list
  - `delalloc_bytes`
  - `new_delalloc_bytes`
  - `defrag_bytes`
  - `disk_i_size`
  - `csum_bytes`

- Fsync/logging fields:
  - `last_trans`
  - `logged_trans`
  - `last_sub_trans`
  - `last_log_commit`
  - directory log index state
  - `last_unlink_trans`
  - `last_reflink_trans`

- Directory and subvolume state:
  - `index_cnt`
  - `dir_index`
  - `first_dir_index_to_log`
  - `last_dir_index_offset`
  - `ref_root_id` for root stubs

- On-disk inode flags:
  - `flags`
  - `ro_flags`

- Reservation and delayed work:
  - embedded `struct btrfs_block_rsv block_rsv`
  - `delayed_node`
  - `delayed_iput`

- Creation time:
  - `i_otime_sec`
  - `i_otime_nsec`

Many fields are protected by `lock`, `log_mutex`, the VFS inode lock, or are specific to directories/files/data relocation as documented inline.

## Important Helpers

Directory log index helpers:
- `btrfs_get_first_dir_index_to_log()`
- `btrfs_set_first_dir_index_to_log()`

`BTRFS_I()` is a type-checked and const-preserving macro that converts a VFS `struct inode *` to `struct btrfs_inode *`.

`btrfs_inode_hash()` hashes inode objectid and root objectid, folding to 32 bits on 32-bit systems.

`btrfs_ino()` returns the Btrfs inode number. On 32-bit systems it uses the stored 64-bit `objectid`, except root stubs use `vfs_inode.i_ino`.

`btrfs_get_inode_key()` fills a `BTRFS_INODE_ITEM_KEY`.

`btrfs_set_inode_number()` updates both Btrfs and VFS inode numbers as needed.

`btrfs_i_size_write()` writes VFS inode size and Btrfs `disk_i_size`.

`btrfs_is_free_space_inode()` checks the free-space-inode runtime flag.

`is_data_inode()` excludes the btree inode objectid.

`btrfs_mod_outstanding_extents()` adjusts outstanding extent count and emits a tracepoint except for free-space inodes.

`btrfs_set_inode_last_sub_trans()` records log transaction modification after buffered, direct, or mmap writes.

`btrfs_set_inode_full_sync()` marks full fsync needed and pessimistically advances `last_reflink_trans` to at least `last_trans`.

`btrfs_inode_in_log()` checks whether the inode is already logged for a generation.

`btrfs_inode_can_compress()` rejects compression for `NODATACOW` or `NODATASUM`.

`btrfs_assert_inode_locked()` asserts VFS inode lock ownership.

`btrfs_update_inode_mapping_flags()` maps `NODATASUM` to stable-writes behavior.

`btrfs_set_inode_mapping_order()` sets folio order ranges under experimental config for data inodes.

## Declared API Groups

Checksum and data integrity:
- `btrfs_calculate_block_csum_folio()`
- `btrfs_calculate_block_csum_pages()`
- `btrfs_check_block_csum()`
- `btrfs_data_csum_ok()`

NOCOW and extents:
- `can_nocow_extent()`
- `btrfs_get_extent()`
- `btrfs_get_extent_allocation_hint()`
- `btrfs_create_io_em()`

Directory/link/subvolume:
- `btrfs_lookup_dentry()`
- `btrfs_set_inode_index()`
- `btrfs_unlink_inode()`
- `btrfs_add_link()`
- `btrfs_delete_subvolume()`

Truncation/expansion/preallocation:
- `btrfs_truncate_block()`
- `btrfs_cont_expand()`
- `btrfs_prealloc_file_range()`
- `btrfs_prealloc_file_range_trans()`

Delalloc:
- `btrfs_del_delalloc_inode()`
- `btrfs_start_delalloc_snapshot()`
- `btrfs_start_delalloc_roots()`
- `btrfs_set_extent_delalloc()`
- `btrfs_set_delalloc_extent()`
- `btrfs_clear_delalloc_extent()`
- `btrfs_merge_delalloc_extent()`
- `btrfs_split_delalloc_extent()`
- `btrfs_run_delalloc_range()`
- `btrfs_writepage_cow_fixup()`

New inode creation:
- `struct btrfs_new_inode_args`
- `btrfs_new_inode_prepare()`
- `btrfs_create_new_inode()`
- `btrfs_new_inode_args_destroy()`
- `btrfs_new_subvol_inode()`

Lifecycle/cache:
- `btrfs_evict_inode()`
- `btrfs_alloc_inode()`
- `btrfs_destroy_inode()`
- `btrfs_free_inode()`
- `btrfs_drop_inode()`
- `btrfs_init_cachep()`
- `btrfs_destroy_cachep()`
- `btrfs_iget_path()`
- `btrfs_iget()`

Metadata/orphan/delayed iput:
- `btrfs_update_inode()`
- `btrfs_update_inode_fallback()`
- `btrfs_orphan_add()`
- `btrfs_orphan_cleanup()`
- `btrfs_add_delayed_iput()`
- `btrfs_run_delayed_iputs()`
- `btrfs_wait_on_delayed_iputs()`

Encoded I/O:
- `btrfs_encoded_io_compression_from_extent()`
- `btrfs_encoded_read_regular_fill_pages()`
- `btrfs_encoded_read()`
- `btrfs_encoded_read_regular()`
- `btrfs_do_encoded_write()`

Locking and bytes:
- `btrfs_inode_lock()`
- `btrfs_inode_unlock()`
- `btrfs_update_inode_bytes()`
- `btrfs_assert_inode_range_clean()`

## Integration Points

This header includes VFS, mm, fscrypt, tracepoints, Btrfs ctree definitions, block reserves, extent maps, and extent I/O trees.

It connects inode code with:
- Delalloc and ordered extents.
- Extent maps and file extent items.
- Checksums and bio validation.
- Tree logging/fsync.
- Subvolume lookup/deletion.
- Orphan cleanup.
- Encoded read/write ioctls.
- Compression, verity, fscrypt, and qgroup-related accounting through downstream implementations.

## Concurrency Notes

`struct btrfs_inode::lock` protects most inode accounting and fsync fields.

`log_mutex` protects inode logging and directory log offset state.

`ordered_tree_lock` protects ordered extents.

`i_mmap_lock` participates in full-sync flag safety.

The VFS inode lock is required for certain runtime flags and reflink/fsync state transitions.

The header uses `READ_ONCE()` and `WRITE_ONCE()` for directory log index state.

## Risks And Edge Cases

On 32-bit systems, inode number handling is special to avoid truncating 64-bit Btrfs objectids.

Root stub inodes intentionally break normal root-reference assumptions and must be identified through `BTRFS_INODE_ROOT_STUB`.

Fsync correctness depends on interactions among `last_trans`, `logged_trans`, `last_sub_trans`, `last_log_commit`, `last_reflink_trans`, and runtime flags. Incorrect locking or stale updates can make fsync skip necessary work.

Compression eligibility must reject `NODATACOW` and `NODATASUM`.

`BTRFS_INODE_NO_DELALLOC_FLUSH` is a deadlock avoidance mechanism; setting/clearing it incorrectly can either deadlock or reduce flushing effectiveness.

## Testing Signals

Relevant tests should cover:
- 32-bit inode-number preservation.
- Fast vs full fsync transitions.
- Reflink followed by fsync and checksum logging.
- Root stub lookup through snapshot/subvolume nesting.
- Delalloc accounting and extent split/merge.
- NODATACOW/NODATASUM compression rejection.
- Encoded read/write paths.
- Verity enable serialization.
- Free-space inode special behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/btrfs_inode.h -->