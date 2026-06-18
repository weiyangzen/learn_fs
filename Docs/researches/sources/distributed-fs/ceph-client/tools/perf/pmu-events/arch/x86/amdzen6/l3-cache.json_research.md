# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen6/l3-cache.json

Purpose: Defines 17 Zen 6 L3 PMU events for coherent L3 lookup state and sampled latency/request source attribution.

Important APIs/types/functions: Objects use `EventName`, `EventCode`, `UMask`, `Unit: L3PMC`, `SliceId`, `ThreadMask`, `EnAllSlices`, `EnAllCores`, and `BriefDescription`. Families are `l3_lookup_state.*`, `l3_xi_sampled_latency.*`, and `l3_xi_sampled_latency_requests.*`.

Control flow: Perf maps these aliases to the L3 PMU with all-core/all-slice settings. Recommended metrics can use lookup counters for L3 accesses/misses and latency/request pairs for average read miss latency by source.

State and persistence: No JSON-mutated state. The persistent behavior is the all-slice L3 event configuration and source-specific latency taxonomy.

Dependencies and integration: Integrates with Zen 6 recommended L3 metrics, L2 fill-source events, and memory locality analysis. The structure mirrors Zen 5 but remains a separate model-specific table.

Risks: Sampled latency requires matching request counts and safe handling of zero requests. L3 uncore aggregation can vary with CCD/slice topology. Source masks for extension memory and near/far cache should be checked against hardware documentation.

Test signals: Validate `perf list l3_`, exercise LLC hit/miss workloads, verify all-slice counting, and run latency metrics for local and remote DRAM scenarios.
