# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/rocketlake/metricgroups.json

## Purpose

`metricgroups.json` is Rocket Lake metric group description metadata for perf. It is not an event list. It maps 138 metric group names to human-readable descriptions, mostly derived from Intel top-down microarchitecture analysis grouping names and generated metric-group categories. Perf uses these descriptions to explain groups shown by metric listing and metric selection features.

## Important APIs, Types, and Data Fields

The file is a single JSON object, not an array. Keys are group names and values are descriptions. Examples include broad groups such as `Backend`, `Frontend`, `MemoryBound`, `Flops`, `Branches`, `Pipeline`, `TopdownL1` through `TopdownL6`, and generated category groups such as `tma_backend_bound_group`, `tma_fetch_latency_group`, `tma_memory_bound_group`, `tma_dtlb_load_group`, `tma_fp_arith_group`, and `tma_retiring_group`. There are also issue-link groups such as `tma_issueBW`, `tma_issueLat`, and `tma_issueTLB`. About 52 keys are topdown or `tma_*_group` style descriptions.

## Control Flow and Data Flow

`jevents.py` handles this file on a separate path from normal event JSON. When an item name ends with `metricgroups.json`, the generator loads it as a dictionary, adds each group name and description to the generated big C string table, stores offsets in `_metricgroups`, and emits a sorted `metricgroups` lookup table. The generated `describe_metricgroup(const char *group)` function performs binary search over that table and returns a description string for a group name.

At runtime, perf list and metric display code can use group names attached to metrics and call the generated description lookup to show what a group means. No hardware counter is programmed directly by this file.

## State and Persistence Behavior

The persistent state is the group-name-to-description mapping. There are no counters, event encodings, sample periods, or PMU units. Ordering in the source file is not semantically important because the generator sorts groups for binary search. The names are externally visible UI and metric-selection contracts; renaming a key can break user habits, tests, or generated metric references even if descriptions remain similar.

## Dependencies and Integration Points

This file depends on generated Intel metric names and perf's metricgroup infrastructure. It integrates with `jevents.py`, generated `pmu-events.c`, `util/metricgroup.c`, `builtin-list.c`, and Python list tooling that displays metrics by group. It complements Rocket Lake event files indirectly: event files provide raw aliases, metric definition files attach formulas to groups, and this file describes those groups for humans.

## Risks and Edge Cases

The schema differs from normal PMU event arrays; treating it as `.[].EventName` data will fail. Duplicate or misspelled group names can make descriptions unavailable for metrics that reference the intended group. Descriptions are mostly generic "Grouping from Top-down Microarchitecture Analysis Metrics spreadsheet" text, so they aid categorization but not detailed diagnosis. Binary-search lookup in generated code assumes the emitted table is sorted by group key. Because this is UI metadata, regressions may appear in `perf list metricgroups` rather than counter behavior.

## Test Signals

Validation should parse the file as a JSON object and confirm 138 key/value pairs. Generator tests should verify `jevents.py` routes it through the metricgroup path and does not try to parse event fields. Runtime tests should check `perf list metricgroups`, metric listing by groups such as `TopdownL1`, `MemoryBound`, and `tma_backend_bound_group`, and `describe_metricgroup` behavior for known and unknown group names. A schema test should reject conversion to event-array format.
