# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/tigerlake/metricgroups.json

## Purpose
`metricgroups.json` defines the named metric-group taxonomy for Tiger Lake. Unlike event files, it is a JSON object with 138 key/value pairs mapping group names to descriptions. The groups classify metrics for topdown analysis, frontend/backend breakdowns, cache and memory analysis, branch behavior, floating point, power, SMT, server/client concerns, and issue-oriented TMA categories.

## Important APIs, Types, and Fields
The API is an object map rather than an array of event records. Keys are metric group identifiers such as `Backend`, `Frontend`, `CacheMisses`, `MemoryBW`, `TopdownL1`, `tma_backend_bound_group`, and `tma_issueTLB`. Values are human-readable descriptions, commonly "Grouping from Top-down Microarchitecture Analysis Metrics spreadsheet" or "Metrics contributing to ..." a TMA category. The schema has no `EventName`, `EventCode`, or `UMask`.

## Control Flow and Data Flow
Build-time perf tooling reads the object and attaches descriptions to metric groups used by Tiger Lake metric definitions elsewhere. Runtime users encounter these strings through `perf list --metricgroups`, `perf stat -M`, or metric browsing. The data flow is from group key to display/filter taxonomy; it does not program hardware counters directly.

## State and Persistence Behavior
The file is static taxonomy metadata. It holds no runtime state and does not persist measurements. Changes affect user-facing grouping and discoverability of metrics, not raw event encodings.

## Dependencies and Integration Points
The file depends on perf's metric group parser accepting object maps. It must stay in sync with Tiger Lake metric definitions that reference these group names. It integrates with all Tiger Lake event files indirectly by organizing derived metrics over frontend, backend, memory, branch, cache, FP, and topdown event formulas.

## Risks and Edge Cases
Tools that assume every JSON file in the architecture directory is an array of event records will fail on this object-shaped file. Renaming a group breaks references from metric definitions and user workflows using `perf stat -M` group filters. The coexistence of legacy-style names (`TopdownL1`) and lower-case TMA group names (`tma_L1_group`) requires preserving exact spelling. Duplicate or near-duplicate categories can confuse users but may be intentional for compatibility.

## Test Signals
Run `jq type` and verify it is `object`, then run perf's PMU/metric generation. `perf list --metricgroups` on a build with Tiger Lake metrics should show representative groups including `Frontend`, `Backend`, `MemoryBound`, `TopdownL1`, and `tma_backend_bound_group`. A reference-integrity check should ensure every group named by metric definitions exists in this map.
