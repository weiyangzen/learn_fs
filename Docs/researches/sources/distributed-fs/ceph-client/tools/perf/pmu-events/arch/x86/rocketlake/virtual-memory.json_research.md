# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/rocketlake/virtual-memory.json

## Purpose
This JSON file defines Rocket Lake virtual-memory and TLB PMU event aliases for perf. It covers first-level and second-level TLB behavior for data loads, data stores, and instruction fetches, including STLB hits, page-walk activity, completed walks by page size, pending walks, and TLB flush events.

The aliases are foundational for memory-translation metrics in `rkl-metrics.json`, including DTLB load/store bottlenecks, ITLB/code STLB misses, page-walk utilization, and page-size breakdowns.

## Data shape and important fields
The file is a JSON array of 22 event objects. The observed keys are `EventName`, `BriefDescription`, `PublicDescription`, `EventCode`, `UMask`, `Counter`, `CounterMask`, and `SampleAfterValue`.

The event families are:

- `DTLB_LOAD_MISSES`: 7 events for load STLB hits, walk activity, completed walks, 1G walks, 2M/4M walks, 4K walks, and pending walks.
- `DTLB_STORE_MISSES`: 7 analogous events for stores.
- `ITLB_MISSES`: 6 events for instruction-side STLB hits and walks, without a 1G-specific completed-walk entry.
- `TLB_FLUSH`: 2 events for DTLB thread flushes and STLB flushes.

All entries use programmable counters `0,1,2,3`. Some events use `CounterMask` to convert an occurrence-style event into a cycles-with-activity or pending-walk occupancy signal. Sample periods are present on normal sampled events.

## Control flow and integration
The file has declarative flow through the perf PMU event generator:

1. `jevents.py` parses the virtual-memory topic JSON.
2. Each object is converted to generated `pmu_event` data with event/umask/cmask encodings.
3. Runtime perf resolves names such as `DTLB_LOAD_MISSES.WALK_ACTIVE` or `ITLB_MISSES.WALK_COMPLETED_4K`.
4. `rkl-metrics.json` uses these aliases in formulas such as `tma_dtlb_load`, `tma_dtlb_store`, `tma_load_stlb_miss`, `tma_store_stlb_miss`, `tma_code_stlb_miss`, and page-size-specific child metrics.

There is no executable logic in the JSON. Interpretation of activity versus completed-walk counts is controlled by event encoding and metric formulas.

## State, persistence, and dependencies
The source file is static. The generated perf event table is the build-time persistence artifact. Runtime state is in core PMU counters programmed for DTLB, ITLB, and TLB flush events.

Dependencies include Rocket Lake's PMU event encodings for TLB miss families, perf's schema support for `CounterMask`, and metric formulas that normalize activity counts by `tma_info_thread_clks` or `tma_info_core_core_clks`. The metrics layer also depends on matching page-size variants; for example, load/store page-walk metrics divide completed 4K, 2M/4M, and 1G counts by the sum of completed walks.

## Risks
The main risk is confusing occurrence counts with cycle/occupancy counts. `WALK_ACTIVE` and `WALK_PENDING` are used as stall or utilization signals, while `WALK_COMPLETED_*` entries are used for page-size breakdowns. Incorrect `CounterMask` or umask values can make metrics look plausible but semantically wrong.

Another risk is denominator fragility in page-size metrics. If no walks complete in a workload, formulas that divide page-size walk counts by total completed walks can become undefined or unstable unless the metric evaluator or caller handles zero counts. Cross-file dependencies also matter because `rkl-metrics.json` combines these events with pipeline clocks and memory activity events.

## Test signals
Useful checks include `jq empty virtual-memory.json`, generated `jevents` output inspection for all 22 aliases, and `perf list --json` checks for DTLB, ITLB, and TLB flush names. Runtime tests should count representative load, store, instruction, and flush events if hardware is available. Metric validation should cover `tma_dtlb_load`, `tma_dtlb_store`, `tma_itlb_misses`, `tma_load_stlb_miss_4k`, `tma_store_stlb_miss_2m`, and `tma_code_stlb_miss_4k`.
