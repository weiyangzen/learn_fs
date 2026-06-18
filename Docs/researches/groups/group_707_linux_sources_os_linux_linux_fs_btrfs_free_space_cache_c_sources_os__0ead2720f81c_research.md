# Group Research: group_707_linux_sources_os_linux_linux_fs_btrfs_free_space_cache_c_sources_os__0ead2720f81c

Scope checked against `Docs/research_subset_a.md`: all files are under included source tree `sources/os/linux/linux`.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/free-space-cache.c -->
# File Research: sources/os/linux/linux/fs/btrfs/free-space-cache.c

## Purpose
Implements Btrfs free-space cache v1 and the in-memory free-space allocator state for block groups. It manages free ranges as a mix of extent entries and bitmap entries, supports cluster-based allocation, serializes/validates the v1 cache inode format, and drives sync/async discard trimming.

## Main Responsibilities
- Creates, looks up, truncates, writes, loads, and removes per-block-group free-space cache inodes.
- Maintains `struct btrfs_free_space_ctl` indexes:
  - `free_space_offset`: offset-ordered rb-tree.
  - `free_space_bytes`: size-ordered cached rb-tree.
- Stores free space as either `struct btrfs_free_space` extent entries or page-sized bitmaps.
- Converts small fragmented free ranges into bitmap entries when extent count pressure is high.
- Merges adjacent extent entries and can steal contiguous free ranges from neighboring bitmaps to improve allocator hit rate.
- Supports allocation from block-group free-space clusters for metadata and `ssd_spread` data allocation.
- Handles zoned Btrfs separately by updating allocation/unusable accounting rather than rb-tree entries.
- Handles discard trimming state, including async trim filters and in-progress trimming ranges.
- Initializes/destroys slab caches for free-space entries and bitmap pages.

## Key Data and Constants
- `BITS_PER_BITMAP = PAGE_SIZE * 8`: bits covered by each in-memory bitmap.
- `MAX_CACHE_BYTES_PER_GIG = 64K`: target memory budget per GiB of block-group free-space metadata.
- `FORCE_EXTENT_THRESHOLD = 1M`: large free ranges are kept as extents rather than bitmaps.
- `btrfs_free_space_cachep`: slab cache for `struct btrfs_free_space`.
- `btrfs_free_space_bitmap_cachep`: page-sized slab cache for bitmap data.
- `struct btrfs_trim_range`: temporary range tracked while discard is running so cache writeout does not lose removed ranges.

## Cache Inode Path
- `lookup_free_space_inode()` reuses a cached `block_group->inode` if present, otherwise finds the free-space inode through a `BTRFS_FREE_SPACE_OBJECTID` header item.
- `__create_free_space_inode()` creates a regular internal inode with `NOCOMPRESS`, `PREALLOC`, `NODATASUM`, and `NODATACOW`, then inserts the free-space header item pointing to that inode.
- `btrfs_remove_free_space_inode()` orphans and unlinks the cache inode, clears the block-group inode reference, and deletes the header item.
- `btrfs_truncate_free_space_cache()` truncates the cache inode to zero using `btrfs_truncate_inode_items()`, clears pagecache and extent maps, resets `disk_cache_state`, and aborts the transaction on failure.

## On-Disk V1 Cache I/O
`struct btrfs_io_ctl` abstracts cache inode page access.

Important helpers:
- `io_ctl_init()`, `io_ctl_free()`: allocate/free page vector.
- `io_ctl_prepare_pages()`: locks/creates pages and optionally reads them uptodate.
- `io_ctl_set_generation()` / `io_ctl_check_generation()`: store/check cache generation in the first page.
- `io_ctl_set_crc()` / `io_ctl_check_crc()`: per-page CRC32C validation; CRC slots are stored at the front of page 0.
- `io_ctl_add_entry()` / `io_ctl_read_entry()`: serialize free-space extent/bitmap descriptors.
- `io_ctl_add_bitmap()` / `io_ctl_read_bitmap()`: serialize bitmap payload pages.

Load/write flow:
- `__load_free_space_cache()` validates inode generation, header generation, CRCs, entry counts, bitmap count, then loads into a temporary free-space control.
- `load_free_space_cache()` only trusts caches with `BTRFS_DC_WRITTEN`, loads into a temporary control, checks free-space total against block-group accounting, then copies into the real control.
- `__btrfs_write_out_cache()` writes extent entries, in-progress trim ranges, pinned extents, then bitmap pages; dirty pages are flushed later.
- `btrfs_wait_cache_io()` waits for ordered writeback, updates the free-space header item, sets `BTRFS_DC_WRITTEN` or `BTRFS_DC_ERROR`, and drops the inode reference.

## In-Memory Free-Space Operations
Core rb-tree helpers:
- `tree_insert_offset()` inserts entries by logical offset. Extent and bitmap entries may share an offset, with extent entries ordered before bitmaps.
- `entry_less()` orders the size index with largest usable extent first.
- `tree_search_offset()` supports exact/fuzzy and bitmap-only lookup.
- `link_free_space()` and `unlink_free_space()` maintain both rb-trees plus free-space and discardable counters.

Bitmap operations:
- `offset_to_bit()`, `bytes_to_bits()`, `offset_to_bitmap()` translate logical offsets into bitmap location.
- `bitmap_clear_bits()` and `btrfs_bitmap_set_bits()` update bitmap bits, entry byte counts, cached max extent size, bitmap extent count, and discard stats.
- `search_bitmap()` finds a contiguous set-bit run; for allocation it uses cached `max_extent_size` to skip fragmented bitmaps.
- `insert_into_bitmap()` adds an incoming range into an existing or newly allocated bitmap when `use_bitmap()` says bitmap representation is preferable.
- `free_bitmap()` removes bitmap entries and adjusts thresholds/statistics.

Extent operations:
- `try_merge_free_space()` merges neighboring extent entries using trim-state-aware rules.
- `steal_from_bitmap_to_end()` and `steal_from_bitmap_to_front()` pull adjacent set bits out of bitmaps to grow extent entries.
- `steal_from_bitmap()` improves allocation quality by preferring large extent entries over split extent+bitmap representations.

Public mutation API:
- `btrfs_add_free_space()`: adds untrimmed free space, or zoned accounting if zoned.
- `btrfs_add_free_space_unused()`: adds space from unused regions; zoned mode may rewind `alloc_offset`.
- `btrfs_add_free_space_async_trimmed()`: used when loading/caching, marks free space trimmed if sync or async discard is enabled.
- `btrfs_remove_free_space()`: consumes a range from extents/bitmaps; zoned mode only advances `alloc_offset` for log replay safety.
- `btrfs_find_space_for_alloc()`: finds and removes an allocation candidate, handling alignment gaps by returning the gap to free space.

## Cluster Allocation
- `btrfs_init_free_cluster()` initializes a reusable allocation cluster.
- `btrfs_find_space_cluster()` builds a cluster from block-group free space, preferring extent entries and falling back to bitmap scanning.
- `setup_cluster_no_bitmap()` pulls qualifying extent entries into the cluster rb-tree.
- `setup_cluster_bitmap()` and `btrfs_bitmap_cluster()` locate sufficient free ranges inside bitmap entries.
- `btrfs_alloc_from_cluster()` allocates from a cluster and updates free-space/discard accounting.
- `btrfs_return_cluster_to_free_space()` moves cluster entries back to the owning block group and queues discard work.

## Discard and Trim
- `btrfs_is_free_space_trimmed()` checks whether all free-space entries in a block group are trimmed.
- `trim_no_bitmap()` trims extent entries.
- `trim_bitmaps()` trims bitmap-backed ranges, with lossy bitmap-level trim-state tracking to avoid repeatedly discarding small skipped ranges.
- `do_trimming()` temporarily reserves the range, calls `btrfs_discard_extent()`, re-adds the space with trimmed/untrimmed state, and removes the range from `trimming_ranges`.
- `btrfs_trim_block_group()`, `btrfs_trim_block_group_extents()`, and `btrfs_trim_block_group_bitmaps()` expose sync and async trim entry points.
- `btrfs_trim_fully_remapped_block_group()` handles remapped block groups during stripe removal/remap completion.

## Concurrency and Locking
- `ctl->tree_lock` protects free-space rb-trees and counters.
- `ctl->cache_writeout_mutex` serializes cache writeout with trim operations and protects bitmap payloads during writeout.
- `block_group->lock` protects block-group cache state and runtime flags.
- `cluster->lock` protects cluster rb-tree and block-group ownership.
- Cache inode lookup uses `memalloc_nofs_save()` to avoid filesystem recursion under transaction contexts.
- Cache read uses committed root search to avoid deadlock while loading cache during tree-root COW.

## Error Handling and Integrity
- Invalid cache generation, CRC mismatch, duplicate entries, or free-space total mismatch cause cache discard and rebuild.
- Transaction errors during cache truncation/removal/writeout abort transactions where required.
- `WARN_ON`, `ASSERT`, and critical logging flag internal invariant violations such as duplicate free-space entries.
- Test-only helpers under `CONFIG_BTRFS_FS_RUN_SANITY_TESTS` allow constructing unusual extent/bitmap states and querying range presence.

## Cross-File Links
- Uses `free-space-cache.h` for data structures and exported prototypes.
- Uses `inode-item.c` through `btrfs_truncate_inode_items()` for cache inode truncation.
- Interacts with block-group, transaction, discard, extent-tree, and file writeback code.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/free-space-cache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/free-space-cache.h -->
# File Research: sources/os/linux/linux/fs/btrfs/free-space-cache.h

## Purpose
Declares the in-memory free-space cache structures and public API implemented by `free-space-cache.c`.

## Main Types
- `enum btrfs_trim_state`
  - `BTRFS_TRIM_STATE_UNTRIMMED`
  - `BTRFS_TRIM_STATE_TRIMMED`
  - `BTRFS_TRIM_STATE_TRIMMING`
- `struct btrfs_free_space`
  - rb-tree nodes for offset and size indexes.
  - `offset`, `bytes`, `max_extent_size`.
  - optional `bitmap`.
  - temporary `list` linkage.
  - trim state and bitmap extent count.
- `struct btrfs_free_space_ctl`
  - spinlock-protected rb-tree indexes.
  - total free-space counters and bitmap/extent thresholds.
  - discardable extent/byte delta arrays.
  - owning block group.
  - cache writeout mutex and active trimming range list.
- `struct btrfs_free_space_op`
  - strategy callback deciding when to use bitmap representation.
- `struct btrfs_io_ctl`
  - page-array cursor and metadata for serializing/deserializing v1 cache inodes.

## Inline Helpers
- `btrfs_free_space_trimmed()` tests for fully trimmed entries.
- `btrfs_free_space_trimming_bitmap()` identifies bitmap entries currently being trimmed.
- `btrfs_trim_interrupted()` checks fatal signals or freezer state.

## Public API Groups
- Slab lifecycle: `btrfs_free_space_init()`, `btrfs_free_space_exit()`.
- Cache inode operations: lookup, create, remove, truncate, load, write, wait.
- In-memory free-space mutation/allocation: add, remove, dump, find allocation space.
- Cluster allocation: initialize, find cluster, allocate from cluster, return cluster.
- Discard trimming: trim entire block group, extents only, bitmaps only, fully remapped groups.
- Space cache v1 toggling: `btrfs_free_space_cache_v1_active()`, `btrfs_set_free_space_cache_v1_active()`.
- Sanity-test helpers when `CONFIG_BTRFS_FS_RUN_SANITY_TESTS` is enabled.

## Design Notes
This header exposes both the allocator-facing API and the cache-inode API, so it is shared by block-group/extent allocation code, discard code, transaction/cache writeout paths, and tests.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/free-space-cache.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/free-space-tree.c -->
# File Research: sources/os/linux/linux/fs/btrfs/free-space-tree.c

## Purpose
Implements Btrfs free-space tree support. Unlike free-space cache v1, the free-space tree stores free-space metadata directly in Btrfs trees using free-space info, extent, and bitmap items. It supports creation, deletion, rebuild, incremental add/remove updates, block-group add/remove, and loading tree contents into block-group in-memory free-space caches.

## Main On-Disk Model
For each block group:
- `BTRFS_FREE_SPACE_INFO_KEY`: one info item keyed by block-group start and length; stores extent count and flags.
- `BTRFS_FREE_SPACE_EXTENT_KEY`: extent-format free range; `objectid=start`, `offset=size`.
- `BTRFS_FREE_SPACE_BITMAP_KEY`: bitmap-format free range; `objectid=bitmap_start`, `offset=covered_bytes`, payload bitmap.

`btrfs_free_space_root()` selects the global free-space tree root. With `EXTENT_TREE_V2`, it uses the block group’s `global_root_id`.

## Thresholds and Format Conversion
- `btrfs_set_free_space_tree_thresholds()` calculates bitmap high/low thresholds from block-group length, sectorsize, bitmap item size, and item overhead.
- `update_free_space_extent_count()` updates extent count in the info item and converts representation when thresholds are crossed.
- `btrfs_convert_free_space_to_bitmaps()` walks existing free-space extent items, builds a little-endian bitmap, deletes extent items, sets `BTRFS_FREE_SPACE_USING_BITMAPS`, then inserts bitmap items.
- `btrfs_convert_free_space_to_extents()` reads bitmap items into memory, deletes bitmap items, clears the bitmap flag, and emits extent items for each contiguous set-bit run.

## Bitmap Helpers
- `free_space_bitmap_size()` computes bytes required to represent a byte range at filesystem sectorsize granularity.
- `alloc_bitmap()` uses `memalloc_nofs_save()` around `kvzalloc()` to avoid filesystem recursion while holding transactions.
- `le_bitmap_set()` explicitly writes little-endian bitmap bits.
- `btrfs_free_space_test_bit()` tests an on-disk bitmap item bit.
- `free_space_modify_bits()` sets or clears bits in an extent buffer and advances the caller’s range.
- `free_space_next_bitmap()` moves to the next writable bitmap item without relying on read-only tree walking.
- `modify_free_space_bitmap()` mutates bitmap-backed free space and adjusts extent count based on neighbor bits before/after the changed range.

## Extent Helpers
- `add_free_space_extent()` merges new free space with immediate left/right extent neighbors, then inserts one combined extent key and updates extent count.
- `remove_free_space_extent()` splits or deletes an existing free-space extent according to four cases:
  - full extent removal,
  - removing from the beginning,
  - removing from the end,
  - removing from the middle into two leftover extents.
- `btrfs_search_prev_slot()` wraps `btrfs_search_slot()` for “greatest key less than target” lookups and asserts expected non-exact search behavior.
- `using_bitmaps()` caches a block group’s free-space-tree representation state.

## Public Add/Remove Hooks
- `btrfs_add_to_free_space_tree()` and `btrfs_remove_from_free_space_tree()` are transaction hooks for free-space changes.
- They no-op when `FREE_SPACE_TREE` compat-ro feature is absent.
- Both allocate a path, locate the block group, take `block_group->free_space_lock`, dispatch to extent or bitmap mutation, abort the transaction on error, and drop the block-group reference.
- Test-visible internal variants `__btrfs_add_to_free_space_tree()` and `__btrfs_remove_from_free_space_tree()` accept a known block group and path.

## Tree Creation, Deletion, and Rebuild
- `populate_free_space_tree()` scans the extent tree for allocated extents/metadata items in a block group and inserts gaps into the free-space tree.
- `btrfs_create_free_space_tree()` creates the free-space tree root, populates all block groups, sets `FREE_SPACE_TREE` and `FREE_SPACE_TREE_VALID`, and clears the untrusted flag after commit.
- `clear_free_space_tree()` deletes all free-space tree items and clears per-block-group `BLOCK_GROUP_FLAG_FREE_SPACE_ADDED`.
- `btrfs_delete_free_space_tree()` clears feature flags, deletes all items, removes the root item/global root, frees the root node, and commits.
- `btrfs_rebuild_free_space_tree()` clears and repopulates the tree, possibly across multiple transactions, while marking the tree untrusted until committed.

## Block Group Integration
- `__add_block_group_free_space()` lazily initializes a new block group’s free-space info item and full-block-group free extent when `BLOCK_GROUP_FLAG_NEEDS_FREE_SPACE` is set.
- `btrfs_add_block_group_free_space()` exposes this for block group creation.
- `btrfs_remove_block_group_free_space()` deletes all free-space tree items belonging to a block group.
- Rebuild logic uses `BLOCK_GROUP_FLAG_FREE_SPACE_ADDED` to avoid double-populating block groups created during rebuild transactions.

## Loading Into In-Memory Cache
- `btrfs_load_free_space_tree()` starts from the block group’s info item in the committed free-space tree and dispatches by representation flag.
- `load_free_space_extents()` iterates extent items and calls `btrfs_add_new_free_space()`.
- `load_free_space_bitmaps()` scans bitmap bits into contiguous ranges and calls `btrfs_add_new_free_space()`.
- Both validate observed extent count against the info item and wake the caching waitqueue after sufficient progress.

## Orphan Cleanup
- `btrfs_delete_orphan_free_space_entries()` removes free-space tree items that appear before the first block group, skipping `EXTENT_TREE_V2` because that mode uses multiple global roots.

## Concurrency and Integrity
- Per-block-group free-space tree mutations are serialized by `block_group->free_space_lock`.
- Tree operations run under a transaction and abort on structural errors.
- `BTRFS_FS_CREATING_FREE_SPACE_TREE` and `BTRFS_FS_FREE_SPACE_TREE_UNTRUSTED` coordinate creation/rebuild state with cache users.
- The file uses extensive assertions to validate item key ranges, expected key types, and extent count consistency.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/free-space-tree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/free-space-tree.h -->
# File Research: sources/os/linux/linux/fs/btrfs/free-space-tree.h

## Purpose
Declares the public interface and constants for Btrfs free-space tree management.

## Constants
- `BTRFS_FREE_SPACE_BITMAP_SIZE = 256`: default bitmap item payload size in bytes.
- `BTRFS_FREE_SPACE_BITMAP_BITS`: number of sectors represented by that bitmap payload.

## Public API
- Tree lifecycle:
  - `btrfs_create_free_space_tree()`
  - `btrfs_delete_free_space_tree()`
  - `btrfs_rebuild_free_space_tree()`
- Block-group setup/removal:
  - `btrfs_add_block_group_free_space()`
  - `btrfs_remove_block_group_free_space()`
  - `btrfs_set_free_space_tree_thresholds()`
- Incremental updates:
  - `btrfs_add_to_free_space_tree()`
  - `btrfs_remove_from_free_space_tree()`
- Loading and lookup:
  - `btrfs_load_free_space_tree()`
  - `btrfs_search_free_space_info()`
  - `btrfs_free_space_root()`
- Cleanup:
  - `btrfs_delete_orphan_free_space_entries()`

## Test Exports
When sanity tests are enabled, the header exposes internal add/remove and conversion helpers plus `btrfs_free_space_test_bit()`.

## Design Notes
This header is intentionally smaller than `free-space-cache.h`; it exposes only the persistent free-space tree API and hides most bitmap/extent mutation internals in `free-space-tree.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/free-space-tree.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/fs.c -->
# File Research: sources/os/linux/linux/fs/btrfs/fs.c

## Purpose
Provides shared Btrfs filesystem-level helpers: checksum dispatch, block-size validation, exclusive-operation state transitions, and superblock feature flag mutation.

## Checksum Support
- `btrfs_csums[]` maps checksum type to digest size and name:
  - CRC32C
  - XXHASH64
  - SHA256
  - BLAKE2b
- `btrfs_csum_type_size()`, `btrfs_super_csum_size()`, `btrfs_super_csum_name()`, and `btrfs_get_num_csums()` expose metadata.
- `btrfs_csum()` computes one-shot checksums.
- `btrfs_csum_init()`, `btrfs_csum_update()`, and `btrfs_csum_final()` provide streaming checksum API through `struct btrfs_csum_ctx`.
- Unknown checksum types hit `BUG()` because mount-time validation is expected to have rejected them.

## Block Size Validation
- `btrfs_supported_blocksize()` accepts common supported block sizes:
  - 4 KiB,
  - `PAGE_SIZE`,
  - `BTRFS_MIN_BLOCKSIZE`.
- Under `CONFIG_BTRFS_EXPERIMENTAL`, larger-than-page block sizes can be accepted except on `HIGHMEM`, where features lack robust large-folio/page-loop coverage.
- The helper asserts the caller already validated power-of-two and min/max bounds.

## Exclusive Operations
Functions serialize operations such as balance, device add/remove, device replace, resize, and swap activation:
- `btrfs_exclop_start()` starts an operation only from `BTRFS_EXCLOP_NONE`.
- `btrfs_exclop_start_try_lock()` allows compatible overlap for same operation or device-add while balance is paused; it returns with `super_lock` held on success.
- `btrfs_exclop_start_unlock()` releases that lock.
- `btrfs_exclop_finish()` clears the operation and notifies sysfs.
- `btrfs_exclop_balance()` transitions balance between active and paused states.

## Feature Flag Mutation
- `__btrfs_set_fs_incompat()` and `__btrfs_clear_fs_incompat()` mutate superblock incompat flags under `fs_info->super_lock`.
- `__btrfs_set_fs_compat_ro()` and `__btrfs_clear_fs_compat_ro()` mutate compat-ro flags similarly.
- All flag changes set `BTRFS_FS_FEATURE_CHANGED` for later user-visible/sysfs update handling.
- These helpers are used by free-space tree creation/deletion to set or clear `FREE_SPACE_TREE` and `FREE_SPACE_TREE_VALID`.

## Concurrency
- `fs_info->super_lock` protects exclusive operation state and superblock feature flag updates.
- Read-side feature checks are generally lockless because feature flags are stable enough after mount except through these controlled mutation paths.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/fs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/fs.h -->
# File Research: sources/os/linux/linux/fs/btrfs/fs.h

## Purpose
Central Btrfs filesystem header. It defines filesystem-wide constants, mount option bits, feature masks, core runtime state structures, checksum context, helper macros, and inline accessors used across the Btrfs implementation.

## Constants and Limits
- `BTRFS_MIN_BLOCKSIZE`: 4 KiB normally, 2 KiB in debug builds for subpage testing.
- `BTRFS_MAX_BLOCKSIZE`: 64 KiB.
- `BTRFS_MAX_EXTENT_SIZE`: 128 MiB.
- `BTRFS_MAX_TRIM_LENGTH`: 2 GiB per trim iteration.
- Superblock offset/size constants and static assertion for `struct btrfs_super_block`.
- Formatting helpers for checksums and keys.
- Metadata reservation estimate helpers:
  - `btrfs_calc_insert_metadata_size()`
  - `btrfs_calc_metadata_size()`
  - `btrfs_csum_bytes_to_leaves()`

## Filesystem State Flags
Defines two major bit groups:
- `BTRFS_FS_STATE_*`: runtime state such as remounting, read-only, transaction aborted, log replay aborted, device replace, emergency shutdown, and test dummy fs.
- `BTRFS_FS_*`: operational flags such as log recovery, quota enabled, creating free-space tree, cleanup space-cache-v1, free-space-tree untrusted, balance/relocation running, discard running, feature changed, and transaction commit requests.

Free-space-related flags:
- `BTRFS_FS_CREATING_FREE_SPACE_TREE`
- `BTRFS_FS_CLEANUP_SPACE_CACHE_V1`
- `BTRFS_FS_FREE_SPACE_TREE_UNTRUSTED`
- `BTRFS_FS_DISCARD_RUNNING`

## Mount Options and Feature Masks
- Mount option bits include `SPACE_CACHE`, `CLEAR_CACHE`, `FREE_SPACE_TREE`, `DISCARD_SYNC`, `DISCARD_ASYNC`, `NODISCARD`, and many unrelated Btrfs options.
- Compat-ro supported feature mask includes `FREE_SPACE_TREE` and `FREE_SPACE_TREE_VALID`.
- Incompat supported masks include stable features and optional experimental features such as `EXTENT_TREE_V2`, `RAID_STRIPE_TREE`, and `REMAP_TREE`.

## Free-Space-Relevant Structures
- `struct btrfs_free_cluster`
  - Holds a cluster rb-tree, max extent size, window start, owning block group, and block-group list linkage.
  - Used by free-space-cache allocation paths.
- `struct btrfs_discard_ctl`
  - Workqueue, delayed work, discard lists, current block group, rate limits, max discard size, counters, and saved-discard-byte accounting.
  - Used by free-space-cache trimming and async discard.
- `struct btrfs_fs_info`
  - The central per-mounted-filesystem object.
  - Contains all root pointers, block-group cache tree, mapping tree, reservations, transactions, mount options, workqueues, locks, discard control, zoned state, free clusters, block sizes, feature state, commit stats, and many subsystem controls.
  - Fields directly relevant to this group include:
    - `block_group_cache_tree`
    - `mount_opt`
    - `super_lock`
    - `super_copy`
    - `discard_ctl`
    - `data_alloc_cluster`
    - `meta_alloc_cluster`
    - `unused_bgs`, `fully_remapped_bgs`
    - `zone_size`, `max_extent_size`
    - `flags` bits for free-space tree/cache state.

## Checksum Context
- `struct btrfs_csum_ctx` holds streaming checksum state for CRC32C, XXHASH64, SHA256, or BLAKE2b.
- Prototypes match implementations in `fs.c`.

## Inline Helpers and Macros
- Inode/fs-info conversions:
  - `folio_to_inode()`
  - `folio_to_fs_info()`
  - `inode_to_fs_info()`
- Block/folio helpers:
  - `btrfs_alloc_write_mask()`
  - `btrfs_min_folio_size()`
  - `btrfs_blocks_per_folio()`
  - `btrfs_is_zoned()`
  - `count_max_extents()`
- Generation accessors:
  - `btrfs_get_fs_generation()`
  - `btrfs_set_fs_generation()`
  - `btrfs_get_last_trans_committed()`
  - `btrfs_set_last_trans_committed()`
- Feature flag macros:
  - `btrfs_set_fs_incompat()`, `btrfs_clear_fs_incompat()`, `btrfs_fs_incompat()`
  - `btrfs_set_fs_compat_ro()`, `btrfs_clear_fs_compat_ro()`, `btrfs_fs_compat_ro()`
- Mount option macros:
  - `btrfs_set_opt()`, `btrfs_clear_opt()`, `btrfs_test_opt()`
- Shutdown and cleaner helpers:
  - `btrfs_fs_closing()`
  - `btrfs_need_cleaner_sleep()`
  - `btrfs_is_shutdown()`
  - `btrfs_force_shutdown()`

## Design Notes
This file is not a single subsystem implementation; it is the shared state contract for the Btrfs filesystem. The free-space cache and free-space tree code rely on it for mount options, feature flags, discard control, block sizes, zoned mode checks, cluster structures, and global filesystem locks.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/fs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/inode-item.c -->
# File Research: sources/os/linux/linux/fs/btrfs/inode-item.c

## Purpose
Implements Btrfs inode item, inode reference, extended inode reference, inode lookup, and inode item truncation helpers. In this group, it is directly relevant because `free-space-cache.c` uses `btrfs_truncate_inode_items()` to truncate free-space cache inodes.

## Inode Reference Lookup
- `btrfs_find_name_in_backref()` scans a `BTRFS_INODE_REF_KEY` item for a matching filename.
- `btrfs_find_name_in_ext_backref()` scans a `BTRFS_INODE_EXTREF_KEY` item for matching parent objectid and filename.
- `btrfs_lookup_inode_extref()` computes the extended-ref hash from parent objectid/name and searches for the matching extref item.

## Inode Reference Deletion
- `btrfs_del_inode_extref()` removes one extended inode ref from an item, deleting the entire item if it was the only ref or compacting the item otherwise.
- `btrfs_del_inode_ref()` first tries the regular inode ref item, then falls back to extended inode refs if not found.
- Both return the deleted index through an optional output pointer.

## Inode Reference Insertion
- `btrfs_insert_inode_extref()` inserts or extends an extended inode ref item keyed by CRC32C hash of parent objectid/name.
- `btrfs_insert_inode_ref()` inserts a regular inode ref item, extends an existing item when possible, detects duplicates, and falls back to extended refs on `-EOVERFLOW`/`-EMLINK` if the filesystem has `EXTENDED_IREF`.

## Inode Item Helpers
- `btrfs_insert_empty_inode()` inserts an empty `BTRFS_INODE_ITEM_KEY` item for a given objectid.
- `btrfs_lookup_inode()` searches for an inode/root item and has special handling for root item lookup with offset `-1`, accepting a preceding matching root item.

## Truncation Logic
`btrfs_truncate_inode_items()` removes or shrinks items associated with an inode.

Inputs are provided through `struct btrfs_truncate_control`:
- inode pointer, optional when not clearing extent ranges.
- target `new_size`.
- inode objectid.
- minimum key type to remove.
- flags for skipping reference updates and clearing file extent ranges.

Behavior:
- Scans inode items backwards from max key.
- Removes all item types greater than or equal to `min_type`, subject to offset/new-size rules for `BTRFS_EXTENT_DATA_KEY`.
- For regular/prealloc file extents:
  - Deletes whole extents or shrinks the last overlapping extent.
  - Updates `sub_bytes`, `last_size`, and delayed extent refs through `btrfs_free_extent()`.
- For inline extents:
  - Shrinks unencoded inline extents in place.
  - Returns `BTRFS_NEED_TRUNCATE_BLOCK` when caller must handle an encoded inline tail.
- Batches adjacent item deletions with `btrfs_del_items()`.
- For shareable roots, periodically backs off with `-EAGAIN` when transaction work should end or delayed-ref reservation needs refill.
- Optionally clears file extent ranges from the in-memory inode extent map through `btrfs_inode_clear_file_extent_range()`.

## Error Handling
- Allocation failure returns `-ENOMEM`.
- Missing refs return `-ENOENT`.
- Structural inconsistencies during extref deletion abort the transaction.
- Truncation aborts the transaction on failed extent-range clearing, extent ref drops, or item deletion errors.

## Cross-File Links
- `free-space-cache.c` calls this function with `min_type = BTRFS_EXTENT_DATA_KEY`, `new_size = 0`, and `clear_extent_range = true` to remove data extents from free-space cache inodes.
- The inode creation helper is used by free-space cache inode creation.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/inode-item.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/inode-item.h -->
# File Research: sources/os/linux/linux/fs/btrfs/inode-item.h

## Purpose
Declares inode item/reference helper APIs and `struct btrfs_truncate_control`, used by inode metadata code and free-space-cache inode truncation.

## Key Definitions
- `BTRFS_NEED_TRUNCATE_BLOCK`: positive return value indicating caller must truncate the final block separately.
- `struct btrfs_truncate_control`
  - Inputs:
    - `inode`
    - `new_size`
    - `ino`
    - `min_type`
    - `skip_ref_updates`
    - `clear_extent_range`
  - Outputs:
    - `extents_found`
    - `last_size`
    - `sub_bytes`

## Inline Helpers
- `btrfs_inode_combine_flags()` combines mutable and read-only inode flags into the u64 on-disk inode-item representation.
- `btrfs_inode_split_flags()` splits the u64 on-disk representation back into two u32 values.
- `btrfs_extref_hash()` computes the extended inode-ref key offset using CRC32C over parent objectid and name.

## Public API
- Truncation:
  - `btrfs_truncate_inode_items()`
- Inode ref insertion/deletion:
  - `btrfs_insert_inode_ref()`
  - `btrfs_del_inode_ref()`
- Inode item creation/lookup:
  - `btrfs_insert_empty_inode()`
  - `btrfs_lookup_inode()`
- Extended ref lookup and name matching:
  - `btrfs_lookup_inode_extref()`
  - `btrfs_find_name_in_backref()`
  - `btrfs_find_name_in_ext_backref()`

## Design Notes
The header isolates inode item mutation contracts from the rest of Btrfs. The free-space cache code depends on this header for creating cache inodes and truncating their extent data safely inside transactions.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/inode-item.h -->