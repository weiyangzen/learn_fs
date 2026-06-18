# Group Research: group_248_btrfs_linux_sources_local_fs_btrfs_linux_fs_btrfs_extent_io_c_source_249d1d59ea8a

Scope: `Docs/research_subset_a.md`, source tree `sources/local-fs/btrfs-linux`.

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/extent_io.c -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/extent_io.c

## Scope

This file implements Btrfs page-cache I/O helpers for file data plus the in-memory extent-buffer implementation used for metadata tree blocks. It covers data read/readahead, data writeback from delalloc through ordered extents and bios, btree metadata writeback, extent-buffer allocation and lookup in the fs-wide xarray, extent-buffer refcount and folio-private lifetime, metadata block reads, dirty/uptodate state propagation, release/invalidate hooks, and byte/bitmap/memcpy helpers for accessing tree blocks across folio boundaries.

It is the central bridge between Btrfs logical extents, the kernel page cache/folio APIs, bio submission, ordered extents, fsverity, metadata tree locking, subpage state, zoned metadata write ordering, and the extent map cache.

## Main APIs And Entry Points

- `extent_buffer_init_cachep()` and `extent_buffer_free_cachep()` create and destroy the extent-buffer slab cache.
- `btrfs_read_folio()` locks the requested file range, waits or skips ordered extents as appropriate, maps the file offsets through extent maps, and submits read bios.
- `btrfs_readahead()` performs the same read mapping over a readahead window, including compressed extent readahead expansion.
- `btrfs_writepages()` drives buffered data writeback through `extent_write_cache_pages()`, `writepage_delalloc()`, `extent_writepage_io()`, and `submit_one_sector()`.
- `extent_write_locked_range()` submits already-delalloc-processed locked file ranges, used by callers that have pre-created ordered extents.
- `btree_writepages()` writes dirty metadata extent buffers from `fs_info->buffer_tree` xarray tags instead of normal file page-cache dirty tags.
- `btrfs_btree_wait_writeback_range()` waits for metadata extent-buffer writeback over a logical bytenr range.
- `extent_invalidate_folio()`, `try_release_extent_mapping()`, and `try_release_extent_buffer()` are address-space release/invalidate helpers for btree/data folios.
- `alloc_extent_buffer()`, `find_extent_buffer()`, `alloc_dummy_extent_buffer()`, `btrfs_clone_extent_buffer()`, `free_extent_buffer()`, and `free_extent_buffer_stale()` implement extent-buffer creation, lookup, cloning, and lifetime.
- `read_extent_buffer_pages_nowait()` and `read_extent_buffer_pages()` submit and wait for metadata block reads with parent/key/generation validation.
- `set_extent_buffer_dirty()`, `btrfs_clear_buffer_dirty()`, `set_extent_buffer_uptodate()`, and `clear_extent_buffer_uptodate()` synchronize extent-buffer flags with per-folio or subpage state.
- `read_extent_buffer()`, `write_extent_buffer()`, `copy_extent_buffer()`, `memcpy_extent_buffer()`, `memmove_extent_buffer()`, `memzero_extent_buffer()`, `memcmp_extent_buffer()`, `extent_buffer_test_bit()`, `extent_buffer_bitmap_set()`, and `extent_buffer_bitmap_clear()` provide safe tree-block memory access.
- `btrfs_inhibit_eb_writeback()` and `btrfs_uninhibit_all_eb_writeback()` let a transaction temporarily discourage WB_SYNC_NONE metadata writeback for selected extent buffers.
- `btrfs_readahead_tree_block()` and `btrfs_readahead_node_child()` perform nonblocking metadata readahead for tree blocks and node children.

## Control Flow And Behavior

Data read starts by locking the inode `io_tree` range and reconciling any overlapping ordered extents. `lock_extents_for_read()` can skip waiting when the locked folios are already dirty or uptodate in ways that cannot be helped by waiting; otherwise it starts and waits ordered extent completion, then retries. `btrfs_do_readpage()` sets folio-private state, zeros beyond i_size, handles already-uptodate sectors, gets cached extent maps through `get_extent_map()`, and distinguishes holes, inline extents, prealloc-as-hole reads, regular extents, and compressed extents. Regular sectors are merged into bios when file offsets and disk sectors are contiguous; compressed reads are kept grouped by compression type and by extent-map identity to avoid corrupting aliased references to the same compressed physical extent.

Data read endio validates fsverity before setting folio uptodate bits, zeros partial EOF sectors, clears subpage lock state, and releases bios. For data reads older than the current fs generation, bio submission can set `csum_search_commit_root` so checksum lookup can use the commit root.

Data writeback first walks dirty folios with normal writeback indexing and tagging semantics. `writepage_delalloc()` captures the dirty/subpage bitmap, locks delalloc ranges with `find_lock_delalloc_range()`, runs `btrfs_run_delalloc_range()`, and removes asynchronously handled compression/inline ranges from the submission bitmap. `extent_writepage_io()` performs COW fixup, maps each remaining sector through `btrfs_get_extent()`, handles sectors beyond i_size by truncating ordered extents, marks dirty/writeback/ordered bits, and submits bios. Endio clears ordered and writeback bits, sets mapping errors, and completes the ordered extent.

Write bio assembly is managed by `struct btrfs_bio_ctrl`. It tracks the current `btrfs_bio`, next file offset, compression type, ordered extent boundary, writeback control, cgroup ownership, readahead state, and last compressed extent-map start. Data write bios are capped at ordered extent boundaries and initialized with the latest device for cgroup writeback compatibility. Errors before submission finish affected ordered sectors manually so stale dirty bits do not cause later writeback without an ordered extent.

Metadata writeback uses `fs_info->buffer_tree`, an xarray indexed by nodesize units. Dirty extent buffers are tagged with xarray marks; WB_SYNC_ALL first moves dirty marks to TOWRITE. `btree_writepages()` batches tagged EBs, checks zoned metadata write-pointer constraints, locks each EB for I/O, clears DIRTY, sets WRITEBACK, updates dirty metadata accounting, zeroes unused leaf/node regions in `prepare_eb_write()`, builds one metadata bio, and submits it. Metadata write endio clears metadata folio writeback bits, clears the xarray writeback mark, wakes waiters, and records btree/log write errors in fs-wide flags.

Extent buffers are allocated around the btree inode page cache. `alloc_extent_buffer()` validates alignment, handles 32-bit page-cache limits, preallocates subpage folio state when needed, allocates folios, attaches them to the btree inode filemap, reuses existing folios/EBs if races are found, sets lockdep class by owner root and tree level, computes an optional direct `addr` when backing pages are physically contiguous, then inserts into `fs_info->buffer_tree`. The `EXTENT_BUFFER_TREE_REF` bit represents the xarray's reference; `check_buffer_tree_ref()` repairs races before I/O or access paths so release_folio cannot drop the tree reference while new users are active.

Extent-buffer freeing is split between normal and stale paths. `free_extent_buffer()` uses a fast atomic decrement when safely above low refcounts, otherwise takes `refs_lock`. If an EB is stale, has only the tree and caller references, and is not dirty or under writeback, the tree reference can be dropped. The final release removes the xarray entry with cmpxchg, detaches folio-private state, and frees through RCU unless it is an unmapped test/dummy buffer.

Metadata reads use `EXTENT_BUFFER_READING` to serialize concurrent reads. If the EB is already uptodate, `btrfs_buffer_uptodate()` validates it against the requested parent check. Otherwise `read_extent_buffer_pages_nowait()` sets READING, takes a ref for endio, builds a metadata read bio over all EB folios, and submits it. Endio records the mirror, validates the tree block via `btrfs_validate_extent_buffer()`, sets or clears uptodate state, clears READING, drops the EB ref, and releases the bio.

The byte access helpers hide whether an EB is backed by one contiguous virtual address, multiple page-sized folios, or a subpage-positioned metadata block. All public read/write/copy helpers validate the EB-relative range before touching memory. Bitmap operations intentionally operate with byte granularity because on-disk bitmap items are little-endian and may straddle page boundaries.

## State And Data Structures

- `struct btrfs_bio_ctrl` carries in-progress data bio state, compression mode, ordered extent boundary, csum generation optimization, writeback control, submit bitmap, readahead control, and compressed extent-map identity.
- `struct extent_buffer` fields managed here include logical `start`, `len`, `folio_size`, `folio_shift`, `addr`, `bflags`, `refs`, `refs_lock`, `writeback_inhibitors`, `log_index`, `read_mirror`, `lock`, folio array, and debug leak list.
- Extent-buffer flags include UPTODATE, DIRTY, TREE_REF, STALE, WRITEBACK, UNMAPPED, WRITE_ERR, ZONED_ZEROOUT, and READING.
- Per-folio Btrfs subpage/private state tracks data dirty/lock/ordered/writeback/uptodate bits and metadata EB refs/dirty/writeback/uptodate bits.
- `fs_info->buffer_tree` is the xarray of live metadata EBs, with PAGECACHE_TAG_DIRTY, PAGECACHE_TAG_WRITEBACK, and PAGECACHE_TAG_TOWRITE marks.
- `fs_info->dirty_metadata_bytes`, fs error flags, log write error flags, zoned metadata state, and transaction writeback inhibition xarrays are updated here.

## Dependencies

- Extent state and delalloc helpers from `extent-io-tree.c`.
- Extent maps from `extent_map.c` and `btrfs_get_extent()`.
- Ordered extent lifecycle, delalloc running, compression, inline extent handling, and COW fixup from inode/file code.
- Bio allocation/submission and checksum handling from `bio.c` and file-item checksum code.
- Metadata validation and tree parent checks from disk I/O/tree-checking paths.
- Subpage state helpers, zoned metadata/data relocation locks, block-group write pointer checks, fsverity, writeback control, cgroup writeback accounting, and kernel folio/page-cache APIs.

## Risks And Invariants

- Read paths must hold the inode extent lock while getting a stable view of extent maps and ordered extents; otherwise reads can race ordered extent completion and observe stale or missing file extent items.
- Compressed reads cannot be merged solely by physical bytenr. Different file ranges can reference the same compressed extent with different offsets, so the code forces bio splits by extent-map start.
- Delalloc writeback must either submit every created ordered range or explicitly mark it finished on error. Leaving dirty bits without an ordered extent can cause later writeback corruption.
- Subpage filesystems require per-sector dirty, ordered, writeback, lock, and uptodate accounting; full-folio flags alone are insufficient.
- Metadata write errors must be recorded outside the EB itself, because the EB may be released before transaction commit detects the error.
- Extent-buffer `TREE_REF` handling is race-sensitive. It is the xarray reference, and release_folio may clear it only when the EB is otherwise unreferenced and not under I/O.
- Folio private state for metadata must be changed under `mapping->i_private_lock` when the EB is mapped in the btree inode.
- `EXTENT_BUFFER_READING` must not be cleared after setting UPTODATE too early; other readers can otherwise return without waiting for validation and I/O completion.
- Zoned metadata writeback relies on serialized write-pointer checks and `meta_write_pointer` advancement before submission.
- Bitmap helpers must preserve byte-order and cross-page behavior; replacing them with word operations would break on-disk bitmap format assumptions.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/extent_io.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/extent_io.h -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/extent_io.h

## Scope

This header defines the public data structures, flags, inline helpers, and exported APIs for Btrfs extent-buffer metadata blocks and folio/page-cache I/O support implemented in `extent_io.c`.

## Types And Data Structures

- The extent-buffer flag enum defines UPTODATE, DIRTY, TREE_REF, STALE, WRITEBACK, UNMAPPED, WRITE_ERR, ZONED_ZEROOUT, and READING bits.
- The page operation enum defines flags used by contiguous folio processing: unlock, start writeback, end writeback, and set ordered.
- `EXTENT_FOLIO_PRIVATE` is the non-subpage folio-private sentinel for folios managed by Btrfs extent state.
- Bitmap macros define byte-granular addressing and first/last byte masks for extent-buffer bitmap items.
- `struct extent_buffer` models a metadata tree block in memory: logical bytenr, nodesize length, backing folio geometry, direct address if possible, flags, fs_info, refcounting, read mirror, writeback inhibitors, log index, RCU head, tree lock, and inline folio array.
- `struct btrfs_eb_write_context` carries writeback control plus the target EB and zoned block group.
- `struct extent_changeset` records bytes changed and optionally a `ulist` of changed ranges for extent-state operations.

## Inline Helpers

- `offset_in_eb_folio()` and `get_eb_offset_in_folio()` compute offsets for normal and subpage/nodesize-less-than-page cases.
- `get_eb_folio_index()` maps an EB-relative offset to the backing folio index.
- `extent_changeset_init()`, `extent_changeset_init_bytes_only()`, `extent_changeset_prealloc()`, `extent_changeset_release()`, and `extent_changeset_free()` manage optional changed-range tracking.
- `wait_on_extent_buffer_writeback()` waits for EB metadata writeback completion.
- `num_extent_pages()` and `num_extent_folios()` compute backing page/folio counts while allowing future high-order folios.
- `extent_buffer_uptodate()` tests EB UPTODATE state.
- UUID header writers wrap `write_extent_buffer()` for fsid/chunk tree UUID fields.

## Public API Surface

The header exposes data read/write/readahead entry points, delalloc clearing, release/invalidate helpers, data folio mapping helpers, extent-buffer allocation/lookup/free/clone, metadata reads, metadata writeback wait, metadata dirty/uptodate state changes, EB byte operations, bitmap operations, page/folio array allocation helpers, debug leak checks, sanity-test allocation, and transaction-scoped EB writeback inhibition.

## Dependencies And Consumers

It includes core kernel folio, rbtree, refcount, rwsem, list, fiemap, and Btrfs tree definitions, and forward-declares Btrfs inode/root/fs/transaction types. Consumers include btree block management, disk I/O, tree modification code, inode read/write paths, compression, fsync/logging, zoned metadata writeback, free-space and extent-tree code, and tests.

## Risks And Invariants

- `struct extent_buffer` assumes at most `INLINE_EXTENT_BUFFER_PAGES` folios, derived from maximum metadata block size and page size.
- EB offset helpers must handle both sectorsize equal to page size and subpage nodesize cases.
- Folio-private values differ between regular and subpage modes; callers must use the helpers rather than interpreting private pointers directly.
- `extent_changeset` can be bytes-only; callers must check `extent_changeset_tracks_ranges()` before using the ulist as a range list.
- Most EB access functions assume the EB has been read and validated or is explicitly unmapped/dummy.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/extent_io.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/extent_map.c -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/extent_map.c

## Scope

This file implements Btrfs in-memory file extent maps: allocation, rb-tree insertion/search/removal, merging adjacent compatible mappings, unpinning maps after ordered extent completion, replacing/dropping ranges, splitting pinned maps, and asynchronous memory-pressure reclaim. Extent maps cache file logical ranges, holes, inline extents, prealloc extents, compression state, physical disk ranges, generation, and fsync logging state.

## Main APIs And Entry Points

- `btrfs_extent_map_init()` and `btrfs_extent_map_exit()` manage the extent-map slab cache.
- `btrfs_extent_map_tree_init()` initializes an inode's extent-map tree and modified-extents list.
- `btrfs_alloc_extent_map()` and `btrfs_free_extent_map()` allocate and release refcounted extent maps.
- `btrfs_lookup_extent_mapping()` finds the first map intersecting a range.
- `btrfs_search_extent_mapping()` finds an intersecting or nearby map for conflict handling.
- `btrfs_add_extent_mapping()` inserts a new map, returning an existing map or trimming/merging on insertion races.
- `btrfs_remove_extent_mapping()` removes a map from an inode tree without dropping caller references.
- `btrfs_drop_extent_map_range()` removes all maps intersecting a range and splits partially overlapping maps when possible.
- `btrfs_replace_extent_map_range()` repeatedly drops a target range and inserts a replacement map until insertion no longer races.
- `btrfs_split_extent_map()` splits a pinned ordered extent map into pre and remaining pieces when an ordered extent is split.
- `btrfs_unpin_extent_cache()` clears PINNED after successful writeback, updates generation, and attempts merging.
- `btrfs_clear_em_logging()` clears LOGGING and attempts merging if safe.
- `btrfs_free_extent_maps()` schedules asynchronous extent-map reclaim, and `btrfs_init_extent_map_shrinker_work()` initializes that work item.

## Control Flow And Behavior

Extent maps are stored in an inode-local rb-tree keyed by file offset. `tree_insert()` rejects overlaps and double-checks neighboring nodes. `tree_search()` returns an exact containing node when possible or a nearby predecessor/successor for callers that need merge/conflict context. Lookups take an extra reference on returned maps; the tree itself owns a reference for inserted maps.

Insertion validates map alignment and physical fields in debug builds. `add_extent_mapping()` inserts directly and then either links the map into `modified_extents` or tries to merge it with neighbors. `btrfs_add_extent_mapping()` handles `-EEXIST` races from concurrent readers/writers: if the requested start falls inside an existing map, it returns that existing map to the caller; otherwise it trims the new map to the gap between neighboring maps and inserts that reduced range.

Merging is intentionally conservative. Maps cannot merge if pinned, compressed, logging, or still on the modified-extents list. `try_merge_map()` also refuses to mutate a map with more than the tree and current-task references, because another user could observe partially updated fields. Merge compatibility requires adjacent logical ranges, equal flags ignoring MERGED, and either physically adjacent regular extents or equal special disk markers for holes/inline. `merge_ondisk_extents()` updates the physical extent envelope and logical offset so maps that cover adjacent parts of one or more regular data extents remain coherent.

Pinned maps represent extents not yet fully persisted. `btrfs_unpin_extent_cache()` looks up the exact start, warns on missing or unexpected maps, records the generation that inserted the file item, clears PINNED, and then tries to merge. `btrfs_clear_em_logging()` clears LOGGING after fsync no longer needs to protect the map from merging.

Range dropping removes every map intersecting `[start, end]`. Fully covered maps are removed directly. Partially covered maps are split into left and/or right replacement maps if spare allocations are available; if splitting a modified map fails due to allocation shortage, the whole map is removed and the inode is marked for full fsync so fast fsync cannot miss new extents. Pinned maps can be skipped when requested.

`btrfs_replace_extent_map_range()` wraps range dropping plus insertion for callers that need an exact replacement, retrying on `-EEXIST` because unrelated partial maps may be inserted while the caller held only the appropriate inode IO-tree lock.

The extent-map shrinker runs asynchronously. It walks filesystem roots and inodes using remembered root/inode cursors, tries to take extent-map tree write locks without blocking, skips empty trees, and scans maps until its budget is consumed. Before removing a modified map from the current or newer fs generation, it takes `i_mmap_lock` in read mode and marks the inode full-sync, avoiding races with fast fsync's inode logging phase. Pinned maps are not reclaimed.

## State And Data Structures

- `struct extent_map` stores rb-node, file `start/len`, `disk_bytenr`, `disk_num_bytes`, decompressed `offset/ram_bytes`, `generation`, flags, refcount, and modified-extents list node.
- `struct extent_map_tree` stores the rb-tree root, modified-extents list, and rwlock.
- Flags handled here include PINNED, compression type bits, PREALLOC, LOGGING, and MERGED.
- `fs_info->evictable_extent_maps` counts reclaimable maps for normal filesystem roots.
- `fs_info->em_shrinker_nr_to_scan`, `em_shrinker_work`, `em_shrinker_last_root`, and `em_shrinker_last_ino` coordinate async shrinker progress.

## Dependencies

This file depends on inode/root/fs structures, Btrfs compression flags, fs generation, fsync full-sync marking, ordered extent semantics, testing-mode checks, root radix/inode xarray traversal, tracing hooks, and kernel rb-tree/refcount/slab primitives.

## Risks And Invariants

- Callers that mutate an extent-map tree must hold `extent_tree.lock` in write mode; lookup callers must obey the tree lock contract used by their path.
- Inserted maps carry an extra tree reference. Removal and replacement must drop the tree reference separately from lookup/caller references.
- Pinned and logging maps must not be merged or removed blindly, because ordered extent completion and fast fsync depend on their exact identity.
- Compressed maps are never merged because physical compressed size and offset semantics do not match logical contiguity.
- Removing a modified current-generation map can make fast fsync miss it; the code must mark the inode full-sync in those cases.
- Partial range-drop split allocation failure is tolerated only because the map can be reloaded from disk and full fsync is forced if logging correctness needs it.
- `try_merge_map()` must avoid modifying maps with external users, because field updates are not atomic as a group.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/extent_map.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/extent_map.h -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/extent_map.h

## Scope

This header defines the Btrfs extent-map data model, special disk address sentinels, extent-map flags, compression helpers, range helpers, and public extent-map tree APIs implemented in `extent_map.c`.

## Types And Constants

- `EXTENT_MAP_LAST_BYTE`, `EXTENT_MAP_HOLE`, and `EXTENT_MAP_INLINE` are special `disk_bytenr` sentinel values above valid physical addresses.
- Extent-map flags track pinned extents, compression algorithms, preallocation, logging, and maps merged from adjacent source maps.
- `struct extent_map` is a compact cached representation of file extents and holes. It intentionally may represent merged ranges, so fields match on-disk file extent items only before merging.
- `struct extent_map_tree` contains the rb-tree, modified-extents list, and rwlock for one inode.

## Inline Helpers

- `btrfs_extent_map_set_compression()` sets the compression flag matching a Btrfs compression type.
- `btrfs_extent_map_compression()` returns the compression type encoded in flags.
- `btrfs_extent_map_is_compressed()` tests compression flags efficiently.
- `btrfs_extent_map_in_tree()` tests rb-node membership.
- `btrfs_extent_map_block_start()` returns the physical start used for I/O, adding logical offset for uncompressed regular extents but not for compressed extents.
- `btrfs_extent_map_end()` returns exclusive logical end and saturates on overflow.

## Public API Surface

The header exposes tree initialization, lookup/search, add/remove/replace/drop/split operations, allocation/free, slab init/exit, unpinning, clearing logging state, memory-pressure reclamation, and shrinker work initialization.

## Dependencies And Consumers

It includes Btrfs `fs.h` for compression types and core structures and is consumed by inode read/write paths, fiemap, fsync/logging, ordered extent completion, page release, and direct/buffered I/O code that needs cached logical-to-physical mapping.

## Risks And Invariants

- `disk_bytenr` sentinels must be compared with `EXTENT_MAP_LAST_BYTE`; valid physical bytenrs are below that range.
- For compressed extents, `block_start()` intentionally ignores `offset`; callers must not apply uncompressed offset rules.
- Merged maps trade exact on-disk item boundaries for memory efficiency, so consumers needing exact file extent item boundaries must consult the tree.
- The structure is kept compact because many maps can exist under memory pressure.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/extent_map.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/fiemap.c -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/fiemap.c

## Scope

This file implements Btrfs FIEMAP reporting for regular files. It walks file extent items, reports inline, regular, compressed, shared, preallocated, hole, and delalloc ranges, merges compatible adjacent FIEMAP records, buffers emitted entries to avoid self-deadlocks, and coordinates with ordered extents and the inode IO tree for a stable enough view of file layout.

## Main APIs And Entry Points

- `btrfs_fiemap()` is the public entry point called by inode operations. It performs generic FIEMAP preparation, optional sync/writeback waiting, inode shared locking, and delegates to `extent_fiemap()`.
- `extent_fiemap()` performs the main scan over the requested range, locks the inode IO-tree range, finds the last meaningful extent, searches the subvolume tree for file extent items, processes holes and extents, handles cache flushing/restart, and emits final buffered entries.
- `emit_fiemap_extent()` merges or buffers FIEMAP extents and signals when the intermediate buffer must be flushed.
- `flush_fiemap_cache()` and `emit_last_fiemap_cache()` write buffered entries to the user FIEMAP buffer.
- `fiemap_search_slot()` finds the first relevant file extent item and clones the leaf for long processing.
- `fiemap_next_leaf_item()` advances within or across leaves while reusing a cloned leaf when possible.
- `fiemap_process_hole()` reports delalloc inside holes or prealloc extents and reports unwritten portions of prealloc extents.
- `fiemap_find_last_extent_offset()` finds the end of the last non-hole file extent item so the last returned extent can receive `FIEMAP_EXTENT_LAST`.

## Control Flow And Behavior

`btrfs_fiemap()` first calls `fiemap_prep()`. If `FIEMAP_FLAG_SYNC` is set, it waits for all ordered extents before taking the inode shared lock, then waits again after the lock because new writes may have started between the initial flush and locking. This is necessary for compression: the generic write-and-wait can start async compression without waiting for compressed writeback and ordered extent completion.

`extent_fiemap()` rounds the requested range to sectorsize boundaries and locks that inode IO-tree range. It finds the last extent end independently from i_size because preallocation can extend past EOF. It then searches for the first file extent item at or before the requested range. The btree leaf is cloned so expensive backref sharedness checks and user-buffer emission do not keep a live subvolume tree leaf locked for too long or trigger lockdep recursion during backref walking.

The main loop processes implicit holes before the current file extent item, then handles the item by type. Inline extents are reported with DATA_INLINE and NOT_ALIGNED. Regular extents report physical bytenr plus file extent offset, and compressed extents add ENCODED while avoiding uncompressed offset adjustment. Prealloc extents and explicit holes are delegated to `fiemap_process_hole()`, which searches the io_tree for delalloc ranges and emits DELALLOC|UNKNOWN records where dirty delayed allocation exists.

Preallocated extents are split for reporting: unwritten sections are emitted with FIEMAP_EXTENT_UNWRITTEN, while delalloc subsections are emitted as DELALLOC|UNKNOWN. Sharedness for regular and prealloc extents is computed with `btrfs_is_data_extent_shared()` only when the user requested actual extents (`fi_extents_max` nonzero); the result adds FIEMAP_EXTENT_SHARED.

`emit_fiemap_extent()` caches one pending extent and merges adjacent entries only when logical addresses, physical addresses, and flags are continuous/equal. It also handles races where the scan had to unlock and restart: newly completed ordered extents can split or replace previously observed delalloc/hole/prealloc ranges, so the cache trims, discards, or partially advances entries to avoid overlapping FIEMAP output.

The intermediate entry array prevents deadlock when the user's FIEMAP buffer is mmaped from the same file. Writing to that buffer may fault through `btrfs_page_mkwrite()` and try to lock the same inode extent range. Therefore `extent_fiemap()` flushes buffered entries only after unlocking the io_tree range and releasing the path. If the cache fills while scanning, it returns the private `BTRFS_FIEMAP_FLUSH_CACHE` sentinel, flushes entries, updates `start/len` to `next_search_offset`, and restarts.

At EOF, if the cached entry reaches the last non-hole extent end and there is no later delalloc before i_size, `FIEMAP_EXTENT_LAST` is added. The final path is freed before flushing to user memory for the same deadlock avoidance reason.

## State And Data Structures

- `struct btrfs_fiemap_entry` is the buffered output tuple: logical offset, physical address, length, and FIEMAP flags.
- `struct fiemap_cache` stores the intermediate entries array, fill position, next restart offset, mapped extent count, and one cached unsubmitted extent.
- `BTRFS_FIEMAP_FLUSH_CACHE` is a private non-errno sentinel telling the caller to unlock, flush buffered entries, and restart scanning.
- `btrfs_backref_share_check_ctx` is reused across sharedness checks and tracks the current cloned leaf bytenr for optimization.
- Cached `extent_state` pointers are used for the locked FIEMAP range and delalloc searches.

## Dependencies

This file depends on Btrfs inode locking, io_tree extent locking, file extent item accessors, path/leaf navigation, extent-buffer cloning/copying, delalloc range search, ordered extent waiting, backref sharedness checks, generic FIEMAP helpers, and kernel signal/reschedule handling.

## Risks And Invariants

- FIEMAP must not emit overlapping extents even when ordered extents complete after the scan unlocks and restarts.
- User-buffer writes must happen after releasing inode extent locks and btree paths, because the buffer may be mmaped from the target file and fault back into Btrfs.
- The cloned leaf's `start` must be set before copying contents, especially for subpage metadata where `start` affects EB folio offset calculations.
- Sharedness checks can be expensive and can lock tree blocks; using a cloned leaf avoids holding live tree locks during that work.
- `FIEMAP_EXTENT_LAST` must account for prealloc past i_size and delalloc after the last file extent.
- `FIEMAP_FLAG_SYNC` requires ordered extent completion beyond generic filemap writeback, particularly for compressed writes.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/fiemap.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/fiemap.h -->
# File Research: sources/local-fs/btrfs-linux/fs/btrfs/fiemap.h

## Scope

This small header declares the Btrfs FIEMAP entry point implemented in `fiemap.c`.

## Public API Surface

- `btrfs_fiemap(struct inode *inode, struct fiemap_extent_info *fieinfo, u64 start, u64 len)` reports file extent layout to the generic FIEMAP infrastructure.

## Dependencies And Consumers

The header includes `<linux/fiemap.h>` and is consumed by Btrfs inode/file operation code that wires FIEMAP into VFS ioctls.

## Risks And Invariants

- Callers rely on `btrfs_fiemap()` to perform FIEMAP preparation, optional sync handling, inode locking, and Btrfs-specific extent reporting. The header intentionally exposes no internal cache or scan helpers.
<!-- END FILE RESEARCH: sources/local-fs/btrfs-linux/fs/btrfs/fiemap.h -->