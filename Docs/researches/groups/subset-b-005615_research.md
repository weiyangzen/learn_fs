# subset-b-005615 Research

Grouped source research for Btrfs free-space cache v1, free-space tree persistence, filesystem-global state helpers, and inode item/back-reference helpers. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/free-space-cache.c -->
# sources/distributed-fs/ceph-client/fs/btrfs/free-space-cache.c

## Purpose

`sources/distributed-fs/ceph-client/fs/btrfs/free-space-cache.c` implements Btrfs' in-memory free-space cache for block groups, the legacy on-disk free-space cache v1 inode format, allocation/clustering helpers used by `find_free_extent()`, and discard/trim accounting for non-zoned block groups. It also contains the zoned block-group free-space accounting path, cache v1 activation cleanup, slab cache initialization, and sanity-test-only insertion/existence helpers. The file was read as a complete 4388-line implementation.

## Important APIs, Types, and Functions

Key exported entry points are `lookup_free_space_inode`, `create_free_space_inode`, `btrfs_remove_free_space_inode`, `btrfs_truncate_free_space_cache`, `load_free_space_cache`, `btrfs_wait_cache_io`, `btrfs_write_out_cache`, `btrfs_init_free_space_ctl`, `btrfs_add_free_space`, `btrfs_add_free_space_unused`, `btrfs_add_free_space_async_trimmed`, `btrfs_remove_free_space`, `btrfs_find_space_for_alloc`, `btrfs_find_space_cluster`, `btrfs_alloc_from_cluster`, `btrfs_return_cluster_to_free_space`, `btrfs_trim_block_group`, `btrfs_trim_block_group_extents`, `btrfs_trim_block_group_bitmaps`, `btrfs_trim_fully_remapped_block_group`, `btrfs_free_space_cache_v1_active`, `btrfs_set_free_space_cache_v1_active`, `btrfs_free_space_init`, and `btrfs_free_space_exit`.

Important internal helpers include the `btrfs_io_ctl` cache-file page/CRC/generation helpers, `link_free_space` and `unlink_free_space`, `tree_search_offset`, `find_free_space`, bitmap mutators such as `bitmap_clear_bits`, `btrfs_bitmap_set_bits`, `search_bitmap`, `insert_into_bitmap`, `remove_from_bitmap`, extent/bitmap stealing helpers, cluster setup helpers, and trim helpers `trim_no_bitmap`, `trim_bitmaps`, `do_trimming`, `reset_trimming_bitmap`, and `end_trimming_bitmap`. The local `struct btrfs_trim_range` records ranges temporarily removed from the free-space rb-tree while a discard is in progress so cache writeout does not lose them.

## Control Flow

Free-space cache v1 load starts in `load_free_space_cache()`. It rejects non-written cache states, looks up the per-block-group cache inode through the tree root commit root, reads the free-space header, validates inode generation, page CRCs, and cache generation through `io_ctl_*`, loads entries into a temporary `btrfs_free_space_ctl`, then copies validated extents/bitmap regions into the real block-group control only if the byte count matches block-group accounting. Any mismatch clears the disk cache state so normal block-group caching rebuilds the information.

Cache v1 writeout starts in `btrfs_write_out_cache()`, which looks up the cache inode and calls `__btrfs_write_out_cache()`. The write path locks cache-file pages, stores the transaction generation in page 0, writes extent entries from both the block-group free-space rb-tree and any active cluster, includes pinned extents from the current transaction, serializes bitmap pages after extent records, CRCs each page, dirties the cache inode pages, starts writeback, and later `btrfs_wait_cache_io()` flushes ordered IO and updates the free-space header with entry counts, bitmap counts, and generation. Failed IO invalidates cache pages, zeroes the inode generation, and moves the block group to `BTRFS_DC_ERROR`.

The allocation path uses a dual index: `free_space_offset` ordered by offset and `free_space_bytes` cached by largest available entry. `btrfs_find_space_for_alloc()` calls `find_free_space()` to locate an extent or bitmap entry satisfying size, alignment, and empty-size requirements, removes the selected bytes, updates discardable statistics, and returns alignment gaps back to the free-space cache. Metadata/data clustering goes through `btrfs_find_space_cluster()` and then `btrfs_alloc_from_cluster()`, moving suitable extent or bitmap entries from the block-group cache into a `btrfs_free_cluster` rb-tree and allocating from that cluster until exhausted.

Freeing paths add ranges through `__btrfs_add_free_space()`, optionally merge adjacent extents according to trim-state rules, decide whether to represent small/fragmented ranges as bitmaps, steal adjacent bitmap ranges back into extents when it improves allocation shape, update discard filters, and queue async discard work for untrimmed space. Removal paths split or consume extent entries, clear bitmap bits, free empty bitmap entries, and update the global free-space and discard counters.

Trimming paths freeze the block group, remove candidate free ranges from the cache under `cache_writeout_mutex`, add the temporary range to `trimming_ranges`, issue `btrfs_discard_extent()`, and restore the region with `TRIMMED` or `UNTRIMMED` state depending on the result. `trim_no_bitmap()` handles extent entries and `trim_bitmaps()` handles bitmap entries with lossy bitmap trim-state tracking. Async discard trims one qualifying region per pass.

Zoned block groups bypass the rb-tree/bitmap allocator. `__btrfs_add_free_space_zoned()` updates `ctl->free_space`, `alloc_offset`, `zone_unusable`, unused/reclaim lists, and reclaim thresholds according to zone capacity and allocation pointer rules.

## State and Persistence Behavior

The primary runtime state is `struct btrfs_free_space_ctl`: a spinlock-protected offset rb-tree, a cached bytes rb-tree, free byte/extent/bitmap counters, bitmap conversion thresholds, discardable byte/extent counters, the block-group start/unit, the owning block group, a cache writeout mutex, and `trimming_ranges`. Each `struct btrfs_free_space` represents either an extent (`bitmap == NULL`) or one bitmap page worth of sectors; it carries offset, bytes, cached max extent size, bitmap extent count, list linkage, and trim state.

On-disk cache v1 state is stored in one hidden inode per block group plus a `BTRFS_FREE_SPACE_OBJECTID` header item in the tree root. The cache inode is NOCOW, NODATASUM, NOCOMPRESS, and PREALLOC; it persists serialized free-space entry records, bitmap pages, page CRCs in page 0, and a transaction generation. The superblock cache generation records whether v1 is active. `btrfs_set_free_space_cache_v1_active(false)` starts a transaction, marks cleanup, removes all cache inodes, commits, and clears the cleanup flag.

Trim state is intentionally coarser for bitmaps than extents: adding untrimmed bytes to a trimmed bitmap marks the whole bitmap untrimmed, and async bitmap trimming can mark a whole bitmap trimmed once skipped fragments are below the async filter. This trades precision for reduced repeated discard work.

## Dependencies and Integration Points

The file integrates with extent-tree allocation, block-group lifecycle, transactions, root-tree items, inode truncation, page cache writeback, subpage extent mapping, file extent helpers, discard workqueues, relocation/remapping, and mount options. Direct includes include `extent-tree.h`, `fs.h`, `free-space-cache.h`, `transaction.h`, `disk-io.h`, `extent_io.h`, `space-info.h`, `block-group.h`, `discard.h`, `subpage.h`, `inode-item.h`, `accessors.h`, `file-item.h`, `file.h`, `super.h`, and `relocation.h`. It is called by block-group caching, allocation, free/pin/unpin, transaction commit, discard/trim ioctls, and mount/remount handling.

## Risks and Edge Cases

The cache v1 format is fragile: stale generation, CRC mismatch, duplicate entries, wrong free-space totals, or page truncation must force rebuild rather than trusting disk state. Writeout races with concurrent trimming are mitigated by `cache_writeout_mutex` and `trimming_ranges`; mistakes there can leak free space across remounts. Bitmap and extent entries can share offsets, so search and insertion ordering must preserve the faster extent-first behavior. Discard accounting depends on trim-state transitions and can overcount or undercount if bitmap extent deltas are wrong. Cluster movement removes entries from the main rb-tree but keeps global counters meaningful, making lock ordering between `ctl->tree_lock` and `cluster->lock` important. Zoned block groups have separate allocation-pointer semantics, so using generic rb-tree removal there would be wrong. Several corruption paths abort transactions or warn under `DEBUG_WARN`; tests need to exercise both normal and intentionally inconsistent states.

## Test Signals

Useful signals are Btrfs free-space-cache sanity tests under `CONFIG_BTRFS_FS_RUN_SANITY_TESTS`, allocation stress with fragmented free space, xfstests that mount with `space_cache=v1`, clear cache, remount after crash/powercut injection, and compare free-space totals with block-group accounting. Additional coverage should include CRC/generation mismatch rebuilds, duplicate cache entry rejection, cache writeout ENOSPC/error injection through `io_ctl_init`, concurrent discard/writeout, sync and async trim of extents and bitmaps, cluster allocation/return paths, zoned block-group free/unusable accounting, and remapped block-group trim completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/free-space-cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/free-space-cache.h -->
# sources/distributed-fs/ceph-client/fs/btrfs/free-space-cache.h

## Purpose

`sources/distributed-fs/ceph-client/fs/btrfs/free-space-cache.h` declares the in-memory free-space cache data structures and public APIs used by Btrfs block-group allocation, cache v1 persistence, clustering, and discard/trim handling. It is the contract between `free-space-cache.c` and block-group, extent-tree, transaction, discard, and sanity-test code. The file was read as a complete 180-line header.

## Important APIs, Types, and Functions

The header defines `enum btrfs_trim_state` with `UNTRIMMED`, `TRIMMED`, and special bitmap-only `TRIMMING` states. `struct btrfs_free_space` is the node stored in offset and bytes rb-trees and represents either a plain free extent or a bitmap-backed region. `struct btrfs_free_space_ctl` owns the rb-trees, counters, bitmap thresholds, discardable statistics, block-group pointer, writeout mutex, and active trimming ranges. `struct btrfs_free_space_op` supplies the `use_bitmap()` policy callback. `struct btrfs_io_ctl` carries cache v1 inode page state for serialization and validation.

Exported functions cover slab lifecycle, cache inode lookup/create/remove/truncate, cache v1 load/write/wait, free-space ctl initialization, add/remove free ranges, free-space cache teardown, trim-state checks, allocator search, diagnostic dumping, cluster setup/allocation/return, trim operations for whole block groups/extents/bitmaps, fully remapped block-group trim, cache v1 active state changes, and sanity-test helpers.

## Control Flow

This header does not implement complex runtime flow, but it exposes the entry points used in the normal sequence: initialize per-block-group `btrfs_free_space_ctl`, load cache v1 or rebuild free space, add/remove free ranges as extents are allocated and freed, optionally form and consume clusters, write cache v1 during transaction commit, and trim or discard untrimmed free ranges. Inline helpers provide cheap trim-state checks and signal/freezer interruption detection for trim loops.

## State and Persistence Behavior

The state declared here is runtime state except for `btrfs_io_ctl`, which describes the transient page cursor used to persist or reload the v1 free-space cache inode. `discardable_extents` and `discardable_bytes` are arrays indexed by `BTRFS_STAT_CURR` and `BTRFS_STAT_PREV` so callers can publish delta-style discard statistics. The cache v1 persistence APIs manipulate hidden free-space inodes and their tree-root header items, while the rb-tree/bitmap structures themselves are in-memory caches.

## Dependencies and Integration Points

The header includes Linux rb-tree, list, spinlock, mutex, freezer, and `fs.h` definitions. It forward declares inode, page, path, transaction, block-group trim, and fs_info types to avoid over-including allocator internals. Integration points are block-group allocation, transaction commit, the discard controller, free-space cache v1 mount options, the Btrfs trim ioctl path, and optional sanity tests.

## Risks and Edge Cases

Callers must hold the correct locks around `btrfs_free_space_ctl` and cluster mutation; the header exposes structures with many counters that can drift if updates skip the implementation helpers. `BTRFS_TRIM_STATE_TRIMMING` is meaningful only for bitmap trim progression, so treating it like a durable trimmed state would lose discard work. The `btrfs_io_ctl` page array and cursor fields are tightly coupled to the v1 on-disk format and should not be reused generically.

## Test Signals

Compile coverage should validate all prototypes against their definitions and include-order use from block-group, extent-tree, discard, and tests. Runtime signals come from free-space cache sanity tests, allocation/free round trips, trim interruption tests using fatal signal or freezer paths, and mount tests that enable, disable, clear, and rewrite cache v1.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/free-space-cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/free-space-tree.c -->
# sources/distributed-fs/ceph-client/fs/btrfs/free-space-tree.c

## Purpose

`sources/distributed-fs/ceph-client/fs/btrfs/free-space-tree.c` implements the persistent Btrfs free-space tree. It stores per-block-group free-space metadata as `BTRFS_FREE_SPACE_INFO_KEY` plus either free-space extent items or free-space bitmap items, supports converting between extents and bitmaps based on fragmentation thresholds, maintains the tree as extents are allocated/freed, creates/deletes/rebuilds the tree, and loads it into the in-memory block-group cache. The file was read as a complete 1825-line implementation.

## Important APIs, Types, and Functions

Exported entry points include `btrfs_free_space_root`, `btrfs_set_free_space_tree_thresholds`, `btrfs_search_free_space_info`, `btrfs_create_free_space_tree`, `btrfs_delete_free_space_tree`, `btrfs_rebuild_free_space_tree`, `btrfs_add_block_group_free_space`, `btrfs_remove_block_group_free_space`, `btrfs_add_to_free_space_tree`, `btrfs_remove_from_free_space_tree`, `btrfs_load_free_space_tree`, and `btrfs_delete_orphan_free_space_entries`. Under sanity tests it also exports `__btrfs_add_to_free_space_tree`, `__btrfs_remove_from_free_space_tree`, bitmap/extent conversion functions, and `btrfs_free_space_test_bit`.

Important internal helpers are `add_new_free_space_info`, `btrfs_search_prev_slot`, `free_space_bitmap_size`, `alloc_bitmap`, `le_bitmap_set`, `update_free_space_extent_count`, `free_space_modify_bits`, `free_space_next_bitmap`, `modify_free_space_bitmap`, `add_free_space_extent`, `remove_free_space_extent`, `using_bitmaps`, `populate_free_space_tree`, `clear_free_space_tree`, `__add_block_group_free_space`, `load_free_space_bitmaps`, `load_free_space_extents`, and `delete_orphan_free_space_entries`.

## Control Flow

Creation begins in `btrfs_create_free_space_tree()`: start a transaction, set `BTRFS_FS_CREATING_FREE_SPACE_TREE` and `BTRFS_FS_FREE_SPACE_TREE_UNTRUSTED`, create and register the free-space root, walk every block group, and call `populate_free_space_tree()`. Population inserts a free-space info item, scans the extent root for allocated extent/metadata items within the block group, and inserts free-space ranges between allocated regions through `__btrfs_add_to_free_space_tree()`. After all block groups are populated, it sets `FREE_SPACE_TREE` and `FREE_SPACE_TREE_VALID` compat-ro flags, commits, and clears the untrusted bit.

Normal updates are guarded by the compat-ro feature flag. `btrfs_add_to_free_space_tree()` and `btrfs_remove_from_free_space_tree()` look up the owning block group, take `block_group->free_space_lock`, ensure pending new block-group free-space items exist through `__add_block_group_free_space()`, choose extent or bitmap representation through `using_bitmaps()`, then either merge/split extent items or set/clear bits in bitmap items. Both wrappers abort the transaction on update failure.

Extent representation uses one key per contiguous free range. Adding free space searches left and right neighbors, deletes adjacent items when needed, inserts the merged item, and updates the extent count. Removing free space finds the containing extent, deletes it, reinserts left/right leftovers, and updates the count. Bitmap representation modifies bits across one or more bitmap items and computes the extent-count delta from the immediate neighboring bits around the modified range.

Representation conversion is automatic in `update_free_space_extent_count()`. If extent count exceeds the high threshold, `btrfs_convert_free_space_to_bitmaps()` walks extent items backwards, builds an in-memory little-endian bitmap, deletes extents, sets `BTRFS_FREE_SPACE_USING_BITMAPS`, and writes bitmap items. If the count falls below the low threshold, `btrfs_convert_free_space_to_extents()` reads bitmap items, deletes them, clears the bitmap flag, and reinserts extent keys for contiguous set-bit runs.

Loading starts in `btrfs_load_free_space_tree()`. It searches the commit root without locking, reads the free-space info item count and flags, then calls either `load_free_space_extents()` or `load_free_space_bitmaps()` to add ranges to the runtime block-group cache using `btrfs_add_new_free_space()`. Both loaders validate counted extents against the persisted expected count and wake the caching control waitqueue after enough free space has been discovered.

Deletion and rebuild are explicit lifecycle operations. `btrfs_delete_free_space_tree()` clears feature flags, deletes all tree items, deletes the root item, unregisters the global root, frees the root node, and commits. `btrfs_rebuild_free_space_tree()` clears existing items, repopulates from block groups over one or more transactions, skips block groups already added while rebuilding, restores feature flags, commits, and clears the untrusted flag. Orphan cleanup removes free-space tree entries before the first block group for non-extent-tree-v2 filesystems.

## State and Persistence Behavior

Persistent state lives in the free-space tree root selected by `btrfs_free_space_root()`. With extent tree v2, the root key offset uses `block_group->global_root_id`; otherwise the single global free-space tree root is used. Each block group has an info item keyed by block-group start and length, storing extent count and flags. Data entries are either extent keys with offset as length and no payload, or bitmap keys with payload bytes sized by sectors represented. Block-group runtime fields cache the bitmap mode and thresholds: `bitmap_high_thresh`, `bitmap_low_thresh`, `using_free_space_bitmaps`, and `using_free_space_bitmaps_cached`.

Feature flags `FREE_SPACE_TREE` and `FREE_SPACE_TREE_VALID` determine whether the tree is active and trusted. During create/rebuild, `BTRFS_FS_FREE_SPACE_TREE_UNTRUSTED` prevents trusting commit-root free-space data until a successful commit. `BLOCK_GROUP_FLAG_NEEDS_FREE_SPACE` and `BLOCK_GROUP_FLAG_FREE_SPACE_ADDED` coordinate new block groups and rebuild transactions.

## Dependencies and Integration Points

The file integrates with Btrfs btree item accessors, global roots, transactions, extent roots, block-group cache trees, the runtime free-space cache loader, and mount feature flags. Direct includes are `messages.h`, `ctree.h`, `disk-io.h`, `locking.h`, `free-space-tree.h`, `transaction.h`, `block-group.h`, `fs.h`, `accessors.h`, `extent-tree.h`, and `root-tree.h`. It is called from extent allocation/free hooks, block-group creation/removal, mount-time block-group caching, and feature conversion/remount paths.

## Risks and Edge Cases

Extent count is the main consistency guard: conversion, loading, add, and remove paths all depend on maintaining accurate deltas when ranges merge or split. Bitmap conversion uses little-endian bit layout and sector-size granularity, so size and alignment bugs can corrupt free-space meaning. `btrfs_search_prev_slot()` intentionally expects no exact key match; callers depend on specific key ordering and can return `-EIO` on surprising tree shapes. Rebuild can allocate new block groups while modifying the free-space tree; `BLOCK_GROUP_FLAG_FREE_SPACE_ADDED` avoids duplicate population. The untrusted flag must be cleared only after commit, otherwise mount-time caching could rely on an incomplete tree. Extent tree v2 uses per-global-root lookup and skips orphan cleanup because a single global scan would be ambiguous.

## Test Signals

Coverage should include xfstests with `space_cache=v2`/free-space-tree enabled, online conversion between extent and bitmap forms, block-group create/delete while the tree is active, rebuild after marking the tree untrusted, mount/load verification after crash injection, and fsck/btrfs-check cross-validation of free-space totals. Sanity tests should directly cover `__btrfs_add_to_free_space_tree`, `__btrfs_remove_from_free_space_tree`, extent-to-bitmap and bitmap-to-extent conversion thresholds, bit tests at bitmap boundaries, orphan entry deletion, extent tree v2 root selection, and transaction abort behavior on corrupted key types or count mismatches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/free-space-tree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/free-space-tree.h -->
# sources/distributed-fs/ceph-client/fs/btrfs/free-space-tree.h

## Purpose

`sources/distributed-fs/ceph-client/fs/btrfs/free-space-tree.h` declares the public interface and bitmap sizing constants for the Btrfs persistent free-space tree. It is consumed by extent allocation/free paths, block-group lifecycle code, mount-time cache loading, and feature-management paths. The file was read as a complete 62-line header.

## Important APIs, Types, and Functions

The header defines `BTRFS_FREE_SPACE_BITMAP_SIZE` as the default 256-byte bitmap payload size and `BTRFS_FREE_SPACE_BITMAP_BITS` as its bit capacity. Public APIs declare threshold calculation, create/delete/rebuild lifecycle operations, free-space tree loading, block-group add/remove hooks, range add/remove hooks, orphan cleanup, free-space info search, and root selection. Under `CONFIG_BTRFS_FS_RUN_SANITY_TESTS`, it exposes internal add/remove and conversion helpers plus `btrfs_free_space_test_bit`.

## Control Flow

The header shapes three flows: feature lifecycle (`btrfs_create_free_space_tree`, `btrfs_delete_free_space_tree`, `btrfs_rebuild_free_space_tree`), normal transaction updates (`btrfs_add_to_free_space_tree`, `btrfs_remove_from_free_space_tree`, block-group add/remove hooks), and mount-time load (`btrfs_load_free_space_tree`). `btrfs_search_free_space_info()` and `btrfs_free_space_root()` are utility entry points shared across those flows.

## State and Persistence Behavior

The constants define the default granularity for newly created bitmap items, but callers must not assume every existing bitmap has that exact size because the last bitmap in a block group can be truncated. The persisted state itself is held in free-space tree btree items, not in this header. The APIs take transaction handles and paths where mutation or COW may be required.

## Dependencies and Integration Points

The header includes `linux/bits.h` for bit sizing and forward declares `btrfs_caching_control`, `btrfs_fs_info`, `btrfs_path`, `btrfs_block_group`, and `btrfs_trans_handle`. Integration points are block-group threshold setup, transaction-time extent accounting, free-space tree feature toggles, and sanity tests that need internal conversion behavior.

## Risks and Edge Cases

The bitmap size constants are defaults rather than universal invariants; code that assumes fixed bitmap item size would mishandle truncated tail bitmaps. The add/remove APIs are no-ops when the compat-ro feature is not active, so callers must not assume persistent free-space-tree state exists on every filesystem. Sanity-test exports expose internals and should not become de facto production APIs.

## Test Signals

Compile coverage should validate declarations against `free-space-tree.c` and call sites. Runtime tests should cover feature enable/disable/rebuild, threshold conversion, truncated final bitmap items, and sanity-test helpers when `CONFIG_BTRFS_FS_RUN_SANITY_TESTS` is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/free-space-tree.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/fs.c -->
# sources/distributed-fs/ceph-client/fs/btrfs/fs.c

## Purpose

`sources/distributed-fs/ceph-client/fs/btrfs/fs.c` implements core filesystem-wide helpers declared in `fs.h`: checksum algorithm metadata and one-shot/incremental checksum operations, supported block-size validation, exclusive operation state transitions, and superblock feature flag setters/clearers. The file was read as a complete 347-line implementation.

## Important APIs, Types, and Functions

The checksum table `btrfs_csums[]` maps Btrfs checksum type IDs to digest size and display name for CRC32C, xxhash64, SHA-256, and BLAKE2b. Exported checksum helpers are `btrfs_csum_type_size`, `btrfs_super_csum_size`, `btrfs_super_csum_name`, `btrfs_get_num_csums`, `btrfs_csum`, `btrfs_csum_init`, `btrfs_csum_update`, and `btrfs_csum_final`.

Other exported helpers are `btrfs_supported_blocksize`, `btrfs_exclop_start`, `btrfs_exclop_start_try_lock`, `btrfs_exclop_start_unlock`, `btrfs_exclop_finish`, `btrfs_exclop_balance`, `__btrfs_set_fs_incompat`, `__btrfs_clear_fs_incompat`, `__btrfs_set_fs_compat_ro`, and `__btrfs_clear_fs_compat_ro`.

## Control Flow

Checksum control flow is switch-based on the already-validated checksum type. One-shot `btrfs_csum()` writes the digest directly to the caller's output buffer in the correct little-endian form for integer digests. Incremental hashing initializes a `btrfs_csum_ctx`, updates the algorithm-specific context, then finalizes to the output buffer. Invalid types hit `BUG()` because mount-time validation is expected to have rejected them.

`btrfs_supported_blocksize()` asserts power-of-two bounds, accepts `PAGE_SIZE`, 4 KiB, and `BTRFS_MIN_BLOCKSIZE`, and under experimental support may accept block sizes larger than page size unless highmem makes that unsafe. Exclusive-operation control uses `fs_info->super_lock` to serialize `exclusive_operation`: start succeeds only from `BTRFS_EXCLOP_NONE`, try-lock allows same-operation reentry or paused-balance plus device-add compatibility, finish resets to none and notifies sysfs, and balance helper transitions between balance and paused states.

Feature flag setters/clearers read the superblock copy, double-check under `super_lock`, update incompat or compat-ro flags, log the change, and set `BTRFS_FS_FEATURE_CHANGED` so sysfs/commit paths can observe changed feature state.

## State and Persistence Behavior

Checksum helpers are stateless except for caller-owned `struct btrfs_csum_ctx`. Exclusive operation state is stored in memory in `fs_info->exclusive_operation` and protected by `super_lock`; it is exported through sysfs notification but is not on-disk state. Feature helpers mutate `fs_info->super_copy` feature bits, which later become persistent through normal superblock commit/write paths. They intentionally do not clear the `BTRFS_FS_FEATURE_CHANGED` bit.

## Dependencies and Integration Points

The file depends on Linux crypto helpers for CRC32C, xxhash, SHA-256, and BLAKE2b through headers included by `fs.h`, plus `messages.h`, `accessors.h`, and `volumes.h`. Checksum helpers are used by metadata/data checksum verification and superblock handling. Exclusive-operation helpers coordinate balance, device add/remove, replace, resize, and swap activation. Feature helpers are used by code that enables/disables format features such as free-space tree and extended inode refs.

## Risks and Edge Cases

Checksum type bounds are trusted after mount validation; any caller passing an unchecked type can trigger `BUG()`. The CRC32C path uses inverted seed/finalization and little-endian storage, so it must remain consistent with on-disk format expectations. Experimental block-size support deliberately rejects highmem larger-than-page cases because not all features implement page-by-page handling. Exclusive-operation callers must pair start/try-lock with unlock/finish exactly; missing finish can block later operations. Feature helpers update only the in-memory super copy and rely on transaction/superblock writeback to persist the change.

## Test Signals

Useful tests include checksum known-answer tests for all supported algorithms, incremental versus one-shot digest equivalence, mount validation of checksum types, supported block-size matrix tests across debug/experimental/highmem configurations, sysfs-visible exclusive-operation transitions during balance/device operations, and feature flag persistence after transactions that enable or clear compat-ro/incompat features.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/fs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/fs.h -->
# sources/distributed-fs/ceph-client/fs/btrfs/fs.h

## Purpose

`sources/distributed-fs/ceph-client/fs/btrfs/fs.h` is a central Btrfs filesystem state header. It defines block-size and extent-size constants, format feature support masks, mount option bits, filesystem runtime flags, exclusive operation types, major runtime structures such as `struct btrfs_fs_info`, `struct btrfs_free_cluster`, discard/device-replace/commit/delayed-root state, and inline helpers for metadata sizing, generation accessors, mount options, shutdown, and test-only behavior. The file was read as a complete 1238-line header.

## Important APIs, Types, and Functions

Important constants include `BTRFS_MIN_BLOCKSIZE`, `BTRFS_MAX_BLOCKSIZE`, `BTRFS_MAX_EXTENT_SIZE`, `BTRFS_MAX_TRIM_LENGTH`, `BTRFS_SUPER_INFO_OFFSET`, `BTRFS_SUPER_INFO_SIZE`, `BTRFS_DIRTY_METADATA_THRESH`, feature support/safe-set masks, `BTRFS_DEFAULT_COMMIT_INTERVAL`, and `BTRFS_DEFAULT_MAX_INLINE`. It defines runtime filesystem state enums (`BTRFS_FS_STATE_*`), `fs_info->flags` bits such as `BTRFS_FS_CREATING_FREE_SPACE_TREE`, `BTRFS_FS_FREE_SPACE_TREE_UNTRUSTED`, `BTRFS_FS_CLEANUP_SPACE_CACHE_V1`, and mount option bits such as `BTRFS_MOUNT_SPACE_CACHE`, `BTRFS_MOUNT_FREE_SPACE_TREE`, `BTRFS_MOUNT_DISCARD_SYNC`, and `BTRFS_MOUNT_DISCARD_ASYNC`.

Major structures are `struct btrfs_dev_replace`, `struct btrfs_free_cluster`, `struct btrfs_discard_ctl`, `enum btrfs_exclusive_operation`, `struct btrfs_commit_stats`, `struct btrfs_delayed_root`, and the large `struct btrfs_fs_info`. Inline/function declarations include folio/inode/fs_info conversion helpers, `btrfs_alloc_write_mask`, `btrfs_min_folio_size`, generation and root-drop accessors, checksum leaf calculation, metadata reservation calculators, zoned-mode detection, max-extent counting, blocks-per-folio calculation, exclusive operation APIs, checksum APIs, feature flag APIs/macros, mount-option macros, cleaner/sleep checks, shutdown forcing, ordered-folio flag aliases, and sanity-test-only exports.

## Control Flow

This header mostly defines data and inline helpers. Typical control flow shaped by it starts at mount: supported feature masks validate superblock flags, mount options populate `fs_info->mount_opt`, block sizes and checksum fields are cached, and `struct btrfs_fs_info` owns roots, locks, counters, workers, reservations, block groups, discard control, quota state, zoned state, and error state. Runtime code then uses `btrfs_test_opt()` and flag bits to branch into feature-specific behavior such as free-space tree loading, cache v1 cleanup, async discard, zoned allocation, qgroups, relocation, and tree-mod-log use.

The inline generation accessors centralize `READ_ONCE`/`WRITE_ONCE` use for transaction generation fields. Metadata reservation helpers compute worst-case node COW costs for insertion and modification. Shutdown helper `btrfs_force_shutdown()` writes `fs_error`, sets emergency shutdown once, logs a critical message, and reports filesystem shutdown. Mount option and feature macros wrap raw bit operations so call sites can use symbolic feature names.

## State and Persistence Behavior

`struct btrfs_fs_info` is the in-memory root of mounted filesystem state. It holds persistent-format mirrors such as `super_copy`, `super_for_commit`, feature bits, checksum type/size, block sizes, generation counters, roots, block-group cache tree, mapping tree, global roots, free chunk space, reservations, transaction pointers, workqueues, device replacement state, discard control, quotas, tree-mod-log state, zoned state, commit stats, and error/shutdown flags. Some fields are persisted indirectly through superblock or btree commits; many are runtime-only synchronization and accounting fields.

The header documents lock expectations for several fields: generation under transaction locking, `last_trans_committed` through accessors, feature flags under `super_lock`, block-group cache under `block_group_cache_lock`, mapping tree under `mapping_tree_lock`, delayed roots under their lock, and exclusive operations under `super_lock`. Mount and feature masks encode on-disk compatibility rules and determine which unknown feature combinations can be mounted.

## Dependencies and Integration Points

The header depends on crypto, block device, memory sizing, time, atomics, percpu counters, completion, lockdep, spinlocks, mutexes, rwsems, lists, pagemap, radix tree, workqueues, wait queues, scheduler, rbtrees, xxhash, filesystem error reporting, Btrfs uapi tree definitions, and local headers `extent-io-tree.h`, `async-thread.h`, `block-rsv.h`, and `messages.h`. Nearly every Btrfs subsystem integrates with it: transactions, roots, extent allocation, free-space cache/tree, scrub, balance, relocation, qgroups, device replacement, discard, zoned mode, compression, delayed refs/items, tree log, sysfs, and tests.

## Risks and Edge Cases

Because this is a central shared contract, field layout and semantic changes have broad blast radius. Feature support masks must stay synchronized with mount validation and btrfs-progs expectations. Mount-option bits must be reflected in option display/parsing code. Locking comments are important; bypassing accessors or using fields under the wrong lock can introduce races. Some values differ under `CONFIG_BTRFS_DEBUG`, `CONFIG_BTRFS_EXPERIMENTAL`, `CONFIG_BLK_DEV_ZONED`, 32-bit builds, and sanity-test builds. `btrfs_force_shutdown()` intentionally marks an emergency shutdown without remounting read-only, so callers must understand how thaw and RO/RW paths diverge.

## Test Signals

Signals include broad Btrfs compile coverage across config matrices, mount tests for feature masks and mount options, lockdep coverage for fs_info locks and exclusive operations, checksum and block-size tests through `fs.c`, zoned and non-zoned allocation tests, free-space tree/cache feature toggles, sysfs feature-change updates, emergency shutdown behavior, and sanity-test builds that exercise `EXPORT_FOR_TESTS` branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/inode-item.c -->
# sources/distributed-fs/ceph-client/fs/btrfs/inode-item.c

## Purpose

`sources/distributed-fs/ceph-client/fs/btrfs/inode-item.c` implements Btrfs inode item helpers for inode references/backreferences, extended inode references, empty inode item insertion, inode lookup, and truncation/removal of inode-associated items and file extents. It is used by directory/link management, inode creation/deletion, free-space cache inode truncation, and file truncate paths. The file was read as a complete 733-line implementation.

## Important APIs, Types, and Functions

Exported lookup/search helpers are `btrfs_find_name_in_backref`, `btrfs_find_name_in_ext_backref`, and `btrfs_lookup_inode_extref`. Reference mutation APIs are `btrfs_insert_inode_ref` and `btrfs_del_inode_ref`; internally they may call `btrfs_insert_inode_extref` or `btrfs_del_inode_extref` when standard inode ref items overflow or extended refs are required. Inode item helpers are `btrfs_insert_empty_inode` and `btrfs_lookup_inode`. The major truncate API is `btrfs_truncate_inode_items()`.

`btrfs_trace_truncate()` bridges truncation decisions into tracepoints for inline and regular file extents. `struct btrfs_truncate_control` is declared in the header and drives truncate behavior through fields such as inode, new size, target inode number, minimum key type, skip-ref-updates, clear-extent-range, and output accounting.

## Control Flow

Name lookup in regular backrefs scans the payload of a `BTRFS_INODE_REF_KEY` item, walking variable-length `struct btrfs_inode_ref` records until a name-length and name comparison matches. Extended backref lookup computes `btrfs_extref_hash(parent, name)` for the item key, searches the tree, and then scans collisions inside the item for matching parent and name.

Insertion first tries a regular inode ref item keyed by inode objectid and parent objectid. If the key exists, it appends a new variable-length ref unless the same name is already present. If insertion overflows the item and the filesystem has `EXTENDED_IREF`, it falls back to inserting/appending an extended inode ref keyed by hash. Deletion does the inverse: remove the regular ref if present, compact or delete the item, and if not found, search and delete the extended inode ref. Extended ref deletion aborts the transaction if the key exists but the named ref cannot be found, because that indicates unexpected metadata inconsistency.

`btrfs_lookup_inode()` is a wrapper around `btrfs_search_slot()` that handles the special root item lookup convention where callers may search for offset `-1` and accept the previous matching root item.

`btrfs_truncate_inode_items()` searches backward from the maximum key for an inode, deleting items with type greater than or equal to `control->min_type`. For file extents, it computes extent end, decides whether to delete or shrink based on `new_size`, handles regular/prealloc extents by updating `num_bytes` or preparing delayed extent reference drops, handles inline extents by shrinking unencoded inline data or returning `BTRFS_NEED_TRUNCATE_BLOCK` for encoded partial-inline truncation, optionally clears the inode file-extent range, batches adjacent item deletions, refills delayed-ref reservation when needed, and backs off with `-EAGAIN` for shareable roots after large deletion work.

## State and Persistence Behavior

All persistent state is stored in Btrfs btree items: inode items, inode ref items, inode extended ref items, root items, and file extent items. Regular and extended refs contain variable-length names stored directly inside item payloads. Truncation mutates file extent items, deletes btree items, queues delayed reference drops through `btrfs_free_extent()`, updates caller-visible counters in `btrfs_truncate_control`, and may clear ranges from the runtime inode file-extent map when operating on a real inode. It does not own long-lived state outside the btree and caller-provided control structure.

## Dependencies and Integration Points

Direct dependencies include `ctree.h`, `fs.h`, `messages.h`, `inode-item.h`, `disk-io.h`, `transaction.h`, `space-info.h`, `accessors.h`, `extent-tree.h`, and `file-item.h`. It integrates with fscrypt name strings, extent buffers, btree path/search/insert/delete/truncate/extend primitives, delayed refs, file-extent map clearing, inode byte accounting, tracepoints, root/shareable-state handling, and feature flags for extended inode refs.

## Risks and Edge Cases

Backref items are variable length, so item-size and memmove calculations must be exact to avoid corrupting adjacent refs. Extended refs use a CRC32C-derived hash and must scan collisions by parent and name. Filesystems without `EXTENDED_IREF` can hit `-EMLINK` when regular inode ref items overflow. Deleting an extref key that lacks the expected named ref is treated as filesystem inconsistency and aborts the transaction. Truncation has many corner cases: partial regular extents require aligned `num_bytes`, inline extents with compression/encryption/other encoding cannot be partially shrunk in place, delayed refs can exhaust reservation and force `-EAGAIN`, and `skip_ref_updates` must only be used when the caller has another way to handle extent refs. The comment `FIXME blocksize != 4096` near extent deletion is a useful audit signal for non-4K assumptions.

## Test Signals

Tests should cover hard-link creation/removal, duplicate-name insertion returning `-EEXIST`, fallback to extended refs under large ref arrays, hash-collision behavior for extrefs, deletion compaction of multi-ref items, root item lookup with offset `-1`, file truncation of regular/prealloc/inline extents, encoded inline partial truncate returning `BTRFS_NEED_TRUNCATE_BLOCK`, delayed-ref reservation pressure returning `-EAGAIN`, free-space cache inode truncation through `btrfs_truncate_free_space_cache()`, and fsck verification after crash injection around reference or truncate mutations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/inode-item.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/inode-item.h -->
# sources/distributed-fs/ceph-client/fs/btrfs/inode-item.h

## Purpose

`sources/distributed-fs/ceph-client/fs/btrfs/inode-item.h` declares inode item, inode reference, extended reference, lookup, and truncate helper APIs for Btrfs. It also defines the truncate-control structure used to parameterize item removal and file extent truncation. The file was read as a complete 116-line header.

## Important APIs, Types, and Functions

The header defines `BTRFS_NEED_TRUNCATE_BLOCK`, returned when the caller must truncate the final block outside `btrfs_truncate_inode_items()`. `struct btrfs_truncate_control` carries inputs (`inode`, `new_size`, `ino`, `min_type`, `skip_ref_updates`, `clear_extent_range`) and outputs (`extents_found`, `last_size`, `sub_bytes`) for truncation. Inline helpers `btrfs_inode_combine_flags()` and `btrfs_inode_split_flags()` convert between the on-disk u64 inode flag representation and split runtime flag fields. `btrfs_extref_hash()` computes extended inode ref key offsets using CRC32C over parent objectid and name.

Declared APIs include `btrfs_truncate_inode_items`, `btrfs_insert_inode_ref`, `btrfs_del_inode_ref`, `btrfs_insert_empty_inode`, `btrfs_lookup_inode`, `btrfs_lookup_inode_extref`, `btrfs_find_name_in_backref`, and `btrfs_find_name_in_ext_backref`.

## Control Flow

This header does not implement the full flows, but it defines how callers drive them. Creation paths call `btrfs_insert_empty_inode()` and then update inode fields. Link/unlink paths insert or delete inode refs by name, with implementation fallback to extended refs as needed. Truncate and eviction paths fill `btrfs_truncate_control`, call `btrfs_truncate_inode_items()`, inspect output counters, and handle `BTRFS_NEED_TRUNCATE_BLOCK` or `-EAGAIN` where appropriate. Inline flag helpers are pure conversions.

## State and Persistence Behavior

The header describes persistent btree item manipulation but owns no storage. `btrfs_truncate_control` is caller-owned transient state that reports how much inode byte accounting should be adjusted and where truncation stopped. Inode flag combination/splitting maps runtime flags to the on-disk inode item flag field. Extended reference hash values are persisted as key offsets for `BTRFS_INODE_EXTREF_KEY` items.

## Dependencies and Integration Points

The header includes Linux types and CRC32C and forward declares fscrypt strings, extent buffers, transactions, roots, paths, keys, inode/extref types, Btrfs inodes, and the truncate control. It integrates with directory/link management, inode creation, inode lookup, file truncation, free-space cache inode truncation, and fscrypt-aware filename handling.

## Risks and Edge Cases

`btrfs_extref_hash()` is a keying helper, not a uniqueness guarantee; implementations must scan hash-collision records. Callers of `btrfs_truncate_inode_items()` must set `inode` when `clear_extent_range` is true. `skip_ref_updates` can be dangerous outside specialized contexts. The split/combined inode flags must stay compatible with on-disk format and runtime read-only flag handling.

## Test Signals

Compile coverage should include fscrypt-name users, truncate callers, and inode ref callers. Runtime signals include hard-link and unlink tests, extended inode ref overflow/collision tests, inode flag round-trip tests, truncate-control behavior for normal file truncate and free-space cache inode truncate, and crash-consistency checks for inode ref and file extent item mutation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/inode-item.h -->
