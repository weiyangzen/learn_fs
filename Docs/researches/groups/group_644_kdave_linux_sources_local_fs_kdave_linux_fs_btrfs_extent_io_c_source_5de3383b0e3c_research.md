# Group Research: group_644_kdave_linux_sources_local_fs_kdave_linux_fs_btrfs_extent_io_c_source_5de3383b0e3c

Scope confirmed: `Docs/research_subset_a.md` includes `sources/local-fs/kdave-linux`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/extent_io.c -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/extent_io.c

This file implements Btrfs data page-cache I/O and metadata extent-buffer I/O. It bridges folios, extent state bits, extent maps, ordered extents, bios, fsverity verification, metadata buffer cache lifetime, and btree block memory access helpers.

Major responsibilities:
- Builds and submits data read/write bios through `struct btrfs_bio_ctrl`, handling compression, readahead, checksum lookup generation hints, ordered-extent boundaries, and cgroup writeback ownership.
- Drives read folio and readahead paths with `btrfs_do_readpage()`, including extent-map lookup, holes, inline extents, compressed extent splitting, i_size zeroing, subpage locking, and fsverity verification.
- Drives buffered writeback through delalloc discovery, folio/subpage dirty bitmaps, ordered extent creation, COW fixup, sector submission, and ordered extent completion/error cleanup.
- Implements btree metadata writeback through the extent-buffer xarray marks, dirty/writeback flags, zoned metadata write-pointer coordination, and metadata bio end I/O.
- Allocates, finds, clones, reads, releases, and frees `struct extent_buffer` objects, including subpage metadata folio state and RCU-delayed frees.
- Provides byte, bitmap, memcpy/memmove, memset, and user-copy helpers over extent buffers that may span multiple folios or have a direct contiguous address.

Key data flows:
- `btrfs_read_folio()` and `btrfs_readahead()` lock the inode IO-tree range, wait or skip ordered extents as appropriate, map file offsets through extent maps, submit data bios, then unlock extent state.
- `btrfs_writepages()` serializes zoned data relocation, walks dirty folios in `extent_write_cache_pages()`, runs delalloc with `writepage_delalloc()`, submits sectors with `extent_writepage_io()`, and flushes the pending write bio at the end.
- `btree_writepages()` walks the filesystem `buffer_tree` xarray by dirty/towrite marks, locks dirty extent buffers, verifies zoned metadata placement, then writes each extent buffer with `write_one_eb()`.
- `alloc_extent_buffer()` obtains or creates the xarray-cached metadata buffer for a logical tree block, attaches folios to the btree inode page cache, handles races with existing buffers, and installs the tree reference.
- Metadata reads use `read_extent_buffer_pages_nowait()` to submit a metadata bio and validate parent checks in `end_bbio_meta_read()` before setting extent-buffer uptodate state.

Concurrency and lifetime:
- Data folio state is coordinated through folio locks, Btrfs subpage state, the inode IO tree, ordered extent locks, and writeback control.
- Extent buffers use `fs_info->buffer_tree` xarray membership, `refs_lock`, `EXTENT_BUFFER_TREE_REF`, `EXTENT_BUFFER_STALE`, dirty/writeback bits, and RCU freeing to avoid races with lookup, release_folio, and I/O completion.
- Btree writeback marks are stored in the buffer-tree xarray rather than the normal page-cache tags alone.
- Transaction writeback inhibition is tracked in `trans->writeback_inhibited_ebs` and suppresses opportunistic writeback while keeping references to inhibited buffers.

Important invariants:
- Delalloc ranges must be locked in folio order, rechecked under the IO-tree lock, and cleaned up if ordered extent setup partially fails.
- Data write bios must not cross ordered extent boundaries, especially for zoned filesystems.
- Compressed reads must not merge separate extent maps that point to the same compressed on-disk extent with different logical offsets.
- Extent buffers must be aligned to sectorsize/nodesize constraints and must not be freed while dirty, under writeback, or reachable through the tree reference.
- Extent-buffer memory helpers check ranges and preserve correct subpage offsets for nodesize smaller than page size.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/extent_io.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/extent_io.h -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/extent_io.h

This header defines the public extent I/O and extent-buffer interface used by Btrfs page-cache, metadata, btree, delalloc, readahead, and release paths.

Primary declarations:
- Extent-buffer runtime flags cover uptodate, dirty, tree reference, stale, writeback, unmapped/dummy buffers, write errors, zoned zeroout, and in-progress reads.
- Page operation bits describe batched folio actions such as unlock, start/end writeback, and ordered marking.
- `struct extent_buffer` is the in-memory representation of a metadata block, with logical start, length, folio size/shift, optional direct address, fs owner, reference state, lock, read mirror, writeback inhibitors, log-tree index, RCU head, and backing folios.
- `struct extent_changeset` records changed byte counts and optionally changed ranges, with a bytes-only sentinel to avoid allocations when callers only need accounting.
- `struct btrfs_eb_write_context` carries metadata writeback state, including zoned block group context.

Important helpers:
- `get_eb_offset_in_folio()` and `get_eb_folio_index()` hide the differences between page-sized metadata, multi-page nodes, high-order folios, and subpage metadata blocks.
- `num_extent_pages()` reports logical page slots for an extent buffer; `num_extent_folios()` reports actual populated folios.
- `extent_buffer_uptodate()` is the fast flag check for metadata block validity.

API surface:
- Data I/O: `btrfs_read_folio()`, `btrfs_readahead()`, `btrfs_writepages()`, `extent_write_locked_range()`, folio extent-private attach/detach, and extent mapping release.
- Metadata I/O: `btree_writepages()`, `btrfs_btree_wait_writeback_range()`, extent-buffer read/readahead helpers, dirty/uptodate state mutation, invalidation, and release.
- Extent-buffer lifecycle: allocate, clone, dummy allocate, find, free, stale free, test-only allocation, and leak debug.
- Extent-buffer memory access: read/write/copy/memzero/memcmp/user nofault copy, bitmap set/clear/test, and full-buffer copy.
- Transaction interaction: inhibit and uninhibit extent-buffer writeback.

The header is the shared contract between inode data I/O, btree metadata I/O, transaction code, subpage support, zoned mode, fsverity-aware reads, and extent-buffer consumers.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/extent_io.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/extent_map.c -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/extent_map.c

This file implements the Btrfs per-inode extent-map cache. Extent maps describe file logical ranges as holes, inline data, prealloc ranges, compressed extents, or regular on-disk extents, and are stored in an rb-tree with reference counting and a modified-extents list for fast fsync.

Major responsibilities:
- Initializes/destroys the extent-map slab cache and per-inode `extent_map_tree`.
- Allocates, frees, inserts, looks up, searches, removes, and replaces extent maps under the tree rwlock.
- Validates extent-map alignment and on-disk length/offset invariants in debug builds.
- Merges adjacent compatible extent maps to reduce memory usage, while excluding pinned, compressed, logging, and modified extents.
- Handles insertion races from `btrfs_get_extent()` by returning an existing map or trimming/merging the new map into the uncovered range.
- Drops or replaces extent-map ranges, splitting maps around the removed range when possible and setting full-fsync state when modified extents cannot be preserved precisely.
- Splits pinned ordered extent maps when ordered extents are split.
- Implements the asynchronous extent-map shrinker worker that scans filesystem roots and inodes to reclaim evictable extent maps under memory pressure.

Key data flows:
- `btrfs_add_extent_mapping()` inserts a newly loaded map; on `-EEXIST`, it searches for the overlapping/nearby map and either returns that map or trims the new one to a gap between neighbors.
- `btrfs_unpin_extent_cache()` clears `EXTENT_FLAG_PINNED` after writeback has persisted a file extent item, updates generation, and attempts merge.
- `btrfs_drop_extent_map_range()` removes all maps intersecting a range, optionally skipping pinned maps and preserving outside portions with up to two split maps.
- `btrfs_replace_extent_map_range()` repeatedly drops overlapping maps and inserts a replacement until no insertion race remains.
- `btrfs_free_extent_maps()` coalesces shrinker requests through an atomic scan count and queues `em_shrinker_work`; the worker resumes from remembered root/inode positions.

Concurrency and lifetime:
- The rb-tree and modified list are protected by `extent_map_tree::lock`.
- Tree membership owns one reference; lookups and callers take/drop additional references with `btrfs_free_extent_map()`.
- Modified extents in `em->list` interact with fast fsync; removing recent modified maps forces full fsync to avoid missing unwritten file extent items.
- The shrinker uses trylocks on inode extent trees and `i_mmap_lock` to avoid racing fsync logging decisions while holding the extent-tree write lock.

Important invariants:
- Extent maps in a tree must not overlap.
- Regular extent-map fields are sectorsize aligned; holes and inline extents use sentinel disk addresses and zero offsets.
- Compressed extent maps are not merged because their physical and logical sizes differ and compression type matters.
- Pinned maps are protected from removal/merge unless callers explicitly clear the pinned state.
- The evictable extent-map counter is maintained only for non-testing filesystem tree roots.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/extent_map.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/extent_map.h -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/extent_map.h

This header defines the extent-map data model and public cache API.

Primary definitions:
- Sentinel disk addresses distinguish special mappings: `EXTENT_MAP_HOLE`, `EXTENT_MAP_INLINE`, and `EXTENT_MAP_LAST_BYTE`.
- Extent-map flags track pinned not-yet-on-disk state, zlib/lzo/zstd compression, preallocation, logging, and synthetic merged maps.
- `struct extent_map` stores file offset, logical length, full on-disk extent bytenr and length, decompressed offset and size, generation, flags, reference count, rb-tree node, and modified-list node.
- `struct extent_map_tree` stores the rb-root, modified extents list, and protecting rwlock.

Important helpers:
- `btrfs_extent_map_set_compression()` and `btrfs_extent_map_compression()` encode/decode compression flags.
- `btrfs_extent_map_is_compressed()` provides a fast compressed check.
- `btrfs_extent_map_in_tree()` tests rb-tree membership.
- `btrfs_extent_map_block_start()` returns the physical start used for I/O, adding `offset` for uncompressed regular extents but not for compressed extents or sentinels.
- `btrfs_extent_map_end()` returns the exclusive logical end with overflow saturation.

API surface:
- Tree setup and lookup: `btrfs_extent_map_tree_init()`, `btrfs_lookup_extent_mapping()`, and `btrfs_search_extent_mapping()`.
- Lifecycle: slab init/exit, allocation, and reference release.
- Mutation: add, remove, drop range, replace range, split, unpin, and clear logging.
- Reclaim: `btrfs_free_extent_maps()` and `btrfs_init_extent_map_shrinker_work()`.

The header is the shared contract between file extent lookup, read/write submission, delalloc/ordered extent completion, fsync logging, fiemap, and memory reclaim.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/extent_map.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/fiemap.c -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/fiemap.c

This file implements Btrfs `FIEMAP` reporting. It walks file extent items from the subvolume tree, supplements holes/prealloc ranges with delalloc state from the inode IO tree, checks sharing through backrefs, and emits merged fiemap extents to userspace.

Major responsibilities:
- Buffers fiemap output in `struct fiemap_cache` so adjacent compatible extents can be merged and so writes to a userspace fiemap buffer do not occur while holding Btrfs extent locks or cloned btree paths.
- Searches file extent items with `fiemap_search_slot()`, using cloned leaves to avoid long locks and lockdep problems while checking shared extents.
- Iterates cloned leaves with `fiemap_next_leaf_item()` while preserving leaf start offsets needed by subpage extent-buffer access.
- Processes implicit holes, explicit hole items, and prealloc extents through `fiemap_process_hole()`, reporting delalloc subranges as `FIEMAP_EXTENT_DELALLOC | FIEMAP_EXTENT_UNKNOWN` and unwritten prealloc gaps as `FIEMAP_EXTENT_UNWRITTEN`.
- Finds the last real extent end with `fiemap_find_last_extent_offset()` so the final emitted extent can receive `FIEMAP_EXTENT_LAST` when appropriate.
- Handles `FIEMAP_FLAG_SYNC` by waiting for ordered ranges before and after taking the inode shared lock, covering compression writeback that may require an extra wait.

Key data flows:
- `btrfs_fiemap()` runs `fiemap_prep()`, optionally waits ordered ranges, takes `BTRFS_ILOCK_SHARED`, optionally waits again, then calls `extent_fiemap()`.
- `extent_fiemap()` rounds the requested range to sectorsize, locks the inode IO-tree range, finds the last extent, positions a btree path, walks file extent items, emits holes/delalloc/prealloc/inline/regular/compressed extents, unlocks, flushes cached output, and emits the final cached extent.
- If the intermediary cache fills, `emit_fiemap_extent()` returns `BTRFS_FIEMAP_FLUSH_CACHE`; `extent_fiemap()` unlocks, releases the path, flushes entries, advances `start` to `next_search_offset`, and restarts the search.
- Regular and prealloc extents call `btrfs_is_data_extent_shared()` when userspace requested actual mappings, adding `FIEMAP_EXTENT_SHARED` if backrefs show sharing.

Concurrency and correctness:
- The inode IO-tree range is locked while correlating file extent items with delalloc state, preventing races with delalloc flushing and ordered extent completion.
- Cloned leaves avoid holding live btree leaves during expensive sharing checks and while userspace output could fault back into the same file.
- The cache logic trims or discards overlapping previously cached extents when concurrent ordered extent completion causes the next btree search to observe newer split file extent items.
- The output path tracks `fi_extents_max` itself because entries are buffered before reaching `fiemap_fill_next_extent()`.

Important invariants:
- Inline extents are reported as data inline and not aligned with physical address zero.
- Compressed extents are reported with `FIEMAP_EXTENT_ENCODED`; their physical contiguity is not merged as if logical length matched physical length.
- Delalloc is only searched up to i_size, while prealloc may extend beyond i_size.
- Final `FIEMAP_EXTENT_LAST` depends on the last non-hole file extent and absence of later delalloc.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/fiemap.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/fiemap.h -->
# File Research: sources/local-fs/kdave-linux/fs/btrfs/fiemap.h

This header declares the Btrfs fiemap entry point.

Primary declaration:
- `btrfs_fiemap(struct inode *inode, struct fiemap_extent_info *fieinfo, u64 start, u64 len)` exposes the filesystem-specific fiemap implementation to inode/file operation code.

Dependencies:
- Includes `<linux/fiemap.h>` for `struct fiemap_extent_info` and fiemap flag definitions.
- Forward use of `struct inode` and `u64` comes from surrounding kernel headers included by consumers.

The header is intentionally minimal: all fiemap behavior, locking, cache buffering, btree walking, delalloc detection, and shared-extent checking live in `fiemap.c`.
<!-- END FILE RESEARCH: sources/local-fs/kdave-linux/fs/btrfs/fiemap.h -->