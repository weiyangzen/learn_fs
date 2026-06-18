# Research: subset-b-005613

Grouped research for Btrfs extent I/O, extent map, and fiemap sources. Each file section preserves the source path and is suitable for reconciliation into the source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/extent_io.c -->
# sources/distributed-fs/ceph-client/fs/btrfs/extent_io.c

## Purpose

`extent_io.c` is the main Btrfs bridge between VFS folio writeback/read paths, Btrfs extent state, extent maps, ordered extents, BIO submission, and metadata extent-buffer lifetime. It handles data folio reads and writes, readahead, delalloc locking and cleanup, metadata tree block read/writeback, extent-buffer allocation/freeing, subpage metadata/data state, and extent-buffer memory access helpers used by tree code.

## Important APIs, Types, And Functions

- `struct btrfs_bio_ctrl` batches read/write state while building `struct btrfs_bio` objects. It tracks the current bio, next logical file offset, compression type, ordered-extent boundary, op flags, max extent generation for checksum lookup optimization, writeback control, subpage submit bitmap, readahead control, and last extent-map start for compressed read correctness.
- Cache lifecycle: `extent_buffer_init_cachep()` and `extent_buffer_free_cachep()` create/destroy the `btrfs_extent_buffer` slab cache. Debug builds also maintain `fs_info->allocated_ebs` via leak debug helpers.
- Data reads: `btrfs_read_folio()`, `btrfs_readahead()`, `lock_extents_for_read()`, `btrfs_do_readpage()`, `submit_extent_folio()`, `end_bbio_data_read()`, and `end_folio_read()` coordinate locked folios, ordered extents, extent-map lookup, holes/inline/compressed extents, fsverity verification, zeroing past EOF, and BIO completion.
- Data writes: `btrfs_writepages()`, `extent_write_cache_pages()`, `extent_writepage()`, `writepage_delalloc()`, `extent_writepage_io()`, `submit_one_sector()`, `extent_write_locked_range()`, and `end_bbio_data_write()` run delayed allocation, create/finish ordered extents, submit normal writeback, and complete folio writeback state.
- Metadata writeback: `btree_writepages()`, `lock_extent_buffer_for_io()`, `prepare_eb_write()`, `write_one_eb()`, `end_bbio_meta_write()`, `btrfs_btree_wait_writeback_range()`, and xarray tag helpers drive dirty/writeback metadata extent buffers.
- Extent buffer lifetime: `alloc_extent_buffer()`, `alloc_dummy_extent_buffer()`, `btrfs_clone_extent_buffer()`, `find_extent_buffer()`, `free_extent_buffer()`, `free_extent_buffer_stale()`, `try_release_extent_buffer()`, and `try_release_subpage_extent_buffer()` manage buffer-tree xarray entries, folios, references, stale/tree refs, and subpage sharing.
- Extent buffer I/O and access: `read_extent_buffer_pages_nowait()`, `read_extent_buffer_pages()`, `end_bbio_meta_read()`, `set_extent_buffer_dirty()`, `btrfs_clear_buffer_dirty()`, `set_extent_buffer_uptodate()`, `clear_extent_buffer_uptodate()`, `read_extent_buffer()`, `write_extent_buffer()`, `memcmp_extent_buffer()`, `copy_extent_buffer*()`, `memcpy_extent_buffer()`, `memmove_extent_buffer()`, `memzero_extent_buffer()`, and bitmap helpers abstract tree-block memory that may span folios or sit inside a subpage folio.
- Readahead helpers: `btrfs_readahead_tree_block()` and `btrfs_readahead_node_child()` create/find metadata blocks and submit nonblocking metadata reads with parent checks.

## Control Flow

Data read starts by locking the inode extent range with `lock_extents_for_read()`. That helper waits for ordered extents unless the locked folio state proves the ordered range can be skipped. `btrfs_do_readpage()` then walks the folio by sectorsize, sets/uses Btrfs folio private state, resolves an extent map, and handles each sector as EOF zeroing, already-uptodate, hole zeroing, inline data already copied by `btrfs_get_extent()`, or BIO-backed read. BIOs are split when compression type changes, when logical/disk contiguity breaks, or when adjacent compressed file extents point at the same compressed extent through different extent maps. Completion updates subpage/folio uptodate bits, runs fsverity where relevant, zeroes EOF tails, and unlocks the correct range.

Data writeback flows from `btrfs_writepages()` into `extent_write_cache_pages()`, which iterates dirty folios by writeback tags, handles cyclic scans, waits on writeback for sync/subpage cases, clears dirty-for-IO, and calls `extent_writepage()`. `extent_writepage()` validates the folio, maps it into Btrfs folio state, calls `writepage_delalloc()` to lock and run delalloc ranges, then `extent_writepage_io()` submits sectors indicated by `bio_ctrl->submit_bitmap`. `submit_one_sector()` obtains the final extent map, rejects holes/inline/compressed cases that should not reach normal writeback, updates dirty/ordered/writeback bits, and appends the sector to a BIO. `end_bbio_data_write()` clears ordered/writeback state and finishes the ordered extent.

Metadata writeback is xarray-tag driven rather than page-cache-tag driven. `btree_writepages()` scans `fs_info->buffer_tree` for dirty/towrite extent buffers, checks zoned metadata write pointer constraints, locks each buffer, clears dirty tags, sets writeback state, zeroes stale tree-block areas with `prepare_eb_write()`, creates a metadata BIO in `write_one_eb()`, and completes in `end_bbio_meta_write()`. Write errors call `set_btree_ioerr()`, which records runtime buffer failure and persistent fs/log error flags needed by transaction commit and log sync paths.

Extent-buffer allocation first checks alignment and existing xarray entries, allocates an `extent_buffer`, preallocates subpage private state if needed, allocates folios, attaches/reuses page-cache folios under `i_private_lock`, inserts into `fs_info->buffer_tree` by xarray compare-exchange, sets the tree reference, then unlocks and drops allocation references. Release paths remove xarray entries with compare-exchange, detach folio private state only when safe, respect dirty/writeback guards, and use RCU freeing for mapped buffers.

## State And Persistence Behavior

The file maintains runtime state in `extent_buffer::bflags`, folio private/subpage bitmaps, inode `io_tree` extent states, inode extent maps, ordered extents, xarray marks on `fs_info->buffer_tree`, and writeback-control counters. Metadata dirty accounting updates `fs_info->dirty_metadata_bytes`; extent-buffer writeback errors set `BTRFS_FS_BTREE_ERR`, `BTRFS_FS_LOG1_ERR`, or `BTRFS_FS_LOG2_ERR`, which influences transaction/log error handling beyond the lifetime of a single buffer. Data write completion persists ordered-extent success/failure through `btrfs_finish_ordered_extent()` and mapping errors.

The actual persistent bytes are not formatted here, but this file decides when data and metadata reach block devices and when tree-block memory is sanitized before writeback. It also stores runtime read mirror choice in `eb->read_mirror`, sets header-written flags before metadata writeback, and enforces parent/generation checks on metadata reads through `btrfs_validate_extent_buffer()`.

## Dependencies And Integration Points

This file integrates Linux folios, page cache, readahead, writeback, BIO/block APIs, fsverity, xarray tags, RCU, slab caches, and Btrfs-specific modules: extent I/O tree locking, extent maps, ordered extents, compression, checksums, tree locking, backrefs, disk I/O, zoned block-group logic, transaction state, subpage state, file item accessors, and device replacement. It is called by Btrfs address-space operations for data and btree inodes, tree block lookup/read paths, transaction dirtying/cleaning paths, release/invalidate folio callbacks, and readahead callers.

## Risks And Edge Cases

- Reference lifetime is delicate: extent buffers have xarray tree refs, ordinary refs, stale refs, RCU freeing, and folio private attachments. Bugs can become use-after-free, leaks, or dirty buffers freed while still referenced.
- Subpage support is high risk because multiple logical sectors or metadata blocks share one folio; dirty, lock, writeback, uptodate, and eb-ref bitmaps must be range accurate.
- BIO merging must preserve both disk contiguity and file logical contiguity. Compressed extents add a correctness constraint around extent-map identity, not just disk bytenr.
- Ordered extent waiting/skip logic prevents read/write deadlocks and missing checksum insertion. Incorrect skip decisions could expose stale data or fail reads due to missing checksums.
- Metadata writeback errors must be recorded outside page state; otherwise transaction commit can succeed with invalid tree blocks.
- Zoned mode requires preserving metadata write order and zeroout semantics; bypassing dirty clear behavior could violate write pointer ordering.
- Range arithmetic is mostly inclusive and often converted to exclusive boundaries; off-by-one or overflow bugs are explicitly guarded in several helpers but remain a broad risk.

## Test Signals

Useful signals include xfstests for Btrfs generic read/write, fsync, compression, delalloc, subpage, zoned mode, fsverity, metadata writeback error injection, and fiemap interactions; Btrfs sanity tests for extent-buffer allocation and `find_lock_delalloc_range()`; fault injection for allocation/BIO errors; lockdep/KASAN/KCSAN for folio/private/refcount races; and debug assertions around extent buffer range access, dirty/writeback state, and extent-map assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/extent_io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/extent_io.h -->
# sources/distributed-fs/ceph-client/fs/btrfs/extent_io.h

## Purpose

`extent_io.h` declares the public interface and core data structures for Btrfs extent-buffer and extent I/O helpers. It exposes metadata tree-block memory abstraction, folio/delalloc helpers, data and metadata writeback/read entry points, extent-buffer allocation/read/release APIs, and small inline utilities used throughout Btrfs tree and file I/O code.

## Important APIs, Types, And Functions

- Extent-buffer flags enumerate runtime buffer state: uptodate, dirty, tree ref, stale, writeback, unmapped, write error, zoned zeroout, and reading.
- Page operation flags describe range operations for delalloc cleanup: unlock, start/end writeback, and set ordered.
- `EXTENT_FOLIO_PRIVATE` is the non-subpage folio-private sentinel for data extent-managed folios.
- Bitmap macros (`BIT_BYTE`, `BYTE_MASK`, first/last masks) support byte-granular little-endian bitmap manipulation inside extent buffers.
- `struct extent_buffer` is the central metadata block abstraction. It stores logical start, length, folio size/shift, runtime flags, fs_info, optional contiguous virtual address, refcount and ref lock, read mirror, writeback inhibitor count, log tree index, RCU head, tree lock, folio array, and debug-only leak/lock owner fields.
- `struct btrfs_eb_write_context` carries metadata writeback context, including writeback control, current buffer, and zoned block-group state.
- Inline helpers `offset_in_eb_folio()`, `get_eb_offset_in_folio()`, and `get_eb_folio_index()` hide differences between page-sized metadata, larger nodes spanning pages, high-order folios, and subpage nodes.
- `struct extent_changeset` plus helpers track changed byte counts and optionally changed ranges; `EXTENT_CHANGESET_BYTES_ONLY` is a sentinel for callers that only need byte totals.
- Declared exported operations cover read/writepages, readahead, extent buffer allocation/cloning/finding/freeing, metadata reads, memory copy/compare/zero/bitmap operations, delalloc range cleanup, invalidate/release, dirty/uptodate state, test allocation helpers, and writeback inhibition.

## Control Flow

This header is mostly declarative, but it shapes control flow by separating data page-cache operations (`btrfs_read_folio()`, `btrfs_writepages()`, `extent_write_locked_range()`, `btrfs_readahead()`) from metadata extent-buffer operations (`alloc_extent_buffer()`, `read_extent_buffer_pages()`, `btree_writepages()`, `btrfs_btree_wait_writeback_range()`). Callers allocate or find an `extent_buffer`, read it through the metadata BIO path, modify it through memory helpers, mark it dirty/uptodate, and let btree writeback submit it later.

The inline offset helpers are central to all extent-buffer memory access. Any caller that reads or writes tree block fields through accessors depends on them to translate an offset inside the logical tree block into the right folio and byte offset.

## State And Persistence Behavior

The header defines runtime state only; it does not persist data directly. However, the state bits it declares decide whether metadata is considered valid, dirty, writeback-active, stale, or failed. `struct extent_buffer` state gates tree-block persistence through metadata writeback, and its `log_index` allows writeback errors to be attributed to the main tree or one of the log trees. `extent_changeset` is transient operation accounting for extent-state changes.

## Dependencies And Integration Points

The header depends on Linux rbtree/refcount/fiemap/spinlock/atomic/rwsem/list/slab definitions and Btrfs headers for messages, ulist, and miscellaneous helpers. It is included by Btrfs files that need tree block memory access, metadata read/write, page-cache extent I/O, delalloc cleanup, and tests. It also forwards many Btrfs structures to avoid broad include coupling.

## Risks And Edge Cases

- `INLINE_EXTENT_BUFFER_PAGES` assumes maximum metadata block size over page size; all extent-buffer users depend on this array being large enough.
- Offset helpers must be correct for both sectorsize equal to page size and sectorsize smaller than page size; mistakes corrupt metadata field access.
- Runtime flags are bit indices, not persisted values. Adding or reordering flags can affect code expectations but not on-disk format.
- `EXTENT_CHANGESET_BYTES_ONLY` uses a sentinel pointer value; callers must honor `extent_changeset_tracks_ranges()` before touching range lists.
- `wait_on_extent_buffer_writeback()` waits on a bit in `bflags`; callers must ensure the buffer lifetime remains valid while waiting.

## Test Signals

Build coverage is important because this header is widely included. Runtime signals include Btrfs sanity tests, metadata read/write tests, subpage tests, lockdep for extent-buffer locks, and debug assertions around extent-buffer access and changeset handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/extent_io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/extent_map.c -->
# sources/distributed-fs/ceph-client/fs/btrfs/extent_map.c

## Purpose

`extent_map.c` implements the in-memory file extent map cache for Btrfs inodes. Extent maps describe logical file ranges and their corresponding on-disk extents, holes, inline data, compression, preallocation, pinning, and logging state. The file provides insertion, lookup, merging, removal, splitting, replacement, unpinning, logging cleanup, and memory-pressure shrinking.

## Important APIs, Types, And Functions

- Cache lifecycle: `btrfs_extent_map_init()` and `btrfs_extent_map_exit()` manage the `btrfs_extent_map` slab cache.
- Tree setup and object lifetime: `btrfs_extent_map_tree_init()`, `btrfs_alloc_extent_map()`, and `btrfs_free_extent_map()`.
- Internal rbtree utilities: `tree_insert()`, `tree_search()`, `lookup_extent_mapping()`, `next_extent_map()`, and `prev_extent_map()`.
- Merge logic: `can_merge_extent_map()`, `mergeable_maps()`, `merge_ondisk_extents()`, `validate_extent_map()`, and `try_merge_map()` combine adjacent safe mappings and enforce debug invariants.
- Public lookup and mutation: `btrfs_lookup_extent_mapping()`, `btrfs_search_extent_mapping()`, `btrfs_add_extent_mapping()`, `btrfs_remove_extent_mapping()`, `btrfs_drop_extent_map_range()`, `btrfs_replace_extent_map_range()`, and `btrfs_split_extent_map()`.
- State transitions: `btrfs_unpin_extent_cache()` clears pinned state after ordered extent completion and updates generation; `btrfs_clear_em_logging()` clears fast-fsync logging state and may merge.
- Shrinker: `btrfs_free_extent_maps()`, `btrfs_init_extent_map_shrinker_work()`, `btrfs_extent_map_shrinker_worker()`, `btrfs_scan_root()`, `find_first_inode_to_shrink()`, and `btrfs_scan_inode()` asynchronously drop evictable extent maps under memory pressure.

## Control Flow

Adding a mapping validates alignment and size assumptions in debug builds, inserts into the inode extent map rbtree, takes the tree reference, optionally links it into `modified_extents`, and increments `fs_info->evictable_extent_maps` for normal fs trees. If insertion collides, `btrfs_add_extent_mapping()` searches the existing nearby map. If the requested start is inside the existing map, the existing map is returned to the caller; otherwise `merge_extent_mapping()` trims the new map to the gap between neighbors and inserts that subset.

Merging is conservative. Maps cannot merge if pinned, compressed, logging, or on the modified list. Mergeable maps must be logically adjacent, have equivalent flags ignoring `EXTENT_FLAG_MERGED`, and either represent physically adjacent regular extents or matching hole/inline sentinels. Regular extent merging recomputes disk bytenr, disk length, offset, and ram bytes so a merged in-memory map can cover adjacent physical extents or different slices of the same physical extent.

Dropping a range uses two preallocated split maps for the worst case where an existing map overlaps both boundaries. It locks the extent map tree, walks intersecting maps, optionally skips pinned maps, preserves logging/modified state where needed, splits left and/or right remainders, removes covered maps, and sets full fsync on the inode if dropping an unsafely partial modified map without split memory. Replacing a range loops drop-and-add until `-EEXIST` no longer occurs.

The shrinker runs asynchronously. It records a scan target atomically, walks fs roots and inodes from saved cursor positions, uses trylocks to avoid blocking hot I/O, removes unpinned maps, marks inodes for full fsync when dropping current-generation modified maps, updates cursors, and emits tracepoints.

## State And Persistence Behavior

Extent maps are runtime cache entries and are not the on-disk source of truth. They mirror file extent items, holes, and inline data but may be merged to reduce memory. Their `generation` and `modified_extents` membership are important for fast fsync correctness. `EXTENT_FLAG_PINNED` prevents premature removal while ordered extents are not safely persisted. When dropping modified maps that may be needed by fast fsync, the code sets inode full-sync state so later fsync falls back to safer tree scanning.

The file updates `fs_info->evictable_extent_maps`, `em_shrinker_last_root`, `em_shrinker_last_ino`, and `em_shrinker_nr_to_scan`, which are runtime memory-management state. Persistent safety is protected indirectly by refusing unsafe merges/removals and by promoting inodes to full fsync when the cache can no longer support fast logging.

## Dependencies And Integration Points

This implementation depends on Linux slab, spin/rw locks, rbtrees, xarrays/radix root iteration, workqueues, percpu counters, and Btrfs inode/root/fs structures. It integrates with `btrfs_get_extent()` callers in read/write paths, ordered extent completion, fast fsync/logging, extent I/O release paths, inode eviction, memory-pressure shrinkers, tracepoints, and tests.

## Risks And Edge Cases

- Ranges use exclusive ends in many helpers but public drop uses inclusive `end`; conversion mistakes can split or remove the wrong bytes.
- Merged maps deliberately diverge from individual on-disk file extent items; code that needs exact disk item boundaries must account for `EXTENT_FLAG_MERGED`.
- Removing modified maps without preserving fast-fsync visibility can lose fsync logging unless full sync is set.
- Pinned maps must not be removed or merged; doing so can race ordered extent completion.
- The rbtree search helpers use neighbor fallback behavior; callers must distinguish strict intersection lookup from nearby search.
- Shrinker trylocks reduce latency but mean reclaim is best effort, and cursor state must remain valid across roots/inodes disappearing.

## Test Signals

Coverage should include extent-map add/lookup/drop/replace/split tests, fast fsync workloads with modified extents, ordered extent unpin paths, compression and hole/prealloc cases, memory pressure shrinker paths, debug builds for `validate_extent_map()`, tracepoint inspection, and stress with concurrent reads/writes/fsync/truncate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/extent_map.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/extent_map.h -->
# sources/distributed-fs/ceph-client/fs/btrfs/extent_map.h

## Purpose

`extent_map.h` defines the in-memory representation and public API for Btrfs inode extent maps. These maps cache the relationship between logical file byte ranges and disk extents, holes, inline extents, compression, preallocation, pinning, merge state, and fast-fsync logging state.

## Important APIs, Types, And Functions

- Sentinel disk bytenrs: `EXTENT_MAP_LAST_BYTE`, `EXTENT_MAP_HOLE`, and `EXTENT_MAP_INLINE` distinguish regular disk mappings from special map types.
- Flags: `EXTENT_FLAG_PINNED`, compression flags for zlib/lzo/zstd, `EXTENT_FLAG_PREALLOC`, `EXTENT_FLAG_LOGGING`, and `EXTENT_FLAG_MERGED`.
- `struct extent_map` stores the rb node, logical `start` and `len`, `disk_bytenr`, `disk_num_bytes`, logical `offset` inside the decompressed extent, `ram_bytes`, file extent `generation`, flags, refcount, and list node for modified extents.
- `struct extent_map_tree` stores the rbtree root, `modified_extents` list, and rwlock.
- Inline helpers set/query compression, test if compressed or in tree, compute block start, and compute logical map end with overflow handling.
- Public API declares tree initialization, lookup/search, add/remove/drop/replace/split, unpin, logging cleanup, allocation/free, shrinker work initialization, and shrinker triggering.

## Control Flow

Callers initialize one `extent_map_tree` per inode, allocate maps as needed while reading file extent items or creating ordered extents, fill fields according to on-disk item semantics, then add them under the tree write lock. Lookup callers use strict intersection for actual mapping and nearby search for conflict handling. Mutation callers remove, replace, split, unpin, or clear logging state as writeback, truncation, COW, and fsync progress.

The inline `btrfs_extent_map_block_start()` is important in I/O paths: compressed maps return the physical start of the compressed extent, while uncompressed maps add `offset` so the caller reaches the physical byte corresponding to the logical map start. Holes and inline extents return their sentinel.

## State And Persistence Behavior

Extent maps are transient cache, but their fields are derived from on-disk file extent items and ordered extent state. `generation`, `EXTENT_FLAG_PINNED`, `EXTENT_FLAG_LOGGING`, and `modified_extents` membership support persistence correctness by keeping fast fsync and ordered extent completion aware of extents that are not safely logged or persisted yet. `EXTENT_FLAG_MERGED` is runtime-only and tells readers the map may cover several adjacent physical/on-disk extents.

## Dependencies And Integration Points

The header depends on Linux compiler annotations, spinlock types, rbtrees, lists, refcounts, and Btrfs compression definitions. It is used by extent I/O, inode extent lookup, file write/truncate, ordered extents, fsync/log tree code, and reclaim/shrinker paths.

## Risks And Edge Cases

- The sentinel values are near `U64_MAX`; comparisons use `< EXTENT_MAP_LAST_BYTE` to distinguish regular extents. Incorrect comparisons can treat holes or inline extents as disk addresses.
- Compression flags are mutually expected by helper semantics but stored as bits; callers should not set multiple compression bits.
- `btrfs_extent_map_end()` saturates to `U64_MAX` on overflow, so range logic must be designed around exclusive end semantics.
- Struct size matters because many extent maps can be resident; adding fields has memory pressure impact.

## Test Signals

Compile coverage across Btrfs is essential. Runtime signals include extent map cache tests, compression read/write tests, hole/prealloc/inline fiemap and read tests, fast fsync tests, and memory pressure shrinker tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/extent_map.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/fiemap.c -->
# sources/distributed-fs/ceph-client/fs/btrfs/fiemap.c

## Purpose

`fiemap.c` implements Btrfs `FIEMAP` reporting. It walks file extent items, detects implicit/explicit holes, prealloc extents, inline extents, compressed extents, delalloc ranges, and shared extents, then emits merged `fiemap` records to userspace while avoiding deadlocks when the userspace fiemap buffer is mmaped to the target file.

## Important APIs, Types, And Functions

- `struct btrfs_fiemap_entry` is the buffered output tuple: logical offset, physical address, length, and fiemap flags.
- `BTRFS_FIEMAP_FLUSH_CACHE` is a private sentinel return code that tells the walker to drop locks/path, flush buffered entries, and restart at a safe offset.
- `struct fiemap_cache` buffers ready entries and one current merge candidate. It tracks array capacity/position, next search offset after a forced flush, mapped extent count, and cached extent fields.
- `flush_fiemap_cache()` writes buffered entries with `fiemap_fill_next_extent()`.
- `emit_fiemap_extent()` merges contiguous compatible records, trims stale overlaps caused by unlocked/researched tree walks, buffers ready entries, stops at `fi_extents_max`, and requests restart when the buffer fills.
- `emit_last_fiemap_cache()` emits the final cached extent.
- `fiemap_search_slot()` finds the first relevant file extent item and clones the leaf to avoid holding live tree locks during expensive shared-extent checks.
- `fiemap_next_leaf_item()` advances within cloned leaves and reclones the next live leaf as needed.
- `fiemap_process_hole()` reports delalloc inside holes/prealloc ranges and unwritten prealloc segments, including shared checks for prealloc extents.
- `fiemap_find_last_extent_offset()` finds the last non-hole file extent end so `FIEMAP_EXTENT_LAST` can be applied correctly.
- `extent_fiemap()` is the main walker; `btrfs_fiemap()` is the public entry point invoked by inode operations.

## Control Flow

`btrfs_fiemap()` first calls `fiemap_prep()`. If sync is requested, it waits for ordered ranges before and after taking the shared inode lock because compression can require a second wait after async compression has started. It then calls `extent_fiemap()`.

`extent_fiemap()` allocates a temporary output cache, backref share-check context, and Btrfs path. It rounds the requested range to sectorsize, locks the inode I/O tree range to stabilize delalloc and extent transitions, finds the last real extent, searches the subvolume tree, and iterates file extent items. Gaps before the next item are treated as implicit holes and passed to `fiemap_process_hole()`. Inline extents are emitted as inline/not-aligned; prealloc and explicit holes are processed for delalloc overlays; regular extents may be marked encoded and/or shared before emission.

When the fiemap cache fills, the code unlocks the I/O tree, releases the path, flushes buffered entries to userspace, adjusts `start`/`len` to `cache.next_search_offset`, and restarts. This avoids writing to a potentially mmaped output buffer while holding locks that `btrfs_page_mkwrite()` may need. At the end, it checks for EOF delalloc and applies `FIEMAP_EXTENT_LAST` when no later real or delalloc extent exists.

## State And Persistence Behavior

FIEMAP is observational and does not persist filesystem state. It temporarily locks `inode->io_tree` ranges to produce a coherent view relative to delalloc flushing and ordered extent completion. With `FIEMAP_FLAG_SYNC`, it actively waits for ordered extents so reported mappings reflect completed writeback. It uses cloned extent buffers to avoid holding live tree locks during expensive operations and a backref share-check context to identify shared extents.

## Dependencies And Integration Points

The file integrates Btrfs backref walking for shared extent detection, inode locking, extent I/O tree locking, file extent item accessors, delalloc search helpers, path/leaf traversal, and the generic Linux fiemap API. It is exposed through `btrfs_fiemap()` declared in `fiemap.h` and used by VFS ioctl/stat-style extent reporting paths.

## Risks And Edge Cases

- The walker may unlock and restart, so file extent items can change between passes. `emit_fiemap_extent()` contains overlap trimming logic to avoid duplicate or overlapping user-visible records.
- Holes and prealloc extents can contain delalloc ranges that are newer than tree items; missing this would underreport dirty data.
- FIEMAP buffers can be mmaped to the same file, so flushing while holding inode I/O tree locks or Btrfs paths can deadlock.
- Shared extent checks can be expensive and must use cloned leaves/backref context carefully.
- `FIEMAP_EXTENT_LAST` must consider both last file extent items and delalloc beyond the previous extent.
- Compression affects physical/logical merge rules; encoded extents cannot be merged simply by logical adjacency if physical layout does not match.

## Test Signals

Good signals include xfstests fiemap coverage for holes, prealloc, delalloc, inline extents, compressed extents, reflink/shared extents, no-holes mode, concurrent writeback/truncate while fiemap runs, sync vs non-sync fiemap, mmaped fiemap buffers, and fault injection for allocation/path failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/fiemap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/fiemap.h -->
# sources/distributed-fs/ceph-client/fs/btrfs/fiemap.h

## Purpose

`fiemap.h` is the small public header for Btrfs fiemap support. It declares the Btrfs-specific `btrfs_fiemap()` entry point used to implement generic FIEMAP extent reporting for Btrfs inodes.

## Important APIs, Types, And Functions

- Includes `<linux/fiemap.h>` for `struct fiemap_extent_info` and FIEMAP flags.
- Declares `int btrfs_fiemap(struct inode *inode, struct fiemap_extent_info *fieinfo, u64 start, u64 len);`.

## Control Flow

Callers include this header and invoke `btrfs_fiemap()` from inode/file operation paths that service FIEMAP requests. The implementation in `fiemap.c` performs prep, optional sync waits, inode locking, extent walking, and userspace record emission.

## State And Persistence Behavior

The header defines no persistent state. The declared API is observational: it reports mappings and may request synchronization through FIEMAP flags, but it does not itself define on-disk format or state transitions.

## Dependencies And Integration Points

This header depends on the Linux fiemap interface and Btrfs code that already has `struct inode` and `u64` visible. It integrates Btrfs inode operations with the implementation in `fiemap.c`.

## Risks And Edge Cases

- The declaration depends on compatible visibility of `struct inode` and `u64`; include ordering in callers must provide those types.
- Any signature change must be coordinated with Btrfs inode operation wiring and the implementation.

## Test Signals

Build coverage validates the declaration. Runtime coverage comes from FIEMAP ioctl tests that exercise `btrfs_fiemap()` through VFS paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/btrfs/fiemap.h -->
