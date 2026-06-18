# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/ivybridge/memory.json

## Purpose

`memory.json` defines 19 Ivy Bridge memory-ordering, load-latency, precise-store, misalignment, offcore DRAM, and page-walk events. It complements `cache.json` by focusing on retired memory transactions, latency thresholds, DRAM miss classes, and memory-ordering machine clears.

## Schema And API Surface

Entries include `EventName`, `EventCode`, `UMask`, `BriefDescription`, `PublicDescription`, `Counter`, `SampleAfterValue`, and for offcore events `MSRIndex`, `MSRValue`, and sometimes `PEBS`. Families are `MEM_TRANS_RETIRED`, `OFFCORE_RESPONSE`, `MISALIGN_MEM_REF`, `MACHINE_CLEARS`, and `PAGE_WALKS`. Representative aliases include `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_128`, `MEM_TRANS_RETIRED.PRECISE_STORE`, `OFFCORE_RESPONSE.ALL_DATA_RD.LLC_MISS.DRAM`, `OFFCORE_RESPONSE.DATA_IN_SOCKET.LLC_MISS.LOCAL_DRAM`, `MISALIGN_MEM_REF.LOADS`, and `MACHINE_CLEARS.MEMORY_ORDERING`.

## Control Flow And Integration

`jevents.py` generates Ivy Bridge aliases from these records. Perf can use latency threshold events for sampling and stat counting, and offcore DRAM aliases require MSR filter programming. Metrics in `ivb-metrics.json` use these events for memory latency, DRAM bound, store bound, page-walk utilization, and machine-clear analysis.

## State And Persistence

The file persists latency thresholds, PEBS capability, sampling defaults, and offcore filter state. Runtime state is measured by PMU counters and can be sampled for precise memory analysis where hardware supports it. The GT threshold suffixes encode increasing latency buckets that consumers must interpret consistently.

## Dependencies

Dependencies include Ivy Bridge PEBS/load-latency support, offcore response MSR programming, and metric formulas that reference the aliases. It integrates with perf stat, perf record, and generated metric tables.

## Risks

Offcore `MSRValue` mistakes can silently change DRAM/local-socket semantics. Latency threshold event names must match formulas and user expectations; changing thresholds breaks longitudinal comparisons. PEBS markings must reflect hardware support or sampling may fail. Some events overlap conceptually with `cache.json`, so duplicate or inconsistent naming can confuse metrics.

## Test Signals

Check JSON parsing and generated table output. On Ivy Bridge, use pointer-chasing or memory-latency workloads to verify increasing `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_*` buckets behave monotonically. DRAM miss workloads should move `OFFCORE_RESPONSE.*DRAM` aliases, and precise store sampling should be tested where supported.
