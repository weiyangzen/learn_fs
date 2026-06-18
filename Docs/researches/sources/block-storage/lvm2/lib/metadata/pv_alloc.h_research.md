# File Research: sources/block-storage/lvm2/lib/metadata/pv_alloc.h

## Scope

`pv_alloc.h` is the internal interface for manipulating `pv_segment` records on a physical volume. It declares the operations that turn free PV extents into LV segment mappings, release those mappings, discard released storage, validate segment invariants, and merge adjacent segment records.

## API Surface

- `alloc_pv_segment_whole_pv()` initializes a PV's segment list as one free segment covering the whole PE range.
- `assign_peg_to_lvseg()` assigns a PE range on a PV to a specific `lv_segment` area.
- `discard_pv_segment()` issues device discard for extents being released when configuration and device support allow it.
- `release_pv_segment()` frees all or part of an allocated PV segment and merges adjacent free space.
- `check_pv_segments()` validates PV/VG extent accounting and LV back-pointers.
- `merge_pv_segments()` merges adjacent PV segments for LV-segment merge routines.

## Dependencies

The header deliberately forward-declares `dm_list`, `dm_pool`, `lv_segment`, `physical_volume`, `pv_segment`, and `volume_group`; it includes only `<inttypes.h>` for fixed-width integer declarations. The implementations live in `pv_manip.c` and depend on the wider LVM2 metadata structures.

## Role In The Allocation Pipeline

This interface is called from LV manipulation and allocation code when concrete logical-volume segment areas need to be materialized onto PV extents. The PV map code identifies free ranges; the LV allocation code chooses ranges; these helpers mutate the authoritative PV segment list and VG/PV allocation counters.

## Risks And Edge Cases

- `release_pv_segment()` can merge with both neighboring free segments, so callers iterating `pv->segments` must restart or otherwise account for list mutation.
- The API works in PE units and assumes callers pass ranges consistent with the owning LV segment's `area_len`.
- Discard behavior is separate from release behavior; freeing metadata state does not guarantee a discard was issued.

## Summary

`pv_alloc.h` is a small but central contract: it exposes the PV segment mutation primitives used to keep the inverse PV extent view consistent with LV segment mappings.
