# Group Research: group_250_btrfs_linux_sources_local_fs_btrfs_linux_fs_btrfs_free_space_cache_c_cd05b8675a7f

Scope: `Docs/research_subset_a.md`; all listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/free-space-cache.c -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/free-space-cache.c

## Summary
Implements Btrfs free-space cache v1 and the in-memory free-space allocator for block groups. It manages free-space extents and bitmap entries, loads and writes legacy cache inodes, allocates from free-space clusters, tracks discard/trim state, handles zoned block-group accounting, and provides sanity-test helpers.

## Main Responsibilities
- Create, find, truncate, write, validate, and remove per-block-group free-space cache inodes.
- Maintain `btrfs_free_space_ctl` rb-trees indexed by offset and available size.
- Represent free space as extent entries or sector-granularity bitmaps, converting small fragmented regions to bitmaps when thresholds are exceeded.
- Add, remove, merge, split, and search free-space ranges for extent allocation.
- Build and allocate from clustered free-space windows for metadata and SSD-spread allocation paths.
- Track discardable bytes/extents and trim state for sync and async discard.
- Implement block-group trimming over extent entries and bitmap entries.
- Provide special accounting behavior for zoned block groups, where free space follows allocation-pointer semantics rather than ordinary arbitrary reuse.

## Key APIs
- Cache inode lifecycle: `lookup_free_space_inode()`, `create_free_space_inode()`, `btrfs_remove_free_space_inode()`, `btrfs_truncate_free_space_cache()`.
- Cache I/O: `load_free_space_cache()`, `btrfs_write_out_cache()`, `btrfs_wait_cache_io()`.
- Free-space control: `btrfs_init_free_space_ctl()`, `btrfs_remove_free_space_cache()`, `btrfs_dump_free_space()`.
- Free-space updates: `btrfs_add_free_space()`, `btrfs_add_free_space_unused()`, `btrfs_add_free_space_async_trimmed()`, `btrfs_remove_free_space()`.
- Allocation: `btrfs_find_space_for_alloc()`, `btrfs_find_space_cluster()`, `btrfs_alloc_from_cluster()`, `btrfs_return_cluster_to_free_space()`, `btrfs_init_free_cluster()`.
- Discard/trim: `btrfs_is_free_space_trimmed()`, `btrfs_trim_block_group()`, `btrfs_trim_block_group_extents()`, `btrfs_trim_block_group_bitmaps()`, `btrfs_trim_fully_remapped_block_group()`.
- Space-cache v1 feature state: `btrfs_free_space_cache_v1_active()`, `btrfs_set_free_space_cache_v1_active()`.
- Slab lifecycle: `btrfs_free_space_init()`, `btrfs_free_space_exit()`.

## Important Behavior
The legacy on-disk cache is stored in an internal inode referenced by a `BTRFS_FREE_SPACE_OBJECTID` item. The cache file starts with page CRCs and a generation, then serializes free-space entries followed by bitmap pages. Loading validates inode generation, cache generation, CRCs, entry counts, duplicate entries, and total free-space accounting before copying the temporary cache into the live block group.

Writeout is asynchronous relative to transaction commit. `btrfs_write_out_cache()` serializes extents, bitmaps, pinned extents from the current transaction, and active trimming ranges, dirties the cache inode pages, and starts writeback. `btrfs_wait_cache_io()` later waits for ordered I/O, updates the cache header counts/generation, and marks the block group `BTRFS_DC_WRITTEN` only if it did not become dirty again.

The in-memory free-space cache uses two trees: `free_space_offset` for address lookup and `free_space_bytes` for largest-first allocation lookup. Extent and bitmap entries can share an offset; ordering makes normal extents preferred before bitmap entries. Bitmap entries maintain `bytes`, `bitmap_extents`, `max_extent_size`, and trim state.

Free-space insertion first tries to merge neighboring extent entries according to trim-state rules. If extent count pressure is high or regions are small/fragmented, space is inserted into bitmap entries. Large regions are forced back to extent entries, and adjacent bitmap ranges are stolen into new extent entries to improve future allocation success.

Allocation prefers extent entries and uses bitmap `max_extent_size` as a cached negative-search result. If alignment creates a leading gap, the gap is returned to free space after the allocation. Cluster allocation moves extents or bitmap entries out of the normal free-space tree into a `btrfs_free_cluster` tree, then allocates from the cluster under its own lock.

Trimming temporarily removes free space from the cache, records it in `trimming_ranges` so cache writeout does not lose it, issues `btrfs_discard_extent()`, then reinserts the range with trimmed or untrimmed state based on discard success. Bitmap trimming has lossy trimmed-state handling to avoid repeatedly discarding tiny fragments.

Zoned mode bypasses the normal tree/bitmap free-space model. Freeing space adjusts `ctl->free_space`, `block_group->alloc_offset`, and `zone_unusable`, and may mark block groups unused or reclaimable when unusable space crosses thresholds.

## State and Synchronization
`ctl->tree_lock` protects the free-space rb-trees, free-space counters, bitmap counts, and discardable counters. `ctl->cache_writeout_mutex` serializes cache writeout against trim operations that may remove bitmap ranges or manipulate `trimming_ranges`.

Block-group state is protected with `block_group->lock`, `data_rwsem`, and transaction dirty-list locks depending on the path. Cluster state is protected by `cluster->lock`, while cluster insertion/removal also occurs under the parent control's `tree_lock`.

Cache inode I/O uses page locks, extent locks, `EXTENT_DELALLOC`, ordered range waits, and inode generation updates. GFP masks deliberately avoid filesystem recursion for cache inode pages.

## Risks
The file has several overlapping accounting systems: free bytes, free extents, bitmap extents, discardable bytes, cache entries, pinned extents, trimming ranges, cluster contents, and zoned unusable space. Any missed update can lead to allocator ENOSPC errors, duplicate free-space exposure, leaked free space, or stale discard counters.

Cache v1 correctness depends on generation and CRC validation. A valid-looking but stale cache could corrupt allocation decisions, so the load path drops the entire temporary cache on mismatches, duplicates, or free-space total mismatches.

Lock ordering is subtle around `tree_lock`, cluster locks, `cache_writeout_mutex`, block-group locks, and transaction locks. The writeout and trim paths intentionally serialize only parts of the state to avoid losing ranges removed for discard.

Bitmap trim state is intentionally approximate. It optimizes async discard behavior but can cause retrimming or conservative untrimmed marking after races, interruption, or partial bitmap scans.

Zoned handling shares public free-space APIs but follows different semantics; callers must not assume arbitrary free-space tree entries exist in zoned mode.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/free-space-cache.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/free-space-cache.h -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/free-space-cache.h

## Summary
Declares the in-memory free-space cache data structures, trim-state model, cache inode I/O context, free-space allocator interfaces, cluster interfaces, trim interfaces, and cache-v1 feature controls.

## Main Contents
- `enum btrfs_trim_state` for untrimmed, trimmed, and in-progress bitmap trimming state.
- `struct btrfs_free_space` representing either an extent entry or bitmap entry.
- `struct btrfs_free_space_ctl` containing free-space rb-trees, counters, discard deltas, block-group ownership, writeout mutex, and trimming range list.
- `struct btrfs_free_space_op` hook for bitmap selection policy.
- `struct btrfs_io_ctl` page-buffer context for reading and writing cache inode contents.
- Function declarations for cache inode lifecycle, cache load/write, free-space mutation, allocation, clustering, trimming, and tests.

## Key Interfaces
The header exposes the allocator-facing APIs `btrfs_add_free_space()`, `btrfs_remove_free_space()`, `btrfs_find_space_for_alloc()`, and cluster allocation helpers, plus the persistence-facing APIs `load_free_space_cache()`, `btrfs_write_out_cache()`, and `btrfs_wait_cache_io()`.

## Important Details
`btrfs_free_space_trimmed()` and `btrfs_free_space_trimming_bitmap()` encode trim-state checks used by discard and allocator accounting. `btrfs_trim_interrupted()` treats fatal signals and freezer state as trim cancellation conditions.

Discard statistics use current/previous delta slots (`BTRFS_STAT_CURR`, `BTRFS_STAT_PREV`) so the discard subsystem can aggregate changes from each block group's free-space control.

`btrfs_io_ctl` is a low-level cursor over cache inode pages. It carries the current page pointer, page array, inode, filesystem info, page count, and serialized entry/bitmap counts.

## Risks
`struct btrfs_free_space` is used in both normal block-group trees and cluster trees; callers must respect which rb-node is currently linked and which lock protects it.

The trim state is per extent or per whole bitmap, not per bit. Bitmap trim state is therefore intentionally lossy, and callers must not interpret `TRIMMED` as proof that every historical fragment has perfect per-sector state.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/free-space-cache.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/free-space-tree.c -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/free-space-tree.c

## Summary
Implements the persistent Btrfs free-space tree, the compat-ro replacement for free-space cache v1. It stores per-block-group free-space information in B-tree items, switches between extent keys and bitmap items, updates the tree during allocation/free operations, loads free space into the in-memory block-group cache, and creates, deletes, or rebuilds the tree.

## Main Responsibilities
- Select the correct free-space root, including extent-tree-v2 per-global-root handling.
- Create and find per-block-group `BTRFS_FREE_SPACE_INFO_KEY` items.
- Maintain extent count and bitmap-format flags for each block group.
- Convert block-group free-space representation between extent items and bitmap items.
- Add and remove free-space ranges in extent or bitmap representation.
- Populate the free-space tree by scanning extent-tree metadata.
- Create, delete, rebuild, and clear the free-space tree.
- Add or remove all free-space items for a block group.
- Load free-space tree contents into the in-memory free-space cache during block-group caching.
- Delete orphan free-space entries that precede the first real block group.

## Key APIs
- Root and threshold helpers: `btrfs_free_space_root()`, `btrfs_set_free_space_tree_thresholds()`, `btrfs_search_free_space_info()`.
- Feature lifecycle: `btrfs_create_free_space_tree()`, `btrfs_delete_free_space_tree()`, `btrfs_rebuild_free_space_tree()`.
- Block-group lifecycle: `btrfs_add_block_group_free_space()`, `btrfs_remove_block_group_free_space()`.
- Range updates: `btrfs_add_to_free_space_tree()`, `btrfs_remove_from_free_space_tree()`.
- Loading and repair: `btrfs_load_free_space_tree()`, `btrfs_delete_orphan_free_space_entries()`.
- Test-exported internals: `__btrfs_add_to_free_space_tree()`, `__btrfs_remove_from_free_space_tree()`, `btrfs_convert_free_space_to_bitmaps()`, `btrfs_convert_free_space_to_extents()`, `btrfs_free_space_test_bit()`.

## Important Behavior
Each block group has an info item keyed by block-group start and length. Free-space payload is stored after the info item as either `BTRFS_FREE_SPACE_EXTENT_KEY` items, where key offset is extent length, or `BTRFS_FREE_SPACE_BITMAP_KEY` items containing little-endian bitmap data. The info item records extent count and the `BTRFS_FREE_SPACE_USING_BITMAPS` flag.

Thresholds compare estimated metadata space for extent items with bitmap item space. When extent count rises above `bitmap_high_thresh`, extents are converted into bitmap items. When count drops below `bitmap_low_thresh`, bitmaps are converted back into extents. The gap between thresholds prevents format thrashing.

Extent-mode removal finds the containing extent key and handles four split cases: full removal, trim from beginning, trim from end, or split into two leftovers. Extent-mode addition searches adjacent left and right neighbors and merges if contiguous before inserting the resulting key.

Bitmap-mode updates locate the bitmap before or containing the target range, set or clear bits across one or more bitmap items, inspect neighboring bits, and adjust the logical extent count by whether the operation merged or split free extents.

Creation builds a new free-space tree root, marks the tree untrusted during population, walks every block group, scans the extent tree for allocated extent and metadata items, and inserts free gaps into the free-space tree. Only after commit is the free-space tree considered trusted for block-group caching.

Rebuild clears the existing tree, repopulates block groups, and handles new block groups created during rebuild by marking `BLOCK_GROUP_FLAG_FREE_SPACE_ADDED` so they are not populated twice.

Loading starts from the block group's info item using the commit root with locking skipped, then either iterates free-space extent keys or reconstructs extents from bitmap bits. Found ranges are added to the in-memory free-space cache via `btrfs_add_new_free_space()`, with wakeups after enough space has been discovered.

## State and Synchronization
`block_group->free_space_lock` serializes modifications for one block group. Path objects are reused carefully and released between insertions/deletions to avoid stale leaf state after tree changes.

The create/rebuild paths set `BTRFS_FS_CREATING_FREE_SPACE_TREE` and `BTRFS_FS_FREE_SPACE_TREE_UNTRUSTED` to prevent consumers from trusting incomplete state. Compat-ro feature bits `FREE_SPACE_TREE` and `FREE_SPACE_TREE_VALID` gate public add/remove/load operations.

Allocation inside tree modification uses NOFS for bitmap buffers because callers hold transaction handles and must not recurse into filesystem allocation or transaction commit paths.

## Risks
Extent count is a central invariant. Conversion and bitmap updates verify counted extents against the info item; mismatches produce errors and transaction aborts because they imply free-space tree corruption.

The code relies on key ordering and reverse searches for the previous slot. Unexpected key types or missing previous slots are treated as corruption or logic errors.

Free-space tree creation and rebuild modify free-space metadata while normal extent allocation hooks may also update the same tree. The `NEEDS_FREE_SPACE` and `FREE_SPACE_ADDED` runtime flags are critical to avoiding duplicate block-group entries.

Bitmap operations use little-endian bit order in extent buffers and must correctly account for block-group boundaries, partial final bitmaps, and adjacent bits across bitmap item boundaries.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/free-space-tree.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/free-space-tree.h -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/free-space-tree.h

## Summary
Declares the public interface and constants for the persistent Btrfs free-space tree.

## Main Contents
- `BTRFS_FREE_SPACE_BITMAP_SIZE` fixed at 256 bytes for default bitmap item payloads.
- `BTRFS_FREE_SPACE_BITMAP_BITS` derived from bitmap size and bits per byte.
- Declarations for free-space tree create/delete/rebuild/load operations.
- Declarations for per-block-group add/remove and per-range add/remove hooks.
- Declarations for info-item lookup and free-space-root selection.
- Additional test-only declarations when `CONFIG_BTRFS_FS_RUN_SANITY_TESTS` is enabled.

## Key Interfaces
Primary callers use `btrfs_add_to_free_space_tree()` and `btrfs_remove_from_free_space_tree()` from allocation/free paths, `btrfs_load_free_space_tree()` from block-group caching, and `btrfs_create_free_space_tree()`, `btrfs_delete_free_space_tree()`, or `btrfs_rebuild_free_space_tree()` from mount or feature-management paths.

## Important Details
The header documents that the final bitmap in a block group may be shorter than the default size and that implementation code must not assume existing bitmap items always have the default payload length.

## Risks
The interface is transaction-oriented. Callers must pass valid transaction handles for mutating operations and must respect feature gating so that free-space tree updates are skipped when the compat-ro feature is not active.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/free-space-tree.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/fs.c -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/fs.c

## Summary
Provides shared Btrfs filesystem helpers for checksum algorithms, supported block-size validation, exclusive-operation state, and superblock feature flag updates.

## Main Responsibilities
- Define checksum algorithm sizes and names.
- Compute one-shot and incremental checksums for CRC32C, xxhash64, SHA-256, and BLAKE2b.
- Validate supported filesystem block sizes for normal and experimental builds.
- Coordinate exclusive filesystem operations such as balance, device add/remove, device replace, resize, and swap activation.
- Set and clear incompat and compat-ro feature flags in the in-memory superblock copy while marking feature state changed.

## Key APIs
- Checksum metadata: `btrfs_csum_type_size()`, `btrfs_super_csum_size()`, `btrfs_super_csum_name()`, `btrfs_get_num_csums()`.
- Checksum calculation: `btrfs_csum()`, `btrfs_csum_init()`, `btrfs_csum_update()`, `btrfs_csum_final()`.
- Block size: `btrfs_supported_blocksize()`.
- Exclusive operations: `btrfs_exclop_start()`, `btrfs_exclop_start_try_lock()`, `btrfs_exclop_start_unlock()`, `btrfs_exclop_finish()`, `btrfs_exclop_balance()`.
- Feature updates: `__btrfs_set_fs_incompat()`, `__btrfs_clear_fs_incompat()`, `__btrfs_set_fs_compat_ro()`, `__btrfs_clear_fs_compat_ro()`.

## Important Behavior
Checksum type is assumed to be validated at mount time; unsupported checksum types hit `BUG()` in checksum dispatch. CRC32C uses Btrfs' inverted CRC convention, while xxhash64, SHA-256, and BLAKE2b use their normal digest flows.

Block-size support always accepts 4 KiB, `PAGE_SIZE`, and `BTRFS_MIN_BLOCKSIZE`. Experimental builds may allow block size larger than page size, except on highmem systems where large folio content cannot always be addressed safely.

Exclusive operation state is protected by `fs_info->super_lock`. Starting an operation succeeds only from `BTRFS_EXCLOP_NONE`, except `btrfs_exclop_start_try_lock()` also permits compatible reentry for the same operation and device add while balance is paused. Finishing clears the state and notifies sysfs.

Feature flag setters and clearers double-check flags under `super_lock`, update `super_copy`, log the change, and set `BTRFS_FS_FEATURE_CHANGED`.

## State and Synchronization
`fs_info->super_lock` protects exclusive-operation state and feature flag updates in `super_copy`. The checksum helpers are stateless except for `struct btrfs_csum_ctx` passed by callers.

## Risks
The checksum dispatch depends on earlier mount-time validation. A bad checksum type reaching these helpers is treated as a kernel bug, not a recoverable error.

Exclusive-operation compatibility is intentionally narrow. Callers must choose the right start helper and must pair successful try-lock paths with `btrfs_exclop_start_unlock()` and later `btrfs_exclop_finish()`.

Feature updates modify the in-memory superblock copy; persistence depends on later superblock write/commit paths noticing `BTRFS_FS_FEATURE_CHANGED`.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/fs.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/fs.h -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/fs.h

## Summary
Defines central Btrfs filesystem constants, runtime state bits, mount option bits, supported feature masks, compression identifiers, and major in-memory structures such as `btrfs_fs_info`, `btrfs_free_cluster`, `btrfs_discard_ctl`, and checksum contexts.

## Main Responsibilities
- Establish global size limits and metadata sizing helpers.
- Define filesystem runtime state flags and long-lived `fs_info->flags` bits.
- Define mount option bit assignments and read-only mount option mask.
- Declare supported compat-ro and incompat feature masks.
- Define compression type identifiers and exclusive operation identifiers.
- Define core runtime structures used across Btrfs subsystems.
- Provide inline helpers for fs generation, transaction generation, metadata reservations, zoned checks, folio block counts, mount option checks, shutdown state, and test builds.

## Key Structures
- `struct btrfs_fs_info`: top-level per-mounted-filesystem state. It owns root pointers, global root tree, fs-root radix tree, block-group tree, mapping tree, reservations, transactions, worker pools, block-group reclaim lists, discard state, qgroup state, scrub state, balance state, dev-replace state, sysfs objects, cached block sizes, zoned-mode fields, commit stats, and debug-only tracking.
- `struct btrfs_free_cluster`: clustered allocation window with rb-tree of reserved free-space entries, max extent size, window start, owning block group, and locks.
- `struct btrfs_discard_ctl`: async discard work, queues, limits, current block group, discard filters, and counters.
- `struct btrfs_dev_replace`: device replacement state, progress, devices, counters, wait queues, locks, and worker task.
- `struct btrfs_delayed_root`: delayed inode/item root state and wait queue.
- `struct btrfs_commit_stats`: commit counters and durations.
- `struct btrfs_csum_ctx`: algorithm-tagged checksum context for CRC32C, xxhash64, SHA-256, and BLAKE2b.

## Key APIs and Helpers
- Metadata sizing: `btrfs_calc_insert_metadata_size()`, `btrfs_calc_metadata_size()`, `btrfs_csum_bytes_to_leaves()`, `count_max_extents()`.
- Generation access: `btrfs_get_fs_generation()`, `btrfs_set_fs_generation()`, `btrfs_get_last_trans_committed()`, `btrfs_set_last_trans_committed()`, `btrfs_set_last_root_drop_gen()`, `btrfs_get_last_root_drop_gen()`.
- Filesystem modes: `btrfs_is_zoned()`, `btrfs_is_shutdown()`, `btrfs_force_shutdown()`, `btrfs_fs_closing()`, `btrfs_need_cleaner_sleep()`.
- Mount and feature checks: `btrfs_test_opt()`, `btrfs_set_opt()`, `btrfs_clear_opt()`, `btrfs_fs_incompat()`, `btrfs_fs_compat_ro()`.
- Folio helpers: `folio_to_inode()`, `folio_to_fs_info()`, `inode_to_fs_info()`, `btrfs_blocks_per_folio()`, ordered-folio flag helpers.

## Important Behavior
`btrfs_fs_info` is the central coordination object for almost every Btrfs subsystem. Many members have explicit lock ownership in comments, including generation under `trans_lock`, root trees under root-specific locks, space info under RCU, block-group lists under `unused_bgs_lock`, and exclusive operation under `super_lock`.

Mount options include both ordinary behavior switches and full read-only options. `BTRFS_MOUNT_FULL_RO_MASK` identifies options that require a mount mode where no new transaction can be allowed.

Supported feature masks distinguish stable incompat features from experimental features. Extent tree v2, RAID stripe tree, and remap tree are only in the supported incompat mask under `CONFIG_BTRFS_EXPERIMENTAL`.

The file defines the free-space and discard structures used by `free-space-cache.c` and `discard.c`. `btrfs_free_cluster` is used to batch allocation from block groups, while `btrfs_discard_ctl` manages async discard queues and rate limiting.

Shutdown helper `btrfs_force_shutdown()` records `-EIO`, sets emergency-shutdown state, logs once, and reports the shutdown through `fserror_report_shutdown()` without directly flipping the superblock read-only flag.

## Risks
Because `btrfs_fs_info` aggregates cross-subsystem state, lock ownership and lifetime rules are spread across many users. Misusing a field without the documented lock can race mount, unmount, transaction commit, reclaim, discard, scrub, balance, or device replacement.

Feature masks define mount compatibility. Accidentally adding a feature to the wrong mask can allow unsafe mounts or reject valid filesystems.

Several helpers use `READ_ONCE()`/`WRITE_ONCE()` for fields with special transaction visibility rules. Direct access to those fields can see inconsistent state or violate ordering assumptions.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/fs.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/inode-item.c -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/inode-item.c

## Summary
Implements low-level Btrfs inode item, inode reference, extended inode reference, inode lookup, and inode item truncation helpers. It manipulates packed inode-ref arrays inside B-tree leaves and performs truncation-time deletion or shortening of file extent items with delayed-ref updates.

## Main Responsibilities
- Search normal inode backref items by name.
- Search extended inode backref items by parent objectid and name.
- Lookup, insert, and delete extended inode refs.
- Insert and delete normal inode refs, falling back to extended refs when the normal item overflows.
- Insert empty inode items.
- Lookup inode/root items with special handling for root item searches using offset `-1`.
- Truncate inode-associated B-tree items and file extents according to a `btrfs_truncate_control`.

## Key APIs
- Ref search: `btrfs_find_name_in_backref()`, `btrfs_find_name_in_ext_backref()`, `btrfs_lookup_inode_extref()`.
- Ref mutation: `btrfs_insert_inode_ref()`, `btrfs_del_inode_ref()`.
- Inode item operations: `btrfs_insert_empty_inode()`, `btrfs_lookup_inode()`.
- Truncation: `btrfs_truncate_inode_items()`.

## Important Behavior
Normal inode refs are stored as variable-length `struct btrfs_inode_ref` records packed into one item keyed by child inode and parent objectid. Search loops walk the packed item by each record's name length and compare the fscrypt-aware name bytes in the extent buffer.

Extended inode refs are keyed by `btrfs_extref_hash(parent_objectid, name)` and can contain collision records in one item. Search checks both parent objectid and name. Insert extends an existing item on hash collision unless the same name already exists.

`btrfs_insert_inode_ref()` first attempts the normal inode-ref item. If item insertion or extension overflows and the filesystem has `EXTENDED_IREF`, it inserts an extended ref. If the name already exists, it returns `-EEXIST`; if overflow cannot be represented, it returns `-EMLINK`.

`btrfs_del_inode_ref()` removes a normal ref by deleting the whole item when it contains only that ref, or memmoving later packed refs down and truncating the item. If no matching normal ref exists, it searches and removes the corresponding extended ref.

`btrfs_truncate_inode_items()` walks backward over all keys for an inode at or above `control->min_type`. For file extents, it deletes items fully beyond `new_size`, shrinks regular extent items that straddle `new_size`, truncates simple inline extents when possible, and returns `BTRFS_NEED_TRUNCATE_BLOCK` when an encoded inline extent cannot be safely shortened in place.

When dropping non-inline file extents, truncation clears file extent range state if requested, subtracts inode bytes, queues `BTRFS_DROP_DELAYED_REF` through `btrfs_free_extent()`, and may return `-EAGAIN` to let higher layers refill delayed-ref reservations or end a long transaction.

## State and Synchronization
All mutations require a transaction handle and use Btrfs path COW mode. Packed item changes use extent-buffer memmove, item truncation, and item extension helpers while the path points at the modified leaf.

Truncation batches adjacent pending item deletions to reduce repeated `btrfs_del_items()` calls. For shareable roots it periodically backs off when large amounts of data have been deleted and the transaction should end.

The truncate control structure carries both inputs and outputs: target inode/objectid, minimum key type, whether to skip ref updates, whether to clear in-memory extent ranges, last truncated size, extent count, and bytes to subtract.

## Risks
Packed inode-ref manipulation depends on exact item sizes and name lengths. A wrong `del_len`, memmove range, or collision check can corrupt directory backrefs.

Extended refs are hash keyed, so collision handling is required. Looking only at the key without validating parent objectid and name would delete or find the wrong ref.

Truncation mixes metadata deletion, inline extent resizing, delayed-ref creation, file extent range clearing, inode byte accounting, and transaction throttling. Error handling must abort the transaction on unrecoverable metadata or ref-update failures.

The `skip_ref_updates` flag is powerful and dangerous; it is only correct for callers that already handle extent references elsewhere.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/inode-item.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/inode-item.h -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/inode-item.h

## Summary
Declares Btrfs inode item/reference helpers and defines the truncate-control structure used by inode item truncation.

## Main Contents
- `BTRFS_NEED_TRUNCATE_BLOCK` return value for truncation paths that must truncate the final block separately.
- `struct btrfs_truncate_control` input/output state for `btrfs_truncate_inode_items()`.
- Inline helpers to combine and split persisted inode flags and read-only inode flags.
- `btrfs_extref_hash()` helper for extended inode reference item keys.
- Declarations for inode ref search, insert, delete, lookup, empty inode insertion, and truncation.

## Key Interfaces
The main public entry points are `btrfs_truncate_inode_items()`, `btrfs_insert_inode_ref()`, `btrfs_del_inode_ref()`, `btrfs_insert_empty_inode()`, `btrfs_lookup_inode()`, `btrfs_lookup_inode_extref()`, `btrfs_find_name_in_backref()`, and `btrfs_find_name_in_ext_backref()`.

## Important Details
`btrfs_truncate_control` separates inputs from outputs in comments. Callers provide inode/objectid, target size, minimum key type, and behavior flags; the truncate helper returns extent count, last size reached, and byte accounting.

Inode item flags are stored on disk as one 64-bit value but split in memory into two 32-bit fields. `btrfs_inode_combine_flags()` and `btrfs_inode_split_flags()` encode that boundary.

`btrfs_extref_hash()` uses CRC32C seeded by parent objectid over the name bytes, producing the key offset for extended inode refs.

## Risks
The truncate control allows `inode` to be `NULL` only when `clear_extent_range` is false. Callers must satisfy that contract because truncation may otherwise dereference the inode while clearing extent state.

Extended-ref hashes can collide, so users of the hash must still compare parent objectid and name inside the item.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/inode-item.h -->