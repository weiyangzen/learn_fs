# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/silvermont/pipeline.json

## Purpose
Defines Silvermont pipeline, branch-retirement, clock, instruction-retirement, divider, machine-clear, allocation-stall, reservation-station-stall, and retired-uop aliases for perf. The 34-entry JSON array provides the core PMU vocabulary for high-level pipeline accounting and branch-misprediction analysis.

## Important APIs, Types, And Event Groups
The file uses perf's core event schema with `EventName`, `EventCode`, `UMask`, `BriefDescription`, `PublicDescription`, `SampleAfterValue`, and optional `PEBS`. Some fixed-counter aliases omit `EventCode` and use `UMask` values that identify fixed counter slots, such as `INST_RETIRED.ANY`, `CPU_CLK_UNHALTED.CORE`, and `CPU_CLK_UNHALTED.REF_TSC`. Programmable aliases include branch retired/mispredicted families, divider busy cycles, machine clears, no-allocation cycles, reservation-station full stalls, and retired uops.

Important groups are `BR_INST_RETIRED.*`, `BR_MISP_RETIRED.*`, `CPU_CLK_UNHALTED.*`, `INST_RETIRED.*`, `CYCLES_DIV_BUSY.ALL`, `MACHINE_CLEARS.*`, `NO_ALLOC_CYCLES.*`, `RS_FULL_STALL.*`, and `UOPS_RETIRED.*`. Several retired branch and instruction events are marked `PEBS`, enabling precise sampling where supported.

## Control Flow
Perf parses the JSON into generated alias rows. At runtime, fixed-counter aliases route to fixed PMU counters while programmable aliases consume one of Silvermont's limited generic counters. PEBS-marked events may enter perf's precise sampling path. Analysis flow generally starts with cycles and instructions, then branches into branch mispredicts, allocation starvation, reservation-station fullness, divider pressure, machine clears, or uop retirement depending on bottleneck symptoms.

## State And Persistence
The JSON persists static event metadata. Runtime state is held by fixed counters, generic counters, PEBS buffers when sampling, and perf event contexts. Because `counter.json` declares only two generic counters, many combinations from this file cannot be measured simultaneously without multiplexing.

## Dependencies And Integration Points
This file depends on Silvermont core PMU support and integrates directly with `counter.json` for fixed/generic counter capacity. It also connects to `frontend.json` for branch-address and decode causes, `memory.json` and `floating-point.json` for machine-clear subcauses, and cache/virtual-memory files for memory-side bottleneck attribution.

## Risks
Fixed-counter aliases are structurally different from normal event-code aliases, so schema handling must preserve entries with missing `EventCode`. Aggregate and component relationships create double-counting hazards, such as all branches versus taken/JCC/call/return classes or all no-allocation cycles versus specific causes. Some descriptions are truncated or terse, so hardware documentation may be needed for exact semantics. PEBS flags must be accurate because false precision support can break sampling expectations.

## Test Signals
Tests include JSON validation, generated event table builds, and `perf list` inspection. Runtime smoke tests should open fixed counters, one branch retired event, one branch-mispredicted event, a no-allocation event, an RS-full event, and a PEBS-capable retired event. Multiplexing behavior should be checked when more than two programmable events are requested.
