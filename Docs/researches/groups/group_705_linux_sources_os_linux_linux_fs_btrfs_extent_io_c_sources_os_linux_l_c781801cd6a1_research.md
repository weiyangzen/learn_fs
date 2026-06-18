# Group Research: group_705_linux_sources_os_linux_linux_fs_btrfs_extent_io_c_sources_os_linux_l_c781801cd6a1

Scope checked against `Docs/research_subset_a.md`: all files are under included source tree `sources/os/linux/linux`.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/extent_io.c -->
# File Research: sources/os/linux/linux/fs/btrfs/extent_io.c

Read completely: 4695 lines.

This file implements Btrfs page-cache/folio I/O helpers and the in-memory `extent_buffer` layer used for metadata blocks. It covers data read/write bio construction, delayed allocation writeback, btree metadata writeback/readback, extent buffer allocation and lifetime, extent-buffer memory access primitives, bitmap helpers, release/invalidation paths, and tree-block readahead.

Core data I/O responsibilities:
- Builds and submits `btrfs_bio` instances through `btrfs_bio_ctrl`, tracking compression type, ordered-extent boundaries, writeback control, file offsets, and extent-map generations.
- Reads data folios with `btrfs_read_folio()` and `btrfs_readahead()`, locking the inode io-tree range first so extent maps are stable against ordered extent completion.
- Handles holes, inline extents, prealloc-as-hole reads, compressed reads, fsverity verification, EOF zeroing, subpage lock/uptodate bits, and checksum lookup optimization via `csum_search_commit_root`.
- Writes dirty folios through `btrfs_writepages()`, `extent_write_cache_pages()`, `extent_writepage()`, `writepage_delalloc()`, and `extent_writepage_io()`.
- Runs delalloc ranges, creates ordered extents, handles async compression/inline submission, truncation past `i_size`, COW fixups, writeback accounting, and final ordered extent completion.
- Provides `extent_write_locked_range()` for call sites that already ran delalloc and hold locked pages.

Core metadata I/O responsibilities:
- Maintains `extent_buffer` objects for btree blocks, backed by folios and indexed by `fs_info->buffer_tree`.
- Implements metadata writeback through `btree_writepages()`, `lock_extent_buffer_for_io()`, `write_one_eb()`, and `end_bbio_meta_write()`.
- Marks dirty/writeback xarray tags, updates `dirty_metadata_bytes`, observes zoned metadata write-pointer ordering, and records transaction/log-tree write errors.
- Implements metadata read through `read_extent_buffer_pages_nowait()`, `read_extent_buffer_pages()`, and `end_bbio_meta_read()`, including parent checks and buffer validation.

Extent buffer lifetime and lookup:
- Creates the `btrfs_extent_buffer` slab cache at init/exit.
- Allocates normal, dummy, cloned, and test extent buffers.
- Attaches extent-buffer folios to the btree inode filemap, including subpage metadata state sharing and private-state reference tracking.
- Uses xarray compare/exchange plus `EXTENT_BUFFER_TREE_REF`, RCU freeing, refcounts, `refs_lock`, and stale/writeback flags to handle races between lookup, release, writeback, and page reclaim.
- Provides `find_extent_buffer()`, `alloc_extent_buffer()`, `free_extent_buffer()`, `free_extent_buffer_stale()`, and `try_release_extent_buffer()`.
- Provides transaction-scoped writeback inhibition for extent buffers through `btrfs_inhibit_eb_writeback()` and `btrfs_uninhibit_all_eb_writeback()`.

Extent buffer memory helpers:
- Provides checked reads/writes/copies over extent buffers that may span multiple folios.
- Supports fast direct access through `eb->addr` when folios are physically contiguous.
- Implements `read_extent_buffer()`, `read_extent_buffer_to_user_nofault()`, `write_extent_buffer()`, `copy_extent_buffer_full()`, `copy_extent_buffer()`, `memcpy_extent_buffer()`, `memmove_extent_buffer()`, `memzero_extent_buffer()`, and `memcmp_extent_buffer()`.
- Implements byte-granular bitmap set/clear/test for Btrfs bitmap items, avoiding word alignment and endian assumptions.

Important interactions:
- Depends on `extent-io-tree` state bits for delalloc, locking, ordered completion, nodatasum, qgroup reservation, and release decisions.
- Depends on `extent_map` lookup for mapping logical file offsets to disk bytenrs, holes, inline extents, prealloc extents, and compressed extents.
- Coordinates with ordered extents, compression, fsverity, csum lookup, inode writeback control, zoned block groups, btree validation, backrefs, transaction state, and the kernel folio/page-cache APIs.
- Uses Btrfs subpage helpers extensively when sectorsize or nodesize is smaller than `PAGE_SIZE`.

Risk and correctness notes:
- This is concurrency-critical code. Correctness relies on careful lock ordering between folio locks, io-tree locks, extent-map tree locks, xarray locks, btree locks, `refs_lock`, and RCU.
- The read path deliberately waits for or skips ordered extents based on folio dirty/uptodate state; mistakes here can expose stale data or miss checksums.
- The write path has many partial-folio/subpage cases where dirty, ordered, writeback, lock, and error bits must stay aligned by sector.
- Metadata write errors are escalated to filesystem/log-tree error flags to prevent committing invalid btree roots.
- Extent-buffer release is intentionally conservative around stale buffers, tree refs, dirty/writeback state, and subpage shared folios.
- Range checks in extent-buffer memory access warn and avoid copying out-of-range data; callers still depend on valid Btrfs item offsets.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/extent_io.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/extent_io.h -->
# File Research: sources/os/linux/linux/fs/btrfs/extent_io.h

Read completely: 412 lines.

This header declares the Btrfs extent I/O and extent-buffer interface implemented by `extent_io.c`. It defines extent-buffer flags, folio operation bits, extent-buffer layout, extent changesets, offset helpers, public data/metadata I/O entry points, and extent-buffer memory primitives.

Core definitions:
- `EXTENT_BUFFER_*` flags track uptodate, dirty, tree reference, stale, writeback, unmapped, write error, zoned zeroout, and read-in-progress state.
- `PAGE_UNLOCK`, `PAGE_START_WRITEBACK`, `PAGE_END_WRITEBACK`, and `PAGE_SET_ORDERED` describe batched folio state operations.
- `EXTENT_FOLIO_PRIVATE` marks non-subpage data folios controlled by Btrfs extent I/O.
- Bitmap macros provide byte-oriented bitmap addressing for on-disk Btrfs bitmap items.
- `struct extent_buffer` stores logical start, length, folio sizing, flags, fs pointer, optional direct address, refcount/lock state, read mirror, writeback inhibitors, log-tree index, RCU hook, rwsem tree lock, and backing folio array.
- `struct btrfs_eb_write_context` carries metadata writeback context, including zoned block group state.

Extent-buffer helpers:
- `offset_in_eb_folio()`, `get_eb_offset_in_folio()`, and `get_eb_folio_index()` hide the differences between normal page-sized metadata, larger metadata blocks, large folios, and subpage metadata.
- `num_extent_pages()` reports how many base pages a metadata block spans.
- `num_extent_folios()` reports the runtime folio count, allowing for a future large-folio-backed extent buffer.
- `extent_buffer_uptodate()` wraps the runtime uptodate flag.

Changeset support:
- `struct extent_changeset` records total changed bytes and optionally records changed ranges in a `ulist`.
- `extent_changeset_init_bytes_only()` uses a sentinel prealloc pointer to avoid range tracking when only byte counts are needed.
- Inline helpers allocate, preallocate, release, and free changesets.

Declared operations:
- Data folio I/O: `btrfs_read_folio()`, `btrfs_readahead()`, `btrfs_writepages()`, and `extent_write_locked_range()`.
- Btree I/O: `btree_writepages()`, `btrfs_btree_wait_writeback_range()`, `read_extent_buffer_pages()`, and `read_extent_buffer_pages_nowait()`.
- Folio private-state helpers: `set_folio_extent_mapped()` and `clear_folio_extent_mapped()`.
- Extent-buffer lifetime: allocate, find, clone, free, stale-free, dummy allocation, test allocation, cache init/exit, and tree-block readahead.
- Extent-buffer memory access: read, write, copy, move, zero, compare, bitmap test/set/clear, dirty/uptodate state changes, and metadata dirty clearing.
- Release/invalidation helpers for folios and extent mappings.
- Writeback inhibition helpers used by transactions.

Important interactions:
- Exposes types used across Btrfs inode, btree, transaction, file, subpage, and writeback code.
- Includes Linux folio/page-cache, fiemap, btrfs tree, locks, refcount, list, and slab dependencies.
- The header is intentionally low-level: many callers use these helpers while holding Btrfs-specific locks.

Risk and correctness notes:
- The offset helpers are central for subpage metadata correctness; using plain page offsets in callers would be wrong.
- The `extent_buffer` struct is memory-sensitive and concurrency-sensitive.
- `extent_changeset` has a sentinel mode; callers must respect `extent_changeset_tracks_ranges()` before using range iteration/preallocation.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/extent_io.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/extent_map.c -->
# File Research: sources/os/linux/linux/fs/btrfs/extent_map.c

Read completely: 1396 lines.

This file implements the Btrfs in-memory extent-map cache for inode file ranges. Extent maps translate logical file offsets to disk bytenrs, holes, inline extents, prealloc extents, compression state, generation, and fast-fsync tracking state. The cache is stored as an rb-tree per inode, with a modified-extents list and an asynchronous filesystem-wide shrinker.

Core cache management:
- Creates and destroys the `btrfs_extent_map` slab cache.
- Initializes each `extent_map_tree` with an rb-root, modified list, and rwlock.
- Allocates/free extent maps with refcounting and sanity checks that freed maps are not still in the rb-tree or modified list.
- Inserts non-overlapping maps with `tree_insert()` and finds exact or nearby maps with `tree_search()`/`lookup_extent_mapping()`.
- Exposes strict lookup through `btrfs_lookup_extent_mapping()` and nearby lookup through `btrfs_search_extent_mapping()`.

Merging and validation:
- Prevents merging maps that are pinned, compressed, being logged, or still in the modified-extents list.
- Merges adjacent maps only when logical ranges, physical ranges or hole/inline markers, and flags are compatible.
- Handles merged physical extent metadata by recomputing disk bytenr, disk length, offset, and ram bytes.
- Tracks `EXTENT_FLAG_MERGED` as an in-memory-only flag.
- Performs debug-only validation of alignment and physical/ram/offset invariants.

Insertion and replacement:
- `btrfs_add_extent_mapping()` inserts a new map and handles `-EEXIST` by returning an existing covering map or trimming the new map into the gap between neighbors.
- `btrfs_replace_extent_map_range()` drops all intersecting maps and inserts a replacement, retrying if concurrent partial coverage caused another `-EEXIST`.
- `replace_extent_mapping()` swaps one rb-tree node for another while preserving modified-list semantics as requested.
- `btrfs_remove_extent_mapping()` removes a map without dropping caller-held references.

Dropping and splitting ranges:
- `btrfs_drop_extent_map_range()` removes maps intersecting an inclusive range.
- Partially overlapping maps are split into left/right remainders when spare extent maps are available.
- If split allocation fails, it removes the whole intersecting map; if that map was modified, it marks the inode for full fsync so fast fsync does not miss new extents.
- `drop_all_extent_maps_fast()` handles whole-file removal without repeated tree searches.
- `btrfs_split_extent_map()` splits a pinned modified ordered extent map into pre/mid maps when an ordered extent must be split.

Pinned/logging state:
- `btrfs_unpin_extent_cache()` clears `EXTENT_FLAG_PINNED`, sets the persisted generation, and attempts merging.
- `btrfs_clear_em_logging()` clears `EXTENT_FLAG_LOGGING` and attempts merging if the map is in the tree.
- Modified extents remain on `tree->modified_extents` for fast fsync tracking until safe removal or full-sync fallback.

Shrinker:
- Tracks evictable extent maps with `fs_info->evictable_extent_maps` for real filesystem trees.
- `btrfs_free_extent_maps()` queues asynchronous reclaim work once per pending scan request.
- The shrinker walks filesystem roots and inode xarrays, using trylocks to avoid blocking active I/O.
- `btrfs_scan_inode()` removes unpinned maps, sets full-sync on inodes when removing recent modified extents, and observes reschedule/lock-break/filesystem-closing conditions.
- Progress resumes from `em_shrinker_last_root` and `em_shrinker_last_ino`.

Important interactions:
- Used by `extent_io.c` data read/write to map file offsets to holes, inline extents, compressed extents, and disk sectors.
- Used by inode and ordered-extent code to pin newly allocated extents until ordered completion and to preserve fast-fsync correctness.
- Coordinates with `btrfs_inode::io_tree` range locks; callers dropping ranges are expected to lock relevant file ranges first.
- Uses Btrfs root/inode generation and modified-list state to decide whether cache eviction can preserve fast-fsync behavior.

Risk and correctness notes:
- The rb-tree contains non-overlapping logical ranges; all insertion/split/merge code protects that invariant.
- Extent maps may represent merged ranges that no longer correspond one-to-one with on-disk file extent items.
- Removing modified maps can cause missed fast-fsync logging unless the inode is forced to full sync; this file contains several safeguards for that.
- Shrinker code intentionally uses trylocks and asynchronous work to avoid reclaim paths blocking filesystem I/O.
- Compressed extents are not merged because physical size and decompressed offset semantics matter to read submission.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/extent_map.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/extent_map.h -->
# File Research: sources/os/linux/linux/fs/btrfs/extent_map.h

Read completely: 195 lines.

This header defines the in-memory Btrfs extent-map data model and public extent-map tree operations. Extent maps describe file logical ranges and their backing disk extents, holes, inline data, compression, preallocation, logging, pinning, generation, and reference state.

Core definitions:
- `EXTENT_MAP_LAST_BYTE`, `EXTENT_MAP_HOLE`, and `EXTENT_MAP_INLINE` are sentinel disk bytenr values above normal physical bytenrs.
- `EXTENT_FLAG_PINNED` prevents eviction/merging before a new extent is safely persisted.
- Compression flags encode zlib, LZO, and ZSTD.
- `EXTENT_FLAG_PREALLOC` marks preallocated extents.
- `EXTENT_FLAG_LOGGING` marks maps currently involved in log-tree work.
- `EXTENT_FLAG_MERGED` records that adjacent maps were combined in memory.

`struct extent_map`:
- Holds rb-tree node, logical `start` and `len`, physical `disk_bytenr` and `disk_num_bytes`, decompressed `offset` and `ram_bytes`, generation, flags, refcount, and modified-list node.
- Comments document how fields map to Btrfs file extent item fields and where inline/hole behavior differs.
- The structure is intentionally compact because large files may cache many maps.

`struct extent_map_tree`:
- Contains the rb-tree root.
- Contains `modified_extents` for fast-fsync tracking.
- Uses an rwlock for tree/list protection.

Inline helpers:
- Set and read compression flags.
- Test whether an extent map is compressed.
- Test whether a map is currently linked into the rb-tree.
- Compute effective block start: compressed maps use `disk_bytenr`, non-compressed regular maps use `disk_bytenr + offset`, and holes/inline maps return their sentinel.
- Compute exclusive logical end with overflow protection.

Declared operations:
- Tree init, lookup/search, add, remove, drop range, replace range, split map, unpin, clear logging, allocate/free, cache init/exit, and shrinker work initialization/freeing.

Important interactions:
- Consumed by Btrfs inode, file, writeback, fiemap, ordered extent, and fsync paths.
- Compression enum comes from Btrfs filesystem definitions.
- Fast-fsync behavior depends on callers preserving list and generation semantics.

Risk and correctness notes:
- Sentinel disk bytenr values must never be confused with normal physical addresses.
- `btrfs_extent_map_block_start()` intentionally differs for compressed and non-compressed extents.
- Callers must hold the appropriate `extent_map_tree` lock when mutating tree/list membership.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/extent_map.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/fiemap.c -->
# File Research: sources/os/linux/linux/fs/btrfs/fiemap.c

Read completely: 928 lines.

This file implements Btrfs FIEMAP support, translating Btrfs file extent items, holes, prealloc extents, delalloc ranges, compression state, and shared-extent checks into user-visible `fiemap` records.

Core responsibilities:
- Provides `btrfs_fiemap()` as the filesystem entry point after `fiemap_prep()`.
- Implements `extent_fiemap()` to scan file extent items over the requested range and emit FIEMAP records.
- Uses a `fiemap_cache` to merge adjacent compatible records and to buffer entries before copying to the user fiemap buffer.
- Handles regular extents, compressed extents, inline extents, explicit holes, implicit holes from `NO_HOLES`, prealloc extents, delalloc ranges, shared extents, and final extent marking.

FIEMAP cache behavior:
- `emit_fiemap_extent()` caches one pending extent, merges it with the next when logical/physical offsets and flags allow, and flushes older records into an intermediary page-sized array.
- The intermediary cache avoids deadlock when the fiemap buffer is mmaped from the same file, because direct writes to the user buffer could trigger `btrfs_page_mkwrite()` while the file range is locked.
- Handles races where ordered extents complete after the code unlocks and restarts, including overlapping newly found file extent items.
- Uses `BTRFS_FIEMAP_FLUSH_CACHE` as an internal restart signal when the intermediary cache is full.
- `emit_last_fiemap_cache()` emits the final cached extent and normalizes the max-entries return.

Tree search and cloned leaves:
- `fiemap_search_slot()` finds the first extent item at or before the requested file offset.
- It clones the leaf with `btrfs_clone_extent_buffer()` and releases the real path to avoid holding btree locks while doing expensive shared-extent backref checks.
- `fiemap_next_leaf_item()` advances through cloned leaves and reuses the clone across leaf transitions when possible.
- Cloned extent buffers are marked unmapped and preserve `start` before copying so subpage offset calculations stay correct.

Hole/prealloc processing:
- `fiemap_process_hole()` searches the inode io-tree for delalloc inside a hole or prealloc range.
- For holes, it emits delalloc extents as `FIEMAP_EXTENT_DELALLOC | FIEMAP_EXTENT_UNKNOWN`.
- For prealloc extents, it emits unwritten prealloc parts and delalloc parts separately.
- Shared-state checks for prealloc extents are done once per extent when output capacity is nonzero.

Extent scanning:
- `fiemap_find_last_extent_offset()` finds the logical end of the last real file extent, skipping explicit hole items, so the final emitted record can get `FIEMAP_EXTENT_LAST`.
- `extent_fiemap()` rounds the requested range to sectorsize, locks the inode io-tree range, searches the subvolume tree, processes implicit gaps, decodes file extent item type/compression/generation/disk bytenr, and emits records.
- Regular extents are checked with `btrfs_is_data_extent_shared()` when user output is requested.
- Compressed extents get `FIEMAP_EXTENT_ENCODED`.
- Inline extents get `FIEMAP_EXTENT_DATA_INLINE | FIEMAP_EXTENT_NOT_ALIGNED`.
- The function responds to fatal signals with `-EINTR` and periodically reschedules.

SYNC behavior:
- `btrfs_fiemap()` calls `fiemap_prep()`.
- With `FIEMAP_FLAG_SYNC`, it waits for ordered ranges before taking the inode lock and again after taking the shared inode lock.
- The second wait covers writes that may have started between initial prep/wait and inode locking.
- The extra ordered wait is especially important for compression, where initial writeback can only kick off async compression before real ordered writeback begins.

Important interactions:
- Uses subvolume tree file extent items as the primary source of extent layout.
- Uses the inode io-tree to detect delalloc inside holes/prealloc extents.
- Uses backref share-check context to report `FIEMAP_EXTENT_SHARED`.
- Uses cloned `extent_buffer` helpers from `extent_io.c`.
- Coordinates with ordered extents, compression, file locking, path release, and user fiemap buffer filling.

Risk and correctness notes:
- FIEMAP must avoid reporting overlapping extents while ordered extents may complete during restarts; cache trimming/discard logic handles those races.
- Holding the io-tree lock while emitting directly to a user buffer can deadlock if the buffer maps the same file, so this file buffers records and releases paths before final emission.
- Shared extent detection can be expensive, motivating cloned leaves and lock release.
- Delalloc detection is only meaningful up to `i_size`; preallocation may extend beyond `i_size`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/fiemap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/btrfs/fiemap.h -->
# File Research: sources/os/linux/linux/fs/btrfs/fiemap.h

Read completely: 11 lines.

This header declares the Btrfs FIEMAP entry point:

- `btrfs_fiemap(struct inode *inode, struct fiemap_extent_info *fieinfo, u64 start, u64 len)`

It includes `<linux/fiemap.h>` and wraps the declaration with a standard include guard.

Important interactions:
- Implemented by `fiemap.c`.
- Exported to Btrfs inode/file operation code that wires FIEMAP into VFS ioctl handling.

Risk and correctness notes:
- The header is only an interface declaration; all behavioral complexity is in `fiemap.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/btrfs/fiemap.h -->