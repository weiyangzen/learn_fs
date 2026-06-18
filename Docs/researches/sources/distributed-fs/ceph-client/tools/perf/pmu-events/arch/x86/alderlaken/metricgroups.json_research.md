<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlaken/metricgroups.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlaken/metricgroups.json

## Purpose
Documents the metric-group descriptions for the Intel `alderlaken` perf model. The file is not a counter table; it gives human-readable help for metric group names that appear in sibling `MetricGroup` fields and in `perf list metricgroups` output.

## APIs, Types, and Functions
This file is a JSON object rather than a JSON event array. `jevents.py` detects the `metricgroups.json` suffix, loads each key/value pair into `_metricgroups`, stores the strings in the generated big C string table, and emits them through `describe_metricgroup()`. It defines 21 groups: `Flops`, `Ifetch`, `Load_Store_Miss`, `Mem_Exec`, `Power`, `Summary`, `TopdownL1`, `TopdownL2`, `TopdownL3`, `load_store_bound`, `tma_L1_group`, `tma_L2_group`, plus 9 more.

## Control Flow
During the pmu-events build, directory walking sees this file before normal event insertion for the model. The generator does not create counters from it; it only records sorted group descriptions that runtime perf queries when listing or explaining metric groups.

## State and Persistence
The JSON object has no mutable runtime state. Its persistent state is the group-name-to-description mapping compiled into generated perf tables; changes are visible only after rebuilding perf's pmu-events output.

## Dependencies and Integration
Depends on sibling `alderlaken` metric files that name these groups, on `jevents.py` metric-group handling, and on `describe_metricgroup()` consumers in perf list/stat UI code. The group names must remain byte-for-byte stable with `MetricGroup`, `DefaultMetricgroupName`, and related fields.

## Risks
Risks are name drift and stale documentation: if a metric moves groups or a group is renamed without updating this object, `perf list metricgroups` and metric help become misleading while metrics still parse. Sorting and duplicate group names should also be watched because `describe_metricgroup()` uses generated lookup tables.

## Test Signals
Test by rebuilding generated pmu-events output, running the pmu-events unit tests that exercise `describe_metricgroup()`, and checking `perf list metricgroups` on an x86 build for representative groups such as `TopdownL1`, `Power`, and `tma_backend_bound_group`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlaken/metricgroups.json -->
