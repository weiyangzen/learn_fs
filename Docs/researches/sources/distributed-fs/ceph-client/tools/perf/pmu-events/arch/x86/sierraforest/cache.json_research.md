# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sierraforest/cache.json

## Purpose

This 63-entry Sierra Forest cache and memory-hierarchy event table describes core PMU aliases for L1D dirty evictions, L2 line movement and requests, LLC references/misses, memory-bound stalls, retired load/cache-level classifications, memory scheduler blocks, retired memory uops, PEBS load-latency thresholds, offcore response filters, and a topdown frontend-cache signal. It is source metadata for perf, not executable code.

## Important APIs, Types, and Data

The schema includes `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, optional `PublicDescription`, `Data_LA`, `MSRIndex`, and `MSRValue`. All core events use generic counters `0,1,2,3,4,5,6,7` except PEBS load-latency threshold aliases, which are restricted to counters `0,1` and program `MSRIndex 0x3F6` with threshold `MSRValue` values from `0x4` through `0x800`. `Data_LA: 1` marks memory uop sampling aliases that can capture data linear address. Offcore `OCR.*` entries program MSRs `0x1a6,0x1a7`.

## Control Flow

Perf resolves a requested alias to its event select, mask, optional MSR filter, and allowed counter set. Normal cache and stall events program generic counters. Offcore-response events require programming the offcore response MSRs before the counter starts. Load-latency aliases rely on PEBS-style sampling and the latency threshold MSR. Higher-level metrics combine these events to separate L2, LLC, local/remote DRAM, scheduler, store-buffer, and frontend-cache pressure.

## State and Persistence Behavior

The persistent state is the checked-in alias table and its hardware filter encodings. Runtime counter state is held in core PMU counters and optional filter MSRs for the duration of a perf session. `SampleAfterValue` persists default sampling periods. `Data_LA` and threshold MSR metadata are part of the observable contract: removing or changing them would alter sampling behavior even if `EventName` stayed stable.

## Dependencies and Integration Points

This file integrates with perf pmu-events generation, `perf list`, `perf stat`, `perf record`, PEBS/data-address sampling support, offcore response MSR programming, and Sierra Forest topdown metric expressions. It complements `memory.json` by providing broader cache residency and scheduler events, and complements `pipeline.json` by providing stall-cause events used for backend and frontend breakdowns.

## Risks

Offcore `MSRValue` filters are high risk because syntactically valid numbers can encode the wrong response type. PEBS load-latency events require both correct counter restrictions and kernel support for the latency threshold MSR. Some LLC descriptions note that systems without an L3 cache reinterpret LLC hits/misses as zero or L2 misses, so metrics must account for SKU topology. `Data_LA` events can be incorrectly exposed as precise sampling candidates if kernel support is missing. Aggregate and subevent aliases can be double-counted if summed blindly.

## Test Signals

Useful tests include schema parsing, alias listing, generated config/MSR comparisons, and `perf stat` runs for L2, LLC, memory-bound stall, and memory-uop families. PEBS tests should verify latency thresholds program `0x3F6` and only schedule on counters `0,1`. Offcore tests should verify MSR filters for local/remote DRAM and snoop responses. Workloads with L1/L2-resident data, LLC misses, store-buffer pressure, and remote memory access should move the expected counters.
