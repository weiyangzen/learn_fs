# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelakex/metricgroups.json

## Purpose

This file defines 139 metric-group descriptions for Ice Lake Xeon perf metrics. It is a lookup table from group name to human-readable description, used to make `perf list metricgroups` and grouped metric output understandable. The groups mirror the group tags used by `icx-metrics.json`, especially Intel top-down microarchitecture analysis groups and issue-oriented bottleneck categories.

The file covers broad categories such as `Backend`, `Frontend`, `Bad`, `Mem`, `Offcore`, `Pipeline`, `Power`, `Server`, `SoC`, `Summary`, and `HPC`; top-down levels `TopdownL1` through `TopdownL6` and `tma_L1_group` through `tma_L6_group`; and many specific top-down contributor groups such as `tma_memory_bound_group`, `tma_fetch_latency_group`, `tma_ports_utilization_group`, `tma_dtlb_load_group`, `tma_store_stlb_miss_group`, and `tma_issue*` groups.

## Important APIs, Types, And Data

Unlike event and metric files, this JSON is an object rather than an array. Keys are metric group names and values are descriptions. Most values are either "Grouping from Top-down Microarchitecture Analysis Metrics spreadsheet", "Metrics for top-down breakdown at level N", "Metrics contributing to <category> category", or "Metrics related by the issue $<issue>".

The effective API is the `_metricgroups` dictionary built by `jevents.py`. The loader treats files ending in `metricgroups.json` specially, reading each key/value pair into a generated string table. Metric and event records are not created from this file; it provides descriptive metadata consumed by perf list and metric group UI paths.

## Control Flow

At build time, `jevents.py` detects `metricgroups.json`, parses the object, and stores each group description in a process-global metric-group map. Later it emits a generated `metricgroups` lookup table and `describe_metricgroup(...)` helper that binary-searches sorted group names in the generated C string table.

At runtime, `perf list metricgroups` and metric-list paths use the generated descriptions when displaying groups. When a metric in `icx-metrics.json` references a group through its `MetricGroup` field, this file gives that group a label. It does not decide group membership; membership remains in each metric record.

## State And Persistence Behavior

The file persists static group-description metadata only. It stores no counter state and no generated state. At build time, its contents are folded into generated C tables. At runtime, the generated table is read-only.

Because keys are stable user-facing names, edits are persistent compatibility changes. Removing or renaming a group description does not remove the metrics themselves, but it can make group discovery less useful and can affect scripts that inspect `perf list --raw-dump metricgroups`.

## Dependencies And Integration Points

The primary dependency is consistency with `MetricGroup` values in `icx-metrics.json`. The file also integrates with `jevents.py`, generated `pmu-events.c`, `builtin-list.c`, `python/ilist.py`, `Documentation/perf-list.txt`, `Documentation/perf-stat.txt`, and tests that iterate all metric groups, including `tests/shell/stat_all_metricgroups.sh`.

The group names reflect Intel's top-down spreadsheet taxonomy, so they depend on the naming conventions used by Intel metric generation scripts and manually maintained perf metrics. The descriptions are model-local in the `icelakex` directory but include generic top-down category names used across Intel server generations.

## Risks And Edge Cases

Schema shape is a risk: this file must remain a JSON object, not an array. Duplicate keys cannot be represented reliably in JSON and would be collapsed by parsers. A typo in a key creates a description for a group that no metric uses, while a typo in `icx-metrics.json` can leave a real group without a description.

There are intentionally similar names, including `MachineClears` and `Machine_Clears`, `MemoryBW` and `Memory_BW`, `MemoryLat` and `Memory_Lat`, plus `TopdownL*`, `TmaL*`, and `tma_L*_group`. Simplifying or deduplicating those names could break existing group references. The many `tma_issue*` keys contain issue tags such as `$issueBW` and `$issueSyncxn`; these are descriptions, not expression variables.

## Test Signals

Use `jq type` to confirm the file is an object and run x86 `jevents.py` generation to confirm metric-group table emission. Runtime checks include `perf list metricgroups`, `perf list --raw-dump metricgroups`, and `perf stat -M` for representative groups such as `TopdownL1`, `TopdownL4`, `MemoryBW`, `Offcore`, `tma_memory_bound_group`, and `tma_issueBW`.

Cross-file validation should compare the set of `MetricGroup` tokens in `icx-metrics.json` against keys in this file and flag missing or unused descriptions. Tests should preserve case-sensitive distinct group names.
