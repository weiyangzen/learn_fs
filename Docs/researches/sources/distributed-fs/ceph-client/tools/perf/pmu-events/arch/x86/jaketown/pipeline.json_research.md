# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/jaketown/pipeline.json

## Purpose

This file is the main Jaketown core pipeline PMU event table. It contains 127 event records for execution, retirement, branch behavior, allocation/issue/dispatch, stall cycles, load blocking, resource pressure, clock cycles, and fixed counters. It supplies the raw hardware events behind many top-down and low-level performance investigations on Sandy Bridge-EP.

The file is static PMU metadata. It does not implement pipeline analysis itself; it exposes the event encodings that perf and generated metric formulas can use.

## Important APIs, Types, And Data Contracts

The JSON array uses the standard perf PMU event schema: `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, `PublicDescription`, plus modifiers such as `CounterMask`, `EdgeDetect`, `Invert`, `AnyThread`, and `PEBS`.

Major event families and counts are:

- Branch execution and retirement: `BR_INST_EXEC` 13, `BR_INST_RETIRED` 8, `BR_MISP_EXEC` 11, `BR_MISP_RETIRED` 6.
- Clock and instruction retirement: `CPU_CLK_THREAD_UNHALTED` 3, `CPU_CLK_UNHALTED` 8, `INST_RETIRED` 3.
- Pipeline activity and stalls: `CYCLE_ACTIVITY` 5, `ILD_STALL` 2, `INT_MISC` 4, `RESOURCE_STALLS` 8, `RESOURCE_STALLS2` 4, `RS_EVENTS` 2.
- Load and memory pipeline blocking: `LD_BLOCKS` 4, `LD_BLOCKS_PARTIAL` 2, `LOAD_HIT_PRE` 2.
- Uop flow: `UOPS_DISPATCHED` 2, `UOPS_DISPATCHED_PORT` 12, `UOPS_EXECUTED` 5, `UOPS_ISSUED` 3, `UOPS_RETIRED` 5.
- Other execution details: `AGU_BYPASS_CANCEL`, `ARITH`, `LSD`, `MACHINE_CLEARS`, `PARTIAL_RAT_STALLS`, `ROB_MISC_EVENTS`, and `OTHER_ASSISTS`.

Fixed-counter records such as `INST_RETIRED.ANY`, `CPU_CLK_UNHALTED.THREAD`, and `CPU_CLK_UNHALTED.REF_TSC` use `Counter: "Fixed counter N"` instead of an `EventCode`-only programmable-counter contract. PEBS flags appear on several retired branch/uop/instruction events.

## Control Flow And Generation Behavior

`jevents.py` reads this file during the Jaketown leaf directory pass, infers topic `pipeline`, and constructs generated event rows. It lowercases event names, converts event encodings and modifiers into perf config strings, and appends precision notes to descriptions when `PEBS` is set.

Modifier fields are especially important in this file. `AnyThread` becomes `any=`, `CounterMask` becomes `cmask=`, `EdgeDetect` becomes `edge=`, and `Invert` becomes `inv=`. These fields distinguish raw event counts from cycle-threshold, transition, or inverted stall-cycle events. For example, `RS_EVENTS.EMPTY_END` uses edge detection plus inversion, and `UOPS_EXECUTED.CORE_CYCLES_NONE` uses inversion to count cycles with no uops.

At runtime, perf event selection follows the generated table. The kernel PMU programs programmable or fixed counters, applies PEBS where available, and enforces counter constraints.

## State And Persistence

This file has no mutable state. Its durable state is the checked-in PMU event schema. Runtime state consists of hardware counters and sampling buffers during perf sessions.

Several records encode scheduling constraints as state-like metadata: fixed-counter-only events cannot be freely assigned to generic PMCs, counter-specific events such as `CYCLE_ACTIVITY.CYCLES_L1D_PENDING` use counter 2, and PEBS events require precise sampling support. `AnyThread` entries aggregate at physical-core scope rather than logical-thread scope.

## Dependencies And Integration Points

Dependencies include the perf PMU event generator, generated x86 PMU tables, Intel Jaketown raw PMU semantics, and perf user interfaces. The file is a key integration point for top-down analysis and ratios generated elsewhere: retirement slots, branch mispredicts, uop dispatch/issue/retire, frontend stalls, and backend resource stalls all come from this table.

It complements `memory.json` for memory-ordering and offcore events. Some families overlap by name, such as `MACHINE_CLEARS`, but with different subevents and analysis purposes.

## Risks And Edge Cases

Pipeline events are easy to misuse because similar names can mean speculative execution, retired execution, cycles, or occurrences. `BR_INST_EXEC` and `BR_INST_RETIRED` are not interchangeable. `UOPS_RETIRED.ALL`, `UOPS_RETIRED.RETIRE_SLOTS`, and inverted stall-cycle forms measure different quantities.

Counter masks and inversion are high-risk encoding fields. Dropping `cmask`, `edge`, or `inv` yields syntactically valid but semantically wrong events. Fixed counter descriptions mention dedicated counters; if generated scheduling metadata ignores that, perf may fail to open the event or report confusing multiplexing.

Some descriptions are truncated or contain typographical errors, for example the first `AGU_BYPASS_CANCEL.COUNT` description ends mid-sentence. Documentation cleanup must avoid changing event encodings.

## Test Signals

Static validation should include JSON syntax, schema checks for required event fields, and generated-table inspection for representative modifiers: `arith.fpu_div` with `edge=1,cmask=1`, `rs_events.empty_end` with `edge=1,inv=1`, `cpu_clk_unhalted.thread_any` with `any=1`, and PEBS metadata for retired branch/uop events.

Runtime smoke tests on compatible hardware can run `perf stat` with `inst_retired.any`, `cpu_clk_unhalted.thread`, `br_misp_retired.all_branches`, `uops_retired.retire_slots`, and `resource_stalls.any`. More focused tests should compare branch-heavy, divide-heavy, and memory-stall microbenchmarks to ensure the expected event families move in the expected direction.
