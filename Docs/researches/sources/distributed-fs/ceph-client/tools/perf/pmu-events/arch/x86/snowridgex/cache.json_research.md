# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/snowridgex/cache.json

## Purpose

`cache.json` is the Snow Ridge X core cache and memory-access PMU catalog for perf. It contains 120 events covering L1/L2/LLC access behavior, memory-bound stalls, retired load uops by hit level, retired memory uops, and a large set of offcore response (`OCR.*`) aliases for data, code, RFO, prefetch, streaming store, and writeback request classes. It lets perf users diagnose cache hierarchy behavior and offcore response sources on Snow Ridge X systems.

## Important APIs, Types, and Data Fields

The file uses perf core event fields including `EventName`, `EventCode`, `UMask`, `BriefDescription`, `PublicDescription`, `Counter`, `SampleAfterValue`, optional `PEBS`, optional `Data_LA`, optional `Deprecated`, and offcore-specific `MSRIndex` and `MSRValue`. Non-OCR cache rows include `CORE_REJECT_L2Q.ANY`, `DL1.DIRTY_EVICTION`, `L2_REJECT_XQ.ANY`, `L2_REQUEST.ALL/HIT/MISS/REJECTS`, `LONGEST_LAT_CACHE.REFERENCE/MISS`, `MEM_BOUND_STALLS.*`, `MEM_LOAD_UOPS_RETIRED.*`, `MEM_UOPS_RETIRED.*`, and `TOPDOWN_FE_BOUND.ALL`.

The dominant family is `OCR.*`: 87 records use `EventCode: "0XB7"` and `UMask: "0x1"` with `MSRIndex` values such as `0x1a6` and `0x1a7` plus long `MSRValue` filters. These describe offcore responses for demand data reads, demand code reads, RFOs, L2 hardware prefetches, all code reads, reads-to-core, L1/L2/core writebacks, streaming writes, and snoop outcomes such as `SNOOP_HITM`, `SNOOP_MISS`, and `SNOOP_NOT_NEEDED`. Fourteen rows carry PEBS support, and eight deprecated `OCR.DEMAND_DATA_RD.*` aliases point users to `OCR.DEMAND_DATA_AND_L1PF_RD.*`.

## Control Flow and Data Flow

The JSON has no internal control flow. Perf's generator converts these records into event aliases. At runtime, simple cache rows program core PMU event select and umask fields, while OCR rows additionally program offcore response filter MSRs from `MSRIndex` and `MSRValue`. Counts flow from per-core PMU counters into perf output. The expected diagnostic flow is to use broad L2/LLC/load-retirement events to identify cache pressure, then use `MEM_BOUND_STALLS.*` and OCR response filters to separate L2, L3, DRAM/MMIO, snoop, prefetch, RFO, and writeback behavior.

## State and Persistence Behavior

The persistent state is the static event and filter metadata. Runtime offcore filter programming, PEBS records, and counts are session state owned by perf and the kernel. `Deprecated` rows are still present as aliases but should be treated as compatibility shims. `PEBS` and `Data_LA` mark events that can participate in precise sampling or data-linear-address capture when the hardware and perf mode support it; they do not store sampled data in the JSON.

## Dependencies and Integration Points

This file depends on Snow Ridge X core PMU support, offcore response MSR programming support, and perf's pmu-events parser preserving `MSRIndex`, `MSRValue`, `PEBS`, `Data_LA`, and `Deprecated` fields. It integrates with `snowridgex/counter.json` for available generic/fixed core counters, `frontend.json` for instruction-fetch and branch-clear causes, `floating-point.json` for FP divider/assist pressure, and uncore memory files when core cache misses need to be correlated with memory-controller traffic.

## Risks and Edge Cases

OCR aliases are filter-heavy and easy to break if `MSRValue` is truncated, normalized incorrectly, or paired with the wrong `MSRIndex`. Some OCR rows use two MSRs while outstanding-latency rows use one, so parsers must preserve comma-separated fields. Deprecated demand-data aliases can double-count conceptually with their replacement names if users select both. PEBS availability is model- and mode-dependent. The file mixes access counts, stall cycles, uop retirement counts, topdown slots, and offcore response counts; downstream metrics need explicit unit handling. Shared-core or system-wide aggregation can obscure which workload generated offcore responses.

## Test Signals

Static tests should parse the JSON, preserve OCR MSR fields, and generate perf tables without dropping deprecated or PEBS metadata. Runtime smoke tests should verify `perf list` exposes `L2_REQUEST.*`, `LONGEST_LAT_CACHE.*`, `MEM_LOAD_UOPS_RETIRED.*`, and representative `OCR.*` aliases. Cache-resident workloads should increase L2 hit and load-hit rows; large streaming reads should move LLC miss and OCR DRAM-like response filters; prefetch-heavy workloads should affect hardware prefetch OCR families; cache-line sharing tests should move snoop outcome filters; selecting deprecated aliases should either work or produce the expected perf deprecation behavior.
