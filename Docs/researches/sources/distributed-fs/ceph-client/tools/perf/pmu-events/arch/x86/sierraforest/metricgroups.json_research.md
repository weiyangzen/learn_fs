# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sierraforest/metricgroups.json

## Purpose

This JSON object maps Sierra Forest metric group names to human-readable group descriptions. It is not an event array. The groups organize perf metric expressions into topdown levels, FLOP, instruction-fetch, memory-execution, power, summary, load/store-bound, and category-specific topdown buckets.

## Important APIs, Types, and Data

The file is a single object whose keys are group names and whose values are descriptions. It contains 21 groups: `Flops`, `Ifetch`, `Load_Store_Miss`, `Mem_Exec`, `Power`, `Summary`, `TopdownL1`, `TopdownL2`, `TopdownL3`, `load_store_bound`, `tma_L1_group`, `tma_L2_group`, `tma_L3_group`, `tma_backend_bound_group`, `tma_bad_speculation_group`, `tma_core_bound_group`, `tma_frontend_bound_group`, `tma_ifetch_bandwidth_group`, `tma_ifetch_latency_group`, `tma_machine_clears_group`, and `tma_resource_bound_group`.

## Control Flow

Perf's metric handling reads these mappings to label and display metric groups. The file does not program hardware counters directly. Its effect appears when metric JSON files assign metrics to these group names and perf presents group descriptions through list or metric-selection interfaces.

## State and Persistence Behavior

The persistent state is the stable set of group labels and descriptions for Sierra Forest. Runtime state is only perf's in-memory grouping of available metrics. Renaming a key changes the grouping API for users and scripts even though no event encoding changes. Descriptions document the intended analysis category and should stay aligned with actual metric formulas in adjacent files.

## Dependencies and Integration Points

This file integrates with Sierra Forest metric expression files, `perf list --metrics`-style output, topdown metric UI grouping, and documentation generated from pmu-events. It depends on exact string matching between metric `MetricGroup` references and these keys. The legacy-looking `TopdownL*` names coexist with newer `tma_*` group names, so both naming styles may be referenced by metrics.

## Risks

Because the schema differs from normal event arrays, generic event validators can incorrectly fail it. Stale group names can orphan metrics or hide them from expected category listings. Similar groups such as `TopdownL1` and `tma_L1_group` can confuse scripts that assume one canonical topdown naming scheme. Description-only changes can still affect generated help and user-facing documentation.

## Test Signals

Validation should include JSON object parsing, key uniqueness, and cross-checks that every Sierra Forest metric group reference resolves to a key here or to a globally accepted group. Perf list tests should show grouped metrics under the expected names. Schema tests should treat this as a metric-group map, not as an event-object array.
