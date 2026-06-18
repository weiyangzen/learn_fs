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
