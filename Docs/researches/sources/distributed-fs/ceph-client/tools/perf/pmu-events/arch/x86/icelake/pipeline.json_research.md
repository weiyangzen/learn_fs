# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelake/pipeline.json

## Purpose

This file is the Ice Lake client pipeline-event catalog for perf. It contains 95 core PMU event records covering arithmetic divider activity, assists, retired branches and mispredictions, CPU clocks, memory-stall cycle activity, execution activity, decode/retire events, recovery cycles, load blocks, loop stream detector activity, machine clears, resource stalls, reservation-station emptiness, top-down slots, uop decode/dispatch/execute/issue/retire behavior, and related pipeline bottleneck signals.

## Important APIs, Types, And Data

Records use the standard event schema with `EventName`, `EventCode`, `UMask`, `Counter`, `CounterMask`, `EdgeDetect`, `SampleAfterValue`, `BriefDescription`, and `PublicDescription`. Major families include `ARITH`, `ASSISTS`, `BR_INST_RETIRED`, `BR_MISP_RETIRED`, `CPU_CLK_UNHALTED`, `CYCLE_ACTIVITY`, `EXE_ACTIVITY`, `ILD_STALL`, `INST_DECODED`, `INST_RETIRED`, `INT_MISC`, `LD_BLOCKS`, `LD_BLOCKS_PARTIAL`, `LOAD_HIT_PREFETCH`, `LSD`, `MACHINE_CLEARS`, `MISC_RETIRED`, `RESOURCE_STALLS`, `RS_EVENTS`, `TOPDOWN`, `UOPS_DECODED`, `UOPS_DISPATCHED`, `UOPS_EXECUTED`, `UOPS_ISSUED`, and `UOPS_RETIRED`.

Important qualifier fields are common. `CounterMask` turns many events into cycle-threshold measurements, for example `CYCLE_ACTIVITY.*`, `LSD.CYCLES_*`, `UOPS_EXECUTED.CYCLES_GE_*`, and `UOPS_RETIRED.TOTAL_CYCLES`. `EdgeDetect` marks transition/count events such as `INT_MISC.CLEARS_COUNT`, `MACHINE_CLEARS.COUNT`, and `RS_EVENTS.EMPTY_END`. Top-down events provide slot-level inputs via `TOPDOWN.SLOTS`, `TOPDOWN.SLOTS_P`, and `TOPDOWN.BACKEND_BOUND_SLOTS`.

## Control Flow

At build time, the perf PMU event generator reads this JSON, validates and normalizes the event records, lowercases aliases, and emits the generated Ice Lake pipeline event table. Runtime perf uses those generated aliases for direct event selection and as dependencies for derived metrics. Metric expansion in `perf stat -M` draws heavily from this file for top-down, branch, bad-speculation, backend, retiring, port-utilization, divider, and instruction-mix formulas.

## State And Persistence Behavior

The file persists static hardware encoding metadata and default sampling periods. Runtime pipeline state, branch predictor state, uop queues, reservation stations, and counter values live in hardware and perf file descriptors only while a measurement is active. Generated aliases preserve semantic qualifiers such as `cmask` and `edge`, but no measured values are stored.

## Dependencies And Integration Points

This file integrates with `icl-metrics.json` more heavily than any other raw catalog in this work item. Metrics reference `BR_INST_RETIRED.*`, `BR_MISP_RETIRED.*`, `CPU_CLK_UNHALTED.*`, `CYCLE_ACTIVITY.*`, `EXE_ACTIVITY.*`, `INST_RETIRED.*`, `INT_MISC.*`, `LD_BLOCKS*`, `MACHINE_CLEARS.*`, `RS_EVENTS.*`, `TOPDOWN.*`, and many `UOPS_*` events. It also integrates with `jevents.py`, generated `pmu-events.c`, `perf list`, `perf stat`, and top-down documentation/metric tests.

## Risks And Edge Cases

Pipeline event semantics are easy to corrupt because the same base selector can represent occurrences, cycles, slots, or thresholded cycles depending on umask/cmask/edge fields. Top-down slot metrics must remain consistent with Ice Lake's pipeline width and perf's top-down event handling. Branch and machine-clear metrics feed several higher-level formulas, so a small encoding mistake can distort many derived bottleneck categories. Counter availability also matters: many entries list only programmable counters `0,1,2,3`, while others include fixed or wider counter sets; changing those fields can make scheduling fail or overconstrain perf.

## Test Signals

Use `jq empty pipeline.json`, run `jevents.py` generation, and run `perf test pmu-events` plus metric parser tests. `perf list` should expose representative aliases such as `topdown.slots`, `br_misp_retired.all_branches`, `uops_dispatched.port_0`, `cycle_activity.stalls_mem_any`, and `int_misc.clear_resteer_cycles`. Runtime tests should include branch-misprediction, divider-heavy, memory-stall, and uop-throughput workloads, plus `perf stat -M TopdownL1,TopdownL2,Pipeline,PortsUtil`.
