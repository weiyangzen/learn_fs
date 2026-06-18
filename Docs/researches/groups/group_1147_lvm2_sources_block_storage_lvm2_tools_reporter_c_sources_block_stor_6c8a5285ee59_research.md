# Group Research: group_1147_lvm2_sources_block_storage_lvm2_tools_reporter_c_sources_block_stor_6c8a5285ee59

Scope: `Docs/research_subset_a.md`, source tree `sources/block-storage/lvm2`.

This grouped report covers LVM2 CLI reporting commands, shared command traversal/validation helpers, simple display commands, removed-command stubs, and the `toollib` public interface.

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/reporter.c -->
# File Research: sources/block-storage/lvm2/tools/reporter.c

## Purpose
`reporter.c` implements LVM2 report-producing commands: `lvs`, `vgs`, `pvs`, `fullreport`, `devtypes`, `lastlog`, plus report format initialization/destruction. It translates report config and CLI options into `dm_report` handles, selects the right object traversal path, and emits basic, JSON, or JSON standard report groups.

## Main Flow
Command entry points call `_report()` with an initial report type. `_report()` creates a `processing_handle`, loads report defaults and command overrides through `_config_report()`, pushes the top report group section, then either runs `_do_report()` for a single report or `process_each_vg()` with `_full_report_single()` for grouped full reports.

`_do_report()` builds a report handle via `report_init()`, determines the final report type from the requested fields, pushes the subreport into the report group, dispatches to the matching iterator, compacts fields if requested, outputs the report, and frees the report handle.

## Important Behavior
- `_get_final_report_type()` promotes report types based on fields: segment fields imply LV/PV segment traversal, PV fields imply PV traversal, and incompatible LV/PV field mixes are rejected.
- `_get_report_options()`, `_get_report_keys()`, and `_get_report_selection()` handle grouped `--configreport` options, `-o` add/remove/replace/compact modes, sort keys, and per-report selection strings.
- LV and segment reports choose callbacks that optionally collect LV info and/or segment status when selected fields require them.
- Merging origins are special-cased: status may be fetched to decide whether a thin snapshot should be reported instead of the origin.
- RAID LV health warnings are emitted when unhealthy RAID volumes need refresh or repair, with different wording when hidden SubLVs require `-a`.
- PV segment reporting fabricates synthetic “free” LV/segment objects for free PV ranges so free space can pass through the common report object API.
- `pvs -a` disables hints, and `pvs --allpvs` also skips device-id filtering, because those modes intentionally broaden device discovery.
- `report_for_selection()` supports non-reporting commands using report expressions for `--select` without causing recursive selection reporting.

## Report Format Lifecycle
`report_format_init()` selects `basic`, `json`, or `json_std`, creates the global `dm_report_group`, optionally initializes command-log reporting, and installs the log report handle. `json_std` enables strict numeric/bin field output and temporarily forces `LC_NUMERIC` to `C` if the active locale uses a non-dot radix character. `report_format_destroy()` destroys report group state, frees the log report, and restores locale state.

## Integration Notes
This file is tightly coupled to `lib/report/report.h`, device-mapper report groups, command argument grouping, config-tree defaults, and `toollib.c` object iterators. Adding report fields or new report types can alter traversal behavior through type promotion, so changes need report/selection tests across `lvs`, `pvs`, `vgs`, `fullreport`, and JSON modes.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/reporter.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/segtypes.c -->
# File Research: sources/block-storage/lvm2/tools/segtypes.c

## Purpose
`segtypes.c` implements the `segtypes` command.

## Behavior
`segtypes()` ignores positional arguments, calls `display_segtypes(cmd)`, and returns `ECMD_PROCESSED`.

## Integration Notes
This is a thin read-only CLI wrapper around the segment-type display helper exposed through `tools.h`. It performs no local validation or filtering.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/segtypes.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/stub.h -->
# File Research: sources/block-storage/lvm2/tools/stub.h

## Purpose
`stub.h` provides function bodies for historical LVM command names that are no longer supported in LVM2.

## Behavior
It defines stubs for `lvmsadc`, `lvmsar`, `pvdata`, `lvmchange`, and `vgconvert`. Each logs explanatory errors and returns `ECMD_FAILED`.

## Integration Notes
Despite the `.h` suffix, this file contains implementations. The stubs preserve command registration compatibility while directing users toward supported replacements such as `dmstats`, `lvs`/`pvs`/`vgs`, `vgcfgbackup`, `dmsetup`, or an older LVM version for LVM1 conversion.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/stub.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/tags.c -->
# File Research: sources/block-storage/lvm2/tools/tags.c

## Purpose
`tags.c` implements the `tags` command.

## Behavior
`tags()` ignores positional arguments, calls `display_tags(cmd)`, and returns `ECMD_PROCESSED`.

## Integration Notes
This is a simple read-only display wrapper around tag reporting support from the tools layer.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/tags.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/tool.h -->
# File Research: sources/block-storage/lvm2/tools/tool.h

## Purpose
`tool.h` is a small common include header for LVM2 tool sources.

## Contents
It includes allocation helpers, `libdevmapper`, generic utility helpers, and `<unistd.h>` behind the `LVM_TOOL_H` include guard.

## Integration Notes
The header comment says most tool source files should include `tool.h`, `lib.h`, or `dmlib.h`. It provides baseline dependencies rather than command-specific declarations.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/tool.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/toollib.c -->
# File Research: sources/block-storage/lvm2/tools/toollib.c

## Purpose
`toollib.c` is the shared execution library for LVM2 CLI commands. It centralizes object traversal over VGs, LVs, PVs, labels, LV segments, and PV segments; `--select` handling; activation helpers; argument/name normalization; command rule enforcement; tag mutation; PV create/remove preparation; and persistent-reservation support.

## Processing And Selection
`init_processing_handle()` creates shared processing state, initializes report formatting when needed, and enables internal report-based selection for non-report commands using `--select`. `init_selection_handle()` builds the selection report handle. `select_match_vg()`, `select_match_lv()`, and `select_match_pv()` call `report_for_selection()` so ordinary commands can filter objects through report expressions. Selection aggregation treats a parent object as selected when at least one child segment/LV/PV matches.

## Object Traversal
- `process_each_vg()` parses VG names/tags, performs label scans, resolves duplicate VG names, optionally locks the global namespace, reads VGs with lockd handling, skips inaccessible VGs according to command context, and invokes a per-VG callback.
- `process_each_lv()` derives VG/LV targets from positional args or option-derived VG names, scans VGs, and delegates per-VG work to `process_each_lv_in_vg()`.
- `process_each_lv_in_vg()` filters visible/hidden/component/sanlock/historical LVs, applies tags and selection, validates LV type/property command rules, orders thin pools first, invalidates stacked LV label scans, and invokes the LV callback.
- `process_each_pv()` maps PV path args to devices, scans all relevant VGs, processes PVs by device/tag/all selection, handles inaccessible VGs, duplicate PV devices, and `-a` non-PV device reporting.
- `process_each_label()` scans labels directly from `lvmcache`, including explicit duplicate-device handling for label reports.
- `process_each_segment_in_lv()` and `process_each_segment_in_pv()` iterate segment lists and propagate aggregate selection state.

## Validation And Rule Enforcement
The file maps generated command-definition LV type/property bits to runtime predicates through `_lv_is_type()` and `_lv_is_prop()`. `_check_lv_types()` validates positional LV type constraints, while `_check_lv_rules()` evaluates conditional `RULE_INVALID` and `RULE_REQUIRE` constraints over options, LV types, and LV properties. This is the bridge between generated command metadata and runtime object safety checks.

## Parameter Parsing Helpers
The file parses common command options for:
- VG creation defaults, system IDs, shared lock types, sanlock lock args, and metadata copy counts.
- Pool, stripe, cache, VDO, writecache, and integrity settings.
- Activation monitoring mode and persistent major/minor numbers.
- LV names, restricted LV names, default VG names from `LVM_VG_NAME`, and `/dev`/`/dev/mapper` path normalization.

## Activation And Background Work
`lv_change_activate()` enforces activation/deactivation constraints for cache pools, merging origins, partial RAID snapshots, duplicate PVs, and uninitialized integrity LVs. `lv_refresh()` refreshes suspend/resume state and starts background polling for active snapshot merges. `vg_refresh_visible()` refreshes visible LVs in a VG. `lv_spawn_background_polling()` launches pvmove or lvconvert polling helpers for in-progress operations.

## PV Create/Remove Workflow
`pvcreate_params_from_args()` parses PV creation/removal options including label sector, metadata copies, metadata ignore, zeroing, alignment, bootloader area, persistent reservations, and shared-VG constraints.

`pvcreate_each_device()` is the main device workflow for `pvcreate`, `pvremove`, `vgcreate`, and `vgextend` callers. It translates names to devices, scans and filters arguments with full MD checks, verifies block-size consistency, classifies existing PV/VG usage, handles force/yes prompts, releases/reacquires the global lock around interactive prompts, rescans devices exclusively, verifies devices did not change, starts persistent reservations when requested, wipes signatures, writes PV labels, removes PV labels, updates device IDs, and invalidates exclusive label-scan state.

## Other Utilities
`change_tag()` applies add/remove tag operations to exactly one VG, LV, or PV target. `lvremove_single()` removes an LV with dependency handling and records removed UUIDs for devices-file updates. `get_rootvg_dev_uuid()` finds the root mount in `/etc/mtab`, maps its device number to a dm UUID, and returns it if it is an LVM UUID. `persist_start_include()` implements direct, supplementary, and automatic persistent-reservation start behavior.

## Integration Notes
`toollib.c` sits between command handlers and lower LVM libraries: metadata read/write, lvmcache, label scanning, device filters, lockd, activation, reporting, config, persistent reservations, and device-id files. The highest-risk areas are duplicate VG/PV handling, lock ordering around prompts and shared VGs, report-selection recursion, command-rule drift, PV filtering, and code paths that intentionally process partially readable or inaccessible metadata.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/toollib.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/tools/toollib.h -->
# File Research: sources/block-storage/lvm2/tools/toollib.h

## Purpose
`toollib.h` declares the shared processing interface used by LVM2 command implementations.

## Main Types
It defines `struct processing_handle`, which carries parent processing context, internal selection-report state, historical-LV inclusion, and caller-specific `custom_handle` data. It also defines callback typedefs for processing one VG, PV, label, LV, LV segment, PV segment, and an LV pre-check callback.

## API Surface
The header declares object iterators for VGs, PVs, labels, LVs, LV segments, PV segments, and PVs within a VG. It also declares processing-handle lifecycle functions, selection helpers, name parsing helpers, option-list utilities, PV/VG creation parameter helpers, activation/refresh helpers, pool/cache/VDO/writecache/integrity parsers, tag mutation, persistent major/minor validation, LV name validation, LV removal, LV type lookup, root VG UUID discovery, and persistent-reservation start inclusion.

## Selection Contract
The header documents the key selection distinction: reporting commands do selection as part of normal `dm_report_object` output, while non-reporting commands use hidden internal report handles to evaluate `--select` before running callbacks. This avoids double reporting for display commands.

## Integration Notes
This file is the contract between individual command files and `toollib.c`. Changes to callback signatures or `processing_handle` semantics affect many command implementations across the tools directory.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/tools/toollib.h -->