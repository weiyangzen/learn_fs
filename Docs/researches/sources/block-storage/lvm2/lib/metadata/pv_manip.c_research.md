# File Research: sources/block-storage/lvm2/lib/metadata/pv_manip.c

## Scope

`pv_manip.c` implements physical-volume segment mutation, discard-on-release, PV segment validation, selected-free-extent counting, and PV resize. It maintains the ordered `pv->segments` covering declared in `pv.h` and updates PV/VG extent counters as allocations change.

## Primary Behavior

- Segment setup and splitting are handled by `_alloc_pv_segment()`, `alloc_pv_segment_whole_pv()`, `_find_peg_by_pe()`, `_add_pv_split_segment()`, and `_pv_split_segment()`.
- `assign_peg_to_lvseg()` splits at the requested start/end, assigns the segment to an LV area, and updates PV/VG allocation counters.
- `discard_pv_segment()` conditionally issues device discard, respecting config, missing devices, device discard capability, and label-at-zero protection.
- `release_pv_segment()` frees full or partial allocations and merges adjacent free segments.
- `pv_list_extents_free()` counts free extents inside selected PE ranges.
- `check_pv_segments()` validates ordered coverage, LV area back-pointers, lengths, and PV/VG extent counters.
- `pv_resize_single()` wraps format-specific PV resize, PE-count recalculation, segment extension/reduction, PV writes, and VG write/commit.

## Invariants Maintained

- `pv->segments` should cover PE range `0..pv->pe_count` without gaps.
- Allocated PV segments must point to LV segment areas of type `AREA_PV`, and those LV areas must point back to the same PV segment.
- `pv->pe_alloc_count`, `vg->free_count`, `vg->extent_count`, and `vg->pv_count` should match the segment lists.
- Adjacent free segments are coalesced after release.

## Risks And Edge Cases

- `release_pv_segment()` mutates the segment list in ways that can invalidate active iterators.
- `assign_peg_to_lvseg()` assumes the selected range is valid and intended to be free.
- `discard_pv_segment()` adjusts discard ranges around possible label placement in the first extent.
- Shrinking a PV is allowed only when removed tail extents are free; failures after PV metadata writes may require recovery from archived metadata.

## Summary

`pv_manip.c` is the authoritative PV segment mutation engine. It turns allocation decisions into concrete `pv_segment` mappings, releases and discards extents, validates cross-links with LV metadata, and resizes PVs while keeping PV and VG extent accounting coherent.
