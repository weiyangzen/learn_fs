<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/tigerlake/virtual-memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/tigerlake/virtual-memory.json

## Purpose

`virtual-memory.json` defines 22 Tiger Lake core PMU events for translation behavior. It covers load, store, and instruction TLB misses; second-level TLB hits; page-walk active and pending cycles; completed page walks by page size; and TLB flush attempts. These definitions let perf distinguish translation cache hits from expensive page walks and flush activity.

## Important APIs, Types, and Data Fields

The file is a JSON array of event objects using `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, `PublicDescription`, and optional `CounterMask`. All events can use counters `0,1,2,3`. `DTLB_LOAD_MISSES` has 7 rows, `DTLB_STORE_MISSES` has 7 rows, `ITLB_MISSES` has 6 rows, and `TLB_FLUSH` has 2 rows.

Load and store families include `STLB_HIT`, `WALK_ACTIVE`, `WALK_COMPLETED`, `WALK_COMPLETED_1G`, `WALK_COMPLETED_2M_4M`, `WALK_COMPLETED_4K`, and `WALK_PENDING`. ITLB has `STLB_HIT`, `WALK_ACTIVE`, `WALK_COMPLETED`, `WALK_COMPLETED_2M_4M`, `WALK_COMPLETED_4K`, and `WALK_PENDING`. `WALK_ACTIVE` entries use `CounterMask: 1` to count cycles when at least one page miss handler is busy. `TLB_FLUSH.DTLB_THREAD` and `TLB_FLUSH.STLB_ANY` count flush attempts.

## Control Flow and Data Flow

There is no local control flow. Perf ingests the rows, emits event aliases, and programs the selected core PMU event select and umask values at runtime. The analysis flow is from first-level TLB misses that hit STLB, to misses that initiate page walks, to active/pending page-walk pressure, and finally to flush activity that can explain translation-cache churn.

## State and Persistence Behavior

The file persists static PMU metadata and default sample periods only. It does not store page tables, TLB contents, fault information, or samples. Runtime counts are per-core/per-thread scheduling dependent. Page-walk completion descriptions explicitly note that a walk can end with or without a page fault, so these counters are translation events rather than fault-only events.

## Dependencies and Integration Points

The catalog depends on Tiger Lake core PMU support and the perf PMU event generator. It integrates with `perf stat`, `perf record`, TLB miss analysis, huge-page validation, code-footprint investigations, memory-latency analysis, and topdown metrics such as `tma_dtlb_load`, `tma_dtlb_store`, and `tma_itlb_misses` in `tgl-metrics.json`. It also complements cache and uncore-memory files by explaining address-translation cost before cache or DRAM service.

## Risks and Edge Cases

`WALK_ACTIVE` and `WALK_PENDING` share the same event/umask in each family but have different semantics because `WALK_ACTIVE` uses `CounterMask: 1`; losing that field changes cycle counting into occupancy-like counting. Completed-walk counts and active/pending cycle counts must not be interpreted as the same unit. Page-size-specific counters only indicate mapping size for completed walks, not total memory footprint. ITLB lacks a 1G-specific row here, so load/store and code-fetch summaries are not perfectly symmetric. Flush attempts can be caused by OS and virtualization behavior outside the measured workload.

## Test Signals

Validation should include JSON parsing, generated perf tables, and `perf list` exposure for DTLB, ITLB, and TLB flush aliases. Runtime tests should use random-access data workloads to raise DTLB load/store walk counters, large-page workloads to shift completions from 4K to 2M/1G rows where applicable, code-footprint workloads to exercise ITLB rows, and mapping/unmapping or context-switch-heavy workloads to move flush counters. Regression tests should confirm `CounterMask` survives generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/tigerlake/virtual-memory.json -->
