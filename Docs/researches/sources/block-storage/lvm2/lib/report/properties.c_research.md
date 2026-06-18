# File Research: sources/block-storage/lvm2/lib/report/properties.c

## Purpose

`properties.c` implements liblvm property accessors for report fields. It bridges the X-macro column definitions in `columns.h` to `struct lvm_property_type` entries and type-specific `*_get_property` / `*_set_property` functions.

## Main Structure

The file defines macro families that expand into property getter/setter functions for VG, PV, LV, LV segment, and PV segment objects:

- Numeric getters: `GET_VG_NUM_PROPERTY_FN`, `GET_PV_NUM_PROPERTY_FN`, `GET_LV_NUM_PROPERTY_FN`, `GET_LVSEG_NUM_PROPERTY_FN`, `GET_PVSEG_NUM_PROPERTY_FN`.
- Signed numeric getter: `GET_LV_SNUM_PROPERTY_FN`.
- String getters: `GET_VG_STR_PROPERTY_FN`, `GET_PV_STR_PROPERTY_FN`, `GET_LV_STR_PROPERTY_FN`, `GET_LVSEG_STR_PROPERTY_FN`, `GET_PVSEG_STR_PROPERTY_FN`.
- Setters exist mainly for `vg_mda_copies`; most fields map to `prop_not_implemented_set`.

## Key Helper Logic

- `_copy_percent()` calls `lv_mirror_percent()` and returns `DM_PERCENT_INVALID` on failure.
- RAID helpers expose mismatch count, sync action, writebehind, min/max recovery rate, integrity mode/block size, and integrity mismatch counts.
- `_snap_percent()` reports snapshot usage only for COW LVs.
- `_data_percent()` reports usage for snapshots, cache/cache pools, thin volumes, and thin pools by querying live status objects and destroying their memory pools afterward.
- `_metadata_percent()` similarly reports cache/thin-pool metadata usage.

## Property Coverage

The file defines getters for many static metadata fields:

- PV: format, UUID, device size/name, metadata area free/size/counts, PE start/size/free/used/counts, attributes, tags, bootloader area, device ID/type.
- LV: UUID/name/full name/path/dm path/parent/attr, major/minor, read-ahead, kernel major/minor/read-ahead, size, segment count, origin, snapshot/copy/RAID/integrity percentages and counters, pvmove/convert/cache/thin/VDO related LVs, tags, modules, metadata size, time, host, active/profile/lock args.
- VG: format, UUID/name/attr, size/free/system ID/lock type/lock args, extent data, max LV/PV, PV/LV/snapshot counts, seqno, tags, metadata area data, profile, missing PV count.
- LVSEG: type, copies, reshape/data offsets, stripes, stripe/region/chunk sizes, thin count/zero/transaction/thin ID, discards/cache mode/cache metadata format, starts/sizes/tags/ranges/devices/monitoring.
- PVSEG: start and size.

Many dynamic/report-only fields are explicitly `prop_not_implemented_get`, especially fields needing live status, kernel state, list-valued reserved handling, or display-only synthesis.

## Public API

Exports:

- `lvseg_get_property()`
- `lv_get_property()`
- `vg_get_property()`
- `pvseg_get_property()`
- `pv_get_property()`
- `lv_set_property()`
- `vg_set_property()`
- `pv_set_property()`

Each delegates to `prop_get_property()` or `prop_set_property()` with the proper report-type mask.

## Important Dependencies

- Includes `columns.h` into `_properties[]`, so column field IDs and property function names must stay aligned.
- Depends on `lib/properties/prop_common.h` for the generic property machinery and X-macro expansion conventions.
- Depends heavily on metadata helpers such as `pv_*_dup`, `lv_*_dup`, `vg_*_dup`, `lvseg_*`, `lv_cache_status`, `lv_thin_status`, and RAID/integrity status helpers.
