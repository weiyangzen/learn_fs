# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/tigerlake/pipeline.json

## Purpose
`pipeline.json` defines 96 Tiger Lake core PMU events for execution pipeline behavior. It covers arithmetic divider use, assists, retired branch and mispredict classes, unhalted cycles, cycle activity stalls, execution port utilization, instruction decode/retirement, recovery cycles, load/store blocking, LSD activity, machine clears, resource stalls, reservation-station empty cycles, topdown slots, uops decoded/dispatched/executed/issued/retired, and fixed-counter architectural events.

## Important APIs, Types, and Fields
The event array uses `EventName`, `EventCode`, `UMask`, `Counter`, `BriefDescription`, `PublicDescription`, and `SampleAfterValue`. Several records add `CounterMask`, `EdgeDetect`, and `Invert`. Fixed-counter events include `INST_RETIRED.ANY`, `INST_RETIRED.PREC_DIST`, `CPU_CLK_UNHALTED.THREAD`, and `CPU_CLK_UNHALTED.REF_TSC`; programmable counterparts include `INST_RETIRED.ANY_P` and `CPU_CLK_UNHALTED.THREAD_P`. Topdown events include `TOPDOWN.SLOTS`, `TOPDOWN.SLOTS_P`, and `TOPDOWN.BACKEND_BOUND_SLOTS`. Port utilization events encode dispatch to port groups such as `PORT_0`, `PORT_2_3`, and `PORT_7_8`.

## Control Flow and Data Flow
Perf builds these records into Tiger Lake core event tables. Runtime event resolution programs fixed or generic counters depending on the `Counter` field. Data flows from core pipeline structures to counters that represent retired instruction classes, cycles meeting a stall condition, edge-detected clears, uop movement between pipeline stages, and topdown slot accounting.

## State and Persistence Behavior
The JSON is immutable metadata. Runtime state lives in PMU counters and optional perf data. Fixed-counter events preserve generic counters for other events; using programmable aliases can change scheduling pressure. Inverted counter-mask events such as `UOPS_EXECUTED.STALL_CYCLES`, `UOPS_ISSUED.STALL_CYCLES`, and `UOPS_RETIRED.STALL_CYCLES` count cycles where the condition is not met, so users must interpret them carefully.

## Dependencies and Integration Points
The file depends on Tiger Lake core PMU encodings and perf support for fixed counters, topdown slots, counter masks, edge detection, and inverted comparisons. It integrates heavily with Tiger Lake metric groups for `Pipeline`, `Retire`, `BadSpec`, `Backend`, `PortsUtil`, `Branches`, `MachineClears`, `LSD`, and topdown TMA categories. It also pairs with `frontend.json` and `memory.json` to explain whether pipeline stalls are frontend-, backend-, memory-, branch-, or recovery-driven.

## Risks and Edge Cases
Counter-mask and invert semantics are easy to misread as simple event counts. Fixed and programmable aliases for instructions and cycles can double-count if used together without intent. Some branch and recovery events count retired outcomes while others count cycles or edge transitions, so derived rates need compatible denominators. Topdown slot events are foundational for metric formulas; incorrect encodings would cascade into many derived metrics. Events with broad names such as `ASSISTS.ANY` or `RESOURCE_STALLS.SCOREBOARD` require hardware documentation for precise interpretation.

## Test Signals
Run JSON syntax validation and perf event-table generation. On Tiger Lake, `perf list` should show fixed-counter, topdown, branch, port, and uop events from this file. Runtime tests should compare `INST_RETIRED.ANY` versus `INST_RETIRED.ANY_P`, fixed and programmable cycle events, and topdown slot metrics. Branch-heavy, divide-heavy, memory-stall, and port-pressure microbenchmarks can validate that representative families move in expected directions.
