# File Research: sources/cow-pools/openzfs/module/zfs/vdev_indirect_mapping.c

## Purpose

Provides the DMU-backed mapping table used by indirect vdevs. Each entry maps a source offset on a removed vdev to a destination DVA, optionally paired with an obsolete-byte count used by mapping condense logic.

## Main APIs And Entry Points

- Accessors: `vdev_indirect_mapping_num_entries()`, `vdev_indirect_mapping_max_offset()`, `vdev_indirect_mapping_object()`, `vdev_indirect_mapping_bytes_mapped()`, and `vdev_indirect_mapping_size()`.
- Lookup: `vdev_indirect_mapping_entry_for_offset()` and `vdev_indirect_mapping_entry_for_offset_or_next()` perform binary search using overlap semantics.
- Lifecycle: `vdev_indirect_mapping_alloc()`, `vdev_indirect_mapping_open()`, `vdev_indirect_mapping_close()`, and `vdev_indirect_mapping_free()`.
- Mutation and obsolete accounting: `vdev_indirect_mapping_add_entries()`, `vdev_indirect_mapping_increment_obsolete_count()`, `vdev_indirect_mapping_load_obsolete_spacemap()`, `vdev_indirect_mapping_load_obsolete_counts()`, and `vdev_indirect_mapping_free_obsolete_counts()`.

## Control Flow And Data Model

The mapping object's bonus buffer stores count, max source offset, bytes mapped, and optionally a separate counts object when `SPA_FEATURE_OBSOLETE_COUNTS` is enabled. Open detects old-format objects by bonus size, reads all mapping entries into memory, and records whether counts are available. Free opens the mapping so it can free the counts object and decrement the feature count before freeing the main object.

Lookup uses a custom binary search because a source offset matches an entry when it lies in `[src_offset, src_offset + asize)`, not only when it equals the entry's starting key. The `or_next` variant returns the next greater mapping entry when the requested offset is in a gap, which is used by condense restart and range walks.

`vdev_indirect_mapping_add_entries()` appends a list of pending entries in `SPA_OLD_MAXBLOCKSIZE` batches, optionally writes matching obsolete counts, updates bytes-mapped and max-offset metadata, frees list nodes, then rebuilds the in-memory entry array by copying old entries and reading back the newly written entries. Entries must be appended in nondecreasing source-offset order and must not be fully obsolete.

Obsolete count loading reads the counts object if present or returns a zero-filled array for old-format mappings. Space-map folding iterates `SM_ALLOC` entries and increments the counts for every mapping entry overlapped by each obsolete range.

## Dependencies And Integration

This file depends on DMU object APIs, bonus buffers, SPA feature flags, DSL sync-context assertions, vdev indirect mapping macros for source/destination fields, and space-map iteration. It is the low-level storage abstraction used by `vdev_indirect.c` condensing, remap, and obsolete-space processing.

## Risks And Invariants

- Mapping entries are assumed sorted by source offset and non-overlapping in the append/search paths.
- The overlap comparator treats range ends as exclusive; off-by-one mistakes would remap the wrong segment.
- Obsolete counts are `uint32_t`; assertions require count plus new obsolete bytes to fit within the mapped entry size.
- In-memory arrays are full copies of on-disk metadata, so allocation size scales with mapping entry count.
- Feature accounting must remain balanced when allocating/freeing counts objects.

## Summary

`vdev_indirect_mapping.c` is the indirect-vdev mapping table manager: it stores, searches, appends, and obsolete-counts source-to-DVA mappings used after vdev removal.
