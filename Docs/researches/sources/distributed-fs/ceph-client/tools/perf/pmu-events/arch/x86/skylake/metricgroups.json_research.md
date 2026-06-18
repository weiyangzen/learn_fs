# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylake/metricgroups.json

## Purpose

`metricgroups.json` maps 137 Skylake metric group names to human-readable group descriptions. Unlike the event files, it is a JSON object rather than an array of event descriptors. It supplies taxonomy for perf metrics, especially top-down microarchitecture analysis groups and issue-oriented groupings.

The file includes broad groups such as `Backend`, `Frontend`, `Retire`, `MemoryBound`, `Flops`, `HPC`, `Power`, and `Summary`; top-down levels such as `TopdownL1` through `TopdownL6` and `tma_L1_group` through `tma_L6_group`; and detailed TMA categories such as `tma_backend_bound_group`, `tma_fetch_latency_group`, `tma_l1_bound_group`, `tma_ports_utilization_group`, and `tma_store_bound_group`.

## Important schema/API surface

The schema is a string-to-string map:

- Keys are metric group identifiers used by metric descriptors in adjacent architecture metric files.
- Values are descriptions shown by tools such as `perf list --metricgroups` or used by documentation/index generation.

Many values are repeated as `Grouping from Top-down Microarchitecture Analysis Metrics spreadsheet`, indicating imported taxonomy from Intel's TMA spreadsheet. Others give explicit descriptions, for example `TopdownL1` as metrics for top-down breakdown at level 1 and `tma_fp_arith_group` as metrics contributing to the `tma_fp_arith` category.

## Control flow and integration

Perf loads this file as metric taxonomy, not as event aliases. Metric descriptors elsewhere reference these group names through `MetricGroup` fields; this file gives those names display text and grouping semantics. A metric query can use these groups to list related metrics, filter output, or organize top-down analysis views.

Because the file is an object, generic event-list code must branch on schema shape. Treating it as an array of events would fail or emit meaningless aliases.

## State and persistence behavior

The file is static taxonomy. It has no runtime state. Persistence is limited to the JSON file and generated metric-group tables.

## Dependencies

The mapping depends on metric descriptors using exactly matching group names. It also depends on perf's metric parser recognizing `metricgroups.json` as a group-description object. Its content depends on Intel top-down microarchitecture analysis terminology and the local Skylake metric files that consume the group identifiers.

## Risks and maintenance notes

Name drift is the main risk. The file contains both legacy-style names (`TopdownL1`, `Frontend`, `MemoryBound`) and lower-case TMA names with `_group` suffixes (`tma_frontend_bound_group`, `tma_memory_bound_group`). If a metric descriptor references a group key not present here, tools may still compute the metric but lose organized display or documentation.

The repeated spreadsheet-derived description is useful as provenance but not very specific. More precise descriptions should be added carefully because existing tools or tests may compare exact strings. Case sensitivity matters for group lookup.

## Test signals

Validation should assert that the JSON root is an object with 137 keys, all values are strings, and expected top-down keys are present. Integration tests should cross-check metric descriptors' `MetricGroup` references against this map and verify `perf list` can show representative groups such as `TopdownL1`, `Frontend`, `MemoryBound`, and `tma_l1_bound_group`.
