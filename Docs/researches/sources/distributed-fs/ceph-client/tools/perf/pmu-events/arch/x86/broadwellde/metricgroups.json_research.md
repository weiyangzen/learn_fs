# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellde/metricgroups.json

## Purpose
Metric group description map for Broadwell-DE perf metrics. It gives human-readable descriptions for 124 group keys used by `bdwde-metrics.json`, including top-down hierarchy groups, issue-oriented groups, category groups, and spreadsheet-derived group names.

## Important APIs, Types, and Functions
Unlike the event files, this file is a JSON object rather than an array. Each key is a metric group name and each value is its description. Important keys include `TopdownL1` through `TopdownL6`, `tma_L1_group` through `tma_L6_group`, category groups such as `Backend`, `Frontend`, `MemoryBound`, `Flops`, `Power`, `SoC`, and contributor groups such as `tma_backend_bound_group`, `tma_fetch_latency_group`, `tma_memory_bound_group`, `tma_ports_utilization_group`, and `tma_store_bound_group`.

## Control Flow
Perf loads this map as metadata for presentation and discovery. Metric definitions assign semicolon-separated `MetricGroup` values; this file lets perf display those groups with descriptions and helps users discover related metrics through group names. It does not schedule counters or evaluate expressions directly.

## State and Persistence
The file is static descriptive state. The persistence contract is name alignment: every group key that metrics reference should either be present here or intentionally omitted, and descriptions should remain accurate for the model-specific Broadwell-DE metric set.

## Dependencies and Integration
The file depends on `bdwde-metrics.json` for actual usage. It bridges top-down metric names to user-facing `perf list` and `perf stat -M <group>` discovery. It also preserves compatibility with group names from Intel's top-down microarchitecture analysis spreadsheet and perf's lowercase `tma_*` naming convention.

## Risks
Risks are mostly documentation and discoverability issues: stale group descriptions, unused group keys, missing keys for metrics, or inconsistent spelling such as `MachineClears` versus `Machine_Clears` can make metric discovery confusing. Because it is an object, array-oriented validation scripts can incorrectly reject it unless they handle this file's schema separately.

## Test Signals
Run `jq empty`, verify object shape with `jq type`, compare all `MetricGroup` tokens from `bdwde-metrics.json` against this map, and check `perf list` output for useful group descriptions. Group smoke tests should include `TopdownL1`, `TopdownL2`, `Frontend`, `Backend`, `MemoryBound`, `Flops`, and a few `tma_*_group` names.
