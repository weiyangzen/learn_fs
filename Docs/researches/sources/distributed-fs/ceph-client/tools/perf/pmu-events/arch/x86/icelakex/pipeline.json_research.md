# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelakex/pipeline.json

## Purpose

This file is a perf PMU event table for the Intel Ice Lake Xeon (`icelakex`) x86 architecture. It contributes the pipeline-oriented core event catalog used by Linux perf's `pmu-events` machinery to resolve user-facing symbolic events such as `UOPS_EXECUTED.THREAD`, `CYCLE_ACTIVITY.STALLS_MEM_ANY`, `TOPDOWN.SLOTS`, and `BR_MISP_RETIRED.ALL_BRANCHES` into raw event selectors, umasks, counter constraints, sampling periods, and descriptive text.

The file contains a JSON array of 93 event objects. The events cover arithmetic/divide activity, branch retirement and branch misprediction, unhalted cycles, cycle and execution stalls, decoder and loop-stream-detector delivery, retired instructions/uops, machine clears, resource stalls, topdown slots, execution-port dispatch, and issue/retirement slot behavior. It is data rather than executable code, but its schema is an API contract for perf's event generation and runtime lookup paths.

## Important APIs, Types, and Fields

Each array entry is an event definition consumed by the perf PMU event parser. The effective type is the standard perf JSON event object with these observed fields:

- `EventName`: required symbolic event name. Names are grouped by hardware block prefixes including `ARITH`, `BR_INST_RETIRED`, `BR_MISP_RETIRED`, `CPU_CLK_UNHALTED`, `CYCLE_ACTIVITY`, `EXE_ACTIVITY`, `INT_MISC`, `LSD`, `TOPDOWN`, `UOPS_DISPATCHED`, `UOPS_EXECUTED`, `UOPS_ISSUED`, and `UOPS_RETIRED`.
- `EventCode`: raw event-select value for programmable-counter events, for example `0xc4` for retired branch events and `0xb1` for uop execution events. Fixed-counter-only events omit `EventCode`.
- `UMask`: unit mask combined with `EventCode`. Several architectural/fixed events retain a `UMask` value even though they bind to fixed counters.
- `Counter`: counter placement constraint. Most entries allow programmable counters `0,1,2,3,4,5,6,7`; some front-end/cache-load events are restricted to `0,1,2,3`; five entries use fixed counters.
- `CounterMask`: cmask threshold for cycle-qualified or thresholded events, such as stall cycles, cycles with at least N executed uops, or end-of-empty-RS periods.
- `Invert`: inverts the cmask comparison for stall/no-progress events such as `UOPS_EXECUTED.STALL_CYCLES`, `UOPS_ISSUED.STALL_CYCLES`, and `UOPS_RETIRED.STALL_CYCLES`.
- `EdgeDetect`: converts a condition into edge/count behavior for events such as `INT_MISC.CLEARS_COUNT`, `MACHINE_CLEARS.COUNT`, and `RS_EVENTS.EMPTY_END`.
- `SampleAfterValue`: default sampling period used when the event is selected for sampling.
- `BriefDescription` and `PublicDescription`: short and extended descriptions surfaced by perf tooling and generated documentation.

The fixed-counter definitions are important because they do not consume the same programmable PMU resources as raw events: `INST_RETIRED.ANY` and `INST_RETIRED.PREC_DIST` use fixed counter 0, `CPU_CLK_UNHALTED.THREAD` uses fixed counter 1, `CPU_CLK_UNHALTED.REF_TSC` uses fixed counter 2, and `TOPDOWN.SLOTS` uses fixed counter 3. The file also provides programmable-counter alternatives for several architectural concepts, including `INST_RETIRED.ANY_P`, `CPU_CLK_UNHALTED.THREAD_P`, and `TOPDOWN.SLOTS_P`.

## Event Families

The largest families are pipeline slot and uop movement signals. `UOPS_EXECUTED.*` tracks per-thread and per-core execution occupancy, thresholded cycles with at least one through four uops, no-dispatch stall cycles, x87 uops, and total executed uops. `UOPS_DISPATCHED.PORT_*` maps dispatch activity to Ice Lake Xeon execution-port groups, including combined groups such as ports `2_3`, `4_9`, and `7_8`. `UOPS_ISSUED.*` tracks RAT-to-RS issue volume, issue stalls, and vector-width mismatch blend uops. `UOPS_RETIRED.*` tracks retirement slots and cycles with no or below-threshold retirement.

The branch family is split into retired branch counts and retired misprediction counts. `BR_INST_RETIRED.*` covers all, conditional, taken/not-taken conditional, far, indirect, near call, return, and near taken branches. `BR_MISP_RETIRED.*` mirrors the important misprediction subcases, including conditional, taken/not-taken conditional, indirect, indirect calls, near taken, returns, and all branches.

The cycle and stall families support topdown and bottleneck analysis. `CPU_CLK_UNHALTED.*` provides distributed, reference, thread, and one-thread-active cycle sources. `CYCLE_ACTIVITY.*` separates cycles and execution stalls with outstanding L1D, L2, or memory loads plus total stalls. `EXE_ACTIVITY.*`, `RESOURCE_STALLS.*`, and `RS_EVENTS.*` describe port-utilization density, store-buffer/scoreboard pressure, and reservation-station emptiness. `TOPDOWN.BACKEND_BOUND_SLOTS`, `TOPDOWN.SLOTS`, and `TOPDOWN.SLOTS_P` provide direct Top-down Microarchitecture Analysis slot signals.

Other diagnostic families include divider activity (`ARITH.*`), microcode assists (`ASSISTS.ANY`), length-changing-prefix decode stalls (`ILD_STALL.LCP`), decoder use (`INST_DECODED.DECODERS` and `UOPS_DECODED.DEC0`), loop-stream-detector activity (`LSD.*`), split-load/store-forwarding blocks (`LD_BLOCKS.*` and `LD_BLOCKS_PARTIAL.ADDRESS_ALIAS`), software-prefetch fill-buffer hits (`LOAD_HIT_PREFETCH.SWPF`), machine clears (`MACHINE_CLEARS.*`), LBR updates and retired pause instructions (`MISC_RETIRED.*`), and precise or architectural instruction retirement (`INST_RETIRED.*`).

## Control Flow and Runtime Use

There is no in-file control flow. The control flow is external:

1. Perf's build-time PMU event tooling reads this JSON file as part of the `arch/x86/icelakex` event directory.
2. The event generator validates JSON shape, converts each event object into generated PMU event tables, and preserves symbolic names, descriptions, raw encodings, constraints, and default sampling periods.
3. At runtime, commands such as `perf list`, `perf stat -e EVENT`, `perf record -e EVENT`, and metric expressions from neighboring metric files resolve an `EventName` against the Ice Lake Xeon table selected for the current CPU model.
4. Perf programs the PMU using `EventCode`, `UMask`, `CounterMask`, `Invert`, `EdgeDetect`, and the counter constraint supplied by `Counter`. Fixed-counter events route to their dedicated counters instead of the programmable counter set.
5. Human-readable descriptions flow into event listing/help output, while `SampleAfterValue` influences default sampling behavior when the event is used in sampling mode.

Because the entries are independent, there are no calls between definitions. Coupling appears through shared raw encodings with different `UMask` or qualifier fields, and through external metric expressions that combine these event names into ratios.

## State and Persistence Behavior

The file itself has no mutable runtime state and no persistence layer. Its persistent contract is the checked-in event catalog. Once built into perf, these definitions become part of the generated event database for Ice Lake Xeon systems.

The state that matters operationally is hardware PMU state programmed by perf when a user selects one of these events: counter allocation, fixed versus programmable counter binding, period reloads from `SampleAfterValue`, and qualifier bits for cmask, invert, and edge-detect behavior. Those settings are transient per perf session and are not stored back into this JSON file.

## Dependencies and Integration Points

This file depends on perf's PMU event JSON schema and the x86 PMU backend's interpretation of Intel event selectors, umasks, cmasks, invert bits, edge-detect bits, PEBS/precise distribution features, fixed counters, and counter constraints. It is integrated by location: the `arch/x86/icelakex` directory associates it with the Ice Lake Xeon CPU model selection path.

It is expected to work with adjacent Ice Lake Xeon JSON files that define other event categories and metrics. Metric files can reference event names declared here, especially `TOPDOWN.SLOTS`, `TOPDOWN.SLOTS_P`, `TOPDOWN.BACKEND_BOUND_SLOTS`, `INST_RETIRED.*`, `CPU_CLK_UNHALTED.*`, `UOPS_*`, branch, and cycle-activity events. If a neighboring metric expression references one of these symbolic names, renaming or removing the event will break metric evaluation even though this JSON file remains syntactically valid.

Descriptions also reference external Intel semantics. For example, `INST_RETIRED.PREC_DIST` relies on Precise Distribution of Instructions Retired behavior, `MISC_RETIRED.LBR_INSERTS` requires Last Branch Record enablement, and `LOAD_HIT_PREFETCH.SWPF` warns that some lock instructions may also increment the event. Those are hardware dependencies, not code dependencies.

## Risks and Edge Cases

The main correctness risk is silent semantic drift. A JSON entry can parse cleanly while still programming the wrong hardware event if `EventCode`, `UMask`, `CounterMask`, `Invert`, `EdgeDetect`, or `Counter` does not match Ice Lake Xeon PMU documentation. This is particularly important for thresholded cycle events and inverted stall events, where a one-bit qualifier changes the meaning from progress cycles to no-progress cycles.

Counter constraints are another risk. Events restricted to counters `0,1,2,3` cannot always be scheduled with arbitrary other events. Fixed-counter events reduce programmable-counter pressure but can conflict with other fixed-counter usage. Multiplexing can skew ratios that combine events from different counter classes or scopes.

Naming stability matters because perf users and metric expressions select events by `EventName`. Case variations in `EventCode` values are harmless JSON strings if the parser normalizes numeric text, but event-name spelling is not harmless. The apparent description mismatch for `UOPS_DISPATCHED.PORT_4_9`, whose brief says ports 4 and 9 while the public description says ports 5 and 9, is a documentation-quality risk worth checking against the upstream Intel event source.

Several entries carry caveats that affect interpretation: `CPU_CLK_UNHALTED.REF_TSC` includes overflow-status behavior notes, `MISC_RETIRED.LBR_INSERTS` requires LBR configuration, `MISC_RETIRED.PAUSE_INST` notes lack of support on early Skylake/Kaby Lake products, `LOAD_HIT_PREFETCH.SWPF` may count some lock instructions, and `BR_MISP_RETIRED.RET` is explicitly non-PEBS. These caveats should remain visible because they change how profiling results should be trusted.

## Test Signals

Useful validation starts with schema and generation checks: parse the file with `jq`, ensure all 93 objects have `EventName`, verify that programmable events have an `EventCode`, and run the repository's perf PMU event-table generation or validation target if available.

Runtime smoke signals on an Ice Lake Xeon host include `perf list` showing representative names from each family, `perf stat -e TOPDOWN.SLOTS,INST_RETIRED.ANY,CPU_CLK_UNHALTED.THREAD`, and focused checks for qualifier-heavy events such as `UOPS_EXECUTED.STALL_CYCLES`, `UOPS_RETIRED.TOTAL_CYCLES`, `INT_MISC.CLEARS_COUNT`, and `RS_EVENTS.EMPTY_END`.

Behavioral sanity workloads should exercise different pipeline paths: branch-heavy code for `BR_INST_RETIRED.*` and `BR_MISP_RETIRED.*`, divide/sqrt loops for `ARITH.*`, memory-latency workloads for `CYCLE_ACTIVITY.*`, vector/SSE-AVX transition workloads for `UOPS_ISSUED.VECTOR_WIDTH_MISMATCH`, store-buffer pressure for `RESOURCE_STALLS.SB` and `EXE_ACTIVITY.BOUND_ON_STORES`, and tight loops for `LSD.*`. For integration with metrics, run `perf stat` metric groups that reference topdown slots and uop events and check that no event-name resolution failures occur.
