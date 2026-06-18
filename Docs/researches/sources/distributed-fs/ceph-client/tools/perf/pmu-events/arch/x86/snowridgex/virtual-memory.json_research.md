# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/snowridgex/virtual-memory.json

## Purpose
`virtual-memory.json` defines 31 Snow Ridge core PMU events for TLB and page-walk behavior. It covers load/store DTLB misses, STLB hits, page-walk completions by page size, page-walk pending cycles, EPT walk cache hits/misses, ITLB fills and misses, and retired memory uops that missed DTLB structures. The file is aimed at diagnosing virtual-memory translation overhead and virtualization translation costs.

## Important APIs, Types, and Fields
Entries use core PMU fields such as `EventName`, `EventCode`, `UMask`, `Counter`, `BriefDescription`, `PublicDescription`, and `SampleAfterValue`. All events use programmable counters `0,1,2,3`. Four events include `PEBS`, enabling precise sampling semantics for selected retired DTLB miss events. Three events include `Data_LA`, identifying events that can provide data linear address information. `SampleAfterValue` differs by event family and controls perf's default sampling period for profile-style use.

## Control Flow and Data Flow
Perf's build-time parser turns the JSON entries into named Snow Ridge core events. Runtime flow is name resolution to event selector and unit mask, followed by programming core PMU counters. Events such as `DTLB_LOAD_MISSES.WALK_COMPLETED_4K` and `DTLB_STORE_MISSES.WALK_PENDING` distinguish count-style and cycle/occupancy-style measurements; `EPT.*` records capture extended page-table walk cache behavior when virtualization is active.

## State and Persistence Behavior
The file stores no mutable state. Hardware counters track translation events during the measurement interval. PEBS-capable records can persist sample payloads in perf data files when profiling; that persistence is owned by perf output, not by this JSON. Events with page-size-specific masks should be interpreted as subsets of broader `WALK_COMPLETED` counters, subject to hardware semantics and possible overlap in faulting paths.

## Dependencies and Integration Points
The definitions depend on Snow Ridge core PMU support, perf's JSON event tooling, and PEBS/Data_LA handling in perf and the kernel. They integrate with memory and cache analysis workflows because TLB misses often explain L1/L2/L3 or offcore latency. Virtualization-related `EPT.*` names integrate with hypervisor and guest workload profiling.

## Risks and Edge Cases
Page-walk events include page walks that fault in several descriptions, so raw counts are not equivalent to successful translations. `WALK_PENDING` events count cycles or outstanding walk occupancy, not completed walks, and require denominator care. EPT events may be unavailable or flat zero on non-virtualized workloads. PEBS/Data_LA fields raise compatibility risk if kernel support for precise address sampling differs across systems.

## Test Signals
Tests should include JSON syntax validation and perf table generation. On supported Snow Ridge systems, `perf list` should expose DTLB, ITLB, and EPT names from this file. Runtime smoke tests can compare `DTLB_LOAD_MISSES.WALK_COMPLETED`, page-size-specific variants, and `DTLB_LOAD_MISSES.STLB_HIT` while running workloads with 4K and huge pages. PEBS tests should verify that precise sampling works for `MEM_UOPS_RETIRED.DTLB_MISS*` where supported.
