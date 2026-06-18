# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellde/bdwde-metrics.json

## Purpose
Broadwell-DE derived metric catalog for Linux perf PMU events. The file defines 145 formula-based metrics for power residency, SMI visibility, uncore frequency, top-down microarchitecture analysis, instruction mix, memory behavior, frontend behavior, floating-point throughput, system utilization, and pipeline efficiency. It turns the raw events from sibling Broadwell-DE JSON files into named `perf stat -M` metrics such as `tma_backend_bound`, `tma_memory_bound`, `tma_frontend_bound`, `tma_retiring`, `tma_info_thread_ipc`, `tma_info_system_dram_bw_use`, and C-state residency metrics.

## Important APIs, Types, and Functions
There are no executable functions. The stable interface is the perf PMU metric schema: `MetricName`, `MetricExpr`, `MetricGroup`, and `BriefDescription` appear on every entry. Optional fields are meaningful API surface too: `MetricThreshold` appears on 91 entries, `PublicDescription` and `ScaleUnit` on 78 entries, `MetricConstraint` on 16 entries, and `MetricgroupNoGroup` on 12 top-down rollup entries. Expressions reference event names from sibling files, fixed events like `cycles` and `instructions`, MSR pseudo-events such as `msr@tsc@`, cstate pseudo-events, perf duration variables, topology variables like `#num_dies`, and helper variables such as `#SMT_on`.

## Control Flow
At perf build time this JSON is parsed into generated PMU event tables. At runtime perf resolves a requested metric name or metric group, expands `MetricExpr`, schedules the referenced counters, evaluates conditional expressions, and presents scaled output. The top-down hierarchy is encoded as data dependencies: level 1 metrics derive from slots and speculation counters; level 2 and lower metrics reuse parent metrics such as `tma_backend_bound`, `tma_memory_bound`, `tma_fetch_latency`, and `tma_core_bound`.

## State and Persistence
The file is immutable source data. Runtime state is created by perf when expressions are expanded, counters are scheduled, multiplexed, and sampled. Persistence concerns are schema stability and expression validity: metric names, group names, formulas, constraints, and thresholds must remain compatible with perf's metric parser and with the event aliases provided by the Broadwell-DE event files.

## Dependencies and Integration
This file depends on sibling event catalogs for cache, memory, frontend, floating-point, pipeline, other, uncore, C-state, and MSR aliases. The formulas integrate with `metricgroups.json` through group names such as `TopdownL1`, `TopdownL2`, `Backend`, `Frontend`, `MemoryBound`, `Flops`, `Power`, `SoC`, and many `tma_*_group` groupings. The 16 constrained metrics include `NO_GROUP_EVENTS` or `NO_GROUP_EVENTS_SMT` restrictions for ratios that cannot safely share counter groups or SMT contexts.

## Risks
The main risks are stale formulas for Broadwell-DE hardware behavior, event alias drift against sibling JSON files, division by zero in formulas with sparse workloads, top-down percentages that do not sum as users expect under multiplexing, and constraints that are too weak or too strong for available counters. Metrics referencing MSRs, C-states, or topology variables may fail or report partial data when kernel support, permissions, or topology discovery is missing.

## Test Signals
Useful signals are successful `jq empty` validation, perf PMU table generation without parser warnings, `perf list` showing all 145 metric names and expected groups, `perf stat -M` runs for `TopdownL1`, `MemoryBound`, `Frontend`, `Flops`, `Power`, and `SoC`, and targeted checks that constrained metrics avoid invalid counter grouping. Formula smoke tests should include SMT enabled and disabled cases, workloads with low event counts, and systems where MSR or C-state events are unavailable.
