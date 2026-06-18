# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswell/virtual-memory.json

## Purpose

This file defines 49 Haswell core virtual-memory and TLB events. It covers DTLB load/store misses, ITLB misses, STLB hits by page size, page-walk completions and durations, PDE cache misses, EPT walk cycles, page-walker memory-source loads, TLB flushes, and ITLB flushes.

## Important APIs, Types, And Data

Records use the standard event schema with `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, and descriptions. Event families include 10 `DTLB_LOAD_MISSES`, 10 `DTLB_STORE_MISSES`, 9 `ITLB_MISSES`, 16 `PAGE_WALKER_LOADS`, `EPT.WALK_CYCLES`, `ITLB.ITLB_FLUSH`, and `TLB_FLUSH.DTLB_THREAD`/`TLB_FLUSH.STLB_ANY`.

The page-walk events distinguish completed walks for 4K, 2M/4M, and 1G pages from walk duration cycles and from memory-source loads in L1, L2, L3, or memory. EPT-prefixed page-walker load events support virtualization-related translation analysis.

## Control Flow

Build-time generation lowercases aliases and emits selector/mask/sample-period metadata into the Haswell core table. Runtime perf uses these aliases directly or through metrics such as `tma_dtlb_load`, `tma_dtlb_store`, `tma_itlb_misses`, and `tma_info_memory_tlb_page_walks_utilization`.

## State And Persistence Behavior

The JSON persists event definitions. TLB occupancy, page-walk behavior, EPT translation activity, and flushes are hardware/runtime state. Sample periods are static hints and do not store any measured state.

## Dependencies And Integration Points

The file depends on Haswell PMU semantics and integrates with `jevents.py`, generated perf tables, top-down memory/TLB metrics, huge-page diagnostics, virtualization/EPT analysis, and `perf stat`/`perf record` workflows. The metric file references `DTLB_LOAD_MISSES.WALK_DURATION`, `DTLB_STORE_MISSES.WALK_DURATION`, `ITLB_MISSES.WALK_DURATION`, and STLB-hit events by name.

## Risks And Edge Cases

Page-size-specific event names are easy to misinterpret on workloads that mix page sizes. Walk-completed events, miss-causes-walk events, walk-duration cycles, and page-walker memory-source loads are related but not interchangeable. EPT events require virtualization contexts and may be zero on ordinary host workloads. TLB flush counts can be dominated by OS behavior and CPU migration rather than application address locality.

## Test Signals

Validate JSON and generated aliases. Runtime checks should include pointer-chasing over large memory, huge-page versus 4K-page comparisons, instruction-footprint stress for ITLB events, and virtualization workloads for EPT/page-walker EPT aliases. Top-down TLB metrics should move with the DTLB/ITLB stressors.
