# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylakex/pipeline.json

## Purpose

`pipeline.json` is the Skylake Server PMU manifest for core pipeline, branch, clock, retirement, execution, dispatch, resource-stall, machine-clear, and uop events. It defines 102 aliases under the `pipeline` topic.

The file gives perf symbolic names for low-level pipeline analysis counters, including top-down support events used to distinguish retiring, bad speculation, front-end/back-end stalls, port utilization, branch behavior, LSD activity, and recovery cycles.

## Important Schema, APIs, and Event Families

The schema is the standard PMU event-array schema. Besides `EventName`, `EventCode`, `UMask`, `Counter`, descriptions, and sampling period, this file uses:

- `CounterMask` for thresholded cycle events and utilization bands.
- `Invert` and `EdgeDetect` for specialized counting semantics.
- `AnyThread` for aliases that count across sibling SMT threads, such as `CPU_CLK_UNHALTED.THREAD_ANY`.
- `PEBS` for precise retired branch and instruction events.
- `Errata`, especially `SKL091` and `SKL044`, on retired branch and instruction aliases.

Important families are:

- `BR_INST_RETIRED.*`, `BR_MISP_EXEC.*`, and `BR_MISP_RETIRED.*` for branch volume and misprediction categories.
- `CPU_CLK_THREAD_UNHALTED.*` and `CPU_CLK_UNHALTED.*` for reference and thread cycles.
- `CYCLE_ACTIVITY.*` for L1D, L2, and memory-related cycles and stalls.
- `EXE_ACTIVITY.*`, `UOPS_DISPATCHED_PORT.PORT_{0..7}`, and `UOPS_EXECUTED.*` for execution port and uop utilization.
- `INST_RETIRED.*`, `UOPS_ISSUED.*`, and `UOPS_RETIRED.*` for retirement, issue, and stall-cycle views.
- `INT_MISC.*`, `MACHINE_CLEARS.*`, and `OTHER_ASSISTS.ANY` for recovery, clears, and assists.
- `LD_BLOCKS.*`, `LD_BLOCKS_PARTIAL.ADDRESS_ALIAS`, and `LOAD_HIT_PRE.SW_PF` for load/store pipeline hazards.
- `LSD.*`, `RS_EVENTS.*`, `ROB_MISC_EVENTS.*`, and `RESOURCE_STALLS.*` for loop stream detector, reservation station, reorder buffer, and resource pressure signals.

## Control Flow and Integration

`jevents.py` loads the 102 JSON objects into `JsonEvent` instances, derives topic `pipeline`, converts event fields into perf event selector strings, and emits them into the SkylakeX generated C table. The runtime integration is standard perf alias lookup for the CPU model. Aliases with `AnyThread` become event strings containing `any=1`; aliases with `CounterMask` become `cmask=` constraints; PEBS aliases receive precise-event description notes.

This file overlaps analytically with `frontend.json` and `memory.json` but uses a broader pipeline topic. For example, `ILD_STALL.LCP` complements `DECODE.LCP`, `CYCLE_ACTIVITY.*` appears in both pipeline and memory contexts with different miss levels, and machine-clear events are split between generic clears here and memory-ordering clears in `memory.json`.

## State and Persistence Behavior

The file is static source data. Generated alias entries are persisted in perf's compiled PMU tables. Runtime state is PMU counter programming and perf sampling output. Default sample periods are part of the generated alias definitions, with many high-volume events using periods such as `2000003` and precise retired events often using `100003` or related values.

## Dependencies

Dependencies include:

- Skylake Server PMU encodings for core pipeline events.
- `jevents.py` support for `AnyThread`, `CounterMask`, `EdgeDetect`, `Invert`, `PEBS`, and errata description annotations.
- perf event parsing and PMU alias matching.
- Kernel/hardware support for precise retired events and any-thread counting.

## Risks and Edge Cases

Many aliases share event codes and are differentiated only by umask, cmask, invert, or edge settings. Examples include `UOPS_EXECUTED.*` on `0xB1`, `UOPS_DISPATCHED_PORT.*` on `0xA1`, `BR_INST_RETIRED.*` on `0xC4`, `BR_MISP_RETIRED.*` on `0xC5`, and `CYCLE_ACTIVITY.*` on `0xA3`. Small field changes can produce valid but semantically wrong aliases.

Errata annotations are user-visible and meaningful. Removing `SKL091` or `SKL044` from retired instruction/branch events would hide known caveats. Conversely, changing only errata text affects descriptions, not counter programming.

Some aliases have overlapping or compatibility names, such as `BR_INST_RETIRED.COND` and `BR_INST_RETIRED.CONDITIONAL`, or `CPU_CLK_UNHALTED.THREAD` and `CPU_CLK_UNHALTED.THREAD_P`. These should be treated as compatibility surface rather than obvious duplication.

Any-thread aliases can behave differently under SMT and may not be comparable to per-thread aliases in scripts unless the selector semantics are understood.

## Test Signals

Useful checks are:

- `jq empty pipeline.json`.
- Generated perf build and `perf list pipeline` inspection.
- `perf stat -e cycles,instructions,uops_retired.retire_slots,br_misp_retired.all_branches <workload>` on SkylakeX hardware.
- Targeted tests for `any=1`, `cmask=`, `edge=`, and `inv=` generated event strings.
- Existing PMU event table tests in `tools/perf/tests/pmu-events.c`, plus hardware smoke tests for PEBS branch/instruction aliases.
