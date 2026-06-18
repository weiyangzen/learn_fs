# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswell/metricgroups.json

## Purpose

This file maps 124 Haswell metric-group names to user-facing descriptions. It provides the descriptive catalog used by perf for top-down groups, spreadsheet-derived categories, issue-oriented subgroups, memory and frontend/backend groupings, power/system groups, and legacy aliases.

## Important APIs, Types, And Data

Unlike the event arrays, this file is a JSON object. Keys are metric group names and values are descriptions. `jevents.py` detects files ending in `metricgroups.json`, records each key/value in `_metricgroups`, and emits a generated lookup table for metric-group descriptions.

The keys include broad groups such as `Backend`, `Frontend`, `Mem`, `Pipeline`, `Power`, `Summary`, `SMT`, `SoC`, `Branches`, `CacheHits`, and `CacheMisses`; top-down levels `TopdownL1` through `TopdownL6` and `tma_L1_group` through `tma_L6_group`; and contribution groups like `tma_backend_bound_group`, `tma_frontend_bound_group`, `tma_memory_bound_group`, `tma_ports_utilization_group`, `tma_dtlb_load_group`, and `tma_store_bound_group`. Most spreadsheet-derived groups share the description "Grouping from Top-down Microarchitecture Analysis Metrics spreadsheet."

## Control Flow

At build time, this file follows a separate control path from event and metric arrays. `jevents.py` loads the object, stores group descriptions, excludes the file from normal event parsing, and later emits a sorted `metricgroups` lookup table into generated C. At runtime, perf uses the generated lookup to describe metric groups in list and metric-discovery paths.

## State And Persistence Behavior

The file persists display metadata only. It does not affect counter programming or metric expression evaluation directly. The generated lookup is static until perf is rebuilt.

## Dependencies And Integration Points

This file integrates with `hsw-metrics.json`, perf's metric listing UI, generated `pmu-events.c`, and any tooling that displays group descriptions. It depends on group names matching the semicolon-separated `MetricGroup` tokens used by metrics; a group description with no matching metric is harmless but stale, while a metric group with no description produces weaker help output.

## Risks And Edge Cases

Because the schema is object-shaped rather than array-shaped, treating this file like a normal event file would break generation. Duplicate or near-duplicate group names such as `MachineClears` and `Machine_Clears`, `MemoryBW` and `Memory_BW`, or legacy `TopdownL*` and newer `tma_L*_group` are intentional compatibility surfaces but can confuse consumers that normalize names. Descriptions are generic for many groups, so they help navigation more than semantic interpretation.

## Test Signals

Run `jq empty`, x86 `jevents.py` generation, and `perf test pmu-events`. `perf list --metricgroups` or equivalent list paths should show descriptions for representative groups such as `TopdownL1`, `tma_backend_bound_group`, `Power`, `SoC`, and `MemoryBW`. A consistency check can compare `MetricGroup` tokens in `hsw-metrics.json` with keys in this file.
