# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/ivybridge/metricgroups.json

## Purpose

`metricgroups.json` defines Ivy Bridge metric group descriptions. It maps group identifiers used by `ivb-metrics.json` to human-readable descriptions so perf can organize and explain metric collections such as topdown levels, backend/frontend categories, memory, power, FLOPs, and issue-specific diagnostic groups.

## Schema And API Surface

Unlike most PMU event JSON files, this file is a JSON object rather than an array. Keys are metric group names and values are description strings. It contains 124 group mappings. Examples include generic groups such as `Backend`, `Frontend`, `Mem`, `Power`, `Summary`, and `HPC`; topdown groups such as `TopdownL1` through `TopdownL6` and `tma_L1_group` through `tma_L6_group`; category groups such as `tma_backend_bound_group`, `tma_fetch_latency_group`, `tma_memory_bound_group`, and issue tags such as `tma_issueBW`, `tma_issueFB`, `tma_issueTLB`, and `tma_issueSyncxn`.

## Control Flow And Integration

`jevents.py` reads metric group descriptions while generating perf's metric tables. At runtime, `perf list metricgroups` and metric display paths use the mapping to present grouped metrics and descriptions. `ivb-metrics.json` references these keys through semicolon-delimited `MetricGroup` fields; this file provides the display metadata for those references.

## State And Persistence

The file persists display taxonomy only. It does not define events, formulas, thresholds, or counter state. The group names are stable identifiers shared with metric entries, and the values are descriptive labels shown to users.

## Dependencies

The primary dependency is `ivb-metrics.json`: every meaningful group here should correspond to metrics using that group, and groups used by metrics should ideally have descriptions here. The file also depends on perf tooling accepting object-shaped metric group JSON, which differs from array-shaped event and metric files.

## Risks

Generic JSON analysis tools can fail if they assume a list of event objects; this file must be handled as a mapping. Misspelled group keys reduce discoverability but may not fail builds. Stale descriptions can make topdown groups misleading, especially for issue tags and generated TMA categories. Removing a group description does not remove metrics, so regressions may surface only in `perf list` UX.

## Test Signals

Use `jq type` to confirm the top-level object shape. Run `jevents.py` generation and `perf list metricgroups` to confirm group descriptions are emitted. Cross-check all semicolon-delimited groups in `ivb-metrics.json` against this map to find missing or unused descriptions.
