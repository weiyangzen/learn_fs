# File Research: sources/block-storage/lvm2/lib/report/values.h

## Purpose

`values.h` is the X-macro catalog of reserved report values and selection aliases. It is consumed by `report.c` to generate reserved value objects and register them with device-mapper reporting.

## Main Contents

Macro forms:

- `TYPE_RESERVED_VALUE(...)`: reserved values for an entire report field type.
- `FIELD_RESERVED_VALUE(...)`: reserved values for a specific field.
- `FIELD_RESERVED_BINARY_VALUE(...)`: convenience form for binary fields where listed names map to value `1`, with blank/no forms for `0`.

## Reserved Values

Major entries include:

- Numeric undefined value: `-1`, with aliases `unknown`, `undefined`, `undef`.
- PV binary aliases: allocatable, exported, missing, used/in use, duplicate.
- VG binary aliases: extendable, exported, partial, clustered, shared.
- VG permission aliases: writeable/rw/read-write and read-only/r/ro.
- `vg_mda_copies` unmanaged value.
- LV binary aliases: initial image sync, image synced, merging, converting, allocation locked, fixed minor, active variants, merge failed, snapshot invalid, suspended, live/inactive table, open, skip activation, zero, check needed.
- VDO binary aliases for compression, deduplication, metadata hints, sparse index.
- LV permission aliases including read-only override.
- `lv_read_ahead` auto value.
- Thin-pool `lv_when_full` values: error, queue, undefined.
- Fuzzy/dynamic/range values for `lv_time` and `lv_time_removed`, handled by `_lv_time_handler` in `report.c`.
- Undefined strings for cache policy, segment monitor, LV health, kernel discards, and VDO write policy.

## Design Notes

- The first reserved name is the display value; later names are selection synonyms.
- Binary display can be numeric or string depending on report settings.
- The file documents that new display values should be self-descriptive and should use appropriate display helpers.
- String-list reserved values for cache settings are noted as TODO/commented out because STR_LIST reserved support is incomplete.
