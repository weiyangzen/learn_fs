# File Research: sources/block-storage/lvm2/lib/report/columns.h

## Purpose

`columns.h` is the central X-macro catalog of LVM2 report columns. It is included by multiple compilation units under different `FIELD(...)` macro definitions to generate field enums, display metadata, property metadata, help text, and field descriptors for commands such as `pvs`, `vgs`, `lvs`, segment reports, label reports, and PV segment reports.

## Main Contents

Each entry has the shape:

`FIELD(report_object_type, structure, sort_type, heading, structure_field, output_width, reporting_function, field_id, description, settable_via_lib)`

The file groups fields by report type:

- `LVS`: LV identity, names, paths, parent/layout/role, activation, size, origin, ancestors/descendants, RAID/cache/thin/VDO/writecache metadata, tags, profile, lock args, creation/removal time, host, modules, historical state.
- `LVSINFO`: kernel major/minor, kernel read-ahead, permissions, suspended/live/inactive table/open-device state.
- `LVSSTATUS`: active status-derived percentages and counters: data/snapshot/metadata/copy percent, cache counters/settings, kernel cache policy/mode/metadata format, health, thin discards/check-needed, snapshot invalid/merge failed, VDO runtime state, writecache counters.
- `LVSINFOSTATUS`: combined LV attr string.
- `LABEL`: PV label/device metadata, including format, UUID, device size/name/major/minor, metadata area free/size, PV header extension version.
- `PVS`: PV size/free/used/status/allocation/export/missing/extents/tags/metadata areas/bootloader area/duplicate/device ID fields.
- `VGS`: VG format/UUID/name/status/permissions/autoactivation/partial/allocation/cluster/shared/size/free/system ID/lock/persistent reservation/extents/counts/tags/profile/metadata area fields.
- `SEGS`: LV segment type, stripes/copies/reshape/data offsets/parity, stripe/region/chunk sizes, thin/cache/integrity/VDO settings, starts/sizes/tags/ranges/devices/monitoring.
- `PVSEGS`: PV segment start and size.

## Important Design Points

- Field ordering is user-visible in report help output, so fields are intentionally grouped and not interleaved across report types.
- Displayed names generally use report-object prefixes and underscores; internal function names normally match field names without underscores.
- `field_id` is the stable identifier used by selection/reserved values and library property APIs.
- The last `settable_via_lib` flag is almost always `0`; `vg_mda_copies` is marked settable via the library.
- This file has no executable logic; correctness depends on every `FIELD` entry matching display functions in `report.c` and property get/set symbols in `properties.c`.

## Dependencies and Consumers

- Included by `report.c` to generate field enum values and `struct dm_report_field_type` descriptors.
- Included by `properties.c` to generate `_properties[]` for liblvm property access.
- Field IDs are referenced by `values.h` for reserved names and selection aliases.
