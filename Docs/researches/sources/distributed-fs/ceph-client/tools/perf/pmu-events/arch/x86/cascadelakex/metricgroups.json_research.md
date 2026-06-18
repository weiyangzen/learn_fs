# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/cascadelakex/metricgroups.json

## Purpose

`sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/cascadelakex/metricgroups.json` is the Cascade Lake X metric-group description catalog for Linux perf's generated PMU metadata. It maps metric group names to short user-facing descriptions used by `perf list metricgroups`, metric browsing, and top-down microarchitecture analysis presentation. The source was read as a complete 140-line JSON object with 138 entries.

## Important APIs, Types, and Data Fields

This file is data, not executable code. Its public contract is a JSON object whose keys are metric-group names and whose values are descriptions. Important keys include high-level groups such as `Backend`, `Frontend`, `BadSpec`, `MemoryBound`, `Pipeline`, `Retire`, `Summary`, `Power`, `Snoop`, and `Server`; top-down level names `TopdownL1` through `TopdownL6`; legacy/generated aliases `tma_L1_group` through `tma_L6_group`; category groups such as `tma_backend_bound_group`, `tma_frontend_bound_group`, `tma_memory_bound_group`, `tma_bad_speculation_group`, and `tma_retiring_group`; and issue labels such as `tma_issueTLB`, `tma_issueRFO`, `tma_issueFB`, and `tma_issueSyncxn`.

Most values use the shared description "Grouping from Top-down Microarchitecture Analysis Metrics spreadsheet"; the top-down levels and `tma_*_group` keys have more specific generated descriptions. The schema is intentionally minimal: there are no event encodings, no metric formulas, and no membership arrays in this file.

## Control Flow and Data Flow

There is no runtime control flow in the JSON. During the perf build, `tools/perf/pmu-events/jevents.py` recognizes files ending in `metricgroups.json`, loads the object, places group names and descriptions into the generated big string table, and emits a sorted `metricgroups` lookup table plus `describe_metricgroup(const char *group)`. Runtime consumers then call through perf's metric-group code to retrieve the description for a group name referenced by metric metadata.

The data flow is therefore: static JSON object -> `jevents.py` generated `pmu-events.c` string offsets -> `describe_metricgroup()` -> `perf list`/metric display. This file does not decide which events belong to a group; metric JSON or generated Intel metric code references these group names through `MetricGroup`.

## State and Persistence Behavior

The file persists static labels and descriptions only. It owns no runtime counters, sampled values, or metric membership state. Once built, its contents are embedded into perf's generated PMU event library and persist as compiled lookup metadata until perf is rebuilt.

## Dependencies and Integration Points

The main dependency is name consistency with Cascade Lake X metrics, especially `clx-metrics.json` and generated Intel top-down metric definitions. The directory is selected for CPUIDs matching `GenuineIntel-6-55-[56789ABCDEF]` in `tools/perf/pmu-events/arch/x86/mapfile.csv`, while lower 6-55 steppings map to `skylakex`; that selection controls when these group descriptions are paired with Cascade Lake X metric tables.

Integration points include `tools/perf/pmu-events/jevents.py` for build-time conversion, `tools/perf/pmu-events/pmu-events.h` for `describe_metricgroup()`, `tools/perf/util/metricgroup.c` for metric-group lookup and expansion, `tools/perf/builtin-list.c` for listing groups and descriptions, and `tools/perf/tests/shell/stat_all_metricgroups.sh` for exercising all listed groups through `perf stat -M`.

## Risks and Edge Cases

The group names are free-form strings, so typos create orphan descriptions or leave referenced metric groups undescribed. Some conceptual aliases coexist, for example `TopdownL1` and `tma_L1_group`, and removing either form can break scripts or metric definitions that still use the older spelling. Description text is not validated against metric membership, so stale descriptions can survive if metrics move groups. Because this file is architecture/model-specific, accidentally sharing it with the wrong CPUID model can expose Cascade Lake X top-down group names on a CPU whose metric formulas or event support differ.

## Test Signals

Useful checks are `jq type`/object parse success, perf build success with generated `pmu-events.c`, `perf list --raw-dump metricgroups` showing representative entries such as `TopdownL1`, `Pipeline`, and `tma_memory_bound_group`, and `perf list metricgroups` returning descriptions rather than blank entries. Consistency tests should compare metric-group names referenced by Cascade Lake X metrics against keys in this file and flag missing or unused descriptions. The shell test `tools/perf/tests/shell/stat_all_metricgroups.sh` is a runtime signal that listed groups can be expanded by `perf stat -M` on the selected system.
