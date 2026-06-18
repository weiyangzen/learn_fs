# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/jaketown/metricgroups.json

## Purpose

This file maps metric group names to user-facing descriptions for the Jaketown PMU event/metric model. Unlike the event JSON files, it is an object rather than an array. It does not define counters or raw events; it gives perf descriptions for groups such as `Backend`, `MemoryBound`, `TopdownL1`, `tma_frontend_bound_group`, and issue-oriented groups like `tma_issueTLB`.

The data supports `perf list metricgroups`, metric browsing, and generated lookup helpers that explain metric groups. It is a metadata index for Intel Top-down Microarchitecture Analysis groupings and derived TMA categories.

## Important APIs, Types, And Data Contracts

`jevents.py` treats any file named `metricgroups.json` specially. Instead of parsing event records, it loads the JSON object, interns each key and description into the generated big C string table, and stores the pair in `_metricgroups`. `print_metricgroups()` later emits a sorted C array and a `describe_metricgroup(const char *group)` binary-search helper.

The keys are the public group identifiers. Descriptions are plain strings. There are no `EventName`, `MetricExpr`, `MetricGroup`, or event-encoding fields in this file. The generator asserts each group name has length greater than one, so empty or one-character names would fail generation.

The file includes both older/top-level names (`Backend`, `Frontend`, `Mem`, `Pipeline`, `HPC`, `Summary`) and newer generated TMA group names (`tma_L1_group` through `tma_L6_group`, category groups, and issue groups). Most legacy entries share the description "Grouping from Top-down Microarchitecture Analysis Metrics spreadsheet"; topdown levels and TMA categories have more specific text.

## Control Flow And Generation Behavior

During the `pmu-events` tree walk, `add_events_table_entries()` returns early for `metricgroups.json`. The file's object entries are collected globally instead of becoming event table rows. At output time, the generated `metricgroups` C array is sorted by group name and searched by `describe_metricgroup()`.

Runtime consumers do not parse this JSON directly. They call generated PMU event APIs through perf's metric and list code. `builtin-list.c` uses metric group information when rendering grouped metric output, and metric parsing/stat code uses generated metric metadata when resolving requested groups.

## State And Persistence

This file has no mutable state. The persistent state is the checked-in JSON mapping and its generated C representation. Because descriptions are compiled into a string table, changes require regenerating/rebuilding perf PMU events before users see them.

The mapping is global within the generated output; duplicate names would overwrite in the Python `_metricgroups` dictionary before printing. In this file all keys are unique.

## Dependencies And Integration Points

Dependencies include `jevents.py`, generated `pmu-events.c`, perf's metric group lookup routines, `perf list --details`, and metric group filtering in `builtin-list.c`. The names should align with `MetricGroup` values emitted by architecture-specific metric generators such as `intel_metrics.py`; stale names here can leave metrics with less helpful descriptions or unreachable documentation.

The file integrates conceptually with the sibling event files by giving names to analysis buckets that use events from `pipeline.json`, `memory.json`, and uncore files. It is not Jaketown hardware programming data by itself.

## Risks And Edge Cases

The main risk is drift between metric definitions and group descriptions. A group can be listed here even if no current metric references it, and a metric can reference a group missing here, which leaves the group less discoverable.

Case and punctuation are significant. `MachineClears` and `Machine_Clears` both appear, as do `TopdownL1` and `tma_L1_group` naming styles. Normalizing names casually would break lookup compatibility.

Since this file is object-shaped while sibling PMU event files are array-shaped, generic tooling must special-case it the same way the perf generator does. Treating it as an event array would produce invalid research, invalid schema validation, or broken generated tables.

## Test Signals

Validation should include `jq type metricgroups.json` returning `object`, generator rebuild coverage for `describe_metricgroup()`, and `perf list metricgroups` output showing representative entries. Tests should query both legacy and TMA names, for example `TopdownL1`, `MemoryBound`, `tma_backend_bound_group`, and `tma_issueTLB`.

Schema tests should ensure every key and value is a non-empty string and should cross-check metric `MetricGroup` names against this file when generated Jaketown metrics are present.
