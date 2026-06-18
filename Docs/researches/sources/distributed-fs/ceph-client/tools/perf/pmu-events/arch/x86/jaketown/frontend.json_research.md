# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/jaketown/frontend.json

## Purpose
This JSON file defines Jake Town frontend PMU events for perf. Its 33 entries cover branch resteers, DSB-to-MITE switches, decoded stream buffer fill cancellations, instruction-cache hits and misses, instruction decode queue sources and occupancy, microcode sequencer delivery, uops not delivered, and instructions written to the instruction queue. It supports frontend bottleneck analysis for instruction fetch, decode, uop cache, and delivery limits.

## Important APIs, Types, And Functions
The file contains declarative event descriptors. Important fields include `EventName`, `EventCode`, `UMask`, `Counter`, `CounterMask`, `EdgeDetect`, `Invert`, `SampleAfterValue`, `BriefDescription`, and `PublicDescription`. All entries use counters `0,1,2,3`. Event families include `BACLEARS`, `DSB2MITE_SWITCHES`, `DSB_FILL`, `ICACHE`, `IDQ`, `IDQ_UOPS_NOT_DELIVERED`, and `INSTS_WRITTEN_TO_IQ`. Several cycle-threshold events use counter masks, edge detection, or inversion to express specific frontend-delivery states.

## Control Flow
There is no executable control flow. Perf parses the JSON aliases and programs core PMU events with optional counter-mask, edge-detect, or invert attributes. The table intentionally distinguishes count events from cycle qualification events, for example DSB or MITE uop delivery versus cycles with any or four uops delivered. These aliases are building blocks for top-down frontend metrics.

## State And Persistence
The file persists hardware encoding metadata and default sampling values. Runtime frontend state, instruction queue occupancy, and uop delivery counts are not stored here; they are sampled from PMU counters. `CounterMask`, `EdgeDetect`, and `Invert` fields persist the conditions needed to count cycles matching frontend states such as zero delivered uops or microcode sequencer switches.

## Dependencies And Integration Points
The file integrates with perf's Jake Town PMU event table and with `jkt-metrics.json`, which references frontend concepts such as frontend bound, fetch latency, fetch bandwidth, DSB switches, and branch resteers. It depends on parser support for counter-mask, inversion, and edge-detect fields and on the core PMU driver mapping those attributes correctly.

## Risks And Edge Cases
Cycle-qualified delivery events are easy to misinterpret as raw uop counts. `Invert` and `CounterMask` mistakes can reverse a metric's meaning, especially for `IDQ_UOPS_NOT_DELIVERED` aliases. Frontend events are sensitive to SMT state and pipeline source, so metric formulas must include appropriate denominators. DSB/MITE terminology should stay aligned with vendor docs to avoid confusing decoded-uop-cache and legacy decode paths.

## Test Signals
Useful checks include JSON syntax validation, event-table generation, and `perf list` visibility. Runtime signals include increased instruction-cache misses under large code footprints, DSB/MITE distribution shifts under uop-cache-friendly versus unfriendly loops, branch resteer events under branch-mispredict microbenchmarks, and top-down frontend metrics resolving all referenced aliases.
