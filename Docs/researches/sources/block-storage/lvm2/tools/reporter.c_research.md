# File Research: sources/block-storage/lvm2/tools/reporter.c

## Purpose
`reporter.c` implements LVM2 reporting commands: `lvs`, `vgs`, `pvs`, `fullreport`, `devtypes`, `lastlog`, and report-format setup/teardown. It converts report configuration and command-line report options into `dm_report` handles, iterates LVM objects through `toollib.c`, and emits basic, JSON, or JSON standard report groups.

## Main Flow
The command entry points call `_report()` with an initial report type. `_report()` initializes a processing handle, reads report configuration via `_config_report()`, pushes a top-level report group, then dispatches either one report with `_do_report()` or a grouped full report through `_full_report_single()`.

`_do_report()` initializes a report handle with options, sort keys, separators, headings, quoting, row mode, and selection. It derives the final report type from selected fields, pushes the report into the active report group, invokes the matching object iterator, optionally compacts fields, outputs the report, and frees the handle.

## Key Behavior
- `_get_final_report_type()` upgrades report types based on requested fields, e.g. segment fields imply LV/PV segment reports.
- `_get_report_options()` handles `-o`, including add, remove, replace, and compact-column forms, and supports per-subreport `--configreport`.
- `_get_report_keys()` and `_get_report_selection()` apply per-report sort and selection expressions.
- LV and segment reporting can collect activation info and/or segment status when fields require it.
- Snapshot merge handling can report a thin snapshot instead of its merging origin when the active table shows the origin has gone.
- RAID health warnings are emitted for unhealthy RAID LVs, especially when hidden SubLVs may need `-a`.
- PV segment reporting fabricates a “free” LV/segment object for free PV ranges so they can flow through the common report object API.
- Full reports group VG, PV, LV, PV segment, and LV segment subreports per VG, with special orphan handling.
- `pvs -a` and `pvs --allpvs` disable hints/device-id filtering where broader device discovery is required.

## Report Format Lifecycle
`report_format_init()` selects `basic`, `json`, or `json_std`, creates the global `dm_report_group`, configures command-log reporting, and installs the log report handle. `json_std` enables strict numeric/bin reporting and temporarily forces `LC_NUMERIC` to `C` when needed so decimal output uses `.`. `report_format_destroy()` destroys the report group/log handle and restores locale state.

## Integration Notes
This file depends on `lib/report/report.h`, device-mapper report groups, command argument grouping, config defaults, selection reporting, and `toollib.c` object iterators. It also exports `report_get_single_selection()` for non-reporting command selection paths.

## Risks
Report type promotion is subtle: adding new fields or report types can silently change which iterator is used. Full-report subreports reject fields that promote to another report type. Locale handling for `json_std`, report-group push/pop balance, and selection recursion are correctness-sensitive.
