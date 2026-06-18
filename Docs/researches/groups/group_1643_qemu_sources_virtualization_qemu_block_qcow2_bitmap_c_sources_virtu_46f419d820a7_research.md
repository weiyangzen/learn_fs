# Group Research: group_1643_qemu_sources_virtualization_qemu_block_qcow2_bitmap_c_sources_virtu_46f419d820a7

Scope: `Docs/research_subset_a.md` includes `sources/virtualization/qemu`. The requested internal group report path was not present, so this report is based on complete reads of the three listed source files.

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/qcow2-bitmap.c -->
# File Research: sources/virtualization/qemu/block/qcow2-bitmap.c

## Purpose

Implements qcow2 persistent dirty bitmap support. It serializes QEMU `BdrvDirtyBitmap` objects into the qcow2 bitmap extension, loads them back on open, reports bitmap metadata, removes persistent bitmaps, and handles read-only/read-write reopen transitions. The file is specifically responsible for the on-disk bitmap directory, bitmap tables, bitmap data clusters, and the consistency protocol using the `IN_USE` and `AUTO` flags.

## Main Data Structures

- `Qcow2BitmapDirEntry`: packed on-disk bitmap directory entry. Contains bitmap table offset/size, flags, type, granularity, name length, and extra-data length.
- `Qcow2BitmapTable`: in-memory description of an on-disk bitmap table: offset and number of 64-bit entries.
- `Qcow2Bitmap`: in-memory list item combining table metadata, flags, granularity, name, and optional `BdrvDirtyBitmap *`.
- `Qcow2BitmapList`: simple queue of `Qcow2Bitmap`.
- `BitmapType`: currently only `BT_DIRTY_TRACKING_BITMAP = 1`.

## Format Limits And Validation

The file defines the qcow2 bitmap extension constraints:

- Maximum bitmap table entries: `BME_MAX_TABLE_SIZE`.
- Maximum physical bitmap size in RAM: `BME_MAX_PHYS_SIZE`.
- Granularity bounds: 2^9 through 2^31.
- Maximum bitmap name size equals `BDRV_BITMAP_MAX_NAME_SIZE`.
- Directory reserved flags are rejected with `BME_RESERVED_FLAGS`.
- Table entry reserved bits are rejected with `BME_TABLE_ENTRY_RESERVED_MASK`.
- Table entries either point to cluster-aligned data clusters or encode an all-ones optimization with `BME_TABLE_ENTRY_FLAG_ALL_ONES`.

Important validators:

- `check_table_entry()` rejects reserved bits, illegal all-ones use with nonzero offsets, and unaligned data offsets.
- `check_constraints_on_bitmap()` validates image length, granularity, computed serialized size, and name length for a bitmap to be stored.
- `check_dir_entry()` validates directory entry fields, type, flags, table bounds, cluster alignment, physical bitmap size, and whether the stored table is large enough for the current virtual image length when the bitmap is valid.

## Bitmap Table And Data I/O

- `bitmap_table_load()` reads a bitmap table from disk, converts entries from big endian, and validates every entry.
- `clear_bitmap_table()` frees all data clusters referenced by a bitmap table and clears their table entries.
- `free_bitmap_clusters()` loads a table, frees all referenced bitmap data clusters, frees the table cluster range, and clears the in-memory table metadata.
- `load_bitmap_data()` deserializes bitmap content from the table into a `BdrvDirtyBitmap`.
  - Empty table entries deserialize as zero ranges.
  - Entries with `BME_TABLE_ENTRY_FLAG_ALL_ONES` deserialize as all-dirty ranges.
  - Nonzero offsets are read from disk cluster by cluster.
- `store_bitmap_data()` allocates one qcow2 cluster for each serialized dirty bitmap cluster that actually contains dirty bits, writes serialized data clusters, and builds the bitmap table.
- `store_bitmap()` writes the bitmap table itself, after storing bitmap data, then records the resulting table offset and size.

## Bitmap Directory Handling

The bitmap directory is loaded and stored through a private list abstraction:

- `bitmap_list_load()` reads the directory, converts each entry to CPU endian, validates structure and constraints, rejects unsupported extra data, enforces the header bitmap count, and builds a `Qcow2BitmapList`.
- `bitmap_list_store()` calculates directory size, writes directory entries in big-endian format, and either updates in place or allocates a new directory.
- `bitmap_directory_to_be()` walks the variable-length directory entries and endian-swaps each entry.
- Helper functions calculate entry size, locate names, copy names, and advance to the next directory entry.

This file treats directory corruption conservatively. Mismatched counts, unsupported extra data, invalid constraints, and malformed variable-length entries fail load and can increment check corruption counters.

## Header Update Protocol

Persistent bitmap metadata is protected by the qcow2 autoclear bitmap feature bit:

- `update_header_sync()` updates the qcow2 header and flushes the protocol file.
- `update_ext_header_and_dir_in_place()` clears `QCOW2_AUTOCLEAR_BITMAPS`, flushes the header, updates the existing directory in place, flushes again, then restores the autoclear bit and flushes. This is used for safe `IN_USE` flag updates where the directory size and bitmap count are unchanged.
- `update_ext_header_and_dir()` allocates and writes a new bitmap directory when the set of bitmaps changes, updates header fields, flushes caches/header, and frees the old directory after success. On failure it frees newly allocated directory clusters and restores the old in-memory header state.

The ordering is central: if an update fails while autoclear is cleared, older QEMU versions or repair tools can discard leaked or inconsistent bitmap metadata safely.

## Loading Persistent Bitmaps

`qcow2_load_dirty_bitmaps()` is called during image open/invalidation:

- If no bitmap extension exists, it returns success immediately.
- Loads the bitmap directory.
- For each bitmap:
  - If the bitmap is marked `IN_USE` and a matching RAM bitmap already exists, it skips loading, supporting shared-storage migration cases.
  - Otherwise creates a dirty bitmap with the stored granularity and name.
  - If `IN_USE` is set, it does not trust the on-disk contents and marks the RAM bitmap inconsistent.
  - If `IN_USE` is clear, it loads bitmap data and then marks the directory entry `IN_USE` so the bitmap is protected while QEMU controls it.
  - If `AUTO` is clear, it disables the bitmap.
- If any `IN_USE` flags must be set and the image can be written, it updates the directory in place.
- If the image cannot be written, created bitmaps become read-only.

Failure releases any bitmaps created during that load attempt.

## Reporting Bitmap Info

`qcow2_get_bitmap_info_list()` loads the bitmap directory and returns QAPI bitmap info objects with:

- Name.
- Granularity.
- User-visible flags derived from `BME_FLAG_IN_USE` and `BME_FLAG_AUTO`.

## Reopen Transitions

`qcow2_reopen_bitmaps_rw()` handles read-only to read-write behavior:

- Loads the directory and matches each stored bitmap to an in-memory bitmap.
- If an on-disk bitmap is not marked `IN_USE`, its RAM bitmap must be read-only and consistent; then the directory is updated to set `IN_USE`.
- If an on-disk bitmap is already `IN_USE`, read-only consistent RAM state is treated as suspicious and rejected.
- After successful directory updates, previously read-only RAM bitmaps are made writable.

`qcow2_reopen_bitmaps_ro()` stores persistent dirty bitmaps without releasing them, then marks persistent RAM bitmaps read-only.

## Storing Persistent Bitmaps

`qcow2_store_persistent_dirty_bitmaps()` is the main persistence writer:

- Loads the current bitmap list or creates an empty one.
- Iterates all block dirty bitmaps.
- Skips nonpersistent and inconsistent bitmaps.
- Keeps read-only persistent bitmaps without rewriting data, but associates them with existing directory entries so they may be released if requested.
- For writable persistent bitmaps:
  - Validates constraints.
  - Adds new directory entries as needed.
  - For existing entries, requires the old entry to be `IN_USE`; old table metadata is queued for freeing after success.
  - Stores data clusters and table clusters.
- Updates the bitmap extension directory/header.
- Frees old bitmap tables only after the new directory has been committed.
- On failure, frees newly written bitmap data/table clusters and leaves old tables intact.

The `release_stored` option is used by inactivation/close/migration flows to release RAM bitmaps after successful store.

## Removal And Resize Checks

`qcow2_co_remove_persistent_dirty_bitmap()` removes a named persistent bitmap:

- If no bitmap extension or no matching bitmap exists, it succeeds.
- Holds `s->lock`, loads the bitmap list, removes the entry, updates extension header/directory, then frees the removed bitmap clusters.

`qcow2_truncate_bitmaps_check()` ensures persistent bitmaps can tolerate image resize:

- All persistent bitmaps must be loaded into RAM.
- Each must pass normal dirty bitmap checks, including not being inconsistent.

## Creation Capability And Size Estimation

`qcow2_co_can_store_new_dirty_bitmap()` checks whether a new persistent bitmap can be created:

- Rejects duplicate names.
- Requires qcow2 v3 or later because v2 lacks autoclear feature support.
- Checks bitmap constraints.
- Checks maximum bitmap count and bitmap directory size.

`qcow2_supports_persistent_dirty_bitmap()` returns whether the image version supports persistent dirty bitmaps.

`qcow2_get_persistent_dirty_bitmap_size()` estimates space needed to copy persistent bitmaps into an image with a given cluster size, including worst-case bitmap data, bitmap table entries, and directory contribution.

## Error And Consistency Model

The file consistently separates unsafe/inconsistent states from valid bitmap contents:

- `IN_USE` means the on-disk bitmap data may be stale or under active ownership.
- Cleanly stored bitmaps clear `IN_USE`; loading writable images sets it again before exposing mutable RAM state.
- Directory/header updates use autoclear ordering to avoid leaving metadata that unsupported readers would preserve incorrectly.
- Old bitmap clusters are freed only after a new directory is durable enough to reference replacement metadata.
- Validation rejects malformed directory and table inputs before bitmap data is trusted.

## Interactions

This file depends heavily on:

- `block/dirty-bitmap.h` serialization/deserialization APIs.
- qcow2 allocation/free helpers such as `qcow2_alloc_clusters()` and `qcow2_free_clusters()`.
- overlap checks via `qcow2_pre_write_overlap_check()`.
- header updates via `qcow2_update_header()`.
- qcow2 state fields: bitmap directory offset/size, bitmap count, autoclear flags, version, cluster size, and lock.
<!-- END FILE RESEARCH: sources/virtualization/qemu/block/qcow2-bitmap.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/qcow2-cache.c -->
# File Research: sources/virtualization/qemu/block/qcow2-cache.c

## Purpose

Implements the shared in-memory cache used by qcow2 L2 table slices and refcount blocks. The cache provides fixed-size table slots, reference counting for checked-out entries, dirty tracking, LRU replacement, writeback ordering, and dependency handling between caches and protocol flushes.

## Main Data Structures

- `Qcow2CachedTable`:
  - `offset`: on-disk offset of the cached table, or zero for empty.
  - `lru_counter`: replacement/cleanup age marker.
  - `ref`: number of active users holding the cached table.
  - `dirty`: whether it must be written back.
- `Qcow2Cache`:
  - Array of `Qcow2CachedTable` entries.
  - Optional dependent cache pointer.
  - Entry count and table size.
  - `depends_on_flush` flag for write ordering after data/refcount writes.
  - Contiguous aligned `table_array` backing all cached table buffers.
  - LRU counters, including `cache_clean_lru_counter` for memory reclamation.

## Cache Allocation And Destruction

`qcow2_cache_create()` allocates metadata entries and one block-aligned memory array sized as `num_tables * table_size`. It asserts that table size is a power of two, at least the minimum qcow2 cluster size, and no larger than the image cluster size.

`qcow2_cache_destroy()` asserts that no entry is still referenced, then frees the table array and metadata.

## Address Helpers

- `qcow2_cache_get_table_addr()` maps a cache slot index to its table buffer.
- `qcow2_cache_get_table_idx()` maps a table pointer back to a cache slot and asserts correct alignment/range.
- `qcow2_cache_get_name()` identifies whether a cache is the refcount block cache, L2 table cache, or unknown for error messages.

## Memory Reclamation

`qcow2_cache_clean_unused()` scans for clean, unreferenced, nonempty entries whose LRU counter is older than the previous cleanup watermark:

- Clears their offsets and LRU counters.
- Releases contiguous ranges with `qcow2_cache_table_release()`.
- On Linux, `qcow2_cache_table_release()` uses `madvise(..., MADV_DONTNEED)` on page-aligned portions of table memory.

This drops resident memory without changing dirty state; only clean, unreferenced entries are eligible.

## Writeback And Flush Ordering

`qcow2_cache_entry_flush()` writes a single dirty cached table to disk:

- Ignores clean or empty entries.
- Flushes dependency cache first if `c->depends` is set.
- Otherwise flushes the protocol file if `depends_on_flush` is set.
- Performs overlap checks:
  - Refcount cache writes use `QCOW2_OL_REFCOUNT_BLOCK`.
  - L2 cache writes use `QCOW2_OL_ACTIVE_L2`.
- Emits block debug events.
- Writes the table with `bdrv_pwrite()`.
- Clears the dirty flag on success.

`qcow2_cache_write()` iterates all cache entries and flushes dirty entries. It preserves an `-ENOSPC` result priority if encountered.

`qcow2_cache_flush()` writes all dirty cache entries, then flushes the underlying protocol node.

## Dependencies

`qcow2_cache_set_dependency()` records that one cache must be flushed before another dirty cache is written. It first resolves existing dependencies that would conflict.

`qcow2_cache_depends_on_flush()` records that a cache must not be written until the protocol file has been flushed. This is used when metadata should only become visible after prior data/refcount writes are durable.

The dependency logic is important for qcow2’s metadata ordering: L2 table updates must not point to clusters before associated data and refcount state are safely written.

## Emptying The Cache

`qcow2_cache_empty()`:

- Flushes the cache.
- Asserts all entries are unreferenced.
- Clears every offset and LRU counter.
- Releases all table memory.
- Resets the cache LRU counter.

This is used when metadata will be modified outside the cache or when cached state must be invalidated.

## Lookup, Miss Handling, And Replacement

`qcow2_cache_do_get()` is the core lookup path:

- Rejects unaligned table offsets and signals image corruption.
- Uses a deterministic lookup start index based on offset.
- Scans the cache for a matching offset.
- Simultaneously tracks the unreferenced entry with the smallest LRU counter as replacement victim.
- If no unreferenced entry exists, aborts; current synchronous usage assumes this cannot happen.
- On miss:
  - Flushes the victim if dirty.
  - Clears its offset while loading.
  - Optionally reads table contents from disk.
  - Sets the new offset.
- Increments the entry refcount and returns the table pointer.

Public wrappers:

- `qcow2_cache_get()` loads table contents from disk.
- `qcow2_cache_get_empty()` allocates a cache slot without reading from disk, used for newly initialized metadata.

## Releasing And Dirtying Entries

`qcow2_cache_put()` decrements the entry refcount and sets a fresh LRU counter when the refcount reaches zero.

`qcow2_cache_entry_mark_dirty()` marks a referenced table dirty and asserts that the entry has a nonzero offset.

`qcow2_cache_is_table_offset()` returns the cached table pointer for a given offset if present.

`qcow2_cache_discard()` invalidates an unreferenced entry, clears offset/LRU/dirty state, and releases the memory for that slot.

## Error And Consistency Model

The cache enforces several key invariants:

- Cached table offsets must be nonzero and aligned to the table size.
- Dirty entries are never evicted without writeback.
- Referenced entries are not selected for replacement or discard.
- Cache users must `put` entries after use; destruction and emptying assert no outstanding references.
- Writeback includes qcow2 metadata overlap checks before writing.

## Interactions

This cache is used by qcow2 cluster/refcount code to manage:

- Active L2 table slices.
- Refcount blocks.
- Metadata update ordering between refcount blocks, data writes, and L2 pointer publication.

It relies on qcow2 state to identify cache type and block layer APIs for reads, writes, and flushes.
<!-- END FILE RESEARCH: sources/virtualization/qemu/block/qcow2-cache.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/qemu/block/qcow2-cluster.c -->
# File Research: sources/virtualization/qemu/block/qcow2-cluster.c

## Purpose

Implements qcow2 guest-to-host cluster mapping, L1/L2 table growth and shrink, L2 allocation and copy-on-write, host offset allocation for writes, discard/zero handling, zero-cluster expansion for downgrades, and compressed L2 entry parsing. This is the core qcow2 allocation and mapping engine.

## L1 Table Management

`qcow2_shrink_l1_table()` shrinks the active L1 table:

- Zeroes removed L1 entries on disk.
- Flushes the file.
- Frees now-unreachable L2 table clusters.
- Clears in-memory entries on partial write failure to avoid stale metadata use.

`qcow2_grow_l1_table()` grows the active L1 table:

- Computes exact or expanded target size, with overflow checks.
- Allocates a new aligned in-memory L1 table.
- Allocates new on-disk clusters for the table.
- Flushes refcount cache before writing new metadata.
- Writes the new L1 table in big endian.
- Updates the qcow2 header fields `l1_size` and `l1_table_offset`.
- Switches in-memory state to the new table and frees the old one.
- Rolls back allocations on failure.

`qcow2_write_l1_entry()` writes one aligned group of L1 entries, using request alignment to avoid read-modify-write where possible, and performs active L1 overlap checks.

## L2 Table Loading And Allocation

`l2_load()` loads the correct L2 slice for a guest offset using the L2 table cache. Qcow2 can cache slices rather than entire L2 tables.

`l2_allocate()` creates a new L2 table for an L1 entry:

- Allocates a full L2 table.
- Flushes refcount metadata before using the new table.
- For each cache slice:
  - If no old L2 table exists, initializes the slice to zero.
  - If an old L2 table exists, reads the old slice and copies it.
  - Marks the new slice dirty.
- Flushes the L2 cache so the new L2 table is on disk before publishing it.
- Updates the L1 entry with `QCOW_OFLAG_COPIED`.
- Restores the old L1 entry and frees the new table on failure.

`get_cluster_table()` ensures the relevant L1 entry and L2 table exist and are writable:

- Grows L1 if needed.
- Detects unaligned L2 offsets as corruption.
- Allocates/COWs the L2 table if the L1 entry is not copied.
- Frees the old L2 table after successful COW.
- Returns the cached L2 slice and index.

## Host Offset Lookup

`qcow2_get_host_offset()` maps a guest offset and byte count to a host offset and subcluster type:

- Handles guest offsets beyond L1 size as unallocated.
- Loads the relevant L2 slice.
- Reads L2 entry and optional subcluster bitmap.
- Rejects zero entries in pre-v3 images.
- Rejects compressed clusters when an external data file is used.
- Checks cluster offset alignment.
- For external data files, verifies host cluster offset matches guest cluster offset.
- Uses `count_contiguous_subclusters()` to return the longest range with the same type and contiguous physical layout.
- Returns compressed cluster entries specially, with the L2 entry in `host_offset`.

Supporting helpers:

- `qcow2_get_subcluster_range_type()` counts contiguous subclusters of one type inside an L2 entry.
- `count_contiguous_subclusters()` extends that count across L2 entries while requiring type and physical contiguity.

## Compressed Cluster Allocation

`qcow2_alloc_compressed_cluster_offset()` allocates space for a compressed cluster:

- Does nothing for external data files.
- Ensures target cluster is not already allocated.
- Allocates byte-granular compressed storage with `qcow2_alloc_bytes()`.
- Computes compressed-sector count.
- Encodes compressed flag, offset, and size into the L2 entry.
- Clears subcluster bitmap for extended L2 images.
- Returns the host data offset.

Compressed clusters are never marked copied.

## Copy-On-Write Execution

`perform_cow()` fills unmodified parts of newly allocated clusters before L2 metadata is updated:

- Computes start and end COW regions from `QCowL2Meta`.
- May merge start and end reads when the skipped middle region is small.
- Temporarily releases `s->lock` while doing I/O.
- Reads old data directly through the driver callback to avoid double throttling and request tracking.
- Encrypts copied regions when the image is encrypted.
- Writes copied regions and optional guest data to the new allocation.
- Marks the L2 cache as depending on a protocol flush if the write succeeds.

`do_perform_cow_read()` and `do_perform_cow_write()` wrap the actual I/O and overlap checks.

## Linking Allocations Into L2

`qcow2_alloc_cluster_link_l2()` publishes newly allocated clusters:

- Allocates an array for old overwritten L2 entries.
- Performs required COW.
- Marks image dirty for lazy refcounts.
- Makes the L2 cache depend on the refcount cache when accurate refcounts are required.
- Loads the relevant L2 slice and marks it dirty.
- Writes new L2 entries with `QCOW_OFLAG_COPIED`.
- Updates extended L2 subcluster allocation/zero bitmaps for the written range.
- Frees old clusters after the new L2 entries are in place, unless `keep_old_clusters` is set.

`qcow2_alloc_cluster_abort()` frees allocated clusters when a request fails before L2 linking.

## L2 Metadata Planning

`calculate_l2_meta()` creates `QCowL2Meta` records for write requests that need COW or L2 updates:

- Checks all affected subclusters for invalid entries.
- Determines whether COW can be skipped when overwriting already normal allocated clusters.
- Computes leading and trailing COW ranges based on cluster type, subcluster bitmaps, compression, zero state, and whether the old cluster is kept.
- Inserts the metadata into `s->cluster_allocs` so concurrent requests can detect dependencies.

This function is the bridge between allocation planning and later metadata publication.

## Write Allocation Path

`qcow2_alloc_host_offset()` is the main allocator for write requests:

- Starts with a guest offset and requested byte count.
- Builds a contiguous host range, potentially shorter than requested.
- Handles in-flight allocation dependencies through `handle_dependencies()`.
- Reuses copied clusters with `handle_copied()`.
- Allocates new clusters with `handle_alloc()` when needed.
- Returns a host offset and adjusted byte count.
- Returns a linked list of `QCowL2Meta` records for the caller to commit or abort.

Supporting pieces:

- `cluster_needs_new_alloc()` classifies whether an L2 entry requires new storage.
- `count_single_write_clusters()` counts contiguous entries that are either reusable or need new allocation.
- `handle_dependencies()` checks overlap with in-flight `QCowL2Meta` requests, shortens the current request where possible, or waits and asks the caller to restart with `-EAGAIN`.
- `qcow2_wait_for_dependencies()` waits for conflicting in-flight allocations for discard/zero paths.
- `handle_copied()` finds already allocated copied clusters that can be written in place and may create metadata for subcluster state changes.
- `do_alloc_cluster_offset()` performs actual allocation, either in the qcow2 file or at the matching guest offset for external data files.
- `handle_alloc()` counts allocatable/COW clusters, allocates storage, adjusts byte counts, and creates L2 metadata.

## Discard Handling

`qcow2_cluster_discard()` discards a cluster-aligned range:

- Waits for conflicting in-flight allocations.
- Iterates by L2 slice.
- Sets `s->cache_discards` while batching discard work.
- Calls `discard_in_l2_slice()` for each slice.
- Processes queued discards after success/failure.

`discard_in_l2_slice()` updates L2 entries for each cluster:

- For full discard, clears the L2 entry/bitmap so reads can fall through to backing.
- For normal discard, preserves zero-read semantics where possible.
- Handles v3 zero flags, extended L2 zero bitmaps, backing-file behavior, and `discard_no_unref`.
- Frees old clusters unless references are intentionally kept.
- Passes discard requests through even when references are kept.

## Zeroing

`qcow2_subcluster_zeroize()` zeroes a subcluster-aligned range:

- Waits for allocation dependencies.
- For raw external data files, writes zeroes to the external data file first.
- For qcow2 v2:
  - Uses discard when no backing file exists.
  - Otherwise returns unsupported because v2 lacks zero flags.
- Splits the range into head partial cluster, full clusters, and tail partial cluster.
- Uses `zero_l2_subclusters()` for partial clusters in extended L2 images.
- Uses `zero_in_l2_slice()` for full clusters.

`zero_in_l2_slice()` marks whole clusters as zero:

- May unmap allocated or compressed clusters.
- Honors `BDRV_REQ_MAY_UNMAP` and `discard_no_unref`.
- Sets extended L2 zero bitmaps or classic `QCOW_OFLAG_ZERO`.
- Frees or discards old clusters if unmapping.

`zero_l2_subclusters()` marks a subset of subclusters zero in the L2 bitmap and rejects partial zeroing of compressed clusters.

## Zero Cluster Expansion

`qcow2_expand_zero_clusters()` prepares images for downgrade to formats that do not support zero clusters:

- Processes the active L1 table.
- Empties the L2 cache before directly modifying inactive snapshot L2 tables.
- Processes each snapshot L1 table.

`expand_zero_clusters_in_l1()` walks L1/L2 metadata:

- Rejects images with subclusters.
- For zero-plain clusters:
  - If there is no backing file, deallocates them.
  - If backed, allocates real clusters and writes zeroes.
- For zero-allocated clusters, writes zeroes to the data file and converts entries to normal allocated entries.
- Preserves sharing semantics by checking L2 refcount and adjusting new cluster refcount when needed.
- Handles active L2 tables through the cache and inactive L2 tables through direct disk I/O.
- Emits progress callbacks by L1 entry.

## Compressed Entry Parsing

`qcow2_parse_compressed_l2_entry()` decodes a compressed L2 entry into:

- Compressed data offset.
- Compressed byte size, derived from compressed-sector count and sector alignment.

It asserts that the entry is actually compressed.

## Error And Consistency Model

The cluster code protects qcow2 metadata with several recurring rules:

- Metadata offsets must be cluster-aligned unless encoded compressed data allows byte granularity.
- L2 tables are flushed before L1 entries publish them.
- Refcount updates and data/COW writes are ordered before L2 updates through cache dependencies.
- Overlap checks precede direct metadata/data writes.
- Old clusters are freed only after replacement metadata is installed.
- In-flight allocations are tracked to serialize overlapping COW and metadata updates.
- External data files require host offsets to match guest offsets and disallow compressed clusters.
- Pre-v3 images cannot contain zero-cluster entries.

## Interactions

This file is tightly coupled to:

- `qcow2-cache.c` for L2 cache get/put/dirty/flush/dependency operations.
- qcow2 refcount allocation/free functions.
- qcow2 overlap checking and corruption signaling.
- Block layer coroutine I/O APIs.
- Dirty/lazy refcount state.
- Extended L2 subcluster helpers from qcow2 headers.
- Snapshot metadata when expanding zero clusters.
<!-- END FILE RESEARCH: sources/virtualization/qemu/block/qcow2-cluster.c -->