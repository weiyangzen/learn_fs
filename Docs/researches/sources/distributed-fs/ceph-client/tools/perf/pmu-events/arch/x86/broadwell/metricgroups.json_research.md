# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwell/metricgroups.json

## Purpose

`metricgroups.json` maps Broadwell metric-group names to user-facing descriptions. It is an object, not an event array, and supplies grouping metadata for `perf list metricgroups`, metric browsing, and top-down microarchitecture analysis organization. Most entries state that the group comes from the Top-down Microarchitecture Analysis Metrics spreadsheet, while top-down levels and generated `tma_*` categories have specific descriptions.

## Important APIs, Types, and Data Fields

The file's public contract is a JSON object where each key is a metric group name and each value is a short description. Important groups include high-level categories such as `Backend`, `Frontend`, `BadSpec`, `MemoryBound`, `Pipeline`, `Retire`, `Summary`, `TopdownL1` through `TopdownL6`, legacy aliases such as `tma_L1_group` through `tma_L6_group`, and many issue/category groups such as `tma_memory_bound_group`, `tma_fetch_latency_group`, `tma_dtlb_load_group`, `tma_issueTLB`, and `tma_ports_utilization_group`.

## Control Flow and Data Flow

There is no control flow inside the file. The perf PMU event generation path loads the object and turns it into metric-group description tables. Runtime consumers use those descriptions when listing or presenting metric groups, and metrics from other JSON files or generated Intel metric code reference these group names through `MetricGroup` fields.

## State and Persistence Behavior

The file persists group labels and descriptions only. It does not own the membership list for each group and does not store runtime metric values. Generated perf artifacts persist a compiled representation of these descriptions.

## Dependencies and Integration Points

The entries depend on the broader Broadwell metric catalog using matching group names. They integrate with `tools/perf/pmu-events/metric.py` helpers that generate group descriptions, `perf list --raw-dump metricgroups`, perf's Python listing helper, and `tools/perf/util/metricgroup.c` for metric group lookup and display.

## Risks and Edge Cases

Because this file is keyed by free-form strings, typos create orphan descriptions or leave referenced metric groups undescribed. Duplicate conceptual groups exist in legacy and generated forms, such as `TopdownL1` and `tma_L1_group`; removing aliases may regress scripts that depend on older names. Description text is not validated against metric membership, so stale descriptions can survive after metrics move groups.

## Test Signals

Validation should include JSON object parsing, generated `pmu-events.c` build success, and `perf list --raw-dump metricgroups` showing representative high-level and `tma_*` group names. A useful consistency check is comparing group names referenced by Broadwell metrics against keys in this file and flagging unreferenced or missing descriptions.
