<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/metrics.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/metrics.json

## Purpose
NVIDIA T410 derived metrics table. It defines 103 perf metrics for topdown L1/backend/frontend breakdowns, branch ratios and MPKI, bus bandwidth, SMT/ST cycle fractions, crypto/integer/FP/SIMD/SVE percentages, TLB MPKI and walk latency, cache miss ratios and MPKI, prefetch accuracy/coverage/usefulness, LLC hit/miss ratios, load/store percentages, IPC, and SVE predicate density.

## APIs, Types, and Functions
Records use `MetricName`, `MetricExpr`, `BriefDescription`, `ScaleUnit`, and `MetricGroup`. Important groups include `TopdownL1`, `Topdown_Backend`, `Topdown_Frontend`, `Cycle_Accounting`, `Branch`, `Bus`, `General`, `Cache`, `Memory`, `Pipeline`, `SVE`, `TLB`, and `Retiring`. Expressions reference raw aliases from the T410 topic files, for example `STALL_SLOT_BACKEND / CPU_SLOT`, `L1D_CACHE_REFILL / INST_RETIRED`, and prefetch-derived numerator/denominator pairs.

## Control Flow, State, and Persistence
`jevents.py` embeds metric metadata into generated perf tables. Runtime perf metric evaluation schedules referenced events where possible, reads counts, evaluates `MetricExpr`, applies `ScaleUnit`, and groups output by `MetricGroup`. The JSON does not persist computed values.

## Dependencies and Integration
Depends on nearly every T410 raw-event topic in this work item plus additional T410 files not in this subset, such as retired, stall, spec operation, and TLB event tables. It is the main integration layer that turns raw PMU aliases into user-facing performance analysis.

## Risks and Test Signals
Risks include missing referenced events when related JSON files are absent or renamed, divide-by-zero expressions, multiplexing errors when metrics require too many counters, overlapping percentages, and formulas that assume specific cache/prefetch semantics. Test signals are `perf list --metrics`, `perf stat -M` for each metric group, expression parser success with no unresolved aliases, controlled frontend/backend/branch/cache/TLB/SVE workloads, and comparison of derived ratios against raw counter sanity checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/nvidia/t410/metrics.json -->
