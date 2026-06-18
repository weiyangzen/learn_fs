# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswell/frontend.json

## Purpose
This JSON file defines 29 Intel Haswell core PMU frontend events for branch resteers, DSB-to-MITE switches, instruction-cache behavior, instruction decode queue delivery, microcode sequencer activity, and frontend under-delivery. The source was read as a complete 275-line JSON array.

## Important APIs, Types, and Functions
Every row has `EventName`, `EventCode`, `UMask`, `BriefDescription`, `Counter`, and `SampleAfterValue`; 16 rows include `PublicDescription`. Specialized fields include `CounterMask`, `EdgeDetect`, `Invert`, and `Errata`. There are 29 unique event names over five event codes: `BACLEARS.ANY` (`0xe6`), `DSB2MITE_SWITCHES.PENALTY_CYCLES` (`0xAB`), `ICACHE.*` (`0x80`), `IDQ.*` (`0x79`), and `IDQ_UOPS_NOT_DELIVERED.*` (`0x9C`).

Important families include `ICACHE.HIT/MISSES/IFETCH_STALL/IFDATA_STALL`, DSB and MITE delivery cycle/uop events, microcode sequencer delivery/switch events, `IDQ.EMPTY`, and `IDQ_UOPS_NOT_DELIVERED.*` aliases. Several aliases intentionally share event code and unit mask but differ by counter masks, edge detection, invert, or descriptive semantics; for example IDQ cycle and uop views use overlapping selectors with different interpretation.

## Control Flow, State, and Persistence
The file has no executable control flow. Build-time generation is handled by `jevents.py`, which preserves event fields in generated perf tables. Runtime perf schedules the events on core programmable counters and applies edge, invert, and counter-mask settings when present.

Static state includes frontend event encodings, counter masks, edge-detect/invert modifiers, errata annotations, and sample-after values. Persistence is generated perf metadata only. Runtime counts depend heavily on workload instruction footprint, branch behavior, decode path selection, microcode usage, SMT state, and backend stalls because several frontend-delivery events are defined relative to whether the backend is stalled.

## Dependencies and Integration Points
Dependencies include Haswell PMU definitions, perf's JSON event schema, `jevents.py`, and kernel x86 PMU support for event modifiers. The file integrates with `perf list`, `perf stat`, and frontend performance analysis. It is an input to top-down-style diagnosis even though this file itself contains no metric expressions.

The events complement cache, branch, pipeline, and instruction-retirement event files. For example, instruction-cache misses can be correlated with ITLB/cache events, IDQ under-delivery with backend stall metrics, and microcode sequencer events with complex instruction or assist-heavy workloads.

## Risks and Test Signals
Risks include errata `HSD135` on `IDQ.EMPTY` and all `IDQ_UOPS_NOT_DELIVERED.*` rows, modifier mistakes for `CounterMask`, `EdgeDetect`, or `Invert`, and ambiguous aliases such as `ICACHE.IFDATA_STALL` and `ICACHE.IFETCH_STALL` sharing the same selector. Frontend under-delivery events are easy to misread without considering backend stall conditions. Events with shared selectors may produce identical raw counts while representing different documented viewpoints.

Test signals include JSON validation, generated-table checks for edge/invert/counter-mask fields, `perf list` visibility, and Haswell hardware smoke tests with branch-mispredict, large instruction footprint, DSB-friendly tight-loop, MITE-heavy decode, and microcoded-instruction workloads. Validation should compare event behavior against expected frontend stress patterns and review errata for the tested stepping.
