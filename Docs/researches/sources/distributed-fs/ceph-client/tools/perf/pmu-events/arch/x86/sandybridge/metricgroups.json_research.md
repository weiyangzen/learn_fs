## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sandybridge/metricgroups.json

### Purpose
`metricgroups.json` maps 117 metric group names to descriptions for Sandy Bridge. It supplies human-readable grouping metadata for top-down microarchitecture analysis, HPC summaries, memory, branch, power, OS, SMT, SoC, and issue-category metrics.

### Important APIs, Types, And Data Fields
Unlike the event files, this file is a JSON object, not an array. Each property name is a metric group key and each value is a description string. Key families include:

- Broad categories such as `Backend`, `Frontend`, `BadSpec`, `Retire`, `MemoryBound`, `MemoryBW`, `MemoryLat`, `Pipeline`, `Power`, `Summary`, `SMT`, `SoC`, and `HPC`.
- Top-down levels `TopdownL1` through `TopdownL6` and aliases such as `tma_L1_group` through `tma_L6_group`.
- Drill-down groups such as `tma_backend_bound_group`, `tma_fetch_latency_group`, `tma_fp_arith_group`, `tma_memory_bound_group`, and `tma_ports_utilization_group`.
- Issue tags such as `tma_issueBW`, `tma_issueFB`, `tma_issueMC`, `tma_issueMS`, `tma_issueTLB`, and related issue labels.

There are no event selectors, functions, or formulas. The API is the group-name-to-description map used by perf's metric display.

### Control Flow And Data Flow
Perf associates `MetricGroup` strings from `snb-metrics.json` with descriptions in this map. When users request metric groups or browse metric lists, perf can display group names and descriptions. Group names in `snb-metrics.json` are semicolon-separated; every group key here must remain compatible with those references.

### State And Persistence
This is static taxonomy metadata. It persists group descriptions but no runtime state or generated counters.

### Dependencies And Integration Points
The file depends on group names used in `snb-metrics.json`. It also reflects Intel's top-down microarchitecture analysis taxonomy. Integration points include perf metric listing, metric group filtering, documentation generation, and any tests that require group descriptions to exist for referenced groups.

### Risks
Because the schema differs from event arrays, tools that assume `.[].EventName` will fail. A missing or renamed group can degrade `perf list --details` output or make metric grouping less discoverable. Descriptions are generic for many groups, so the practical consistency risk is key coverage rather than prose precision.

### Test Signals
Validate the file as a JSON object, compare its keys against all semicolon-separated `MetricGroup` references in `snb-metrics.json`, and run perf metric-list tests to ensure groups such as `TopdownL1`, `MemoryBound`, `Flops`, and `tma_backend_bound_group` are discoverable.
