<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswellx/pipeline.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswellx/pipeline.json

## Purpose

`pipeline.json` defines 130 Haswell-X core PMU events for instruction retirement, branches and mispredictions, cycles, frontend and backend stalls, machine clears, move elimination, load blocking, loop stream detector activity, resource stalls, reservation station behavior, uop issue/execute/retire accounting, and execution port usage. These aliases are the core raw inputs for top-down analysis in `hsx-metrics.json`.

The file uses the standard perf PMU event JSON array schema. Records include `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, and optional fields such as `CounterMask`, `Invert`, `AnyThread`, `EdgeDetect`, `PEBS`, `Errata`, `BriefDescription`, and `PublicDescription`.

## Important event families

Branch events include executed and retired branch counts (`BR_INST_EXEC.*`, `BR_INST_RETIRED.*`) plus misprediction counts (`BR_MISP_EXEC.*`, `BR_MISP_RETIRED.*`). These feed bad speculation, branch resteer, and branch misprediction metrics.

Cycle and instruction events include fixed/general counter aliases such as `CPU_CLK_UNHALTED.THREAD`, `CPU_CLK_UNHALTED.THREAD_P`, `CPU_CLK_THREAD_UNHALTED.ONE_THREAD_ACTIVE`, `CPU_CLK_UNHALTED.REF_TSC`, `CPU_CLK_UNHALTED.REF_XCLK`, `INST_RETIRED.ANY`, `INST_RETIRED.ANY_P`, and `INST_RETIRED.PREC_DIST`. These are foundational for CPI, IPC, frequency, utilization, and multiplexing metrics.

Pipeline stall families include `CYCLE_ACTIVITY.CYCLES_L1D_PENDING`, `CYCLES_L2_PENDING`, `CYCLES_LDM_PENDING`, `CYCLES_NO_EXECUTE`, and matching `STALLS_*` events; `RESOURCE_STALLS.ANY`, `ROB`, `RS`, and `SB`; `ILD_STALL.IQ_FULL` and `ILD_STALL.LCP`; `LD_BLOCKS.NO_SR`, `LD_BLOCKS.STORE_FORWARD`, and `LD_BLOCKS_PARTIAL.ADDRESS_ALIAS`.

Uop accounting is extensive: `UOPS_ISSUED.*`, `UOPS_EXECUTED.*`, `UOPS_EXECUTED_PORT.PORT_0` through `PORT_7` and `_CORE` variants, `UOPS_DISPATCHED_PORT.PORT_0` through `PORT_7`, and `UOPS_RETIRED.ALL`, `RETIRE_SLOTS`, `STALL_CYCLES`, `CORE_STALL_CYCLES`, and `TOTAL_CYCLES`. These drive TMA retiring, backend, core-bound, port-utilization, and stalls calculations.

Other important families include `ARITH.DIVIDER_UOPS`, `LSD.CYCLES_4_UOPS`, `LSD.CYCLES_ACTIVE`, `LSD.UOPS`, `MACHINE_CLEARS.COUNT`, `CYCLES`, `MASKMOV`, `SMC`, `MOVE_ELIMINATION.*`, `OTHER_ASSISTS.ANY_WB_ASSIST`, `ROB_MISC_EVENTS.LBR_INSERTS`, and `RS_EVENTS.EMPTY_*`.

## Control flow and evaluation model

There is no imperative control flow in the file. Perf parses each event alias into PMU event selector fields and schedules requested events on fixed or programmable counters. Fields such as `CounterMask`, `Invert`, `AnyThread`, `EdgeDetect`, and `PEBS` alter the low-level event selection and sampling behavior.

Some aliases intentionally describe cycle-qualified counts rather than simple event occurrences. For example, `CYCLE_ACTIVITY.CYCLES_NO_EXECUTE` uses `CounterMask: 4`, and `UOPS_RETIRED.TOTAL_CYCLES` uses `CounterMask: 16` with `Invert: 1`. These encodings are consumed directly by metric formulas and must preserve their exact semantics.

## State and persistence behavior

The file persists static event metadata. Runtime state is counter allocation, fixed-counter availability, any-thread counting mode, PEBS configuration, sampling period, and multiplexing handled by perf and the kernel PMU driver. `SampleAfterValue` values provide defaults for profiling and do not represent accumulated state in the source tree.

## Dependencies and integration points

This is the main raw-event dependency for `hsx-metrics.json` top-down formulas. Examples include `IDQ_UOPS_NOT_DELIVERED.CORE` as a frontend-bound input, `UOPS_RETIRED.RETIRE_SLOTS` for retiring, `UOPS_ISSUED.ANY` and branch misprediction events for bad speculation, cycle activity and resource stalls for memory/core bound, and port events for port utilization.

It integrates with `metricgroups.json` indirectly through the metrics that consume these event names. It also depends on perf's x86 PMU generator understanding fixed counters, programmable counters, PEBS flags, errata fields, and event modifiers.

## Risks and maintenance notes

This file has high blast radius because many TMA and summary metrics rely on exact event names and semantics. Renaming an event alias breaks metric expressions. Changing `CounterMask`, `Invert`, `AnyThread`, or fixed-counter metadata can silently change measurements even if JSON parsing succeeds.

Errata annotations such as `HSD11`, `HSD135`, and `HSD140` indicate known hardware caveats. Tests and documentation should avoid treating affected events as universally precise. Fixed-counter aliases and `_ANY` variants require careful scheduling because they may count per-thread or any-thread cycles differently.

The event list includes many related names with similar encodings, such as `UOPS_EXECUTED_PORT.*` and `UOPS_DISPATCHED_PORT.*`; maintenance mistakes are easy to miss without cross-checking against Intel event tables.

## Test signals

Validation should include JSON parsing, perf PMU table generation, `perf list` visibility for representative branch, cycle, stall, uop, and port aliases, and expression resolution for top-down metrics in `hsx-metrics.json`. Hardware smoke tests should exercise `perf stat -e cycles,instructions,UOPS_RETIRED.RETIRE_SLOTS,BR_MISP_RETIRED.ALL_BRANCHES` and `perf stat -M TopdownL1` on matching Haswell-X systems. Parser tests should specifically assert preservation of `CounterMask`, `Invert`, `AnyThread`, fixed-counter names, PEBS flags, and errata metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswellx/pipeline.json -->
