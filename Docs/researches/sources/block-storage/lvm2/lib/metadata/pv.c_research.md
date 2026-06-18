# File Research: sources/block-storage/lvm2/lib/metadata/pv.c

## Purpose

`pv.c` is a compact accessor and reporting helper file for LVM2 physical volumes. It exposes PV identity, naming, size, status, metadata-area, usage, and label information, mostly for reporting and external-library style getters, while bridging PV objects to lvmcache metadata-area state.

## Key Responsibilities

- Duplicates report strings for PV format, name, UUID, tags, device ID, and device ID type.
- Returns core PV fields such as ID, format type, VG ID, device pointer, visible VG name, device name, PV size, PE size/start/count, bootloader area start/size, allocated PE count, status, free space, used space, and computed size field.
- Reads current device size through `dev_get_size()`.
- Reports PV metadata-area count, used metadata-area count, minimum MDA size, and minimum MDA free space by consulting lvmcache.
- Classifies PVs as orphan, real PV, missing PV, or used PV based on `vg_name`, status bits, format flags, and PV header extension flags.
- Produces the three-character PV attribute string for duplicate/allocatable/used, exported, and missing status.
- Sets or clears the ignored flag on a PV's metadata areas while keeping lvmcache and VG format-instance MDA lists coherent.
- Returns the cached label for a PV.

## Main Data And APIs

- Public functions include `pv_fmt_dup()`, `pv_name_dup()`, `pv_id()`, `pv_uuid_dup()`, `pv_tags_dup()`, `pv_deviceid_dup()`, `pv_deviceidtype_dup()`, `pv_format_type()`, `pv_vg_id()`, `pv_dev()`, `pv_vg_name()`, `pv_dev_name()`, `pv_size()`, `pv_dev_size()`, `pv_size_field()`, `pv_free()`, `pv_status()`, `pv_pe_size()`, `pv_ba_start()`, `pv_ba_size()`, `pv_pe_start()`, `pv_pe_count()`, `pv_pe_alloc_count()`, `pv_mda_count()`, `pv_mda_used_count()`, `is_orphan()`, `is_pv()`, `is_missing_pv()`, `is_used_pv()`, `pv_attr_dup()`, `pv_mda_size()`, `lvmcache_info_mda_free()`, `pv_mda_free()`, `pv_used()`, `pv_mda_set_ignored()`, and `pv_label()`.
- The file uses a simple `pv_field(handle, field)` macro for field getters, with a FIXME noting that handle validity is not checked.

## Control Flow Notes

- `is_used_pv()` treats any non-orphan PV as used, and for orphan PVs only reports used when the format supports PV flags and the lvmcache PV header extension has `PV_EXT_USED`.
- `pv_attr_dup()` prioritizes duplicate-device status (`d`) over allocatable (`a`), then orphan-used (`u`), then `-`; the second and third characters report exported and missing state.
- `pv_mda_set_ignored()` is simple for orphan PVs, but for non-orphan PVs it prevents disabling all VG metadata areas, then iterates cached PV MDAs and matching VG FID MDAs by location to update ignored bits and move ignored MDAs back to the in-use list when unignoring.
- `lvmcache_info_mda_free()` returns the minimum free space across MDAs that can report free sectors, or zero when no suitable MDA exists.

## Dependencies

This file depends on `metadata.h` helpers, lvmcache lookups and MDA iteration, device helpers, tag formatting, ID formatting, duplicate-device detection, MDA location comparison, and MDA ignored-state setters.

## Risks And Edge Cases

- Most getters directly dereference PV fields and assume a valid PV object, VG pointer, device pointer, and memory pool when needed.
- `pv_name_dup()` and `pv_dev_name()` assume `pv->dev` is non-null; missing PV callers need to avoid these paths or tolerate lower-level behavior.
- `pv_mda_set_ignored()` uses location matching rather than a direct per-PV MDA index; comments note this should be improved.
- `is_used_pv()` returns `-1` on missing cache info, so callers must distinguish error from boolean used/not-used.
- `pv_label()` logs an internal error only for real cached PV expectations; dummy PVs from PV iteration may legitimately have no label.

## Summary

`pv.c` is the PV reporting/accessor layer. It keeps callers away from direct struct-field access for common PV properties and centralizes lvmcache-backed metadata-area accounting and ignored-MDA state changes.
