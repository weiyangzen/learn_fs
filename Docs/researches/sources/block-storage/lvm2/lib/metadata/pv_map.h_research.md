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
