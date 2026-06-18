# Group Research: group_1132_lvm2_sources_block_storage_lvm2_lib_metadata_pv_h_sources_block_sto_3f1632017e73

This grouped report covers the six LVM2 physical-volume metadata files listed for subset A. All listed source files were read completely. Together they define the physical-volume data model, PV selection/range parsing, PV segment assignment/release, resize handling, and the inverse PV free-space maps consumed by LV allocation.

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/metadata/pv.h -->
# File Research: sources/block-storage/lvm2/lib/metadata/pv.h

## Scope

`pv.h` is the core internal declaration for `struct physical_volume` and the PV accessor/query API. It is a compact metadata header for LVM2's block-storage layer, tying a PV's identity, backing device, format instance, VG association, capacity, bootloader area, physical extent layout, labels, and tags into one object.

## Primary Data Model

- `struct physical_volume` stores the PV UUID, optional `old_id` used during `pvchange -u`, `struct device *dev`, device hint and persistent device-id fields, format type/instance pointers, and provisional VG name/id fields used before a full parent `volume_group` exists.
- The `vg` pointer is maintained when the PV is on a parent VG's `pvs` list. The header explicitly distinguishes this from the earlier `vg_name`/`vg_id` fields.
- Capacity and state are tracked through `status`, `size`, bootloader area fields, PE fields (`pe_size`, `pe_start`, `pe_count`, `pe_alloc_count`, alignment), label state, `label_sector`, ordered `segments`, and PV `tags`.
- `segments` is documented as an ordered list of `pv_segment` entries covering the complete PV data area. Implementations in `pv_manip.c` rely on that invariant for split, merge, validation, free counting, and resizing.

## API Surface

The function declarations are mostly read-only accessors and duplicators:

- Identity/name/display helpers: `pv_fmt_dup()`, `pv_name_dup()`, `pv_dev_name()`, `pv_uuid_dup()`, `pv_tags_dup()`, `pv_deviceid_dup()`, `pv_deviceidtype_dup()`.
- Device/VG helpers: `pv_dev()`, `pv_vg_name()`, `pv_label()`.
- Size/allocation helpers: `pv_size()`, `pv_size_field()`, `pv_dev_size()`, `pv_free()`, `pv_used()`, `pv_status()`.
- PE/BA metadata helpers: `pv_pe_size()`, `pv_pe_start()`, `pv_ba_start()`, `pv_ba_size()`, `pv_pe_count()`, `pv_pe_alloc_count()`.
- Metadata-area helpers: `pv_mda_size()`, `lvmcache_info_mda_free()`, `pv_mda_free()`, `pv_mda_count()`, `pv_mda_used_count()`, `pv_mda_set_ignored()`.
- Classification helpers: `is_orphan()`, `is_missing_pv()`, `is_used_pv()`, `is_pv()`.

## Dependencies

The header depends on LVM2 ID support and libdevmapper list/pool-visible types. It forward-declares `struct device`, `struct format_type`, `struct volume_group`, `struct lvmcache_info`, and `struct label`, keeping the physical-volume model available without including the full metadata graph.

## Role In The PV Metadata Flow

This file is the shared contract used by `pv_list.c`, `pv_manip.c`, and `pv_map.c`. Those implementation files read and mutate `dev`, `status`, `pe_count`, `pe_alloc_count`, `pe_start`, `vg`, `segments`, and `tags` as the basis for allocation eligibility, PE range filtering, segment assignment, discard, release, map creation, validation, and resize.

## Risks And Edge Cases

- `vg_name`/`vg_id` and `vg` can temporarily represent different lifecycle stages; callers need to know whether the PV is attached to a full VG object.
- `is_labelled` gates `label_sector` validity, so direct label-sector consumers must honor that bit.
- `wrong_vg` records a metadata/device mismatch case where metadata includes a PVID but the actual PV belongs elsewhere.
- Correctness depends on `segments` remaining a complete ordered covering of the PV. The header declares the invariant; `pv_manip.c` enforces and repairs it during segment operations.

## Summary

`pv.h` defines the physical-volume object at the center of LVM2 metadata. It exposes the state used by PV selection, allocation, reporting, metadata-area management, and resize code while keeping most behavior in companion implementation files.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/metadata/pv.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/metadata/pv_alloc.h -->
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
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/metadata/pv_alloc.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/metadata/pv_list.c -->
# File Research: sources/block-storage/lvm2/lib/metadata/pv_list.c

## Scope

`pv_list.c` builds and clones command-scoped PV selection lists. It parses user-supplied PV arguments, optional physical-extent ranges, and tag selectors into `struct pv_list` entries with `pe_ranges` suitable for allocation and pvmove-style operations.

## Primary Functions

- `_add_pe_range()` appends a `struct pe_range` to a selected PV after rejecting overlap with existing ranges.
- `_xstrtouint32()` wraps `strtoul()` with error, no-progress, and `UINT32_MAX` overflow checks.
- `_parse_pes()` parses PE selectors after a PV name. With no selector it selects the whole PV; otherwise it accepts colon-prefixed single extents, start/end ranges, and start-plus-length forms.
- `_create_pv_entry()` validates PV availability, filters non-allocatable/missing/full PVs when requested, coalesces repeated references to the same device, initializes `pe_ranges`, and delegates PE parsing.
- `create_pv_list()` is the public entry point. It accepts explicit PV names, optional PE ranges, and `@tag` selectors, then returns a memory-pool-owned `dm_list` of selected PVs.
- `clone_pv_list()` shallow-copies a PV list into a new memory-pool-owned list.
- `pv_list_to_dev_list()` converts selected PVs with usable devices and aliases into `device_list` entries.

## Summary

`pv_list.c` normalizes user or caller PV selections into memory-pool-owned `pv_list` records with explicit PE ranges. Its main correctness responsibilities are argument parsing, overlap prevention, allocation eligibility filtering, and preserving selected ranges for later free-space mapping.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/metadata/pv_list.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/metadata/pv_manip.c -->
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
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/metadata/pv_manip.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/metadata/pv_map.c -->
# File Research: sources/block-storage/lvm2/lib/metadata/pv_map.c

## Scope

`pv_map.c` builds temporary inverse maps of free PV extents for an allocation attempt. The persistent metadata maps logical-volume areas to physical extents; this file constructs the reverse view: free `pv_area` ranges grouped by `pv_map`, sorted for allocator consumption.

## Primary Functions

- `_insert_area()` inserts a `pv_area` into a map's `areas` list in largest-first order and increments the map's total free PE count.
- `_remove_area()` removes an area and subtracts its full count from the map total.
- `_create_single_area()` allocates and initializes one free area.
- `_create_alloc_areas_for_pv()` intersects a requested PE range with free `pv_segment` entries.
- `_create_all_areas_for_pv()` applies whole-PV or explicit `pe_ranges` filtering.
- `_create_maps()` filters selected PVs by allocatable status, temporary allocation prohibition, and missing state, then deduplicates maps by device.
- `create_pv_maps()` builds the output map list.
- `consume_pv_area()`, `reinsert_changed_pv_area()`, and `pv_maps_size()` support allocator consumption and accounting.

## Risks And Edge Cases

- The file-level comment notes overlap is not handled; callers are expected to provide non-overlapping ranges.
- `_insert_area()` has a local FIXME because reinsertion compares `unreserved` for the changed area against `count` for existing areas, mixing two scales.
- `pe_count` is updated from full area `count`, not current provisional `unreserved`.
- Deduplication is by backing device pointer.

## Summary

`pv_map.c` creates the allocator's temporary free-space view from PV segment metadata and selected PE ranges. It is intentionally transient: allocation attempts can consume and reinsert `pv_area` records without directly mutating persistent PV segment mappings.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/metadata/pv_map.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/metadata/pv_map.h -->
# File Research: sources/block-storage/lvm2/lib/metadata/pv_map.h

## Scope

`pv_map.h` declares the temporary inverse mapping structures used during LV allocation. Since persistent metadata stores logical-to-physical mappings on LV segments, this header provides the PV-oriented free-area view needed when selecting physical extents for new or extended LVs.

## Data Structures

- `struct pv_area` represents a contiguous free PE range on a PV map. It records the owning `pv_map`, starting PE, total extent count, per-allocation-pass `unreserved` count, and list linkage.
- `struct pv_area_used` records a provisional use of a `pv_area` during construction of parallel allocation candidates. Multiple records can reference the same `pv_area`, but their combined `used` extents must not exceed the area's count.
- `struct pv_map` groups free areas for one `physical_volume`, tracks total free PEs across active areas in `pe_count`, and links into the top-level PV map list.

## API Surface

- `create_pv_maps()` builds the intersection between selected/allocatable PVs and free space in a VG.
- `consume_pv_area()` consumes extents from the front of an area after allocation chooses it.
- `reinsert_changed_pv_area()` reorders an area after provisional allocation or rollback changes its effective availability.
- `pv_maps_size()` returns the total free PE count represented by a PV map list.

## Summary

`pv_map.h` defines the allocator's temporary PV free-space model: PVs contain sorted free areas, areas can be provisionally reserved by parallel allocation searches, and chosen areas are later consumed or materialized into persistent PV/LV segment mappings.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/metadata/pv_map.h -->