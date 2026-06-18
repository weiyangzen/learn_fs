# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/emeraldrapids/pipeline.json

## Purpose

`pipeline.json` defines Emerald Rapids pipeline, retirement, branch, top-down, and execution-port PMU events for Linux perf. It contains 124 event objects covering arithmetic divider use, assists, branch retirement and misprediction, unhalted clocks, memory-stall cycle activity, execution activity, retired instructions and uops, integer vector operations, load blocking, loop stream detector activity, machine clears, resource stalls, reservation-station state, top-down slots, dispatched execution ports, and issued/executed/retired uops.

The file is declarative PMU metadata. Its purpose is to let perf name, encode, schedule, sample, and display these microarchitectural events for the Emerald Rapids CPU model. It does not implement the counters; it describes how perf should program CPU PMU hardware.

## Important APIs, Types, and Data

The schema is a JSON array of event objects. Common fields are `EventName`, `EventCode`, `UMask`, `Counter`, `BriefDescription`, `PublicDescription`, and `SampleAfterValue`. Qualifier fields include `CounterMask`, `EdgeDetect`, `Invert`, `Deprecated`, `MSRIndex`, and `MSRValue`. Some architectural events use fixed counters and omit `EventCode`, such as `INST_RETIRED.ANY`, `CPU_CLK_UNHALTED.THREAD`, `CPU_CLK_UNHALTED.REF_TSC`, and `TOPDOWN.SLOTS`.

The file's event families include:

- `ARITH`: divider-active events, including deprecated aliases for older names and replacements such as `ARITH.DIV_ACTIVE` and `ARITH.IDIV_ACTIVE`.
- `ASSISTS`: `ASSISTS.ANY` for hardware microcode assists.
- `BR_INST_RETIRED` and `BR_MISP_RETIRED`: retired branch and mispredicted branch categories including conditional, taken, far, indirect, call, return, and near-taken variants.
- `CPU_CLK_UNHALTED`: thread, reference, distributed, one-thread-active, C0 wait, pause, and fixed-counter clock events.
- `CYCLE_ACTIVITY`: cycles and stalls while L1D, L2, or broader memory-subsystem load misses are outstanding.
- `EXE`, `EXE_ACTIVITY`, `UOPS_DISPATCHED`, and `UOPS_EXECUTED`: AMX activity, port utilization, load/store/execution bound cycles, dispatch-port counts, uop execution counts, and stall cycles.
- `INST_DECODED`, `INST_RETIRED`, `UOPS_ISSUED`, and `UOPS_RETIRED`: decoder use, retired instruction/uop accounting, macro-fusion, NOPs, precise distribution, repeat-string iterations, issue cycles, and retirement stalls.
- `INT_MISC`, `MACHINE_CLEARS`, `RS`, `RS_EMPTY`, and `RESOURCE_STALLS`: recovery after clears, unknown branch cycles, uop dropping, machine clears, reservation-station emptiness, store-buffer stalls, and serializing-operation stalls.
- `INT_VEC_RETIRED`: 128-bit and 256-bit integer vector add, multiply, shuffle, and VNNI instruction retirement.
- `LD_BLOCKS`, `LOAD_HIT_PREFETCH`, and `LSD`: load blocking causes, software-prefetch fill-buffer hits, and loop stream detector cycles/uops.
- `TOPDOWN`: backend-bound, bad-speculation, branch-mispredict, memory-bound, and slot denominator events for Top-down Microarchitecture Analysis.

Seven entries are marked deprecated and intentionally remain as compatibility aliases: `ARITH.DIVIDER_ACTIVE`, `ARITH.FP_DIVIDER_ACTIVE`, `ARITH.INT_DIVIDER_ACTIVE`, `RS_EMPTY.COUNT`, `RS_EMPTY.CYCLES`, `UOPS_EXECUTED.STALL_CYCLES`, and `UOPS_RETIRED.STALL_CYCLES`.

## Control Flow

There is no executable control flow in the file. Perf control flow is data driven: the PMU event generator or runtime loader parses the JSON, selects records matching Emerald Rapids, and registers event aliases. When a user requests an event, perf resolves the alias, validates counter constraints, programs fixed or programmable counters using the event encoding fields, applies qualifiers such as edge detection, inversion, counter masks, and MSR filters, and then reads or samples the resulting hardware counts.

Top-down analysis adds a higher-level flow. `TOPDOWN.SLOTS` or `TOPDOWN.SLOTS_P` supplies the denominator, and the bound/speculation slot events supply components that perf metrics can combine into percentages. Fixed-counter events leave programmable counters available for other events, while `_P` variants expose programmable-counter alternatives when needed by grouping or sampling.

## State and Persistence Behavior

The JSON file is static source metadata. Runtime state is held in CPU PMU counters, fixed counters, overflow status bits, and any MSR programming performed while an event is active. `SampleAfterValue` provides default sampling periods, but actual period state is managed by perf and the kernel.

Counter availability is part of the persistent metadata contract. Most events allow counters 0 through 7, but some are restricted to 0 through 3, some top-down bad-speculation events are counter 0 only, and fixed-counter events are bound to fixed counters 0 through 3. Qualifiers such as `CounterMask`, `EdgeDetect`, and `Invert` alter how the hardware increments during an active measurement but do not persist after the event is removed.

## Dependencies and Integration Points

The file depends on the Linux perf PMU event schema, x86 Emerald Rapids model detection, kernel PMU driver support for the listed event encodings, and Intel's architectural and model-specific PMU definitions. It integrates with `perf list`, `perf stat`, `perf record`, event grouping, top-down metrics, generated PMU tables, counter scheduling, fixed-counter handling, and tooling that validates vendored perf data against upstream Linux.

The events are also integration points for higher-level performance diagnosis. Branch events feed control-flow and bad-speculation metrics. `CPU_CLK_UNHALTED` and `INST_RETIRED` are denominator inputs for IPC and utilization metrics. `CYCLE_ACTIVITY`, `RESOURCE_STALLS`, `RS`, and `EXE_ACTIVITY` support front-end versus back-end stall attribution. `TOPDOWN` events anchor Intel TMA. `UOPS_DISPATCHED` and `UOPS_EXECUTED` expose execution-port pressure and throughput.

## Risks and Edge Cases

Encoding accuracy is the main risk. An incorrect `EventCode`, `UMask`, `CounterMask`, `Invert`, `EdgeDetect`, or fixed-counter assignment changes the measured hardware condition while still producing plausible-looking counts. Counter constraints are especially important for top-down events and events limited to counters 0 through 3.

Deprecated aliases must stay coherent with their replacement events. Removing them can break user scripts, while changing their encodings can make historical event names diverge from the intended replacement. Events with `_P` suffixes are programmable-counter alternatives to fixed architectural events and should not be treated as exact duplicates in all scheduling contexts.

Some descriptions are terse or use architecture-specific terms such as RS, RAT, LSD, PEBS, PDIR, PDIST, C0.1/C0.2, and AMX. Consumers should avoid deriving semantics from names alone. Clock events have caveats around halt states, hyper-thread distribution, throttling, pause/umwait/tpause behavior, and fixed-counter overflow status. MSR-filtered entries such as `INT_MISC.UNKNOWN_BRANCH_CYCLES` and `UOPS_RETIRED.MS` require correct MSR programming.

Hardware and virtualization can affect availability and counts. Fixed counter 3 top-down slots, PEBS precise distribution, AMX activity, and model-specific port mappings depend on Emerald Rapids PMU support. Multiplexing may make ratios misleading unless `enabled` and `running` time are considered by perf.

## Test Signals

Useful checks include JSON parser validation, perf PMU event generation, `perf list` coverage for all 124 aliases, and static validation of unique names, deprecated aliases, counter constraints, fixed-counter names, event codes, umasks, and qualifier fields. On capable hardware, smoke tests should schedule representative events from each family, including `TOPDOWN.SLOTS`, `INST_RETIRED.ANY`, `CPU_CLK_UNHALTED.THREAD`, branch retired and mispredicted events, `CYCLE_ACTIVITY.STALLS_TOTAL`, `UOPS_DISPATCHED.PORT_0`, and `UOPS_RETIRED.SLOTS`.

Metric-level tests should verify top-down formulas that use these events, especially denominator consistency and counter scheduling for grouped measurements. Regression checks should compare the file against the upstream Linux Emerald Rapids PMU database and run perf parser tests that exercise fixed counters, programmable alternatives, MSR-backed events, deprecated aliases, and counter-mask/invert/edge-detect qualifiers.
