# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen3/recommended.json

## Purpose

`amdzen3/recommended.json` defines 34 recommended Zen 3 perf aliases and metrics. It mixes raw event aliases for commonly used counters with derived `MetricName`/`MetricExpr` records for branch prediction, L2/L3 cache, TLB, decoder, and data-fabric analysis.

## Important records and schema

The file includes two kinds of records:

- Event aliases with `EventName`, `EventCode`, `UMask`, optional `Unit`, optional `PerPkg`, and `BriefDescription`.
- Derived metrics with `MetricName`, `MetricExpr`, `MetricGroup`, optional `ScaleUnit`, optional `MetricConstraint`, and `BriefDescription`.

Important metrics include:

- `branch_misprediction_ratio`: `d_ratio(ex_ret_brn_misp, ex_ret_brn)`.
- L2 access/miss/hit metrics: `all_l2_cache_accesses`, `l2_cache_accesses_from_l2_hwpf`, `all_l2_cache_misses`, `l2_cache_misses_from_l2_hwpf`, and `all_l2_cache_hits`.
- L3 metrics: `l3_cache_accesses`, `l3_misses`, and `l3_read_miss_latency`, the last using `(xi_sys_fill_latency * 16) / xi_ccx_sdp_req1`.
- Frontend cache ratios: `op_cache_fetch_miss_ratio` and `ic_fetch_miss_ratio`.
- TLB metrics: `l1_itlb_misses`, `l2_itlb_misses`, `l1_dtlb_misses`, `l2_dtlb_misses`, and `all_tlbs_flushed`.
- Decoder/execution metrics: `macro_ops_dispatched`, `macro_ops_retired`, and `sse_avx_stalls`.
- Data-fabric metrics: `all_remote_links_outbound` and `nps1_die_to_dram`, marked package-scoped where applicable.

## Control flow and integration

`jevents.py` parses metric expressions using perf's metric parser and emits generated metric tables. At runtime, `perf stat -M <MetricName>` expands formulas into the referenced raw events. This file depends on raw aliases defined across `cache.json`, `core.json`, `memory.json`, `floating-point.json`, `other.json`, and `data-fabric.json`.

## State and persistence

The file persists user-visible recommended metric names and formulas. Derived metrics are effectively API contracts: scripts and documentation may reference names such as `branch_misprediction_ratio` and `all_l2_cache_misses`.

## Dependencies

Dependencies include all referenced Zen 3 event files plus perf metric functions such as `d_ratio`. `L3PMC` and `DFPMC` records depend on AMD uncore PMU routing, and `PerPkg` depends on package aggregation support.

## Risks

Formula drift is the main risk: a referenced alias rename or semantic change breaks metric parsing or changes metric meaning. Ratios require denominator safety; `d_ratio` helps, but unusual workloads can still produce unintuitive values. Data-fabric sums are approximate and topology-sensitive. Raw and derived records in one file increase maintenance risk because schema validation must accept both shapes.

## Test signals

Run JSON validation, `metric_test.py`/PMU event generation, and `perf list --details` checks. On Zen 3 hardware, run representative `perf stat -M` commands for branch, L2/L3, TLB, decoder, and data-fabric groups and confirm formulas resolve and produce plausible non-negative values.
