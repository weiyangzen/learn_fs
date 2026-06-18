# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/tigerlake/cache.json

## Purpose
`cache.json` defines 68 Tiger Lake core PMU events for cache hierarchy, memory instruction retirement, offcore request flow, snoop outcomes, software prefetches, super queue pressure, and locked or split memory accesses. It provides the main event vocabulary for analyzing L1D/L2/L3 behavior and core-originated memory traffic on Tiger Lake.

## Important APIs, Types, and Fields
The event schema includes `EventName`, `EventCode`, `UMask`, `Counter`, `BriefDescription`, `PublicDescription`, and `SampleAfterValue`. Some records add `CounterMask`, `EdgeDetect`, `Data_LA`, `MSRIndex`, and `MSRValue`. There are 20 `Data_LA` events, mostly retired memory load/store and load-source events, enabling address-aware sampling. Three OCR events use `MSRIndex`/`MSRValue` to program offcore response filters. `L1D_PEND_MISS.FB_FULL_PERIODS` uses `CounterMask: 1` plus `EdgeDetect: 1`, so it counts periods rather than cycles.

## Control Flow and Data Flow
Perf ingests the JSON into Tiger Lake event tables. Runtime flow resolves event names such as `L2_RQSTS.DEMAND_DATA_RD_MISS`, `MEM_LOAD_RETIRED.L3_MISS`, or `OFFCORE_REQUESTS_OUTSTANDING.DEMAND_DATA_RD_GE_6`, then programs generic core counters or offcore filter MSRs as required. The file distinguishes request counts, hit/miss counts, outstanding occupancy, cycles with outstanding requests, and retired-load data source classification.

## State and Persistence Behavior
The JSON is static. Runtime state is in core PMU counters, offcore response MSRs, and optional perf samples with data linear addresses. Events with occupancy or cycles semantics must be normalized differently from simple request counts. Fixed hardware resources such as offcore response filter MSRs can constrain multiplexing when users request several OCR-filtered events together.

## Dependencies and Integration Points
The file depends on Tiger Lake model matching, perf's JSON generator, kernel PMU support for offcore response programming, and Data_LA sampling support. It integrates with `memory.json` latency events, `frontend.json` instruction-cache events, `pipeline.json` stall/topdown events, and metric groups that classify cache hits, cache misses, memory bandwidth, memory latency, snoop, and prefetch behavior.

## Risks and Edge Cases
Several event families have similar names but different semantics: `L2_RQSTS.*` counts L2 accesses, `MEM_LOAD_RETIRED.*` classifies retired load sources, and `OFFCORE_REQUESTS_OUTSTANDING.*` counts occupancy or cycles. Misusing them as interchangeable cache miss rates can produce incorrect analysis. OCR events require MSR filters and can conflict with other offcore events. Address sampling through `Data_LA` is hardware/kernel dependent. `LONGEST_LAT_CACHE.MISS` includes speculative and prefetch behavior, so it is not identical to retired load L3 misses.

## Test Signals
Use `jq empty`, PMU table generation, and `perf list` on Tiger Lake to confirm representative names. Runtime checks should exercise memory streaming and pointer-chasing workloads, comparing `MEM_LOAD_RETIRED.L1_HIT/L2_HIT/L3_MISS`, `L2_RQSTS.*`, and `OFFCORE_REQUESTS_OUTSTANDING.*`. OCR tests should verify that events with `MSRIndex`/`MSRValue` can be scheduled and that perf reports conflicts or multiplexing clearly when resources are exhausted.
