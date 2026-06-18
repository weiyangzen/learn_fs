# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/ivybridge/cache.json

## Purpose

`cache.json` defines 104 Ivy Bridge cache and offcore memory hierarchy events. It covers L1D replacement and pending misses, L2 requests and line state transitions, L2 writebacks, store lock requests, offcore responses, outstanding offcore requests, LLC hit/miss outcomes, and retired memory uops. These aliases are the core data source for Ivy Bridge cache, memory-bound, bandwidth, latency, and topdown metrics.

## Schema And API Surface

Entries are perf core PMU event objects with fields such as `EventName`, `EventCode`, `UMask`, `BriefDescription`, `PublicDescription`, `Counter`, `CounterMask`, `SampleAfterValue`, `AnyThread`, `PEBS`, `MSRIndex`, and `MSRValue`. The large event families include `OFFCORE_RESPONSE`, `L2_RQSTS`, `OFFCORE_REQUESTS_OUTSTANDING`, `L2_TRANS`, `MEM_UOPS_RETIRED`, `MEM_LOAD_UOPS_RETIRED`, `L2_LINES_OUT`, `L2_LINES_IN`, `L2_L1D_WB_RQSTS`, and `L1D_PEND_MISS`. `OFFCORE_RESPONSE.*` entries use MSR programming fields to select offcore filters.

## Control Flow And Integration

`jevents.py` converts these declarations into generated C aliases for the Ivy Bridge model table. At runtime, perf resolves names to PMU event encodings; for offcore response aliases it must also program the associated model-specific register filter. These events are referenced heavily by `ivb-metrics.json`, for example in formulas for L1/L2/L3 MPKI, memory bandwidth, DRAM bound, data sharing, false sharing, fill-buffer fullness, and memory-level parallelism.

## State And Persistence

The file persists event encodings and offcore MSR filters, not measurements. PEBS-capable events and sample-after defaults affect profiling behavior. `AnyThread` changes thread aggregation semantics on SMT systems. The offcore `MSRIndex` and `MSRValue` fields are critical persistent state because they represent the extra filter beyond the base event code and umask.

## Dependencies

Dependencies include Intel Ivy Bridge core PMU definitions, perf support for offcore response MSR filters, and metric expressions in `ivb-metrics.json`. It also depends on consistent alias naming with other Ivy Bridge topic files, because topdown formulas cross-reference events from cache, memory, frontend, floating-point, pipeline, and branch files.

## Risks

The biggest risk is invalid or mismatched offcore filter programming: an incorrect `MSRValue` can count a different response class while still appearing syntactically valid. PEBS and sample-after defaults must match hardware capabilities. Renaming aliases can break `ivb-metrics.json` expressions. Counter constraints and any-thread settings can change multiplexing and SMT interpretation.

## Test Signals

Beyond JSON parsing and `jevents.py` generation, run metric-expression validation and `perf list` on Ivy Bridge. Runtime smoke tests should exercise cache-friendly and cache-thrashing workloads, plus offcore DRAM reads, and confirm plausible movement in `L1D.REPLACEMENT`, `L2_RQSTS.*`, `LONGEST_LAT_CACHE.*`, and `OFFCORE_RESPONSE.*` aliases.
