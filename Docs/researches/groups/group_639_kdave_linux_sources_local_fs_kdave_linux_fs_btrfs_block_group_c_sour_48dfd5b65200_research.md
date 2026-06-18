# Group Research: group_639_kdave_linux_sources_local_fs_kdave_linux_fs_btrfs_block_group_c_sour_48dfd5b65200

Scope confirmed: `Docs/research_subset_a.md` includes `sources/local-fs/kdave-linux`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/block-group.c -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/block-group.c

This file is the main Btrfs block group implementation. It manages block group creation, lookup, reference lifetime, free-space discovery, read-only transitions, removal, reclaim, chunk allocation, dirty block group persistence, and teardown.

Major responsibilities:
- Maintains the filesystem-wide block group cache as an rb-tree keyed by logical start.
- Selects allocation profiles with balance/restripe awareness via `btrfs_get_alloc_profile()`.
- Implements refcounted block group lifetime with `btrfs_get_block_group()` and `btrfs_put_block_group()`.
- Coordinates NOCOW writers, pending reservations, trim/scrub freezing, swap extents, and read-only block group transitions.
- Loads and maintains free-space state from the old space cache, free-space tree, or extent tree scan.
- Creates, persists, updates, and removes block group items and related device extent records.
- Drives unused block group deletion and reclaim-by-relocation.
- Implements two-phase chunk allocation and system chunk metadata reservation.

Key data flows:
- Mount-time discovery starts in `btrfs_read_block_groups()`, finds block group items through `find_first_block_group()`, validates them against chunk maps with `read_bg_from_eb()`, builds in-memory `struct btrfs_block_group` objects in `read_one_block_group()`, excludes superblock stripes, loads zoned info, adds the group to the rb-tree and `space_info`, and initializes global block reserves.
- New chunk creation starts with `btrfs_chunk_alloc()`, which serializes allocation through `space_info->chunk_alloc` and `fs_info->chunk_mutex`, calls `do_chunk_alloc()`, creates a block group through lower volume code, inserts chunk metadata, and leaves extent-tree/device-tree insertion for phase 2.
- Phase 2 runs in `btrfs_create_pending_block_groups()`, inserting the block group item, chunk item if still needed, device extents, and free-space tree records before clearing the `BLOCK_GROUP_FLAG_NEW` runtime flag.
- Allocation accounting uses `btrfs_add_reserved_bytes()` to move bytes from may-use to block group reserved state, `btrfs_update_block_group()` to convert reserved bytes to used bytes or used bytes to pinned bytes, and `btrfs_free_reserved_bytes()` to release unused reservations.

Free-space cache behavior:
- `btrfs_cache_block_group()` starts asynchronous caching unless the filesystem is zoned or the block group is remapped.
- `caching_thread()` samples size class, tries the old space cache when enabled, then uses the free-space tree or falls back to scanning extent items with `load_extent_tree_free()`.
- `btrfs_add_new_free_space()` adds ranges while skipping `fs_info->excluded_extents`, which are populated by `exclude_super_stripes()`.
- Caching has progress wakeups through `struct btrfs_caching_control`, `CACHING_CTL_WAKE_UP`, and `btrfs_wait_block_group_cache_progress()`.

Removal and reclaim:
- `btrfs_remove_block_group()` requires the group to be read-only unless remapped, detaches it from allocation clusters, dirty/cache IO lists, rb-tree, `space_info`, sysfs, free-space cache/tree, and block group item storage.
- Removed groups can keep their chunk map until `frozen` users finish, protecting scrub/trim users from address reuse.
- `btrfs_delete_unused_bgs()` processes `fs_info->unused_bgs`, handles async discard, zoned reclaim heuristics, pinned extent cleanup, read-only marking, transaction removal, and deleted block group tracking.
- `btrfs_reclaim_block_groups()` sorts reclaim candidates by used bytes and relocates sparse groups through `btrfs_reclaim_block_group()`.

Concurrency and locking:
- `fs_info->block_group_cache_lock` protects the rb-tree and caching block group list.
- `space_info->groups_sem` serializes allocator-facing list changes and read-only decisions.
- `space_info->lock` plus `block_group->lock` protect byte counters and state.
- `fs_info->unused_bgs_lock` protects `bg_list` membership across unused, reclaim, fully remapped, deleted, and new block group lists.
- `fs_info->chunk_mutex` serializes system chunk reservation and chunk tree modifications.
- `ro_block_group_mutex` prevents races with dirty block group cache writeback when toggling read-only state.
- Dirty block group lists are protected by `transaction->dirty_bgs_lock`; cache writeback is additionally coordinated by `cache_write_mutex`.

Important invariants:
- Block group items must match chunk maps by start, length, and type flags.
- Extents must not span block group boundaries in `btrfs_update_block_group()`.
- System chunk allocation must not recursively occur through `btrfs_chunk_alloc()`.
- A removed block group’s logical/physical range must not be reused while frozen trim/scrub users remain.
- Zoned filesystems bypass normal cache loading and depend on allocation offsets, zone capacity, active zones, and zone unusable accounting.
- Data-only non-zoned block groups may use size classes to reduce fragmentation.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/block-group.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/block-group.h -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/block-group.h

This header defines the public block group model and API used by Btrfs allocation, free-space, discard, zoned, transaction, relocation, and cleanup code.

Primary declarations:
- `enum btrfs_disk_cache_state` tracks old free-space cache persistence: written, error, clear, setup.
- `enum btrfs_block_group_size_class` classifies data-only block groups into small, medium, large, or unset allocation classes.
- `enum btrfs_discard_state` tracks async discard phases, including fully remapped discard.
- `enum btrfs_chunk_alloc_enum` defines chunk allocation pressure modes from no-force to force-for-extent.
- `enum btrfs_block_group_flags` defines runtime-only flags such as removed, new, zone active, needs free-space tree insertion, fully remapped, and stripe removal pending.
- `enum btrfs_caching_type` tracks free-space cache state: no cache, started, finished, error.
- `struct btrfs_caching_control` is the refcounted async cache worker state.
- `struct btrfs_block_group` is the central in-memory representation of a logical block group.

Important `struct btrfs_block_group` fields:
- Addressing and ownership: `fs_info`, `start`, `length`, `flags`, `global_root_id`.
- Space counters: `pinned`, `reserved`, `used`, `delalloc_bytes`, `bytes_super`, `remap_bytes`, `zone_unusable`.
- Persistence mirrors: `last_used`, `last_remap_bytes`, `last_identity_remap_count`, `last_flags`.
- Free-space and cache state: `free_space_ctl`, `disk_cache_state`, `cached`, `caching_ctl`, bitmap thresholds.
- Placement in global structures: rb-tree node, raid-type list, cluster list, multipurpose `bg_list`, read-only list, discard list, dirty list, IO list, active zone list.
- Synchronization and lifetime: `lock`, `data_rwsem`, `free_space_lock`, `refs`, `frozen`, `reservations`, `nocow_writers`.
- Zoned state: `alloc_offset`, `zone_capacity`, `meta_write_pointer`, `physical_map`, `last_eb`.
- Allocation policy: `full_stripe_len`, `size_class`, `reclaim_mark`.

Inline helpers:
- `btrfs_block_group_end()` returns exclusive logical end.
- `btrfs_is_block_group_used()` checks used, reserved, pinned, or remap bytes under the block group lock.
- `btrfs_is_block_group_data_only()` excludes mixed data/metadata groups from data-only optimizations.
- `btrfs_block_group_available_space()` subtracts used, pinned, reserved, super, and zoned-unusable bytes.
- `btrfs_block_group_done()` uses a memory barrier before checking finished/error cache states.
- Allocation profile helpers wrap `btrfs_get_alloc_profile()` for data, metadata, and system groups.

API surface:
- Lookup and iteration: `btrfs_lookup_first_block_group()`, `btrfs_lookup_block_group()`, `btrfs_next_block_group()`.
- Lifetime: `btrfs_get_block_group()`, `btrfs_put_block_group()`.
- Cache and free-space loading: `btrfs_cache_block_group()`, `btrfs_add_new_free_space()`.
- Read-only, NOCOW, reservation, swap, freeze, and size-class controls.
- Mount/read, create, remove, dirty-writeback, chunk allocation, reclaim, and teardown entry points.

The header is the contract that lets allocator, transaction, discard, zoned, inode/free-space-cache, relocation, and volume/chunk code coordinate around the same block group object.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/block-group.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/block-rsv.c -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/block-rsv.c

This file implements Btrfs metadata block reserves. A block reserve is a logical bucket of metadata reservation with `size`, `reserved`, `full`, type, target `space_info`, and optional qgroup reservation counters.

The opening comment is the design guide:
- Normal reserve path calls `btrfs_reserve_metadata_bytes()`, charges `space_info->bytes_may_use`, and adds bytes to a reserve.
- Use path calls `btrfs_use_block_rsv()` during tree block allocation and subtracts `nodesize` from `reserved`.
- Finish path calls `btrfs_block_rsv_release()` to shrink reserve size and free or redirect excess.
- Reserve types distinguish transaction, delayed operations, chunk, global, delalloc, delayed refs, empty fallback, tree-log, remap, and temporary unbounded operations.

Core operations:
- `block_rsv_release_bytes()` shrinks reserve size, trims excess `reserved`, optionally moves excess into a destination reserve, frees remaining may-use bytes, and reports qgroup release.
- `btrfs_block_rsv_migrate()` consumes bytes from one reserve and adds them to another.
- `btrfs_init_block_rsv()` and `btrfs_init_metadata_block_rsv()` initialize reserve objects and attach metadata `space_info`.
- `btrfs_alloc_block_rsv()` and `btrfs_free_block_rsv()` allocate/free dynamic reserve objects.
- `btrfs_block_rsv_add()` reserves metadata bytes and grows both `size` and `reserved`.
- `btrfs_block_rsv_refill()` tops up `reserved` to a requested amount without growing `size`.
- `btrfs_block_rsv_release()` redirects excess preferentially to the global reserve for delayed refs, or to delayed refs for other compatible reserves.
- `btrfs_block_rsv_use_bytes()` consumes reserved bytes and clears `full` if needed.
- `btrfs_block_rsv_add_bytes()` adds bytes directly, optionally growing `size`.

Global reserve management:
- `btrfs_update_global_block_rsv()` sizes the global reserve from root, extent, checksum, free-space, block-group, and raid-stripe tree usage, plus unlink/delayed-ref minimums, capped at 512 MiB.
- It updates `space_info->bytes_may_use` directly under `space_info->lock` and reserve lock.
- It can force chunk allocation if the global reserve size reaches the total metadata space.
- `btrfs_init_global_block_rsv()` wires filesystem reserves to system, metadata, metadata-remap, and zoned treelog sub-group space infos, then updates the global reserve.
- `btrfs_release_global_block_rsv()` drains the global reserve and warns if other global reserves still carry size or reserved bytes.

Root-to-reserve routing:
- `btrfs_init_root_block_rsv()` assigns extent/csum/free-space/block-group/raid-stripe roots to delayed refs, root/dev/quota roots to global, chunk root to chunk reserve, tree-log root to treelog reserve, remap root to remap reserve, and leaves other roots without a specific reserve.
- `get_block_rsv()` prefers the transaction reserve for shareable roots, uuid root, and csum additions, then the root reserve, then the empty reserve.

Allocation fallback behavior:
- `btrfs_use_block_rsv()` first tries the selected reserve.
- For global reserves, it may refresh sizing once.
- Tree-log allocations fail immediately on reserve failure to force fsync fallback to transaction commit.
- Non-global metadata allocations may fall back to the global reserve if compatible.
- Final fallback uses `BTRFS_RESERVE_FLUSH_EMERGENCY`.
- `failfast` reserves return immediately on shortage, supporting unbounded truncate/iput style work.

Concurrency:
- Reserve state is protected by each `block_rsv->lock`.
- Global reserve updates take `space_info->lock` and reserve lock together.
- Some fast/stale checks are allowed through helpers in the header, but mutation is locked.

This file is tightly coupled to `space-info`, transaction accounting, delayed refs, chunk metadata reservation, root initialization, and ENOSPC behavior.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/block-rsv.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/block-rsv.h -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/block-rsv.h

This header defines the metadata block reserve interface.

Main type:
- `enum btrfs_rsv_type` names reserve categories: global, delalloc, transaction, chunk, remap, delayed operations, delayed refs, tree-log, empty fallback, and temporary.
- `struct btrfs_block_rsv` stores `size`, `reserved`, target `space_info`, spinlock, `full`, `failfast`, compact reserve type, and qgroup reservation counters.

Important fields:
- `size` is the desired reservation size for the logical operation.
- `reserved` is the amount currently charged and available.
- `space_info` chooses which Btrfs space pool owns the reservation.
- `full` is a cached fullness indicator, intentionally exposed through a data-race-tolerant fast helper.
- `failfast` changes shortage behavior for unbounded temporary operations.
- `qgroup_rsv_size` and `qgroup_rsv_reserved` track quota-group metadata reservation separately from normal metadata reservation because qgroups account net extent usage rather than full B-tree update pessimism.

Public API:
- Initialization and allocation: `btrfs_init_block_rsv()`, `btrfs_init_metadata_block_rsv()`, `btrfs_alloc_block_rsv()`, `btrfs_free_block_rsv()`.
- Root/global setup: `btrfs_init_root_block_rsv()`, `btrfs_init_global_block_rsv()`, `btrfs_update_global_block_rsv()`, `btrfs_release_global_block_rsv()`.
- Reserve mutation: `btrfs_block_rsv_add()`, `btrfs_block_rsv_refill()`, `btrfs_block_rsv_migrate()`, `btrfs_block_rsv_use_bytes()`, `btrfs_block_rsv_add_bytes()`, `btrfs_block_rsv_release()`.
- Allocation selection: `btrfs_use_block_rsv()`.
- Space-cache support: `btrfs_check_trunc_cache_free_space()`.

Inline helpers:
- `btrfs_unuse_block_rsv()` returns a consumed block back to a reserve, then releases excess.
- `btrfs_block_rsv_full()` deliberately uses `data_race()` for a fast approximate fullness check.
- `btrfs_block_rsv_reserved()` and `btrfs_block_rsv_size()` return locked snapshots for contexts that tolerate stale values but should avoid KCSAN warnings.

The header is the shared reservation contract used by transaction, tree block allocation, inode/delalloc accounting, chunk metadata, delayed refs, and free-space-cache code.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/block-rsv.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/btrfs_inode.h -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/btrfs_inode.h

This header defines the in-memory Btrfs inode structure, inode runtime flags, key inline helpers, and function prototypes for inode, delalloc, csum, encoded IO, directory, orphan, and locking operations.

Runtime flags:
- Cover close/writeback behavior, dummy/defrag state, async extents, full fsync requirements, property/xattr cache bits, no-delalloc-flush deadlock avoidance, verity-in-progress, free-space inode tagging, COW write error handling, and root-stub directory inodes.
- Several comments document required locking, especially `BTRFS_INODE_NEEDS_FULL_SYNC`, which must be set under VFS inode locking or equivalent exclusion.

`struct btrfs_inode` contents:
- Embeds ownership through `root` and, on 32-bit systems, an explicit 64-bit `objectid`.
- Stores compression properties, defrag compression controls, and inode flags.
- Uses `lock` for transaction/log counters, delalloc counters, outstanding extents, csum bytes, disk size, and private file data.
- Contains `extent_tree` for extent maps and `io_tree` for range state.
- Optionally tracks file extent item coverage through `file_extent_tree` when holes must be represented.
- Has `log_mutex` for tree-log operations.
- Tracks ordered extents with `ordered_tree_lock`, rb-tree root, and last node.
- Maintains delalloc inode list membership, runtime flags, full generation, transaction/log generation fields, delayed inode node, block reserve, delayed iput list, mmap lock, and embedded VFS inode.
- Uses unions to reuse fields by inode type: file delalloc counters vs directory log indexes, defrag bytes vs relocation block group start, index counter vs csum bytes, reflink transaction vs root-stub ref root id.

Key inline helpers:
- `BTRFS_I()` is a type-checked const-preserving container conversion from VFS inode to Btrfs inode.
- `btrfs_inode_hash()` hashes inode objectid with root objectid.
- `btrfs_ino()` preserves full inode numbers on 32-bit systems and handles root stubs specially.
- `btrfs_get_inode_key()` and `btrfs_set_inode_number()` bridge in-memory inode identity to B-tree keys.
- `btrfs_i_size_write()` updates both VFS i_size and Btrfs `disk_i_size`.
- `btrfs_is_free_space_inode()` tags special free-space-cache inodes, which are relevant to block group cache writeback.
- `btrfs_mod_outstanding_extents()` updates outstanding extent accounting and traces normal inodes.
- `btrfs_set_inode_last_sub_trans()`, `btrfs_set_inode_full_sync()`, and `btrfs_inode_in_log()` maintain fsync/logging state.
- `btrfs_inode_can_compress()` rejects compression for NODATACOW/NODATASUM.
- `btrfs_update_inode_mapping_flags()` controls stable write requirements based on checksumming.
- `btrfs_set_inode_mapping_order()` configures folio order for data inodes under experimental support.

Declared operation groups:
- Checksumming: metadata block checksums and data checksum verification.
- NOCOW: `can_nocow_extent()`, which interacts with block group NOCOW writer tracking.
- Directory/subvolume mutation: lookup, unlink, add link, delete subvolume, inode index allocation.
- Delalloc: start delalloc for roots/snapshots, set/clear/merge/split delalloc extent state.
- Inode lifecycle: allocate, destroy, free, drop, evict, iget, cache init/destroy.
- Extent and IO: get extent, preallocation, delalloc writeback, writepage COW fixup, encoded read/write.
- Transaction updates and cleanup: update inode, orphan add/cleanup, delayed iputs, inode byte accounting.
- Locking: `btrfs_inode_lock()` and `btrfs_inode_unlock()` with shared, try, and mmap lock modes.

Relationship to the other files in this group:
- Includes `block-rsv.h` because each inode embeds a `struct btrfs_block_rsv`.
- Free-space inodes are used by block group old space-cache persistence in `block-group.c`.
- NOCOW declarations depend on block group read-only and NOCOW writer coordination.
- Delalloc and inode block reserves feed the metadata reservation machinery implemented in `block-rsv.c`.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/btrfs_inode.h -->