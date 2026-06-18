# sources/distributed-fs/openafs/src/vol/vg_cache_impl.h

## Purpose

`vg_cache_impl.h` is the private cross-file interface for the volume-group cache implementation. It is shared by `vg_cache.c` and `vg_scan.c`, not intended for normal callers.

## Important APIs, Types, and Constants

The key constant is `VVGC_SCAN_TBL_LEN`, set to 4096, defining how many discovered volume headers a scanner thread batches before flushing into the global cache under `VOL_LOCK`. The header includes `vg_cache_impl_types.h`, declares the global `VVGCache_hash_table` and `VVGCache`, and exposes internal helpers used across implementation files: `_VVGC_flush_part`, `_VVGC_flush_part_r`, `_VVGC_scan_start`, `_VVGC_state_change`, `_VVGC_entry_purge_r`, `_VVGC_dlist_add_r`, and `_VVGC_dlist_del_r`.

`VVGC_HASH(volumeId)` maps a volume id to a hash bucket by masking with `VolumeHashTable.Mask`, so it depends on volume package hash-table sizing.

## Control Flow and State Contract

The header allows the scanner to transition a partition to `UPDATING`, flush existing entries, batch newly discovered mappings, and reconcile deletes that occur during the scan. It also lets the public delete path add to the scanner delete-list and purge global cache entries with shared logic.

## Dependencies and Integration Points

It depends on the private type definitions in `vg_cache_impl_types.h`, volume package hash globals, and the DAFS volume lock model. Including this header outside the implementation effectively opts into internal state and should be avoided.

## Risks and Test Signals

Because the hash macro is a simple mask, tests should use a `VolumeHashTable.Size`/`Mask` combination that matches package initialization. Cross-file tests should verify the scan table length and delete-list logic do not depend on implementation details hidden from public callers. Static checks should flag accidental inclusion of this private header by unrelated modules.
