# File Research: sources/block-storage/lvm2/lib/report/report.c

## Purpose

`report.c` is the main LVM2 report engine implementation for standard LVM report objects. It defines report object wrappers, field display functions, reserved values and selection support, report initialization, report object dispatch, device-type reporting, and command-log reporting.

## Core Data Model

- `struct lvm_report_object` bundles the possible backing objects for one report row: VG, LV with info/status, PV, LV segment, PV segment, and label.
- `_report_types[]` maps report type IDs (`VGS`, `LVS`, `PVS`, `SEGS`, etc.) to object extractors and field prefixes.
- `_fields[]` is generated from `columns.h`; `columns-devtypes.h` and `columns-cmdlog.h` similarly generate device-type and command-log field tables.
- `_log_report_types[]` and `_devtypes_report_types[]` provide alternate schemas for command-log and device-type reports.

## Reserved Values and Selection

The file includes `values.h` under multiple macro definitions to generate:

- Static reserved value constants and name arrays.
- `struct dm_report_reserved_value _report_reserved_values[]`.
- Field-number enum entries generated from `columns.h`.

Reserved values support named binary display/selection aliases, undefined numeric values, LV permission names, thin-pool `when_full` names, VDO/cache undefined names, and dynamic fuzzy time matching.

## Fuzzy Time Parser

A substantial early section implements fuzzy time parsing for LV creation/removal time selection:

- Token classes cover numbers, relative/absolute units, weekdays, months, labels such as today/yesterday/noon/midnight, and time zones.
- `_preparse_fuzzy_time()` tokenizes non-standard time strings.
- `_recognize_time_items()` maps strings/numbers to semantic time tokens.
- `_check_time_items()` rejects ambiguous or mixed absolute/relative combinations.
- `_translate_time_items()` converts a fuzzy expression into a time range string.
- `_lv_time_handler()` exposes parsing and dynamic value extraction to device-mapper report selection.

## Display Function Families

The file implements field display functions referenced by `columns.h`:

- Primitive/string/list helpers: `_field_string`, `_field_set_value`, `_field_set_string_list`, `_string_disp`, `_chars_disp`, `_uuid_disp`, `_tags_disp`.
- Binary handling: `_binary_disp` switches between numeric `0/1` and blank/word display based on strict/numeric report settings; `_binary_undef_disp` handles unknown.
- Size and numeric handling: `_size32_disp`, `_size64_disp`, `_uint32_disp`, `_uint8_disp`, `_int32_disp`.
- Device/PV/VG display: device major/minor/name/size, PV UUID/status/size/free/used/metadata areas/device IDs, VG status/size/free/system ID/locks/persistent reservation/metadata/LV/snapshot counts.
- LV display: name/full name/path/dm path/parent/origin/data/metadata/pool/log/convert/move LVs and UUIDs, modules, profile, lock args, attr string, permissions, active states, health, time/removed time/host, layout/role, historical status.
- Segment display: segment type, starts/sizes, ranges/devices, stripes/data stripes/reshape/data offsets/parity, chunk/region/stripe sizes, thin/cache/integrity/VDO/writecache settings.
- Live status fields: data/snapshot/metadata/copy percentages, cache counters/settings, kernel cache policy/mode/metadata format, thin discards/check-needed, snapshot invalid/merge-failed, VDO runtime state, writecache counters.

## LV Relationship Traversal

The report can synthesize ancestry and descendant fields:

- `_find_ancestors()` follows COW origins, thin origins/external origins, and optional historical indirect origins.
- `_find_descendants()` follows snapshot COWs, thin descendants via `segs_using_this_lv`, and optional historical indirect GLVs.
- `cmd->include_historical_lvs` controls whether historical LVs appear in these list fields.

## RAID, Integrity, Cache, Thin, VDO, Writecache Handling

Specialized display logic covers:

- RAID sync action, mismatch count, writebehind, recovery rates, integrity mode/block size/mismatches.
- Cache policy/settings from metadata and kernel status, plus cache counters.
- Thin pool discard policy, transaction IDs, thin IDs, zeroing, metadata/data percent, out-of-data/read-only health.
- VDO configuration fields from `seg->vdo_params` and runtime status from `SEG_STATUS_VDO_POOL`.
- Writecache block size and runtime counters.

## Report Initialization and Dispatch

- `report_headings_str_to_type()` parses heading mode strings.
- `report_init()` builds `dm_report` handles with flags for alignment, buffering, headings, field prefixes, quoting, columns-as-rows, and multiple output. It selects the correct schema for command-log, device-type, or normal LVM reports.
- `report_init_for_selection()` creates a selection-only report handle.
- `report_get_prefix_and_desc()` returns object type prefix/description.
- `report_object()` builds an `lvm_report_object`, fills fallback labels/devices where needed, hides orphan VGs behind dummy/unknown VGs, and either evaluates selection or emits a report row.
- `report_devtypes()` iterates `dev_known_types`.
- `report_cmdlog()`, `report_reset_cmdlog_seqnum()`, and `report_current_object_cmdlog()` implement structured command-log report rows.

## Important Edge Cases

- Orphan VGs are never reported directly; dummy and unknown VGs are used for PV reporting context.
- Some fields return reserved undefined values rather than empty strings to preserve sorting/selection semantics.
- Live status fields depend on activation/device-mapper status. If activation is unavailable, binary active fields often report unknown.
- Shared VG exclusive activation checks may query `lvmlockd`.
- Several list fields use dummy empty lists because string-list reserved values are noted as TODO.
