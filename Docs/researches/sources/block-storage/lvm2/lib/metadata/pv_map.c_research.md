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
