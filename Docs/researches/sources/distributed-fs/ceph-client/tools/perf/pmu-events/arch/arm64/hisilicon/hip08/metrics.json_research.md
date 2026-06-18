<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/hisilicon/hip08/metrics.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/hisilicon/hip08/metrics.json

## Purpose
Hip08 derived metrics table for topdown-style performance diagnosis. It defines frontend, bad speculation, retiring, backend, fetch latency/bandwidth, branch misprediction and flush submetrics, core and memory bound classes, execution port utilization, cache-level bounds, and store bound metrics.

## APIs, Types, and Functions
Records use perf metric schema fields such as `MetricName`, `MetricExpr`, `MetricGroup`, `DefaultMetricgroupName`, `BriefDescription`, and `PublicDescription`. Metric names include `frontend_bound`, `bad_speculation`, `retiring`, `backend_bound`, `fetch_latency_bound`, `branch_mispredicts`, `machine_clears`, `core_bound`, `memory_bound`, `idle_by_itlb_miss`, `bp_misp_flush`, `rob_stall`, `l1_bound`, `l2_bound`, `mem_bound`, and `store_bound`.

## Control Flow, State, and Persistence
`jevents.py` preserves metric expressions into generated perf metadata. At runtime, perf metric evaluation reads underlying PMU events from `core-imp-def.json` and standard ARM64 events, computes formulas over measured counts, and reports percentages or ratios. No metric state is persisted by the JSON.

## Dependencies and Integration
Depends heavily on Hip08 event aliases such as `FETCH_BUBBLE`, `BR_MIS_PRED`, `EXE_STALL_CYCLE`, `MEM_STALL_L1MISS`, and cache/TLB events. It integrates with `perf stat -M` and provides the main human-facing analysis layer above raw Hip08 counters.

## Risks and Test Signals
Risks include divide-by-zero expressions, formulas that assume Intel-like topdown slot semantics on Hip08, missing source events, and percentage metrics that are not mutually exclusive. Test signals are `perf list --metrics`, `perf stat -M` on Hip08, expression parser success, no missing-event warnings, and sanity under branch-heavy, memory-bound, core-bound, and frontend-bound microbenchmarks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/hisilicon/hip08/metrics.json -->
