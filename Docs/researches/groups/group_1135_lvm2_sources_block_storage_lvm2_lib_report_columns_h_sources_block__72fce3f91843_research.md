# Group Research: group_1135_lvm2_sources_block_storage_lvm2_lib_report_columns_h_sources_block__72fce3f91843

Scope: `Docs/research_subset_a.md` includes `sources/block-storage/lvm2`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/report/columns.h -->
# File Research: sources/block-storage/lvm2/lib/report/columns.h

## Purpose

`columns.h` is the central X-macro catalog of LVM2 report columns. It is included under different `FIELD(...)` macro definitions to generate report field enums, field descriptors, property metadata, help text, and property bindings for `pvs`, `vgs`, `lvs`, segment, label, and PV segment reports.

## Main Contents

Each row has the shape:

`FIELD(report_object_type, structure, sort_type, heading, structure_field, output_width, reporting_function, field_id, description, settable_via_lib)`

The file groups fields by report type:

- `LVS`: LV identity, names, paths, parent/layout/role, activation, sizes, origin, ancestors/descendants, RAID/cache/thin/VDO/writecache metadata, tags, profile, lock args, timestamps, host, modules, historical state.
- `LVSINFO`: kernel major/minor, kernel read-ahead, permissions, suspended/live/inactive table/open-device state.
- `LVSSTATUS`: active/runtime percentages and counters for snapshots, cache, thin, RAID, VDO, and writecache.
- `LVSINFOSTATUS`: combined LV attribute string.
- `LABEL`: PV label/device metadata, including format, UUID, device size/name/major/minor, metadata area free/size, PV header extension version.
- `PVS`: PV size/free/used/status/allocation/export/missing/extents/tags/metadata areas/bootloader area/duplicate/device ID fields.
- `VGS`: VG format/UUID/name/status/permissions/autoactivation/partial/allocation/shared/size/free/system ID/lock/persistent reservation/extents/counts/tags/profile/metadata area fields.
- `SEGS`: LV segment type, stripe/RAID/thin/cache/integrity/VDO settings, ranges, devices, tags, monitoring.
- `PVSEGS`: PV segment start and size.

## Design Notes

- Field order is user-visible in `-o help`, so report types are intentionally not interleaved.
- Display names usually use report-object prefixes and underscores; display function names usually match without underscores.
- `field_id` is the stable key used by selection, reserved values, and liblvm properties.
- `vg_mda_copies` is the only listed field marked settable via liblvm.
- There is no executable logic here; correctness depends on matching display functions in `report.c` and property accessors in `properties.c`.

## Dependencies and Consumers

- Included by `report.c` to generate field enums and `struct dm_report_field_type` arrays.
- Included by `properties.c` to generate `_properties[]`.
- Field IDs are referenced by `values.h` reserved values and selection aliases.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/report/columns.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/report/properties.c -->
# File Research: sources/block-storage/lvm2/lib/report/properties.c

## Purpose

`properties.c` implements liblvm property accessors for report fields. It bridges `columns.h` to `struct lvm_property_type` entries and type-specific `*_get_property` / `*_set_property` functions.

## Main Structure

The file defines macro families for VG, PV, LV, LV segment, and PV segment property access:

- Numeric getters: `GET_VG_NUM_PROPERTY_FN`, `GET_PV_NUM_PROPERTY_FN`, `GET_LV_NUM_PROPERTY_FN`, `GET_LVSEG_NUM_PROPERTY_FN`, `GET_PVSEG_NUM_PROPERTY_FN`.
- Signed numeric getter: `GET_LV_SNUM_PROPERTY_FN`.
- String getters: `GET_VG_STR_PROPERTY_FN`, `GET_PV_STR_PROPERTY_FN`, `GET_LV_STR_PROPERTY_FN`, `GET_LVSEG_STR_PROPERTY_FN`, `GET_PVSEG_STR_PROPERTY_FN`.
- Setters are mostly `prop_not_implemented_set`; `vg_mda_copies` is implemented through `vg_set_mda_copies`.

## Key Helper Logic

- `_copy_percent()` calls `lv_mirror_percent()` and falls back to `DM_PERCENT_INVALID`.
- RAID helpers expose mismatch count, sync action, writebehind, recovery rates, integrity mode/block size, and integrity mismatch counts.
- `_snap_percent()` handles COW snapshot usage.
- `_data_percent()` reports snapshot, cache/cache-pool, thin-volume, and thin-pool data usage from live status objects, destroying temporary pools afterward.
- `_metadata_percent()` reports cache/thin-pool metadata usage.

## Property Coverage

Implemented static metadata getters cover:

- PV: format, UUID, device size/name, MDA free/size/counts, PE start/size/free/used/counts, attributes, tags, bootloader area, device ID/type.
- LV: UUID/name/full name/path/dm path/parent/attr, major/minor, read-ahead, kernel major/minor/read-ahead, size, segment count, origin, snapshot/copy/RAID/integrity percentages and counters, pvmove/convert/cache/thin/VDO related LVs, tags, modules, metadata size, time, host, active/profile/lock args.
- VG: format, UUID/name/attr, size/free/system ID/lock type/lock args, extent data, max LV/PV, PV/LV/snapshot counts, seqno, tags, metadata area data, profile, missing PV count.
- LV segment: type, copies, reshape/data offsets, stripes, stripe/region/chunk sizes, thin count/zero/transaction/thin ID, discards/cache mode/cache metadata format, starts/sizes/tags/ranges/devices/monitoring.
- PV segment: start and size.

Many dynamic or display-only fields use `prop_not_implemented_get`, especially fields requiring live device-mapper status, activation state, reserved-value synthesis, or string-list display behavior.

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

Each delegates to `prop_get_property()` or `prop_set_property()` with the relevant report-type mask.

## Dependencies

- Includes `columns.h` into `_properties[]`.
- Depends on `lib/properties/prop_common.h` for generic property machinery.
- Depends heavily on metadata, activation, RAID, cache, thin, and integrity helpers.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/report/properties.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/report/properties.h -->
# File Research: sources/block-storage/lvm2/lib/report/properties.h

## Purpose

`properties.h` declares the liblvm property access API implemented by `properties.c`.

## API Surface

It includes device-mapper, metadata, report, and common property definitions, then declares:

- `lvseg_get_property`
- `lv_get_property`, `lv_set_property`
- `vg_get_property`, `vg_set_property`
- `pvseg_get_property`
- `pv_get_property`, `pv_set_property`

## Design Notes

- All APIs take a concrete LVM metadata object plus a mutable `struct lvm_property_type *prop`.
- Getters fill the requested property from the internal generated property table.
- Setters only work where the table marks a field writeable and a setter exists.
- The header intentionally does not expose `_properties[]` or generated accessor internals.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/report/properties.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/report/report.c -->
# File Research: sources/block-storage/lvm2/lib/report/report.c

## Purpose

`report.c` is the main LVM2 report engine implementation for normal LVM reports, device-type reports, and command-log reports. It defines report row wrappers, display functions, reserved value registration, fuzzy time selection, report initialization, object dispatch, and command-log rows.

## Core Data Model

- `struct lvm_report_object` bundles possible backing objects for one row: VG, LV with info/status, PV, LV segment, PV segment, and label.
- `_report_types[]` maps `VGS`, `LVS`, `PVS`, `SEGS`, `LABEL`, etc. to object extractors and field prefixes.
- `_fields[]` is generated from `columns.h`.
- `_devtypes_fields[]` and `_log_fields[]` are generated from `columns-devtypes.h` and `columns-cmdlog.h`.
- Dummy and unknown VGs provide PV reporting context for orphan or used orphan PVs.

## Reserved Values and Selection

The file includes `values.h` under multiple macro definitions to generate:

- Static reserved value constants and name arrays.
- `_report_reserved_values[]` for `dm_report_init_with_selection()`.
- Field-number enum entries generated from `columns.h`.

Reserved values cover named binary display/selection aliases, undefined numeric values, LV and VG permissions, thin-pool `when_full` states, VDO/cache undefined states, and dynamic fuzzy time values.

## Fuzzy Time Parser

A large early section implements fuzzy time parsing for `lv_time` and `lv_time_removed` selection:

- Token classes cover numbers, relative and absolute units, weekdays, months, labels such as today/yesterday/noon/midnight, and time zones.
- `_preparse_fuzzy_time()` tokenizes non-standard date/time strings.
- `_recognize_time_items()` maps tokens to semantic time items.
- `_check_time_items()` rejects ambiguous or mixed absolute/relative combinations.
- `_translate_time_items()` converts fuzzy input into an absolute time range.
- `_lv_time_handler()` exposes parsing and dynamic value extraction to device-mapper reporting.

## Display Functions

The file implements the display functions referenced by `columns.h`:

- Primitive helpers: strings, chars, UUIDs, tags, string lists, binary display, numeric display, sizes, percentages.
- Device/PV/VG display: device numbers/names/sizes, PV UUID/status/size/free/used/MDA/device IDs, VG attributes/permissions/locks/persistent reservation/metadata/LV/snapshot counts.
- LV display: names, paths, parent/origin/data/metadata/pool/log/convert/move LVs and UUIDs, modules, profile, lock args, attr string, permissions, activation states, health, timestamps, host, layout/role, historical state.
- Segment display: type, starts/sizes, ranges/devices, stripes/data stripes/reshape offsets, RAID parity/copies, chunk/region/stripe sizes, thin/cache/integrity/VDO settings.
- Live status display: snapshot/data/metadata/copy percentages, cache counters and kernel settings, thin discards/check-needed, snapshot invalid/merge failed, VDO runtime state, writecache counters.

## LV Relationship Traversal

The report can synthesize ancestry and descendant lists:

- `_find_ancestors()` follows COW origins, thin origins/external origins, and optional historical indirect origins.
- `_find_descendants()` follows snapshot COWs, thin descendants through `segs_using_this_lv`, and optional historical indirect GLVs.
- `cmd->include_historical_lvs` controls whether historical LVs are emitted in these list fields.

## Feature-Specific Handling

Specialized logic covers:

- RAID sync action, mismatch count, writebehind, min/max recovery rates, reshape lengths, parity chunks, and integrity settings.
- Cache policy/settings from metadata and kernel status, plus cache block and hit/miss counters.
- Thin-pool discard policy, transaction IDs, thin IDs, zeroing, metadata/data usage, out-of-data/read-only health.
- VDO configuration fields from `seg->vdo_params` and runtime operating/compression/index states from `SEG_STATUS_VDO_POOL`.
- Writecache block size and runtime counters.

## Report Initialization and Dispatch

- `report_headings_str_to_type()` parses heading mode strings.
- `report_init()` builds `dm_report` handles and selects normal, device-type, or command-log schemas.
- `report_init_for_selection()` creates a selection-only report handle.
- `report_get_prefix_and_desc()` returns report prefix/description.
- `report_object()` builds `struct lvm_report_object`, fills fallback labels/devices, hides orphan VGs behind dummy/unknown VGs, and either evaluates selection or emits a row.
- `report_devtypes()` iterates `dev_known_types`.
- `report_cmdlog()`, `report_reset_cmdlog_seqnum()`, and `report_current_object_cmdlog()` implement structured command-log rows.

## Important Edge Cases

- Orphan VGs are never reported directly.
- Undefined values often use reserved values rather than blank strings to preserve sorting and selection semantics.
- Live status fields depend on activation/device-mapper state; activation-disabled cases often report unknown.
- Shared VG exclusive activation checks may query `lvmlockd`.
- Several string-list fields use empty dummy lists because reserved values for `STR_LIST` are noted as incomplete.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/report/report.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/report/report.h -->
# File Research: sources/block-storage/lvm2/lib/report/report.h

## Purpose

`report.h` declares public report types, selection state, command-log row shape, and reporting APIs used by LVM command and processing code.

## Main Definitions

Report type bit flags:

- `CMDLOG`, `FULL`
- `LVS`, `LVSINFO`, `LVSSTATUS`, `LVSINFOSTATUS`
- `PVS`, `VGS`, `SEGS`, `PVSEGS`, `LABEL`
- `DEVTYPES`

Heading modes:

- `REPORT_HEADINGS_UNKNOWN`
- `REPORT_HEADINGS_NONE`
- `REPORT_HEADINGS_ABBREV`
- `REPORT_HEADINGS_FULL`

`struct selection_handle` wraps a selection-only `dm_report`, preserves original/effective report type masks, and stores the selected result.

`struct cmd_log_item` is the row object for command-log reporting, including sequence number, type, context, object identity, group identity, message, errno, and return code.

## API Surface

Declared APIs include:

- Report format lifecycle: `report_format_init`, `report_format_destroy`
- Report creation: `report_init`, `report_init_for_selection`
- Selection helpers: `report_get_single_selection`, `report_for_selection`
- Metadata helpers: `report_headings_str_to_type`, `report_get_prefix_and_desc`
- Emission and cleanup: `report_object`, `report_devtypes`, `report_cmdlog`, `report_output`, `report_free`
- Command-log helpers: `report_reset_cmdlog_seqnum`, `report_current_object_cmdlog`

## Dependencies

The header exposes metadata, label, and activation types through `metadata-exported.h`, `label.h`, and `activate.h`.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/report/report.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/report/values.h -->
# File Research: sources/block-storage/lvm2/lib/report/values.h

## Purpose

`values.h` is the X-macro catalog of reserved report values and selection aliases. It is consumed by `report.c` to generate reserved value objects and register them with device-mapper reporting.

## Main Contents

Macro forms:

- `TYPE_RESERVED_VALUE(...)`: reserved values for an entire report field type.
- `FIELD_RESERVED_VALUE(...)`: reserved values for a specific field.
- `FIELD_RESERVED_BINARY_VALUE(...)`: convenience form for binary fields where listed names map to value `1`, with generated blank/no forms for `0`.

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
- New display values are expected to be self-descriptive and use appropriate display helpers.
- `STR_LIST` reserved values for cache settings are noted as TODO/commented out.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/report/values.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/snapshot/snapshot.c -->
# File Research: sources/block-storage/lvm2/lib/snapshot/snapshot.c

## Purpose

`snapshot.c` implements the LVM segment type handler for snapshot volumes, including metadata import/export, device-mapper target selection/status, module requirements, dmeventd monitoring hooks, and segment type initialization.

## Metadata Import/Export

- `_snap_text_import()` reads `chunk_size`, `origin`, and either `cow_store` or `merging_store`.
- It rejects metadata specifying both COW and merging storage.
- It resolves origin and COW LVs with `find_lv()` and initializes the segment with `init_snapshot_seg()`.
- `_snap_text_export()` writes `chunk_size`, `origin`, and either `cow_store` or `merging_store` depending on `MERGING`.

## Device-Mapper Support

When `DEVMAPPER_SUPPORT` is enabled:

- `_snap_target_name()` returns `snapshot-merge` during merge activation unless `laopts->no_merging` is set.
- `_snap_target_status_compatible()` accepts `snapshot-merge` status.
- `_snap_target_percent()` parses snapshot target status, reports invalid/merge-failed states, accumulates used/total sectors, handles metadata-only cases as 0%, and reports full devices as 100%.
- `_snap_target_present()` caches availability checks for `snapshot`, `snapshot-origin`, and conditionally `snapshot-merge`; it also records `SNAPSHOT_FEATURE_FIXED_LEAK` based on target version.
- `_snap_modules_needed()` adds the snapshot kernel module name.

## Dmeventd Hooks

When `DMEVENTD` is enabled:

- `_target_registered()` checks monitoring registration for the COW LV.
- `_target_set_events()` registers/unregisters events through the snapshot DSO with a fixed timeout.
- `_target_register_events()` and `_target_unregister_events()` wrap event toggling.

## Segment Type Registration

`_snapshot_ops` wires import/export, target/status/presence/percent/module, dmeventd, and destroy callbacks.

`init_snapshot_segtype()` or shared-object `init_segtype()` allocates a `struct segment_type` with:

- name `SEG_TYPE_NAME_SNAPSHOT`
- flags `SEG_SNAPSHOT | SEG_CANNOT_BE_ZEROED | SEG_ONLY_EXCLUSIVE`
- optional `SEG_MONITORED` when a dmeventd DSO path is configured.

## Important Edge Cases

- Import rejects missing or incorrectly typed `origin`/COW metadata.
- Merge target presence is checked only for merging snapshot segments.
- Target support checks are cached statically for process lifetime.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/snapshot/snapshot.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/striped/striped.c -->
# File Research: sources/block-storage/lvm2/lib/striped/striped.c

## Purpose

`striped.c` implements the segment type handler for both striped and linear LVM segments. Linear is represented as the same handler with one area.

## Metadata and Display

- `_striped_name()` reports `linear` when `area_count == 1`; otherwise it reports the segment type name.
- `_striped_display()` prints a single stripe for linear segments, or stripe count, stripe size, and each stripe for striped segments.
- `_striped_text_import_area_count()` reads `stripe_count`.
- `_striped_text_import()` reads `stripe_size` for multi-stripe segments, reads the `stripes` array, divides `area_len` by area count, and imports areas through `text_import_areas()`.
- `_striped_text_export()` writes `stripe_count`, optional `stripe_size`, and area mappings.

## Segment Merge Logic

- `_striped_segments_compatible()` allows merges only when area count, stripe size, area types, PV identity, PE continuity, and tags match.
- It currently supports PV-backed areas only, with comments noting possible relaxation.
- `_striped_merge_segments()` extends logical and area lengths, then merges corresponding PV segments.

## Device-Mapper Support

When enabled:

- `_striped_target_status_compatible()` treats `linear` target status as compatible.
- `_striped_add_target_line()` emits either a linear target for one area or a striped target for multiple areas, then appends area mappings with `add_areas_line()`.
- `_striped_target_present()` caches target availability and requires both `linear` and `striped` targets when activation is enabled.

## Segment Type Registration

`_striped_ops` wires name/display/import/export/merge and optional device-mapper callbacks.

`_init_segtype()` allocates a handler with:

- supplied name, `striped` or `linear`
- target flags, `SEG_STRIPED_TARGET` or `SEG_LINEAR_TARGET`
- common flags `SEG_CAN_SPLIT | SEG_AREAS_STRIPED`

Public constructors:

- `init_striped_segtype()`
- `init_linear_segtype()`

## Important Edge Cases

- `_striped_add_target_line()` rejects zero-area segments.
- Linear and striped share behavior; the distinction is mostly `area_count` and target/name selection.
- Target presence is cached statically.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/striped/striped.c -->