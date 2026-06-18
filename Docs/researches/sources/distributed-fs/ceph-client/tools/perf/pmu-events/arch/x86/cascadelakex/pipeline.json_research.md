# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/cascadelakex/pipeline.json

## Purpose

`sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/cascadelakex/pipeline.json` defines Cascade Lake X core PMU events for execution pipeline analysis. It covers branch instruction retirement and misprediction, core/reference cycle accounting, cycle activity stalls, execution-port utilization, instruction and uop retirement, machine clears, allocation/resource stalls, loop stream detector activity, load blocking, assists, reservation-station emptiness, and divider activity. The source was read as a complete 953-line JSON array with 102 event objects.

## Important APIs, Types, and Data Fields

This file uses perf's standard PMU event object schema. All rows include `EventName`, `Counter`, `SampleAfterValue`, and `BriefDescription`; most rows include `EventCode` and `UMask`; many include `PublicDescription`. Optional fields exercise important perf parser paths: `CounterMask` appears on threshold/cycle-counting events, `Invert` appears on "no uops" or "less than threshold" forms, `EdgeDetect` appears on transition/end events, `AnyThread` appears on core-wide logical-thread variants, `PEBS` marks precise retired branch events, and `Errata` marks branch-retired rows affected by `SKL091`.

Major event families include `ARITH`, `BR_INST_RETIRED`, `BR_MISP_EXEC`, `BR_MISP_RETIRED`, `CPU_CLK_THREAD_UNHALTED`, `CPU_CLK_UNHALTED`, `CYCLE_ACTIVITY`, `EXE_ACTIVITY`, `ILD_STALL`, `INST_DECODED`, `INST_RETIRED`, `INT_MISC`, `LD_BLOCKS`, `LD_BLOCKS_PARTIAL`, `LOAD_HIT_PRE`, `LSD`, `MACHINE_CLEARS`, `OTHER_ASSISTS`, `PARTIAL_RAT_STALLS`, `RESOURCE_STALLS`, `ROB_MISC_EVENTS`, `RS_EVENTS`, `UOPS_DISPATCHED_PORT`, `UOPS_EXECUTED`, `UOPS_ISSUED`, and `UOPS_RETIRED`.

Fixed-counter rows include `CPU_CLK_UNHALTED.REF_TSC` on fixed counter 2 and `CPU_CLK_UNHALTED.THREAD`/`THREAD_ANY` on fixed counter 1. Programmable rows generally use counters `0,1,2,3`. Port rows `UOPS_DISPATCHED_PORT.PORT_0` through `PORT_7` use event code `0xA1` with one umask per execution port. Threshold rows such as `UOPS_EXECUTED.CORE_CYCLES_GE_1` through `GE_4`, per-thread `CYCLES_GE_*`, `STALL_CYCLES`, and `UOPS_RETIRED.TOTAL_CYCLES` rely on `CounterMask` and sometimes `Invert` to change the hardware condition being counted.

## Control Flow and Data Flow

There is no executable control flow in the JSON itself. Build-time flow runs through `jevents.py`, which lowers each object into a generated event string such as `event=...,umask=...,period=...` plus optional `cmask=`, `inv=`, `edge=`, and `any=` fields. PEBS settings become precision metadata in descriptions and runtime event capability. Errata strings are appended to generated descriptions as specification-update notes.

At runtime, users select these names through `perf stat`, `perf record`, metric formulas, or top-down analysis. Perf resolves the symbolic event name in the Cascade Lake X table, configures the kernel PMU event with the encoded selector and modifiers, and uses the counts to diagnose pipeline bottlenecks. Data flow differs by family: branch rows count retired or speculative branch behavior; cycle rows count unhalted or reference cycles; `CYCLE_ACTIVITY` rows attribute stalls while cache/memory misses are outstanding; port/uop rows measure execution width, issue, and retirement pressure; machine-clear and assist rows expose pipeline flush or microcode-assist causes.

## State and Persistence Behavior

The file persists static event encodings, descriptions, sampling defaults, precision hints, errata annotations, and counter constraints. It does not store live branch, cycle, stall, or uop counts. Runtime state is held by CPU PMU counters and perf event contexts; fixed counters and programmable counters are allocated only while a perf event is active. Any generated metadata persists in perf's compiled PMU tables until the tool is rebuilt.

## Dependencies and Integration Points

The table depends on Cascade Lake X PMU behavior for Intel server cores derived from Skylake/Cascade Lake, including fixed counters, PEBS for precise branch-retired variants, Hyper-Threading semantics for `AnyThread`, and correct interpretation of `CounterMask`, `Invert`, and `EdgeDetect`. It is selected through the x86 mapfile entry for `GenuineIntel-6-55-[56789ABCDEF]`.

Integration points include `tools/perf/pmu-events/jevents.py` for event-string generation, generated `pmu-events.c` and `pmu-events.h` for lookup, `perf list` for display, `perf stat` for direct counts and top-down metric formulas, `perf record` for sampling PEBS-capable rows, and `tools/perf/tests/pmu-events.c` plus shell tests for generated-table validation. The file also supplies raw ingredients for metric groups described by `metricgroups.json`, especially `Pipeline`, `Branches`, `BadSpec`, `PortsUtil`, `Retire`, `Frontend`, and top-down `tma_*` groups.

## Risks and Edge Cases

Counter semantics are easy to misread. `CounterMask` and `Invert` rows often count cycles satisfying a threshold condition rather than raw event occurrences, so using them as numerator/denominator terms without unit awareness can produce invalid metrics. `AnyThread` variants count activity from either logical thread on a physical core and are not interchangeable with per-thread events. Fixed-counter events can schedule differently from programmable events and may interact with kernel/NMI watchdog constraints.

Branch-retired rows marked with errata `SKL091` should be treated carefully in tests and documentation. PEBS rows require precise-event support and may fail or degrade if the kernel, privilege level, or hardware constraints do not allow precise sampling. Execution-port and uop events are low-level microarchitectural signals; port binding, fused uops, macro-fusion, and SMT sharing can make direct source-code attribution misleading. Some rows have aliases or near-duplicates, such as `BR_INST_RETIRED.COND` and `BR_INST_RETIRED.CONDITIONAL`, so metric formulas should choose one spelling consistently.

## Test Signals

Static checks should validate JSON parsing, generated perf build success, and field coverage for optional modifiers (`CounterMask`, `Invert`, `EdgeDetect`, `AnyThread`, `PEBS`, `Errata`). `perf list` should show representative families such as `BR_INST_RETIRED.ALL_BRANCHES`, `CPU_CLK_UNHALTED.THREAD`, `CYCLE_ACTIVITY.STALLS_MEM_ANY`, `UOPS_DISPATCHED_PORT.PORT_0`, and `UOPS_RETIRED.RETIRE_SLOTS`.

Runtime smoke tests on matching hardware should verify `perf stat` accepts a mix of fixed-counter and programmable rows. CPU-bound loops should move `INST_RETIRED.ANY`, `CPU_CLK_UNHALTED.THREAD`, and `UOPS_RETIRED.RETIRE_SLOTS`; unpredictable branches should increase `BR_MISP_RETIRED.*`; memory-latency workloads should affect `CYCLE_ACTIVITY.STALLS_MEM_ANY`; arithmetic kernels should move port/uop and `ARITH.DIVIDER_ACTIVE` counters when applicable. Sampling tests should cover at least one PEBS branch-retired event and report permission or precision failures separately from JSON/generation failures.
