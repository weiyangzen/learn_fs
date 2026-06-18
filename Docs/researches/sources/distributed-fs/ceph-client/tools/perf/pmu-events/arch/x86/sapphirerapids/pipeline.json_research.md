# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sapphirerapids/pipeline.json

## Purpose
`pipeline.json` defines 124 Sapphire Rapids core PMU events for general pipeline analysis: arithmetic divider activity, assists, branch retirement and misprediction, unhalted clocks, cycle activity, execution port utilization, instruction/uop retirement, machine clears, vector integer instructions, load blocks, LSD, resource stalls, reservation station empty states, top-down slots, dispatched/executed/issued/retired uops, and AMX busy time.

## Important APIs, types, and schema fields
Rows use standard perf event fields plus modifier fields `CounterMask`, `EdgeDetect`, `Invert`, `Deprecated`, `MSRIndex`, and `MSRValue`. Fixed-counter events are present: `CPU_CLK_UNHALTED.THREAD` uses fixed counter 1, `CPU_CLK_UNHALTED.REF_TSC` fixed counter 2, and `TOPDOWN.SLOTS` fixed counter 3. General-counter variants such as `CPU_CLK_UNHALTED.THREAD_P`, `REF_TSC_P`, and `TOPDOWN.SLOTS_P` are also defined. Several cycle events use counter masks and inversion to distinguish busy, idle, or stall cycles.

## Control flow and integration
Perf's generator compiles the event records; runtime event lookup maps names to raw event select/umask/fixed counter encodings. These events are foundational for `perf stat`, top-down analysis, IPC/uop metrics, branch diagnostics, and execution-port studies. `UOPS_RETIRED.MS` and `INT_MISC.UNKNOWN_BRANCH_CYCLES` use MSR `0x3F7` filters, while topdown and CPU clock fixed counters depend on architectural PMU support.

## State and persistence behavior
The file persists the core pipeline event vocabulary and raw encodings. Measurement state is in core PMU counters, fixed counters, and extra MSRs at runtime. Deprecated rows preserve compatibility: `ARITH.DIVIDER_ACTIVE`, `ARITH.FP_DIVIDER_ACTIVE`, `ARITH.INT_DIVIDER_ACTIVE`, `RS_EMPTY.COUNT`, `RS_EMPTY.CYCLES`, `UOPS_EXECUTED.STALL_CYCLES`, and `UOPS_RETIRED.STALL_CYCLES` point to replacement names.

## Dependencies
Dependencies include the Sapphire Rapids PMU programming model, architectural fixed counters, perf's top-down metric code, metric group taxonomy, and sibling files for memory/frontend/floating-point details. `counter.json` supplies the core counter capacity that makes fixed versus generic event scheduling meaningful. This file integrates with broad metric groups such as `Pipeline`, `Branches`, `Retire`, `PortsUtil`, `TopdownL1`, `Backend`, `BadSpec`, and many `tma_*` categories.

## Risks and edge cases
Pipeline events are heavily reused by metrics, so renaming or changing encodings has broad blast radius. Fixed-counter rows have different shape from generic events and can be broken by validators that require `EventCode`. Deprecated aliases must stay present until intentionally removed because scripts may depend on them. Counter masks and inversion fields materially change cycle semantics for stall/empty/threshold events. Top-down slot events must remain consistent with perf's metric formulas, or high-level TMA percentages become wrong while raw counts still look valid.

## Test signals
Static validation should parse JSON, generate PMU tables, check deprecated replacement text, verify fixed-counter rows, and ensure alias/replacement encodings remain coherent. Runtime validation should include `perf stat` smoke tests for cycles, instructions, topdown slots, branch events, uop dispatch ports, divider loops, AMX workloads where available, and branch-mispredict microbenchmarks. Perf metric tests should cover top-down formulas that consume `TOPDOWN.*`, `UOPS_*`, `CPU_CLK_UNHALTED.*`, branch, and machine-clear events.
