<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/graniterapids/metricgroups.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/graniterapids/metricgroups.json

## Purpose
Granite Rapids metric-group description map for perf. The file defines 143 group-name keys used by `gnr-metrics.json` and maps each to a human-readable description for grouped metric discovery, selection, and display.

## APIs, Types, and Functions
The effective API is a JSON object whose keys are metric group names and whose values are descriptions. It has no local functions or concrete C types. Keys include broad domains such as `Backend`, `Bad`, `Branches`, `Compute`, `Frontend`, `HPC`, `Mem`, `MemoryBW`, `MemoryLat`, `MemoryTLB`, `Offcore`, `Pipeline`, `Power`, `Server`, `SoC`, `Summary`, and `TopdownL1` through `TopdownL6`; bottleneck-view groups such as `BvBC`, `BvBO`, `BvCB`, `BvFB`, `BvIO`, `BvMB`, `BvML`, `BvMP`, `BvMS`, `BvMT`, `BvOB`, and `BvUW`; TMA rollup groups such as `tma_L1_group` through `tma_L6_group`; category contributor groups such as `tma_memory_bound_group`, `tma_fetch_latency_group`, and `tma_ports_utilization_group`; and issue tags such as `tma_issueBW`, `tma_issueLat`, `tma_issueTLB`, `tma_issueFB`, and `tma_issueSyncxn`.

## Control Flow, State, and Persistence
Perf loads this map alongside metric definitions. When metrics declare semicolon-separated `MetricGroup` values, the group names are resolved against this file to provide descriptions and to support user selection of whole groups. There is no runtime mutation in the JSON; state lives in perf's in-memory metric-group registry after parsing.

The control relationship is one level removed from counters: selecting a group causes perf to select all metrics in `gnr-metrics.json` tagged with that group, which in turn expands into the metric dependency graph and raw event schedule. The group map therefore affects discoverability and command-line ergonomics, not the raw hardware encodings.

## Dependencies and Integration
This file depends on the group tags used in `gnr-metrics.json`. The observed metric catalog heavily uses `TopdownL4`, `tma_L4_group`, `Mem`, `TopdownL3`, `tma_L3_group`, `Offcore`, `MemoryTLB`, `MemoryBW`, `Fed`, `Server`, `TopdownL5`, and pipeline/front-end/back-end tags, so stale or missing descriptions for those names would degrade `perf list --metricgroups` output. The naming convention also integrates with Intel's Top-down Microarchitecture Analysis spreadsheet terminology, which is referenced by most broad group descriptions.

## Risks
The primary risk is drift: if a metric adds a new `MetricGroup` tag that is absent here, grouped discovery becomes inconsistent. Conversely, unused keys are harmless but can mislead users if they appear as supported groups with no metrics. Case and punctuation matter (`MachineClears` and `Machine_Clears`, `MemoryBW` and `Memory_BW`, `MemoryLat` and `Memory_Lat` are distinct), so accidental normalization by tools would break lookups. Generic descriptions for many groups are adequate for machine readability but not very explanatory for users trying to choose between similar bottleneck-view or issue groups.

## Test Signals
Useful tests are JSON parse success, checking every semicolon-separated `MetricGroup` tag in `gnr-metrics.json` has a key here, checking every key here is either used or intentionally retained for compatibility, and verifying `perf list --metricgroups` shows descriptions for top-down levels, issue groups, memory groups, front-end groups, and SoC/power groups. Runtime selection tests should include `perf stat -M TopdownL1`, `-M tma_L3_group`, `-M MemoryBW`, `-M Frontend`, `-M Offcore`, `-M Power`, and at least one `tma_issue*` group to ensure group names expand into metrics rather than only displaying descriptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/graniterapids/metricgroups.json -->
