# File Research: sources/cow-pools/openzfs/module/zfs/space_map.c

## Role

`space_map.c` implements OpenZFS's on-disk space map object format and core operations for reading, writing, loading, estimating, truncating, allocating, and freeing space maps. A space map is an append-only log of allocation or free extents. Higher-level code uses it for metaslab space maps, DTLs, and log space maps.

The file understands the legacy single-word encoding, space map v2 double-word encoding, and debug entries that record TXG/sync-pass context or pad blocks.

## Entry Decoding And Iteration

`sm_entry_is_debug()`, `sm_entry_is_single_word()`, and `sm_entry_is_double_word()` classify raw 64-bit words by prefix.

`space_map_iterate()` streams through the first `end` bytes of a space map object. It prefetches the stream, holds each DMU buffer, walks 64-bit words, updates current TXG and sync-pass on debug entries, decodes single-word or double-word entries, reconstructs shifted absolute offsets and runs, validates alignment and bounds against `sm_start`, `sm_size`, and `sm_shift`, then calls the supplied callback with a `space_map_entry_t`.

Double-word entries store run and vdev in the first word and type/offset in the second word. Single-word entries have no vdev ID and use `SM_NO_VDEVID`.

## Incremental Destruction

`space_map_incremental_destroy()` destructively deletes entries from the end of a space map while invoking a callback for each logical entry. It cannot simply scan backwards because the second word of a double-word entry is not self-identifying, so `space_map_reversed_last_block_entries()` reads the final block and builds a reverse-order buffer while preserving double-word pairs.

For each reversed entry, the function invokes the callback, updates `smp_alloc` in the opposite direction of the destroyed record, and subtracts one or two words from `smp_length`. Debug entries only reduce length. When the map reaches length zero, allocated space must also be zero.

Callers are responsible for holding the correct higher-level locks because this path mutates the map.

## Loading Into Range Trees

`space_map_load_length()` and `space_map_load()` replay a space map into a `zfs_range_tree_t`. When loading `SM_FREE`, the target range tree is first populated with the entire map range. During iteration, entries matching the requested map type add ranges and opposite entries remove ranges. On read error the target tree is vacated.

`space_map_load_callback()` verifies that adding a segment will not exceed the map size before adding it.

## Histograms

The file supports optional on-disk histograms stored in `space_map_phys_t`. `space_map_histogram_clear()` clears the histogram only when the bonus buffer has the modern physical size. `space_map_histogram_verify()` ensures the in-core range tree has no ranges below the space map allocation shift. `space_map_histogram_add()` transfers range-tree histogram buckets into the space map's 32 buckets, normalizing ranges larger than the representable bucket range into the last bucket.

Histogram feature reference counts are managed when allocating and freeing space map objects if `SPA_FEATURE_SPACEMAP_HISTOGRAM` is enabled and the object's bonus size uses the modern format.

## Writing

`space_map_write()` is the public write path. It requires syncing context, dirties the bonus buffer, keeps `smp_object` updated for compatibility, returns early for empty trees, updates `smp_alloc` according to `SM_ALLOC` or `SM_FREE`, records initial range-tree node/space counts, calls `space_map_write_impl()`, then verifies the range tree was not changed while writing.

`space_map_write_impl()` writes an intro debug entry, estimates final size in debug builds, holds the last data block at the append offset, then walks the range tree. It chooses double-word entries only when `SPA_FEATURE_SPACEMAP_V2` is active and offset/run/vdev requirements exceed single-word capacity, a vdev ID is present, or the testing tunable forces occasional double-word entries.

`space_map_write_seg()` performs the actual append. It splits long segments by the maximum representable run, advances blocks as needed, and pads a one-word remainder at the end of a block with an empty debug entry so a two-word entry is never split across blocks. It updates `smp_length` as words are written.

## Object Lifecycle

`space_map_open()` allocates an in-core `space_map_t`, stores geometry and object fields, holds the DMU bonus buffer, discovers the data block size, and returns the opened map. `space_map_close()` releases the bonus buffer and frees the in-core object.

`space_map_truncate()` either frees/reallocates the object if the bonus size or block sizes are outdated, or frees all data ranges in place. It clears the histogram, dirties the bonus buffer, and resets `smp_length` and `smp_alloc`.

`space_map_alloc()` allocates a DMU object with `DMU_OT_SPACE_MAP` data and `DMU_OT_SPACE_MAP_HEADER` bonus data, using the configured indirect block shift `space_map_ibs`. `space_map_free_obj()` decrements the histogram feature count when appropriate and frees the object. `space_map_free()` wraps object free and clears the in-core object ID.

## Estimation And Accessors

`space_map_estimate_optimal_size()` computes a worst-case byte estimate for writing a range tree to a space map. It uses range-tree histograms rather than walking every segment, accounts for single-word versus double-word encodability, feature state, forced double-word testing, split entries for very large ranges, and worst-case debug padding.

`space_map_object()`, `space_map_allocated()`, `space_map_length()`, and `space_map_nblocks()` expose object ID, allocated bytes, logical encoded length, and number of data blocks.

## Risks And Invariants

Encoding and decoding must agree exactly across single-word, double-word, and debug entries. A double-word entry may not cross a data-block boundary, which is why padding debug entries exist.

All offsets and lengths are stored shifted by `sm_shift`; callers must provide aligned ranges within `[sm_start, sm_start + sm_size)`. Write paths assume syncing context and no concurrent mutation of the source range tree. Truncation and incremental destruction modify on-disk metadata and require caller-side synchronization.
