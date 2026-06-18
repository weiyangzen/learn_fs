# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen5/recommended.json

Purpose: Defines 63 recommended Zen 5 perf metrics spanning branch prediction, L1/L2/L3 cache behavior, op-cache and instruction-cache ratios, TLBs, macro-op dispatch/retire, SSE/AVX stalls, UMC memory-controller rates/bandwidth, and Data Fabric bandwidth.

Important APIs/types/functions: This file uses `MetricName`, `MetricExpr`, `MetricGroup`, `ScaleUnit`, `BriefDescription`, and sometimes `PerPkg`. Expressions reference events from many sibling JSON files plus perf built-ins such as `instructions` and `duration_time`, with `d_ratio(...)` used for ratio safety.

Control flow: Perf evaluates these metrics as user-facing recommended summaries. The file ties raw events together: branch misprediction from `ex_ret_brn_misp/ex_ret_brn`, L2 metrics from request/status/prefetch events, L3 latency from sampled latency divided by requests, TLB metrics from branch/load-store TLB events, UMC bandwidth from CAS commands, and fabric bandwidth from Data Fabric beat counters.

State and persistence: No runtime state. The persistent contract is cross-file metric dependency wiring and metric group names such as `branch_prediction`, `l1_dcache`, `l2_cache`, `l3_cache`, `tlb`, `decoder`, `memory_controller`, and `data_fabric`.

Dependencies and integration: Depends on Zen 5 `branch-prediction.json` even though that file is outside this work item, plus `decode`, `execution`, `floating-point`, `inst-cache`, `l2-cache`, `l3-cache`, `load-store`, `memory-controller`, and `data-fabric`. Integrates with perf's metric parser and generated pmu-events tables.

Risks: This file is the most fragile cross-file integration point: any event rename or generation-specific spelling difference breaks a metric. Long Data Fabric formulas hard-code 12 DRAM channels, 8 IO complexes, 16 CFI instances, and 6 links. `PerPkg` metrics must not be interpreted per core. Some ratios depend on nonzero denominators and compatible multiplexing groups.

Test signals: Run `perf list --metrics`, `perf stat -M` for each metric group, a dependency scan that resolves every referenced event/metric name, parser tests for long expressions, and workload sanity checks for cache, memory, branch, and fabric bandwidth metrics.
