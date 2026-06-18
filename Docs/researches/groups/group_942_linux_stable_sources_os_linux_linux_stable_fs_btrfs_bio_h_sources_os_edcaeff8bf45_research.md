# Group Research: Btrfs BIO, Block Group, Block Reserve, And Inode Interfaces

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/bio.h -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/bio.h

## Purpose

`bio.h` defines Btrfs' high-level I/O wrapper around the kernel `struct bio`. `struct btrfs_bio` carries filesystem-specific context needed before and after the generic block layer sees an I/O: inode/file offset, checksum state, ordered extent state, metadata parent checks, mirror selection, split-I/O accounting, and Btrfs end-I/O callbacks.

## Main Data Structures And APIs

- `BTRFS_BIO_INLINE_CSUM_SIZE` reserves 64 inline bytes for read checksum storage before falling back to external checksum memory.
- `btrfs_bio_end_io_t` is the Btrfs-level completion callback type.
- `struct btrfs_bio` embeds `struct bio` last, which is required because `bio_alloc_bioset()` allocates enough trailing memory based on that layout.
- `btrfs_bio()` converts a generic `struct bio *` back to `struct btrfs_bio *`.
- Bioset lifecycle:
  - `btrfs_bioset_init()`
  - `btrfs_bioset_exit()`
- Allocation and initialization:
  - `btrfs_bio_init()`
  - `btrfs_bio_alloc()`
- Completion/submission:
  - `btrfs_bio_end_io()`
  - `btrfs_submit_bbio()`
  - `btrfs_submit_repair_write()`
  - `btrfs_repair_io_failure()`
- `REQ_BTRFS_CGROUP_PUNT` aliases `REQ_FS_PRIVATE` for submission through `blkcg_punt_bio_submit`.

## State Carried By `struct btrfs_bio`

- Common fields:
  - `inode` and `file_offset` identify the data or metadata object covered by the I/O.
  - `end_io` and `private` carry caller completion context.
  - `pending_ios` tracks split physical I/Os under one logical Btrfs bio.
  - `mirror_num` selects or records a mirror.
  - `status` preserves the first split bio error.
- Data read union state:
  - `csum`, `csum_inline`, and `saved_iter` support checksum verification and read repair.
  - `csum_search_commit_root` forces checksum lookup against the commit root.
- Data write union state:
  - `ordered` links the bio to ordered extent completion.
  - `sums` points at checksums generated for writeback.
  - `csum_work`, `csum_done`, and `csum_saved_iter` support synchronous or async checksum calculation.
  - `orig_physical` is needed for zone append.
  - `orig_logical` is needed when checksumming fscrypt bios.
- Metadata read union state:
  - `parent_check` carries tree parentness verification state.
- Internal end-I/O state:
  - `end_io_work` allows read completion work to be deferred.
- Boolean flags distinguish scrub bios, remapped copy I/O, async checksums, and zone append eligibility.

## Integration Points

This header is shared by the Btrfs I/O stack. Data reads use it for checksum validation and read repair. Data writes use it to connect bios to ordered extents and checksum generation. Metadata callers use it for parent checks but remain responsible for metadata-specific validation. The repair APIs connect failed logical/file offsets to mirrors and physical addresses.

## Risks And Invariants

- `struct bio bio` must remain the last member; moving it would break bioset allocation assumptions.
- The union fields are context-specific. Callers must not interpret read checksum fields as write ordered-extent fields, or metadata parent-check fields as data-I/O fields.
- Split I/O completion depends on `pending_ios` and `status` preserving the first error while all split physical bios finish.
- Zone append and fscrypt checksum paths depend on `orig_physical` and `orig_logical` being populated consistently before submission.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/bio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/block-group.c -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/block-group.c

## Purpose

`block-group.c` implements Btrfs block-group lifecycle and accounting. It covers allocation-profile selection, block-group lookup/refcounting, free-space caching, mount-time block-group loading, read-only transitions, unused block-group deletion, relocation-based reclaim, dirty block-group persistence, chunk allocation phases, system chunk metadata reservation, frozen block-group cleanup, swap extent pins, data block-group size classes, and fully remapped block-group recovery.

## Major Functional Areas

### Allocation Profile Selection

- `get_restripe_target()` checks active balance conversion state and returns a target profile for data, system, or metadata block groups.
- `btrfs_reduce_alloc_profile()` filters available profiles by writable device count and picks the highest redundancy profile available, preferring RAID1C4, RAID6, RAID1C3, RAID5, RAID10, RAID1, DUP, then RAID0.
- `btrfs_get_alloc_profile()` reads the filesystem's available profile bits under `profiles_lock`, combines them with the requested block-group type, and reduces to the chunk-format allocation profile.
- `set_avail_alloc_bits()` and `clear_avail_alloc_bits()` maintain `avail_data_alloc_bits`, `avail_metadata_alloc_bits`, and `avail_system_alloc_bits`.
- `clear_incompat_bg_bits()` clears RAID56 or RAID1C34 incompat bits only after verifying no remaining block groups use those profile families.

### Block-Group Cache And Lookup

- `btrfs_create_block_group()` allocates and initializes an in-memory `struct btrfs_block_group`, including free-space control, locks, lists, reference count, discard state, frozen counter, and size/full-stripe metadata.
- `btrfs_add_block_group_cache()` inserts the block group into `fs_info->block_group_cache_tree`, keyed by logical start.
- `btrfs_lookup_first_block_group()`, `btrfs_lookup_block_group()`, and `btrfs_next_block_group()` provide refcounted tree iteration and lookup.
- `btrfs_get_block_group()` / `btrfs_put_block_group()` manage lifetime. Final put warns about leaked pinned/reserved bytes, cancels any remaining discard list entry, frees free-space control, chunk physical maps, and the block-group object.

### NOCOW And Reservation Pins

- `btrfs_inc_nocow_writers()` looks up the containing block group, checks it is not read-only under `bg->lock`, increments `nocow_writers`, and returns a referenced block group.
- `btrfs_dec_nocow_writers()` decrements `nocow_writers`, wakes waiters at zero, and drops the lookup reference.
- `btrfs_wait_nocow_writers()` waits for all NOCOW writers to exit.
- `btrfs_dec_block_group_reservations()` and `btrfs_wait_block_group_reservations()` coordinate the window between extent allocation and ordered-extent creation, especially before relocating or removing read-only data block groups.

### Free-Space Caching

- `btrfs_get_caching_control()` and `btrfs_put_caching_control()` manage caching-control references.
- `btrfs_wait_block_group_cache_progress()` waits for free-space cache progress after allocation failure, requiring progress plus enough free space or cache completion.
- `load_extent_tree_free()` scans committed extent-tree items, derives gaps as free space, excludes superblock stripes, periodically wakes waiters, and reschedules to avoid starving commit-root users.
- `load_block_group_size_class()` samples up to five file extents from the committed extent tree to infer a best-effort data block-group size class.
- `caching_thread()` chooses old space cache, free-space tree, or extent-tree scan, updates `cached` state, optionally fragments free space under debug options, clears excluded extents, and wakes waiters.
- `btrfs_cache_block_group()` starts or joins caching work, except on zoned filesystems and remapped block groups where allocator behavior does not use the normal cache.
- `btrfs_add_new_free_space()` adds free ranges to the in-memory free-space cache while skipping `excluded_extents`.

### Mount-Time Loading

- `read_bg_from_eb()` verifies a block-group item matches the corresponding chunk map.
- `find_first_block_group()` scans the block-group root, which is either the block-group tree or extent tree depending on feature flags.
- `exclude_super_stripes()` maps physical superblock locations back to logical addresses and marks those logical stripes excluded from free space; zoned block groups must not contain superblock stripes.
- `read_one_block_group()` constructs an in-memory block group from an on-disk item, validates mixed/data/metadata compatibility, loads zoned information, initializes free-space state for full/empty/zoned cases, inserts it into caches and space info, marks empty groups unused or queues discard, and marks unwritable chunks read-only.
- `fill_dummy_bgs()` creates full dummy block groups from chunk maps for read-only rescue cases where block-group items cannot be trusted or loaded.
- `btrfs_read_block_groups()` scans all on-disk block-group items, handles old space-cache invalidation, adds sysfs profile entries, marks unmirrored RAID0/SINGLE groups read-only when mirrored groups exist, initializes global reserves, and verifies chunk/block-group mapping consistency. With `IGNOREBADROOTS`, it falls back to dummy block groups.

### Block-Group Removal And Unused Cleanup

- `remove_block_group_item()` deletes a block-group item from the block-group root.
- `btrfs_remove_bg_from_sinfo()` subtracts block-group totals from `space_info`.
- `btrfs_start_trans_remove_block_group()` calculates metadata reservation units needed to remove a block group and starts a transaction using the global reserve fallback.
- `btrfs_remove_block_group()` performs full removal:
  - Requires the block group to be read-only or remapped.
  - Cancels free-space cache I/O and dirty-list membership.
  - Removes free-space inode/cache state.
  - Erases the block group from the lookup tree and space-info RAID list.
  - Updates allocation profile availability and feature bits.
  - Waits for caching if needed and removes caching-control list entries.
  - Removes free-space tree entries and on-disk block-group item.
  - Marks the block group removed.
  - Removes the chunk map immediately only if no freezer is active.
- `clean_pinned_extents()` clears block-group ranges from current and previous transaction pinned extents under `unused_bg_unpin_mutex`.
- `btrfs_link_bg_list()` adds a block group to an fs list with consistent refcounting.
- `btrfs_delete_unused_bgs()` drains `unused_bgs`, skipping or retrying groups that are still used, read-only due to balance, singular for their profile, fully remapped, not fully discarded with async discard, needed for outstanding reservations, or still containing unwritten zoned metadata. Eligible groups are marked read-only, optionally zone-finished, have pinned extents cleared, and are removed through `btrfs_remove_chunk()`.

### Reclaim

- `should_reclaim_block_group()` triggers reclaim when a block group crosses below its reclaim threshold from above.
- `btrfs_reclaim_block_group()` validates that the group is not reserved, pinned, or read-only; skips empty groups into unused cleanup; sets it read-only; relocates its chunk; and records reclaim statistics/errors.
- `btrfs_reclaim_block_groups()` sorts reclaim candidates by used bytes, runs relocation under the exclusive balance operation, interleaves unused block-group deletion to avoid long cleaner stalls, and preserves retry candidates.
- `btrfs_reclaim_bgs_work()`, `btrfs_reclaim_bgs()`, and `btrfs_mark_bg_to_reclaim()` connect reclaim to worker scheduling and threshold detection.
- Zoned filesystems use `btrfs_zoned_should_reclaim()` to decide whether reclaim should run.

### Read-Only State

- `inc_block_group_ro()` is the internal accounting path. It rejects swap-pinned groups, checks whether enough alternate space exists unless forced, increments `ro`, moves available or zone-unusable bytes into `bytes_readonly`, and links the group to `ro_bgs`.
- `btrfs_inc_block_group_ro()` wraps this with transaction handling, dirty-block-group commit synchronization, optional chunk preallocation, zoned activation, system chunk checks, read-only mount handling, and `ro_block_group_mutex`.
- `btrfs_dec_block_group_ro()` decrements `ro` and reverses readonly/zone-unusable accounting when the count reaches zero.
- `btrfs_inc_block_group_swap_extents()` refuses to pin swap extents in read-only groups, and `btrfs_dec_block_group_swap_extents()` releases swap pins.

### Dirty Block-Group Persistence

- `insert_block_group_item()` writes a new block-group item, including v2 remap fields when `REMAP_TREE` is enabled, and updates `last_*` mirrors.
- `update_block_group_item()` updates on-disk used/remap/identity-remap/flags values only when they changed, with rollback of `last_*` values on most failures.
- `cache_save_setup()` prepares old free-space cache writeback: creates/looks up free-space inodes, invalidates cache generation before writing, truncates stale cache files, preallocates contiguous cache space, and marks disk-cache state.
- `btrfs_setup_space_cache()` prepares dirty groups with `BTRFS_DC_CLEAR` before commit when old space cache is enabled.
- `btrfs_start_dirty_block_groups()` starts cache writeback before the transaction critical section, creates pending block groups, updates block-group items, retries once after delayed refs, and requeues groups whose item does not exist yet.
- `btrfs_write_dirty_block_groups()` completes dirty block-group updates in the commit critical section, waits for cache I/O, handles rare free-space endio races that create new block groups, and aborts the transaction on persistent metadata update errors.
- `btrfs_update_block_group()` updates superblock bytes-used, block-group `used/reserved/pinned`, space-info counters, pinned extents, dirty-list membership, unused-list membership, and reclaim-list membership.

### Chunk Allocation

- `should_alloc_chunk()` decides whether to allocate a chunk based on force mode, limited mode free-space threshold, and 80% usage.
- `btrfs_force_chunk_alloc()` forces allocation for a given type.
- `do_chunk_alloc()` reserves system chunk metadata, creates the chunk/block group, adds the chunk item, handles degraded/scrub/discard `-ENOSPC` exceptions by creating a system chunk and retrying, then returns a referenced block group.
- `btrfs_chunk_alloc()` is phase 1 of chunk allocation:
  - Rejects re-entry and direct system chunk allocation.
  - Serializes allocation through `space_info->chunk_alloc` and `fs_info->chunk_mutex`.
  - Preserves mixed data/metadata allocation behavior.
  - Optionally forces metadata allocation after a configured data/metadata ratio.
  - Creates the chunk and chunk item, activates zoned data groups for extent allocation, clears force/full state, and returns whether a chunk was allocated.
- `btrfs_create_pending_block_groups()` is phase 2:
  - Inserts block-group items.
  - Adds chunk items if not already inserted.
  - Inserts device extents.
  - Adds free-space tree entries.
  - Adds sysfs RAID profile entries.
  - Releases delayed-ref reservations for block-group inserts and marks still-unused new groups unused.
- The two-phase design prevents deadlocks from inserting extent-tree block-group items while COWing extent-tree nodes.

### System Chunk Metadata Reservation

- `get_profile_num_devs()` determines how many device items a profile can require.
- `reserve_chunk_space()` reserves system metadata in `chunk_block_rsv`, creating a system chunk if free system space is insufficient. It must run under `chunk_mutex`.
- `check_system_chunk()` reserves enough system space to add/remove a chunk item and update device items.
- `btrfs_reserve_chunk_metadata()` reserves system space for chunk-tree updates outside normal chunk allocation/removal.

### Teardown And Cleanup

- `btrfs_put_block_group_cache()` waits for caching and releases free-space inode references.
- `check_removing_space_info()` warns on leaked pinned/may-use/reserved/reclaim bytes and removes child subgroups.
- `btrfs_free_block_groups()` drains caching, unused, reclaim, fully-remapped, zoned-active, and rb-tree block-group lists; removes free-space caches; asserts list/refcount/swap invariants; releases global reserves; and removes space-info sysfs state. It must run after workers stop.
- `btrfs_freeze_block_group()` and `btrfs_unfreeze_block_group()` delay chunk-map removal while trim/scrub/discard users may still reference a removed block group. Final unfreeze removes the chunk map and any leftover free-space cache.

### Size Classes And Fully Remapped Groups

- `btrfs_calc_block_group_size_class()` maps allocation size to small (`<=128K`), medium (`<=8M`), or large.
- `btrfs_block_group_should_use_size_class()` enables size classes only for non-zoned data-only block groups.
- `btrfs_use_block_group_size_class()` sets or validates a block group's size class, returning `-EAGAIN` for racing first allocations of mismatched sizes unless forced.
- `btrfs_maybe_reset_size_class()` clears the class when an eligible group becomes empty and unreserved.
- `btrfs_mark_bg_fully_remapped()` queues remapped groups for async discard or the fully-remapped list.
- `btrfs_populate_fully_remapped_bgs_list()` reconstructs the fully-remapped list at mount by comparing block-group and chunk trees, handling cases where unmount happened before async discard removed dead stripes/device extents.

## Dependencies

- Btrfs subsystems: extent tree, block-group tree, free-space cache/tree, space-info accounting, chunk/device mapping, transactions, delayed refs, relocation, discard, sysfs, tree log, zoned allocation, RAID56 mapping, ref verification, and filesystem feature flags.
- Kernel primitives: rb trees, lists, refcounts, spinlocks, rwsems, mutexes, workqueues, wait queues, sequence locks, ratelimits, and kobjects.
- Important shared state:
  - `fs_info->block_group_cache_tree`
  - `fs_info->mapping_tree`
  - `fs_info->space_info`
  - `fs_info->unused_bgs`
  - `fs_info->reclaim_bgs`
  - `fs_info->fully_remapped_bgs`
  - `fs_info->caching_block_groups`
  - `fs_info->excluded_extents`
  - `space_info` counters and RAID lists
  - `transaction->dirty_bgs`, `io_bgs`, `deleted_bgs`, and `pinned_extents`

## Risks And Invariants

- Chunk allocation must preserve its two-phase structure. Inserting block-group items into the extent tree during phase 1 can deadlock with extent-tree COW.
- System chunk updates must be serialized by `chunk_mutex`; otherwise chunk-tree COW can recurse into system allocation.
- Block-group removal must keep chunk maps alive while `frozen` users exist, because trim/scrub/discard can still rely on old logical-to-physical mappings.
- Dirty block-group updates rely on delayed-ref reservation counters. Forgetting to increment/decrement update or insert reservations leaks metadata reserve state.
- Free-space cache writeback races with block-group deletion and free-space endio workers; `cache_write_mutex`, dirty locks, and `io_list` ownership are central.
- NOCOW writers, reservations, swap extents, and read-only transitions must be coordinated before relocation/removal to avoid writing into moved or read-only groups.
- Zoned mode changes accounting semantics: `alloc_offset`, `zone_unusable`, active groups, metadata write pointers, and zone finish/activation paths must stay consistent.
- Feature bits and available profile bits must only be cleared after verifying no remaining block groups use the profile.
- Size classes are an optimization; enforcement must allow desperate fallback without corrupting block-group accounting.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/block-group.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/block-group.h -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/block-group.h

## Purpose

`block-group.h` declares the in-memory block-group model and public APIs for Btrfs block-group lookup, caching, allocation, accounting, reclaim, deletion, freezing, swap pins, size classes, and fully remapped block groups.

## Main Types

- `enum btrfs_disk_cache_state` tracks old free-space-cache persistence:
  - `BTRFS_DC_WRITTEN`
  - `BTRFS_DC_ERROR`
  - `BTRFS_DC_CLEAR`
  - `BTRFS_DC_SETUP`
- `enum btrfs_block_group_size_class` categorizes data block groups by allocation size:
  - none, small, medium, large.
- `enum btrfs_discard_state` tracks async discard passes over extents, bitmaps, reset cursor state, and fully remapped groups.
- `enum btrfs_chunk_alloc_enum` controls chunk allocation force:
  - no force, limited, force, force for extent allocation.
- `enum btrfs_block_group_flags` defines runtime flags such as removed, to-copy, relocating repair, chunk item inserted, active zone, zoned data relocation, free-space-tree needs/added, sequential zone, new block group, fully remapped, and stripe-removal pending.
- `enum btrfs_caching_type` tracks in-memory free-space cache progress.
- `struct btrfs_caching_control` represents async caching work with list linkage, mutex, wait queue, `btrfs_work`, target block group, progress counter, and reference count.
- `struct btrfs_block_group` is the central block-group state object.

## `struct btrfs_block_group` State

Important fields include:

- Identity and accounting:
  - `fs_info`, `inode`, `start`, `length`, `flags`, `global_root_id`
  - `pinned`, `reserved`, `used`, `delalloc_bytes`, `bytes_super`
  - `remap_bytes`, `identity_remap_count`
  - committed mirrors: `last_used`, `last_remap_bytes`, `last_identity_remap_count`, `last_flags`
- Free-space cache and allocation:
  - bitmap thresholds
  - `cached`, `caching_ctl`
  - `free_space_ctl`
  - `cluster_list`
  - `data_rwsem`
  - `full_stripe_len`
  - `size_class`
- Tree/list membership:
  - rb-tree `cache_node`
  - RAID/profile list `list`
  - shared `bg_list` for unused/reclaim/deleted/new lists
  - `ro_list`, `discard_list`, `dirty_list`, `io_list`, `active_bg_list`
- Coordination:
  - `lock`
  - `refs`
  - `frozen`
  - `reservations`
  - `nocow_writers`
  - `free_space_lock`
  - `swap_extents`
- Zoned fields:
  - `alloc_offset`
  - `zone_unusable`
  - `zone_capacity`
  - `meta_write_pointer`
  - `physical_map`
  - `zone_finish_work`
  - `last_eb`
- Reclaim/discard:
  - `discard_index`
  - `discard_eligible_time`
  - `discard_cursor`
  - `discard_state`
  - `reclaim_mark`

## Inline Helpers

- `btrfs_block_group_end()` returns `start + length`.
- `btrfs_is_block_group_used()` checks `used`, `reserved`, `pinned`, or `remap_bytes` under `bg->lock`.
- `btrfs_is_block_group_data_only()` excludes mixed groups and selects true data groups.
- `btrfs_block_group_available_space()` subtracts used, pinned, reserved, super stripes, and zone-unusable bytes.
- `btrfs_data_alloc_profile()`, `btrfs_metadata_alloc_profile()`, and `btrfs_system_alloc_profile()` wrap `btrfs_get_alloc_profile()`.
- `btrfs_block_group_done()` tests cache completion/error with a memory barrier.

## Public API Surface

The header exposes APIs for:

- Lookup/lifetime:
  - `btrfs_lookup_first_block_group()`
  - `btrfs_lookup_block_group()`
  - `btrfs_next_block_group()`
  - `btrfs_get_block_group()`
  - `btrfs_put_block_group()`
- NOCOW/reservation waits:
  - `btrfs_inc_nocow_writers()`
  - `btrfs_dec_nocow_writers()`
  - `btrfs_wait_nocow_writers()`
  - `btrfs_dec_block_group_reservations()`
  - `btrfs_wait_block_group_reservations()`
- Free-space cache:
  - `btrfs_wait_block_group_cache_progress()`
  - `btrfs_cache_block_group()`
  - `btrfs_get_caching_control()`
  - `btrfs_add_new_free_space()`
- Block-group creation/deletion/reclaim:
  - `btrfs_start_trans_remove_block_group()`
  - `btrfs_remove_bg_from_sinfo()`
  - `btrfs_remove_block_group()`
  - `btrfs_delete_unused_bgs()`
  - `btrfs_mark_bg_unused()`
  - `btrfs_reclaim_block_groups()`
  - `btrfs_reclaim_bgs_work()`
  - `btrfs_reclaim_bgs()`
  - `btrfs_mark_bg_to_reclaim()`
  - `btrfs_read_block_groups()`
  - `btrfs_make_block_group()`
- Read-only/dirty/cache commit handling:
  - `btrfs_inc_block_group_ro()`
  - `btrfs_dec_block_group_ro()`
  - `btrfs_start_dirty_block_groups()`
  - `btrfs_write_dirty_block_groups()`
  - `btrfs_setup_space_cache()`
  - `btrfs_update_block_group()`
- Reservation and chunk allocation:
  - `btrfs_add_reserved_bytes()`
  - `btrfs_free_reserved_bytes()`
  - `btrfs_chunk_alloc()`
  - `btrfs_force_chunk_alloc()`
  - `check_system_chunk()`
  - `btrfs_reserve_chunk_metadata()`
  - `btrfs_get_alloc_profile()`
  - `btrfs_rmap_block()`
- Teardown:
  - `btrfs_put_block_group_cache()`
  - `btrfs_free_block_groups()`
- Freeze/swap/size-class/remap:
  - `btrfs_freeze_block_group()`
  - `btrfs_unfreeze_block_group()`
  - `btrfs_inc_block_group_swap_extents()`
  - `btrfs_dec_block_group_swap_extents()`
  - `btrfs_calc_block_group_size_class()`
  - `btrfs_use_block_group_size_class()`
  - `btrfs_block_group_should_use_size_class()`
  - `btrfs_mark_bg_fully_remapped()`
  - `btrfs_populate_fully_remapped_bgs_list()`

## Dependencies

The header depends on Linux synchronization/refcount/list/rbtree primitives, Btrfs free-space cache definitions, public Btrfs tree flags, and forward declarations for transaction, inode, chunk map, and fs-info objects.

## Risks And Invariants

- Several counters are protected by different locks. `used/reserved/pinned/remap_bytes/swap_extents` require `bg->lock`; list membership often requires fs-level list locks or `groups_sem`.
- `bg_list` is intentionally multiplexed across several lists, so code must not assume a block group can be on unused, reclaim, deleted, and new lists simultaneously.
- The `frozen` counter protects logical/physical reuse after deletion; it is not a general reference count.
- Zoned-only fields must be interpreted only when the filesystem is zoned.
- Size-class state is best-effort and valid only for eligible data-only non-zoned block groups.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/block-group.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/block-rsv.c -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/block-rsv.c

## Purpose

`block-rsv.c` implements Btrfs metadata block reserves. A block reserve is a logical bucket with desired `size`, current `reserved` bytes, a metadata `space_info`, qgroup metadata reserve mirrors, and policy flags. These reserves allow transaction, delayed refs, delayed items, chunk updates, tree log, global fallback, remap, truncate, and temporary metadata users to reserve pessimistically and then release or migrate unused space safely.

## Block Reserve Model

The file-level comment defines the lifecycle:

- Reserve:
  - `btrfs_block_rsv_add()` and `btrfs_block_rsv_refill()` reserve metadata bytes through `btrfs_reserve_metadata_bytes()`.
  - Reserved bytes are accounted in `space_info->bytes_may_use`.
  - `btrfs_block_rsv_add()` also grows `block_rsv->size`.
- Use:
  - `btrfs_use_block_rsv()` selects the correct reserve and consumes bytes when tree blocks are allocated.
- Finish:
  - `btrfs_block_rsv_release()` shrinks `size`, returns excess `reserved` bytes, and preferentially refills delayed refs or global reserves before freeing to `space_info`.

Reserve types have distinct roles:

- Transaction, delayed operations, and chunk reserves are scoped to specific operations.
- Global reserve is the overflow reserve for extent tree updates and ENOSPC recovery paths such as eviction/truncate.
- Delalloc reserve covers per-inode metadata for file extents, inode updates, and checksums.
- Delayed refs reserve tracks expected delayed-reference metadata demand and is preferentially refilled from excess.
- Empty reserve falls back to on-demand reservation.
- Temp reserve supports unbounded operations such as truncate/iput, with `failfast` allowing work to stop and retry with a new reservation.

## Main APIs And Behavior

- `block_rsv_release_bytes()` is the core release helper:
  - Shrinks `size` by requested bytes or all bytes for `(u64)-1`.
  - Caps `reserved` to `size`.
  - Optionally computes qgroup excess.
  - Moves excess bytes to a destination reserve if it is not full.
  - Frees remaining excess from `space_info->bytes_may_use`.
- `btrfs_block_rsv_migrate()` consumes bytes from a source reserve and adds them to a destination reserve.
- `btrfs_init_block_rsv()` clears and initializes a reserve.
- `btrfs_init_metadata_block_rsv()` initializes a metadata reserve and binds it to metadata `space_info`.
- `btrfs_alloc_block_rsv()` allocates a heap reserve.
- `btrfs_free_block_rsv()` releases all bytes and frees it.
- `btrfs_block_rsv_add()` reserves metadata and grows `size/reserved`.
- `btrfs_block_rsv_check()` checks whether a reserve has at least `min_percent` of its target.
- `btrfs_block_rsv_refill()` only reserves the delta needed to satisfy `num_bytes`.
- `btrfs_block_rsv_release()` chooses the refill target:
  - delayed refs reserve releases excess toward global reserve.
  - most other non-global reserves release excess toward delayed refs if it is not full.
  - cross-`space_info` transfers are disallowed.
- `btrfs_block_rsv_use_bytes()` subtracts reserved bytes or returns `-ENOSPC`.
- `btrfs_block_rsv_add_bytes()` adds already-reserved bytes to a reserve and optionally grows `size`.

## Global And Root Reserve Setup

- `btrfs_update_global_block_rsv()` sizes the global reserve from root usage:
  - Starts with tree root usage.
  - Adds extent, checksum, and free-space tree global roots.
  - Adds block-group root for `BLOCK_GROUP_TREE`.
  - Adds stripe root for `RAID_STRIPE_TREE`.
  - Ensures enough minimum space for unlink metadata and delayed refs.
  - Caps reserve size at 512 MiB.
  - Updates `space_info->bytes_may_use`, grants tickets when shrinking, and may force chunk allocation if reserve size reaches total metadata space.
- `btrfs_init_root_block_rsv()` assigns root-level reserves:
  - extent/checksum/free-space/block-group/raid-stripe roots use delayed refs reserve.
  - root/device/quota roots use global reserve.
  - chunk root uses chunk reserve.
  - tree log uses treelog reserve.
  - remap root uses remap reserve.
  - other roots default to no root reserve.
- `btrfs_init_global_block_rsv()` binds fs-wide reserves to the right `space_info`:
  - chunk reserve uses system space.
  - remap reserve uses metadata-remap space.
  - global/trans/empty/delayed/delayed-refs use metadata space.
  - treelog uses metadata space, or a dedicated zoned treelog subgroup.
  - Then it initializes global reserve sizing.
- `btrfs_release_global_block_rsv()` releases the global reserve and warns if other fs-wide reserves still have size or reserved bytes.

## Reserve Selection And Use

- `get_block_rsv()` chooses a reserve for a tree block allocation:
  - Shareable roots, UUID root, and checksum-tree writes during checksum insertion use the transaction reserve.
  - Otherwise use `root->block_rsv`.
  - Fall back to `empty_block_rsv`.
- `btrfs_use_block_rsv()` consumes one tree block worth of metadata:
  - Tries the selected reserve first.
  - Honors `failfast`.
  - Refreshes global reserve once if using it.
  - Emits ENOSPC debug warnings for most non-delayed-ref failures.
  - Attempts a direct no-flush reservation.
  - Refuses tree-log fallback to global/emergency reserves so fsync can fall back to full transaction commit.
  - May consume from global reserve if same `space_info`.
  - As a last resort, attempts `BTRFS_RESERVE_FLUSH_EMERGENCY`.
- `btrfs_check_trunc_cache_free_space()` verifies a reserve has enough bytes for truncating free-space cache plus inode update.

## Dependencies

- Space-info accounting:
  - `btrfs_reserve_metadata_bytes()`
  - `btrfs_space_info_free_bytes_may_use()`
  - `btrfs_space_info_update_bytes_may_use()`
  - `btrfs_try_granting_tickets()`
- Root/tree accounting:
  - `btrfs_root_used()`
  - `btrfs_calc_insert_metadata_size()`
  - `btrfs_calc_metadata_size()`
  - `btrfs_calc_delayed_ref_bytes()`
- Filesystem feature checks:
  - block-group tree
  - RAID stripe tree
  - zoned mode
- Transaction/root identity is needed to choose reserves safely.

## Risks And Invariants

- `size` and `reserved` must be changed under `block_rsv->lock`.
- Releasing bytes must not transfer reserves across different `space_info` objects.
- The global reserve is deliberately protected from tree-log allocations; consuming it for fsync log trees can increase transaction-abort risk.
- `failfast` is critical for truncate/temp reserves because those operations are unbounded and must be able to stop, commit/re-reserve, and continue.
- Global reserve sizing must include roots introduced by optional features, or ENOSPC handling can under-reserve metadata required to finish commits.
- Qgroup reserve fields mirror but do not exactly match normal metadata reserve semantics; callers must release qgroup excess through the provided output when needed.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/block-rsv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/block-rsv.h -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/block-rsv.h

## Purpose

`block-rsv.h` declares Btrfs metadata block reserve types, the `struct btrfs_block_rsv` layout, and APIs for initializing, adding, refilling, migrating, consuming, releasing, and querying metadata reservations.

## Main Types

- `enum btrfs_rsv_type` defines reserve classes:
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
- `struct btrfs_block_rsv` contains:
  - `size`: desired reserve size.
  - `reserved`: currently reserved bytes.
  - `space_info`: backing metadata/system/remap/treelog space pool.
  - `lock`: protects reserve counters and flags.
  - `full`: fast fullness marker.
  - `failfast`: used by truncate/temp-style operations.
  - `type`: reserve type.
  - `qgroup_rsv_size` and `qgroup_rsv_reserved`: qgroup metadata reservation mirrors.

## Public API Surface

- Initialization/allocation:
  - `btrfs_init_block_rsv()`
  - `btrfs_init_root_block_rsv()`
  - `btrfs_alloc_block_rsv()`
  - `btrfs_init_metadata_block_rsv()`
  - `btrfs_free_block_rsv()`
- Reserving/checking/refilling:
  - `btrfs_block_rsv_add()`
  - `btrfs_block_rsv_check()`
  - `btrfs_block_rsv_refill()`
- Movement and consumption:
  - `btrfs_block_rsv_migrate()`
  - `btrfs_block_rsv_use_bytes()`
  - `btrfs_block_rsv_add_bytes()`
  - `btrfs_block_rsv_release()`
- Global/root integration:
  - `btrfs_update_global_block_rsv()`
  - `btrfs_init_global_block_rsv()`
  - `btrfs_release_global_block_rsv()`
  - `btrfs_use_block_rsv()`
  - `btrfs_unuse_block_rsv()`
- Truncate/free-space-cache guard:
  - `btrfs_check_trunc_cache_free_space()`

## Inline Helpers

- `btrfs_unuse_block_rsv()` adds one block back to a reserve without growing its target, then releases excess.
- `btrfs_block_rsv_full()` is a lockless/data-race-annotated fast path for fullness.
- `btrfs_block_rsv_reserved()` returns `reserved` under the spinlock to avoid KCSAN warnings.
- `btrfs_block_rsv_size()` returns `size` under the spinlock to avoid KCSAN warnings.

## Dependencies

The header forward-declares transaction, root, space-info, fs-info, and flush enum types. It depends on Linux integer, compiler, and spinlock definitions.

## Risks And Invariants

- Direct reads of `size`, `reserved`, and `full` can trigger data races unless using the provided helpers or holding `lock`.
- `qgroup_rsv_size/reserved` have different semantics from normal metadata reserve bytes and represent an upper bound for qgroup metadata demand.
- Callers must bind reserves to the correct `space_info`; migration/release logic assumes reserve space types are meaningful.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/block-rsv.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/btrfs_inode.h -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/btrfs_inode.h

## Purpose

`btrfs_inode.h` defines the in-memory Btrfs inode structure, inode runtime flags, inode helper functions, inode creation argument structure, and the public inode-layer API used by Btrfs writeback, delalloc, checksums, VFS operations, fsync/logging, orphan handling, preallocation, encoded I/O, and inode lifecycle code.

## Runtime Flags

The anonymous enum defines `runtime_flags` bits for:

- `BTRFS_INODE_FLUSH_ON_CLOSE`: force ordered operation flushing on close after truncate-to-zero patterns.
- `BTRFS_INODE_DUMMY`: dummy inode state.
- `BTRFS_INODE_IN_DEFRAG`: inode is under defrag.
- `BTRFS_INODE_HAS_ASYNC_EXTENT`: async extent state exists.
- `BTRFS_INODE_NEEDS_FULL_SYNC`: inode must use full fsync; must be set under VFS inode lock except creation/loading contexts.
- `BTRFS_INODE_COPY_EVERYTHING`: fsync/logging copy-all state.
- `BTRFS_INODE_HAS_PROPS`: inode property cache exists.
- `BTRFS_INODE_SNAPSHOT_FLUSH`: snapshot-related flush state.
- `BTRFS_INODE_NO_XATTRS`: logged inode is known to have no xattrs until a new xattr is added.
- `BTRFS_INODE_NO_DELALLOC_FLUSH`: prevents flushing this inode's delalloc while holding dirty range locks and starting a transaction.
- `BTRFS_INODE_VERITY_IN_PROGRESS`: serializes verity enablement.
- `BTRFS_INODE_FREE_SPACE_INODE`: marks free-space cache inodes.
- `BTRFS_INODE_NO_CAP_XATTR`: marks absence of capability xattrs.
- `BTRFS_INODE_COW_WRITE_ERROR`: records COW/writeback error so fast fsync waits for ordered extents and avoids logging unwritten extent maps.
- `BTRFS_INODE_ROOT_STUB`: marks a synthetic directory inode for a subvolume entry without a root reference from the current snapshot.

## `struct btrfs_inode`

Major fields include:

- Identity:
  - `root`
  - `objectid` on 32-bit systems
  - embedded `vfs_inode`
- Compression and defrag:
  - `prop_compress`
  - `defrag_compress`
  - `defrag_compress_level`
- Core lock:
  - `lock` protects transaction/log counters, delalloc counters, disk size, outstanding extents, csum bytes, VFS byte updates, and file private data setup.
- Extent state:
  - `extent_tree`: cached extent maps.
  - `io_tree`: range state such as dirty, locked, delalloc.
  - `file_extent_tree`: tracks file extent item coverage when `NO_HOLES` is not enabled.
- Logging:
  - `log_mutex`
  - `last_trans`
  - `logged_trans`
  - `last_sub_trans`
  - `last_log_commit`
  - `last_unlink_trans`
  - `last_reflink_trans`
  - directory log index fields.
- Delalloc and ordered extents:
  - `outstanding_extents`
  - `ordered_tree_lock`
  - `ordered_tree`
  - `ordered_tree_last`
  - `delalloc_inodes`
  - `delalloc_bytes`
  - `new_delalloc_bytes`
  - `defrag_bytes`
  - `csum_bytes`
- File/directory size and indexing:
  - `disk_i_size`
  - `index_cnt`
  - `dir_index`
  - `first_dir_index_to_log`
  - `last_dir_index_offset`
- Relocation/root-stub unions:
  - `reloc_block_group_start`
  - `ref_root_id`
- Flags:
  - `runtime_flags`
  - persistent inode `flags`
  - `ro_flags`
- Reservation and delayed work:
  - embedded `block_rsv`
  - `delayed_node`
  - `delayed_iput`
- Metadata:
  - `generation`
  - creation time fields `i_otime_sec` and `i_otime_nsec`
  - `i_mmap_lock`

## Inline Helpers And Macros

- `BTRFS_DIR_START_INDEX` sets real directory entries to start at position 2 after `.` and `..`.
- `btrfs_get_first_dir_index_to_log()` and `btrfs_set_first_dir_index_to_log()` wrap `READ_ONCE`/`WRITE_ONCE`.
- `BTRFS_I()` is a type-checked, const-preserving conversion from VFS inode to Btrfs inode.
- `btrfs_inode_hash()` hashes an objectid/root pair.
- `btrfs_ino()` returns the 64-bit inode number, using `objectid` on 32-bit platforms except root stubs.
- `btrfs_get_inode_key()` fills a `BTRFS_INODE_ITEM_KEY`.
- `btrfs_set_inode_number()` updates both Btrfs and VFS inode numbers where needed.
- `btrfs_i_size_write()` updates VFS `i_size` and `disk_i_size`.
- `btrfs_is_free_space_inode()` and `is_data_inode()` classify special inodes.
- `btrfs_mod_outstanding_extents()` adjusts outstanding extent count and traces non-free-space inodes.
- `btrfs_set_inode_last_sub_trans()` records that writes happened in the current log transaction.
- `btrfs_set_inode_full_sync()` sets full-sync state and pessimistically updates `last_reflink_trans`.
- `btrfs_inode_in_log()` checks whether an inode is already logged for a generation and no newer subtransaction needs logging.
- `btrfs_inode_can_compress()` rejects compression for NODATACOW/NODATASUM inodes.
- `btrfs_assert_inode_locked()` asserts the VFS inode rwsem is held.
- `btrfs_update_inode_mapping_flags()` sets/clears stable writes based on NODATASUM.
- `btrfs_set_inode_mapping_order()` configures folio order range for data inodes when experimental support is enabled.

## Public Inode API Surface

The header declares APIs for:

- Checksums and read validation:
  - `btrfs_calculate_block_csum_folio()`
  - `btrfs_calculate_block_csum_pages()`
  - `btrfs_check_block_csum()`
  - `btrfs_data_csum_ok()`
- NOCOW and extents:
  - `can_nocow_extent()`
  - `btrfs_get_extent()`
  - `btrfs_create_io_em()`
  - `btrfs_get_extent_allocation_hint()`
- Delalloc/writeback:
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
- Directory and namespace operations:
  - `btrfs_lookup_dentry()`
  - `btrfs_set_inode_index()`
  - `btrfs_unlink_inode()`
  - `btrfs_add_link()`
  - `btrfs_delete_subvolume()`
- Inode creation:
  - `struct btrfs_new_inode_args`
  - `btrfs_new_inode_prepare()`
  - `btrfs_create_new_inode()`
  - `btrfs_new_inode_args_destroy()`
  - `btrfs_new_subvol_inode()`
- Truncate, expansion, and preallocation:
  - `btrfs_truncate_block()`
  - `btrfs_cont_expand()`
  - `btrfs_prealloc_file_range()`
  - `btrfs_prealloc_file_range_trans()`
- Lifecycle/cache:
  - `btrfs_evict_inode()`
  - `btrfs_alloc_inode()`
  - `btrfs_destroy_inode()`
  - `btrfs_free_inode()`
  - `btrfs_drop_inode()`
  - `btrfs_init_cachep()`
  - `btrfs_destroy_cachep()`
  - `btrfs_iget_path()`
  - `btrfs_iget()`
  - `btrfs_find_first_inode()`
- Inode item/orphan/delayed iput:
  - `btrfs_update_inode()`
  - `btrfs_update_inode_fallback()`
  - `btrfs_orphan_add()`
  - `btrfs_orphan_cleanup()`
  - `btrfs_add_delayed_iput()`
  - `btrfs_run_delayed_iputs()`
  - `btrfs_wait_on_delayed_iputs()`
- Encoded I/O:
  - `btrfs_encoded_io_compression_from_extent()`
  - `btrfs_encoded_read_regular_fill_pages()`
  - `btrfs_encoded_read()`
  - `btrfs_encoded_read_regular()`
  - `btrfs_do_encoded_write()`
- Locking and accounting:
  - `btrfs_inode_lock()`
  - `btrfs_inode_unlock()`
  - `btrfs_update_inode_bytes()`
  - `btrfs_assert_inode_range_clean()`
- Dentry integration:
  - `btrfs_dentry_operations`

## `struct btrfs_new_inode_args`

This structure groups inode creation inputs and prepared outputs:

- Inputs:
  - parent directory inode
  - dentry
  - new inode
  - orphan flag
  - subvolume flag
- Prepared outputs:
  - default ACL
  - ACL
  - fscrypt name

It separates pre-transaction preparation from transaction-time inode creation.

## Dependencies

This header sits at the boundary between Btrfs and VFS/MM infrastructure. It depends on Linux inode, mapping, mm, fscrypt, locking, trace, and ACL types, plus Btrfs ctree, block reserve, extent map, and extent I/O tree definitions.

It connects to Btrfs subsystems including transactions, ordered extents, checksums, extent maps, delalloc, tree log, orphan items, delayed inode/items, free-space cache inodes, encoded I/O, fscrypt, verity, and subvolume roots.

## Risks And Invariants

- Many fields in `struct btrfs_inode` are protected by `inode->lock`; direct unsynchronized access risks stale values and KCSAN reports.
- `BTRFS_INODE_NEEDS_FULL_SYNC` must be set under the correct locks to avoid races where fsync starts fast and later needs full sync.
- `BTRFS_INODE_NO_DELALLOC_FLUSH` prevents deadlocks when transaction reservation could otherwise flush the same inode/range whose locks are already held.
- `disk_i_size` and VFS `i_size` intentionally differ during ordered writeback; helpers must preserve ordered-data semantics.
- 32-bit inode numbers require special handling through `objectid` to avoid truncation.
- Root stub inodes represent missing root references from snapshot contexts and must not be treated like normal subvolume root references.
- Compression eligibility must respect NODATACOW/NODATASUM flags to avoid checksum and COW semantic violations.
- Outstanding extent, delalloc, csum, and qgroup accounting is distributed across inode writeback and transaction code, so helper usage matters for ENOSPC correctness.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/btrfs_inode.h -->