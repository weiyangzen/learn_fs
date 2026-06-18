# Group Research: group_949_linux_stable_sources_os_linux_linux_stable_fs_btrfs_free_space_cache_43869d4f8c6f

Scope: `Docs/research_subset_a.md`; all listed Btrfs source files were read in full.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/free-space-cache.c -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/free-space-cache.c

## Purpose

Implements Btrfs free-space cache v1 and the runtime free-space cache used by block groups. It stores free space as extent entries or page-sized bitmaps, serializes/deserializes v1 cache inodes, provides allocation/removal helpers, manages allocation clusters, and drives synchronous/asynchronous discard trimming. It is the central in-memory allocator-side representation for non-zoned block groups, while zoned block groups take a specialized accounting path.

## Main Data Flow

- V1 cache inode lifecycle: `lookup_free_space_inode()`, `create_free_space_inode()`, `btrfs_remove_free_space_inode()`, and `btrfs_truncate_free_space_cache()` manage hidden per-block-group free-space cache inodes under the tree root.
- Cache read path: `load_free_space_cache()` validates block-group state, reads the cache inode into a temporary `btrfs_free_space_ctl`, verifies CRC/generation/space totals, then copies entries into the live block-group cache.
- Cache write path: `btrfs_write_out_cache()` serializes extents, bitmaps, pinned extents, and active trim ranges into the cache inode; `btrfs_wait_cache_io()` waits for writeback and marks the cache item valid.
- Allocation path: `btrfs_find_space_for_alloc()` searches by bytes or offset, handles full-stripe alignment gaps, clears bits/removes extents, updates discard accounting, and returns the chosen logical bytenr.
- Free path: `btrfs_add_free_space()`, `btrfs_add_free_space_unused()`, and `btrfs_add_free_space_async_trimmed()` add free regions, merge neighbors, choose extent vs bitmap representation, and queue async discard work when appropriate.
- Remove path: `btrfs_remove_free_space()` consumes free regions from extents or bitmaps, splitting/relinking extents as needed.
- Cluster path: `btrfs_find_space_cluster()`, `btrfs_alloc_from_cluster()`, and `btrfs_return_cluster_to_free_space()` move suitable extents/bitmaps into per-allocation clusters for less fragmented allocation.
- Trim path: `btrfs_trim_block_group()`, `btrfs_trim_block_group_extents()`, `btrfs_trim_block_group_bitmaps()`, and `btrfs_trim_fully_remapped_block_group()` discard free ranges while preserving free-space state and avoiding cache-write races.

## Internal Representation

The live cache is held by `struct btrfs_free_space_ctl` in two rbtrees: `free_space_offset` for bytenr ordering and `free_space_bytes` for largest-extent-first allocation. `struct btrfs_free_space` represents either a contiguous extent or a bitmap. Bitmap entries cover `BITS_PER_BITMAP * ctl->unit` logical bytes and track `bytes`, `max_extent_size`, `bitmap_extents`, and trim state. `entry_less()` intentionally sorts the bytes tree with larger available chunks first.

The code dynamically converts additions to bitmap-backed entries once the extent count exceeds memory thresholds. `recalculate_thresholds()` limits memory roughly by block-group size, while `use_bitmap()` keeps large extents as extents, avoids bitmaps for very small block groups, and includes debug fragmentation forcing. Large contiguous regions are also stolen back from adjacent bitmaps by `steal_from_bitmap*()` to improve allocation quality.

## On-Disk V1 Cache Format

`struct btrfs_io_ctl` walks cache-inode pages. Page 0 stores an array of per-page CRC32C values followed by the cache generation. Entries are written as `struct btrfs_free_space_entry` records, with bitmap payload pages appended after the entry list. `io_ctl_*` helpers map pages, read/write entries, add bitmap pages, zero trailing pages, and verify CRC/generation on load. `MAX_CACHE_BYTES_PER_GIG` and the first-page CRC/generation layout limit writable cache inode size.

## Concurrency And Locking

- `ctl->tree_lock` protects the free-space rbtrees, free-space counters, bitmap counters, and discardable counters.
- `ctl->cache_writeout_mutex` serializes cache writeout with trim bitmap/range manipulation and protects `trimming_ranges`.
- `block_group->lock`, `dirty_bgs_lock`, `data_rwsem`, and `cache_write_mutex` coordinate cache state transitions, dirty block groups, delalloc-sensitive data block groups, and cache truncation/writeback.
- Cluster operations use both `ctl->tree_lock` and `cluster->lock`; entries moved to clusters may have their bytes-index node cleared to prevent normal rbtree relinking.
- Cache inode lookup uses `memalloc_nofs_save()` and commit-root path flags in sensitive paths to avoid filesystem recursion and tree-root deadlocks.

## Error Handling And Integrity Checks

The load path rejects invalid inode generations, CRC mismatches, duplicate entries, zero-length entries, and free-space totals that do not match block-group accounting. Bad caches are cleared and rebuilt. Write failures invalidate inode pages, zero the inode generation, set `BTRFS_DC_ERROR`, and leave the caller responsible for aborting or retrying as appropriate. Many structural assumptions use `ASSERT()`/`WARN_ON()` because cache corruption or duplicate entries imply allocator metadata inconsistency.

## Zoned Behavior

For zoned filesystems the extent/bitmap free-space cache is bypassed. `__btrfs_add_free_space_zoned()` updates `ctl->free_space`, `alloc_offset`, and `zone_unusable`, and may mark block groups unused or reclaimable. `btrfs_remove_free_space()` advances `alloc_offset` during log replay if needed. Dumping reports free space after the allocation pointer.

## Integration Points

This file depends on block-group state, transaction commit state, extent-tree pinned extents, discard control, inode truncation/update helpers, page cache/folio operations, and mount options such as `DISCARD_SYNC`/`DISCARD_ASYNC`. It is used by allocation, block-group caching, transaction commit cache writeout, async discard, relocation/remapping cleanup, and Btrfs sanity tests.

## Test Hooks

Under `CONFIG_BTRFS_FS_RUN_SANITY_TESTS`, `test_add_free_space_entry()` inserts exact extent/bitmap entries without normal merging, and `test_check_exists()` checks whether any free space overlaps a range. These are deliberately lower-level than production add/remove paths.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/free-space-cache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/free-space-cache.h -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/free-space-cache.h

## Purpose

Declares the runtime free-space cache v1 data structures, trim-state model, cache inode I/O context, and public APIs implemented by `free-space-cache.c`. This header is the interface used by block-group caching, allocation, discard, transaction writeout, and sanity-test code.

## Key Types

- `enum btrfs_trim_state`: distinguishes untrimmed, trimmed, and in-progress bitmap trimming states. `BTRFS_TRIM_STATE_TRIMMING` is bitmap-specific and allows long bitmap trim passes to preserve state.
- `struct btrfs_free_space`: one free-space extent or bitmap entry, indexed by offset and size rbtrees, with offset/bytes/max extent size, optional bitmap pointer, list hook, trim state, and bitmap extent count.
- `struct btrfs_free_space_ctl`: per-block-group controller containing free-space rbtrees, counters, bitmap thresholds, discardable statistics, block-group backpointer, writeout mutex, and active trimming ranges.
- `struct btrfs_free_space_op`: policy hook for deciding whether an extent should be represented as a bitmap.
- `struct btrfs_io_ctl`: transient page-walking state for reading/writing cache inodes.

## Public API Surface

The header exposes initialization/teardown, cache-inode lookup/create/remove/truncate, cache load/write/wait, runtime free-space add/remove/query/allocation, cluster setup/allocation/return, discard trimming entry points, remapped block-group trimming, v1 activation toggling, and test-only insertion/query helpers.

## Inline Helpers

`btrfs_free_space_trimmed()` and `btrfs_free_space_trimming_bitmap()` classify trim state. `btrfs_trim_interrupted()` provides a common trim cancellation predicate using fatal signals and freezer state.

## Integration Notes

The header includes `fs.h` because `struct btrfs_free_cluster` and other Btrfs-wide types are part of the public free-space interface. Consumers must respect the locking documented implicitly by the implementation: most operations acquire internal locks, but cluster return/allocation and cache writeout participate in block-group and transaction locking.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/free-space-cache.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/free-space-tree.c -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/free-space-tree.c

## Purpose

Implements the on-disk free-space tree feature, which stores block-group free space in a B-tree rather than v1 cache inodes. It supports extent and bitmap item formats, conversion between them, free-space add/remove hooks, tree creation/deletion/rebuild, block-group add/remove records, loading into the runtime cache, and cleanup of orphaned free-space tree entries.

## On-Disk Model

Each block group has a `BTRFS_FREE_SPACE_INFO_KEY` item keyed by block-group start and length. Free ranges are represented either as `BTRFS_FREE_SPACE_EXTENT_KEY` items, where key objectid is start and key offset is length, or as `BTRFS_FREE_SPACE_BITMAP_KEY` items containing little-endian bitmaps. `BTRFS_FREE_SPACE_USING_BITMAPS` in the info item selects the representation for a block group.

`btrfs_free_space_root()` returns the free-space root. For extent tree v2 it uses `block_group->global_root_id` as the global root key offset; otherwise it uses the default free-space tree root.

## Format Switching

`btrfs_set_free_space_tree_thresholds()` computes high/low thresholds for converting between extents and bitmaps based on block-group length, sectorsize, and `BTRFS_FREE_SPACE_BITMAP_BITS`. `update_free_space_extent_count()` updates the info item extent count and triggers conversion:

- `btrfs_convert_free_space_to_bitmaps()` walks existing extent items backwards, builds a memory bitmap, deletes extents, marks the info item as bitmap-backed, validates the counted extents, and inserts bitmap items.
- `btrfs_convert_free_space_to_extents()` reads bitmap items into a memory bitmap, deletes bitmaps, clears the bitmap flag, emits extent keys for contiguous set bits, and validates the resulting extent count.

Memory bitmap allocation uses `memalloc_nofs_save()` around `kvzalloc()` because callers hold transactions and must avoid filesystem recursion.

## Add And Remove Paths

`btrfs_add_to_free_space_tree()` and `btrfs_remove_from_free_space_tree()` are feature-gated wrappers. They look up the containing block group, lock `block_group->free_space_lock`, ensure pending block groups have their initial free-space records, and dispatch to extent or bitmap implementations based on `using_bitmaps()`.

Extent mode:

- `add_free_space_extent()` merges immediate left/right neighbors and adjusts extent count.
- `remove_free_space_extent()` handles full deletion, trimming from front/back, and middle split cases.

Bitmap mode:

- `modify_free_space_bitmap()` finds affected bitmap items, sets or clears bits across bitmap boundaries, checks adjacent bits before/after the modified range, and computes the resulting extent-count delta.
- `free_space_modify_bits()`, `free_space_next_bitmap()`, and `btrfs_free_space_test_bit()` are the low-level bitmap cursor helpers.

Errors in these transactional paths generally abort the transaction because free-space tree mismatch would corrupt allocator metadata.

## Tree Lifecycle

`btrfs_create_free_space_tree()` creates the free-space tree root, marks the tree untrusted during construction, populates each block group by walking the extent tree, sets `FREE_SPACE_TREE` and `FREE_SPACE_TREE_VALID`, commits, and then clears the untrusted flag. `populate_free_space_tree()` adds the free-space info item and fills gaps between extent/metadata items found in the extent tree.

`btrfs_delete_free_space_tree()` clears feature flags, deletes all free-space tree items, deletes the root item, removes it from the global root tree, frees the root block, and commits.

`btrfs_rebuild_free_space_tree()` clears and repopulates an existing tree, allowing transaction restarts. New block groups created during rebuild are marked so the rebuild pass can skip already-added groups.

## Block-Group Hooks

`btrfs_add_block_group_free_space()` adds initial free-space records for new block groups if the feature is enabled. `__add_block_group_free_space()` handles `BLOCK_GROUP_FLAG_NEEDS_FREE_SPACE` and marks `BLOCK_GROUP_FLAG_FREE_SPACE_ADDED` to avoid rebuild duplication. `btrfs_remove_block_group_free_space()` walks backward through all free-space tree items for a block group and deletes info/extent/bitmap entries.

## Loading Runtime Cache

`btrfs_load_free_space_tree()` reads the info item using commit-root/no-lock path settings and then loads either extents or bitmaps into the in-memory block-group free-space cache with `btrfs_add_new_free_space()`. The bitmap loader reconstructs contiguous ranges by scanning sectorsize-granular bits and validates the reconstructed extent count. Both loaders periodically wake waiters after enough space is found.

## Orphan Cleanup

`btrfs_delete_orphan_free_space_entries()` removes entries before the first block group for non-extent-tree-v2 filesystems. This handles stale free-space tree entries that may predate the first valid block group. The helper starts a transaction, deletes leading items, and logs successful cleanup.

## Concurrency And Trust

The free-space tree is modified under transactions and `block_group->free_space_lock`. During creation/rebuild, `BTRFS_FS_CREATING_FREE_SPACE_TREE` and `BTRFS_FS_FREE_SPACE_TREE_UNTRUSTED` prevent consumers from trusting partially built data. Loading uses commit-root traversal to avoid deadlocks similar to block-group caching.

## Test Hooks

Several functions are exported under `CONFIG_BTRFS_FS_RUN_SANITY_TESTS`: add/remove internals, format conversion helpers, and bitmap bit testing. These provide direct coverage of format transitions and range modifications.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/free-space-tree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/free-space-tree.h -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/free-space-tree.h

## Purpose

Declares the public interface for the Btrfs free-space tree feature implemented in `free-space-tree.c`.

## Constants

`BTRFS_FREE_SPACE_BITMAP_SIZE` is 256 bytes for newly created bitmap items, and `BTRFS_FREE_SPACE_BITMAP_BITS` is the number of sectors represented by that default bitmap. The header notes that existing bitmap items may be smaller, especially the last bitmap in a block group.

## Public API Surface

The header exposes threshold calculation, free-space tree create/delete/rebuild, runtime loading, block-group add/remove hooks, transactional range add/remove hooks, orphan-entry cleanup, info-item lookup, and root lookup.

## Test-Only API

With Btrfs sanity tests enabled, the header exposes internal add/remove helpers, conversion helpers, and bitmap bit testing. This allows unit-style tests to exercise extent/bitmap tree behavior without going through all normal mount or allocation paths.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/free-space-tree.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/fs.c -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/fs.c

## Purpose

Provides core Btrfs filesystem helpers shared across the subsystem: checksum type metadata and dispatch, supported block-size validation, exclusive operation state transitions, and feature flag mutation helpers for incompat and compat-ro superblock flags.

## Checksum Helpers

`btrfs_csums[]` maps checksum type IDs to digest sizes and names. Public helpers return a checksum size/name/count and compute full or incremental checksums:

- `btrfs_csum()` computes CRC32C, xxhash64, SHA-256, or BLAKE2b in one call.
- `btrfs_csum_init()`, `btrfs_csum_update()`, and `btrfs_csum_final()` provide streaming checksum contexts.
- CRC32C uses Btrfs' inverted on-disk format; xxhash64 is little-endian; SHA-256 and BLAKE2b write raw digest bytes.

The code assumes checksum type validation happened at mount time and uses `BUG()` for impossible defaults.

## Block Size Validation

`btrfs_supported_blocksize()` accepts 4K, `PAGE_SIZE`, and `BTRFS_MIN_BLOCKSIZE`. Under `CONFIG_BTRFS_EXPERIMENTAL`, larger-than-page block sizes are allowed except for highmem configurations, where large folio content cannot always be accessed safely and several features are not large-folio ready.

## Exclusive Operations

`btrfs_exclop_start()`, `btrfs_exclop_start_try_lock()`, `btrfs_exclop_start_unlock()`, `btrfs_exclop_finish()`, and `btrfs_exclop_balance()` coordinate mutually exclusive operations such as balance, device add/remove, replace, resize, and swap activation. State is protected by `fs_info->super_lock`; completion notifies sysfs.

## Feature Flag Mutation

`__btrfs_set_fs_incompat()`, `__btrfs_clear_fs_incompat()`, `__btrfs_set_fs_compat_ro()`, and `__btrfs_clear_fs_compat_ro()` update superblock feature flags under `super_lock`, log transitions, and set `BTRFS_FS_FEATURE_CHANGED` so user-visible feature state can be refreshed. These helpers back macros in `fs.h`, including those used by free-space tree creation/deletion.

## Integration Notes

This file is infrastructure rather than free-space-specific, but it directly supports this group through checksum helpers, feature flag updates for `FREE_SPACE_TREE`/`FREE_SPACE_TREE_VALID`, mount/block-size constraints, and `btrfs_fs_info` state conventions declared in `fs.h`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/fs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/fs.h -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/fs.h

## Purpose

Defines central Btrfs filesystem-wide constants, feature/mount/state flags, major runtime structures, checksum interfaces, exclusive operation APIs, and common inline helpers. It is a foundational header used by the free-space cache/tree code and most Btrfs modules.

## Constants And Feature Masks

The header defines block-size limits, max extent size, max trim length, superblock location/size, metadata reservation formulas, checksum formatting, and common key formatting. It enumerates supported compat-ro and incompat feature masks, including `FREE_SPACE_TREE`, `FREE_SPACE_TREE_VALID`, `BLOCK_GROUP_TREE`, stable incompat features, and experimental features such as extent tree v2/remap/stripe tree when configured.

Mount option bits include space-cache and free-space-tree options (`SPACE_CACHE`, `CLEAR_CACHE`, `FREE_SPACE_TREE`, `NOSPACECACHE`) as well as discard, compression, degraded, ref-verify, checksum-ignore, and full-read-only options. `BTRFS_MOUNT_FULL_RO_MASK` identifies options that require no new transactions.

## Runtime State Flags

Two flag enums distinguish filesystem state and operational flags. Relevant free-space-related bits include `BTRFS_FS_CREATING_FREE_SPACE_TREE`, `BTRFS_FS_CLEANUP_SPACE_CACHE_V1`, `BTRFS_FS_FREE_SPACE_TREE_UNTRUSTED`, `BTRFS_FS_DISCARD_RUNNING`, `BTRFS_FS_FEATURE_CHANGED`, and zoned tracking flags. Shutdown and read-only helpers use `fs_state`.

## Major Structures

- `struct btrfs_dev_replace`: tracks device replacement state, cursors, errors, scrub progress, synchronization, and worker task.
- `struct btrfs_free_cluster`: holds allocation-cluster rbtrees, max size/window start, fragmentation state, owning block group, and list hook. Free-space cache code fills and drains these clusters.
- `struct btrfs_discard_ctl`: manages async discard workqueues, discard lists, rate limits, max discard size, accounting, and saved discard bytes. Free-space trimming updates this.
- `struct btrfs_fs_info`: the central per-filesystem object, containing root pointers, global root registry, block-group tree, mapping tree, block reservations, transaction state, mount options, locks, worker pools, dirty/caching block-group lists, allocation clusters, discard control, qgroup state, zoned state, block size/checksum settings, exclusive operation state, and debugging fields.

## Inline Helpers

The header provides helpers for deriving `btrfs_fs_info` from folios/inodes, computing allocation GFP masks without filesystem recursion, reading/writing generation fields with `READ_ONCE`/`WRITE_ONCE`, checksum leaf calculations, metadata reservation sizing, zoned mode detection, max-extent counting, blocks per folio, mount option manipulation, feature flag macros, closing/cleaner/shutdown checks, emergency shutdown, and ordered-folio flag aliases.

## API Declarations

It declares checksum helpers from `fs.c`, exclusive operation helpers, ioctl path validation, supported block-size validation, feature flag mutation helpers, and test-only inode destruction support. `EXPORT_FOR_TESTS` resolves to either external or static visibility depending on sanity-test configuration.

## Integration Notes

For this group, `fs.h` supplies `struct btrfs_fs_info`, `struct btrfs_free_cluster`, `struct btrfs_discard_ctl`, mount option bits, feature flag macros, block-size fields, zoned detection, checksum context declarations, and filesystem state flags used by `free-space-cache.c` and `free-space-tree.c`. The locking fields in `btrfs_fs_info` define much of the surrounding concurrency contract.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/fs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/inode-item.c -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/inode-item.c

## Purpose

Implements helpers for Btrfs inode item lookup/creation, inode reference insertion/removal, extended inode references, and inode item truncation. In this group it matters because free-space cache v1 uses `btrfs_insert_empty_inode()` to create cache inodes and `btrfs_truncate_inode_items()` to truncate cache inode extents.

## Inode Reference Helpers

`btrfs_find_name_in_backref()` scans packed `BTRFS_INODE_REF_KEY` subrecords in an item and matches by name. `btrfs_find_name_in_ext_backref()` scans `BTRFS_INODE_EXTREF_KEY` records and matches by parent objectid plus name. `btrfs_lookup_inode_extref()` searches the hashed extended-ref key and returns the matching extref record if present.

`btrfs_insert_inode_ref()` inserts a normal inode ref, extends an existing packed item if needed, detects duplicate names, and falls back to `btrfs_insert_inode_extref()` when the normal item overflows and the `EXTENDED_IREF` incompat feature is enabled. `btrfs_del_inode_ref()` removes a normal ref by compacting or deleting the item and falls back to `btrfs_del_inode_extref()` if the normal ref is missing.

## Inode Item Helpers

`btrfs_insert_empty_inode()` inserts an empty `BTRFS_INODE_ITEM_KEY` for a given objectid. `btrfs_lookup_inode()` searches for an inode/root item and includes special handling for root-item lookups with offset `-1`, where the preceding matching root item may satisfy the lookup.

## Truncation Algorithm

`btrfs_truncate_inode_items()` removes all items for an inode at or above `control->min_type`, and for file extents removes or shrinks extents at/after `control->new_size`. It walks backward from the highest key for the inode, batches adjacent deletions, updates `control->last_size`, `control->sub_bytes`, and `control->extents_found`, and can return `BTRFS_NEED_TRUNCATE_BLOCK` for inline extents that cannot be partially truncated due to compression/encryption/encoding.

For regular extents it may shrink the extent item, clear in-memory file extent ranges when requested, and drop delayed extent refs with `btrfs_free_extent()` unless `skip_ref_updates` is set. For shareable roots it periodically backs off with `-EAGAIN` when transactions should end or delayed-ref reservations need refill.

## Error Handling And Transactions

Most modifying paths use COW-capable `btrfs_search_slot()` and abort the transaction on unexpected metadata inconsistency or delayed-ref/free-extent errors. Path allocation failure returns `-ENOMEM`; missing refs generally return `-ENOENT`; normal-ref overflow can become `-EMLINK` or extended-ref insertion.

## Integration Notes

This file depends on ctree/search primitives, extent-buffer accessors, transactions, delayed refs, extent-tree freeing, file extent accessors, and tracing. The free-space cache truncate path constructs a `btrfs_truncate_control` with `min_type = BTRFS_EXTENT_DATA_KEY`, `new_size = 0`, and `clear_extent_range = true` to remove cache inode file extents safely.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/inode-item.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/inode-item.h -->
# File Research: sources/os/linux/linux-stable/fs/btrfs/inode-item.h

## Purpose

Declares inode-item and inode-reference helper APIs implemented by `inode-item.c`, plus the truncate-control structure used by generic inode truncation callers including the free-space cache code.

## Key Definitions

`BTRFS_NEED_TRUNCATE_BLOCK` is a positive return value indicating the caller must truncate the last block separately. `struct btrfs_truncate_control` carries truncate inputs (`inode`, `new_size`, `ino`, `min_type`, `skip_ref_updates`, `clear_extent_range`) and outputs (`extents_found`, `last_size`, `sub_bytes`).

## Inline Helpers

`btrfs_inode_combine_flags()` and `btrfs_inode_split_flags()` convert between on-disk 64-bit inode flags and in-memory writable/read-only flag halves. `btrfs_extref_hash()` computes the key offset for extended inode refs using CRC32C over parent objectid and name.

## Public API Surface

The header declares truncate, inode-ref insert/delete, empty inode insertion, inode lookup, extended-ref lookup, and name-search helpers for normal and extended backrefs.

## Integration Notes

The free-space cache code uses this interface when creating hidden cache inodes and when truncating cache inode file extent items. Other Btrfs directories/inode code use the same helpers for link count/reference management and file truncation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/btrfs/inode-item.h -->
