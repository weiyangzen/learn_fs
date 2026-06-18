# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwell/pipeline.json

## Purpose

`pipeline.json` defines 137 Broadwell core PMU events for execution pipeline analysis. It covers branch execution and retirement, branch mispredicts, core and reference cycles, cycle activity and stalls, instruction retirement, allocation/issue/retirement uops, port utilization, resource stalls, machine clears, move elimination, load blocking, loop stream detector activity, and floating-point divide activity.

## Important APIs, Types, and Data Fields

The file is a JSON event array. Common fields include `EventName`, `EventCode`, `UMask`, `Counter`, `CounterMask`, `Invert`, `AnyThread`, `PEBS`, `SampleAfterValue`, `BriefDescription`, and `PublicDescription`. Event families include `BR_INST_EXEC`, `BR_INST_RETIRED`, `BR_MISP_EXEC`, `BR_MISP_RETIRED`, `CPU_CLK_THREAD_UNHALTED`, `CPU_CLK_UNHALTED`, `CYCLE_ACTIVITY`, `INST_RETIRED`, `UOPS_EXECUTED`, `UOPS_EXECUTED_PORT`, `UOPS_DISPATCHED_PORT`, `UOPS_ISSUED`, `UOPS_RETIRED`, `RESOURCE_STALLS`, `RS_EVENTS`, `MACHINE_CLEARS`, `LD_BLOCKS`, `LSD`, `MOVE_ELIMINATION`, `INT_MISC`, and `ARITH`.

Several rows expose fixed counters, such as `CPU_CLK_UNHALTED.THREAD`, `CPU_CLK_UNHALTED.REF_TSC`, and retired-instruction variants. Many top-down style rows use `CounterMask` to count cycles meeting a threshold, for example `UOPS_EXECUTED.CORE_CYCLES_GE_*` and `CYCLE_ACTIVITY.STALLS_*`.

## Control Flow and Data Flow

The file has no executable branches. Perf's event generator transforms these rows into lookup data. Runtime control is driven by user selection of events: branch rows configure branch event-select/umask pairs, cycle rows may select fixed or programmable counters, and uop/stall rows use counter masks and sometimes inversion to measure cycle occupancy. Results feed top-down analysis, low-level pipeline bottleneck diagnosis, and direct `perf stat` ratios.

## State and Persistence Behavior

The file persists hardware encodings and sampling defaults. It stores no live pipeline state. Generated tables preserve enough metadata for perf to select fixed counters, programmable counters, PEBS-capable events, any-thread variants, and event constraints.

## Dependencies and Integration Points

The catalog depends on Broadwell core PMU behavior, Hyper-Threading semantics for `AnyThread` events, fixed-counter availability, and PEBS support for precise retired branch/instruction events. It integrates with perf's generated PMU tables, top-down metric groups, `perf stat` ratio calculations, `perf record` sampling, and tests that parse all metric groups or expand PMU event names.

## Risks and Edge Cases

Counter constraints are a key risk: some events are tied to fixed counters or a subset of programmable counters, and some `CYCLE_ACTIVITY` events specifically require counter `2`. Incorrect `CounterMask` or `Invert` values change the event's unit from occurrence count to cycle threshold logic. `AnyThread` rows count activity from either logical thread on a physical core and are not interchangeable with per-thread rows. Branch execution events and retired branch events answer different questions; mixing them in metrics can produce misleading rates.

## Test Signals

Test signals include JSON parse success, generated table build success, `perf list` visibility for representative branch, cycle, uop, and stall rows, and `perf stat` acceptance of fixed-counter and programmable-counter rows. Sanity workloads should show retired instructions and unhalted cycles increasing on CPU-bound loops, branch mispredict events increasing on unpredictable branches, and port/uop counters moving during arithmetic-heavy loops.
