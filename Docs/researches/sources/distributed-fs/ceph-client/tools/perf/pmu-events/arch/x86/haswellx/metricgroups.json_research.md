<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswellx/metricgroups.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswellx/metricgroups.json

## Purpose

`metricgroups.json` maps 124 metric group names to user-facing descriptions for the Haswell-X PMU metrics. It documents the grouping vocabulary referenced from `hsx-metrics.json` and shown by perf metric listing and selection interfaces.

Unlike the event files, this JSON is an object, not an array. Each property name is a group identifier and each value is a description string. The effective API is the perf metric group description schema.

## Important group families

The file contains legacy and broad analysis groups such as `Summary`, `Power`, `Pipeline`, `Frontend`, `Backend`, `BadSpec`, `MemoryBound`, `MemoryBW`, `MemoryLat`, `MemoryTLB`, `Offcore`, `CacheHits`, `CacheMisses`, `Branches`, `PortsUtil`, `SMT`, `OS`, `Server`, `SoC`, `HPC`, and `PGO`.

It also defines top-down hierarchy groups: `TopdownL1` through `TopdownL6` and corresponding `tma_L1_group` through `tma_L6_group`. Category-specific TMA groups include examples such as `tma_backend_bound_group`, `tma_frontend_bound_group`, `tma_fetch_latency_group`, `tma_memory_bound_group`, `tma_mem_latency_group`, `tma_ports_utilization_group`, `tma_retiring_group`, `tma_store_bound_group`, and `tma_store_op_utilization_group`.

Issue-oriented TMA groups such as `tma_issueBW`, `tma_issueFB`, `tma_issueL1`, `tma_issueLat`, `tma_issueMC`, `tma_issueMS`, `tma_issueRFO`, `tma_issueSyncxn`, and `tma_issueTLB` let related diagnosis metrics be surfaced together.

## Control flow and lookup model

There is no imperative control flow. Perf loads or compiles this mapping and uses it when displaying group descriptions or resolving metric group names. The control path is a lookup from a metric's `MetricGroup` token to a description string.

Most values say they come from the Top-down Microarchitecture Analysis Metrics spreadsheet. A smaller set gives specific descriptions for top-down levels and TMA category/issue groups. The distinction matters for user documentation, not counter programming.

## State and persistence behavior

The file persists only static group metadata. It does not affect measured counter state directly. It affects user-facing discovery and organization of metrics, which can influence which metric expressions perf schedules together.

## Dependencies and integration points

The main dependency is cross-file consistency with `hsx-metrics.json`: every group token referenced by metric records should either have a description here or be intentionally handled as a built-in/implicit group. This file does not depend on `memory.json`, `other.json`, or `pipeline.json` directly, but those event files provide the raw counters behind metrics assigned to these groups.

Perf tooling must parse this file as an object; treating it like the array-shaped event files is an error. That shape difference is a useful test signal for parsers.

## Risks and maintenance notes

Stale or missing group descriptions do not usually break counter collection, but they degrade `perf list`/metric discovery and can confuse users selecting metric groups. Naming drift is the main risk: if `hsx-metrics.json` adds or renames a `MetricGroup` token without updating this file, group documentation becomes incomplete.

Group names use multiple naming conventions, including legacy CamelCase, underscore variants such as `Memory_BW`, and TMA names with `_group` suffixes. Normalizing names without preserving compatibility could break user workflows and metric selection.

## Test signals

Tests should confirm valid JSON object shape, uniqueness of keys, non-empty string descriptions, and cross-reference coverage from `hsx-metrics.json` `MetricGroup` tokens. Perf-level validation should include `perf list metricgroups` or equivalent listing behavior and selection of representative groups such as `TopdownL1`, `MemoryBW`, `tma_L3_group`, and `tma_issueBW`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswellx/metricgroups.json -->
