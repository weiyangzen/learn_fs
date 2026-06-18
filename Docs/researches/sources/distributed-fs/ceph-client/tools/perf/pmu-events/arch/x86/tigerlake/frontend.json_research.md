# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/tigerlake/frontend.json

## Purpose
`frontend.json` defines 39 Tiger Lake events for instruction fetch, decode, uop-cache delivery, microcode sequencer delivery, frontend latency, and frontend bandwidth limitations. It supports analysis of DSB-to-MITE switches, instruction cache misses and stalls, ITLB/STLB frontend misses, IDQ delivery source, and cycles where the frontend delivered too few uops.

## Important APIs, Types, and Fields
The event records use standard core PMU fields plus `CounterMask`, `EdgeDetect`, `Invert`, `MSRIndex`, and `MSRValue`. Seventeen `FRONTEND_RETIRED.*` events use MSR programming to configure frontend-retired latency or miss filters. `DSB2MITE_SWITCHES.COUNT` and `IDQ.MS_SWITCHES` use edge detection to count transitions rather than level cycles. `IDQ_UOPS_NOT_DELIVERED.CYCLES_FE_WAS_OK` uses `Invert: 1`, changing the comparison semantics for the counter mask.

## Control Flow and Data Flow
The file is converted into Tiger Lake event tables by perf tooling. Runtime event resolution programs the core PMU and, for frontend-retired events, auxiliary MSR filter values. Data flows from hardware frontend structures into counters representing delivered uops, stall cycles, or retired instructions that experienced a particular frontend problem. The latency threshold family `FRONTEND_RETIRED.LATENCY_GE_*` provides several cutoffs from 1 through 512 cycles.

## State and Persistence Behavior
No file-local state exists. Hardware counters collect over the measurement interval. MSR-filtered frontend events may be constrained by shared filter resources and can interact with scheduling/multiplexing. Threshold counters can overlap by design; for example, an instruction meeting a 128-cycle threshold also meets lower thresholds depending on hardware semantics, so users should not sum them as disjoint buckets.

## Dependencies and Integration Points
The file depends on Tiger Lake frontend PMU encodings and perf support for MSR-based event filters. It integrates with topdown metrics for frontend bound analysis, with `cache.json` instruction cache and memory hierarchy events, and with `pipeline.json` IDQ/uop delivery and machine-clear events.

## Risks and Edge Cases
MSR-filtered events can fail to schedule with other filter-heavy events or produce confusing multiplexing. Edge-detected switch events differ from cycle-count events with similar names. Threshold latency events are easy to overcount if treated as mutually exclusive. Some descriptions refer to aliases, such as `DECODE.LCP` mirroring `ILD_STALL.LCP`, so duplicate use can double-count the same underlying signal.

## Test Signals
Baseline tests are JSON validation, PMU event generation, and `perf list` visibility. Runtime checks should compare `IDQ.DSB_UOPS`, `IDQ.MITE_UOPS`, and `IDQ.MS_UOPS` under code-cache-friendly and decode-heavy workloads. Branchy or large-code-footprint workloads should raise selected `FRONTEND_RETIRED.*` miss or latency counters. Scheduling tests should request multiple MSR-filtered frontend events and verify perf handles constraints predictably.
