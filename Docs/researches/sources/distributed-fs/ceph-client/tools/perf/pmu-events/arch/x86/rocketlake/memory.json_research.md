# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/rocketlake/memory.json

## Purpose

`memory.json` is Rocket Lake's perf PMU catalog for memory-latency stalls, L3-miss demand reads, offcore DRAM response filters, transactional-memory events, and machine clears caused by memory ordering. It contains 60 rows covering `CYCLE_ACTIVITY`, HLE/RTM transaction lifecycle and abort categories, `MEM_TRANS_RETIRED` load latency thresholds, DRAM/L3-miss `OCR` filters, `OFFCORE_REQUESTS`, `OFFCORE_REQUESTS_OUTSTANDING`, `TX_EXEC`, and `TX_MEM`.

## Important APIs, Types, and Data Fields

Rows use `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, and often `PublicDescription`. Optional fields include `CounterMask`, `MSRIndex`, `MSRValue`, and `Data_LA`. Thirty-two rows use MSR selectors. Eight `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_*` rows use MSR `0x3F6` with threshold values from `0x4` through `0x200` and mark `Data_LA: 1`. Twenty-four `OCR.*` rows use offcore response MSRs `0x1a6,0x1a7` for demand code/data/RFO, prefetch, other, and streaming write requests with DRAM, local DRAM, or L3-miss response masks.

## Control Flow and Data Flow

Build-time flow is JSON parsing and generated table creation through `jevents.py`. Runtime flow is perf programming core counters plus latency or offcore MSR filters for selected aliases. The data path splits into three analysis streams. `CYCLE_ACTIVITY` and `OFFCORE_REQUESTS*` quantify L3-miss demand-load cycles and outstanding requests. `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_*` samples or counts retired loads exceeding configured latency thresholds. Transactional rows count HLE/RTM starts, commits, abort causes, and TSX memory conflicts or capacity failures.

## State and Persistence Behavior

The file persists event definitions and selector constants only. Runtime memory latency, transaction state, abort causes, and offcore response state live in CPU hardware for the measurement interval. Threshold selectors in MSR `0x3F6` are part of each alias's meaning. `Data_LA` marks address-capable load-latency rows but does not persist sampled addresses. L3-miss cycles, outstanding-request cycles, retired-load latency events, and transaction abort counts are different measurement units.

## Dependencies and Integration Points

This catalog depends on Rocket Lake PMU support for latency threshold MSR programming, offcore response filters, and transactional-memory events. It integrates with `perf stat`, `perf record`, `perf mem`, memory-latency profiling, TSX/HLE diagnostics, offcore bandwidth and locality metrics, and top-down memory-bound analysis. It complements `cache.json`, where L1/L2/L3 hit and snoop outcomes are more detailed.

## Risks and Edge Cases

Threshold rows overlap: a load slower than 512 cycles also satisfies lower threshold concepts, depending on hardware event semantics, so metrics must avoid naive summation. DRAM and local-DRAM aliases use the same masks in this file for several request classes, so naming should be checked against current Intel guidance before building locality claims. Offcore response MSRs are scarce and can conflict when many `OCR` events are grouped. TSX/HLE events may be unavailable, disabled, or uninteresting on systems with TSX disabled by microcode or kernel policy. Address-capable latency rows require precise sampling setup to produce useful addresses.

## Test Signals

Validation should include JSON parsing, generated table build success, and `perf list` visibility for latency, offcore, and transaction aliases. Pointer-chasing and cache-miss microbenchmarks should move L3-miss cycle and load-latency threshold rows. Remote or high-latency memory scenarios should increase higher thresholds. TSX/HLE test programs should move start, commit, and abort counters when TSX is enabled. Group scheduling tests should check conflicts among MSR-filtered offcore rows.
