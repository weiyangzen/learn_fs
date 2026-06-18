# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwell/virtual-memory.json

## Purpose

`virtual-memory.json` defines 38 Broadwell core PMU events for TLB misses, page walks, TLB flushes, and extended page table walk cycles. It separates load, store, and instruction TLB behavior and provides page-size-specific walk completion counters.

## Important APIs, Types, and Data Fields

The file is a JSON event array using standard perf PMU event fields. Important families are `DTLB_LOAD_MISSES.*`, `DTLB_STORE_MISSES.*`, `ITLB_MISSES.*`, `PAGE_WALKER_LOADS.*`, `TLB_FLUSH.*`, `ITLB.ITLB_FLUSH`, and `EPT.WALK_CYCLES`. Common fields include `EventName`, `EventCode`, `UMask`, `Counter`, `CounterMask`, `SampleAfterValue`, `BriefDescription`, and `PublicDescription`. The DTLB and ITLB miss families include `MISS_CAUSES_A_WALK`, `STLB_HIT`, `STLB_HIT_4K`, `STLB_HIT_2M`, `WALK_COMPLETED`, `WALK_COMPLETED_4K`, `WALK_COMPLETED_2M_4M`, `WALK_COMPLETED_1G`, and `WALK_DURATION`.

## Control Flow and Data Flow

There is no executable control flow. Build-time perf tooling turns the JSON rows into generated event tables. At runtime, perf programs Broadwell PMU counters for selected TLB/page-walk events. Miss-causes-walk rows count miss occurrences, walk-duration rows count cycles spent walking, page-walker-load rows identify which cache/memory level supplied page-table data, and flush rows count invalidation activity.

## State and Persistence Behavior

The file is static metadata and stores no page tables, mappings, TLB state, or counter samples. `SampleAfterValue` sets default sampling periods for generated metadata.

## Dependencies and Integration Points

This file depends on Broadwell PMU definitions for DTLB, ITLB, second-level TLB, page walker, EPT, and flush events. It integrates with perf list/stat/record, virtual memory performance analysis, huge-page tuning, virtualization profiling through EPT walk cycles, and top-down memory/TLB metric groups.

## Risks and Edge Cases

Page-size suffixes must be interpreted carefully: 2M/4M and 1G walk-completion events do not represent the same workload class as 4K events. Walk counts and walk-duration cycles are different units and should not be added directly. EPT walk cycles are virtualization-specific and may be zero or unsupported outside nested/guest contexts. Some rows have only brief descriptions, so downstream UI may expose sparse documentation. TLB flush counters can be affected by OS scheduling and shootdown behavior outside the profiled process.

## Test Signals

Validation should include JSON parse/build success, event visibility in `perf list`, and representative `perf stat` runs for DTLB, ITLB, page-walker, flush, and EPT rows. Workloads with random memory access should increase DTLB misses and page walks; large-page workloads should shift page-size-specific counters; virtualization workloads are the right signal for `EPT.WALK_CYCLES`.
