# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/knightslanding/pipeline.json

## Purpose

`pipeline.json` defines Knights Landing perf aliases for core pipeline, retirement, branch, cycle, allocation-stall, recycle-queue, reservation-station, machine-clear, divider, and uop-retirement events. It contains 45 records that provide the common denominators and bottleneck counters used with the cache, memory, front-end, and floating-point event files.

## Important APIs, Types, and Schema

The file follows the perf event JSON schema. Its event families are:

- `BR_INST_RETIRED`: nine precise retired-branch classes, including all branches, calls, far branches, indirect calls, conditional jumps, non-return indirects, relative calls, returns, and taken conditional jumps.
- `BR_MISP_RETIRED`: the corresponding nine precise mispredicted retired-branch classes.
- `CPU_CLK_UNHALTED`: programmable and fixed-counter cycle events, including fixed counter 1 for core cycles and fixed counter 2 for reference cycles.
- `INST_RETIRED`: fixed and programmable retired-instruction events, including fixed counter 0 and precise programmable variants.
- `MACHINE_CLEARS`: all machine clears and self-modifying-code clears.
- `NO_ALLOC_CYCLES`: allocation pipeline no-uop cycles for all causes, mispredict wait, not-delivered/IQ-empty, RAT stall, and ROB full.
- `RECYCLEQ`: retired load/store recycle queue causes, including store-forwarding blocks, split loads/stores, locks, and store-address buffer full.
- `RS_FULL_STALL`: reservation station full stalls, including MEC-specific stalls.
- `UOPS_RETIRED`: all retired uops and micro-sequencer uops.
- `CYCLES_DIV_BUSY.ALL`: cycles when the divider is busy.

Several records include `PEBS: "1"` and two recycle-queue load/split events include `Data_LA: "1"`, marking precise sampling and data linear-address support. Fixed events use `Counter: "Fixed counter 0"`, `Fixed counter 1`, or `Fixed counter 2` rather than generic `0,1`.

## Control Flow and Data Flow

Perf maps each `EventName` to either a fixed counter or a programmable core event selector. Fixed events omit `EventCode` and rely on their fixed counter and umask identity; programmable events use `EventCode`, optional `UMask`, and `Counter: "0,1"`.

The practical analysis flow is compositional. Cycle and instruction events provide denominators; branch events feed prediction rates; allocation and reservation-station stall events identify front-end/back-end allocation pressure; recycle-queue events explain memory-ordering and forwarding hazards; and uop-retired events distinguish complex micro-sequencer flows from normal retirement.

## State and Persistence Behavior

The file is static metadata and does not mutate state. At runtime, perf may program fixed counters, generic counters, and precise sampling modes according to these descriptors. PEBS and data-address flags affect sampling capability but do not create persistence in the JSON itself.

## Dependencies and Integration Points

`pipeline.json` depends on perf's KNL event-map integration and on `counter.json` for the presence of three fixed core counters and two programmable core counters. It is a central integration file for performance analysis because sibling files often need its denominators: `frontend.json` branch/front-end counts pair with branch and cycle events; `floating-point.json` SIMD uop counts pair with `UOPS_RETIRED` and `INST_RETIRED`; `cache.json` and `memory.json` counts pair with cycles and instructions for rate calculations.

## Risks and Edge Cases

The biggest semantic risk is confusing fixed-counter aliases with programmable aliases. `INST_RETIRED.ANY`, `CPU_CLK_UNHALTED.THREAD`, and `CPU_CLK_UNHALTED.REF_TSC` use fixed counters, while similarly named `_P` or `REF` variants use programmable events. Event grouping and availability differ between those forms.

Precise branch and recycle-queue events can carry PEBS/data-address expectations. If tooling drops `PEBS` or `Data_LA`, sampling behavior may differ from the alias metadata. `CYCLES_DIV_BUSY.ALL` counts divider busy cycles whether or not another divide uop is stalled waiting, so it is not a direct stall metric. `NO_ALLOC_CYCLES` categories can overlap in interpretation and should be analyzed with care.

Some rows omit `UMask` or `EventCode` because they are fixed or base programmable events. Schema checks must allow these legitimate omissions instead of treating them as malformed.

## Test Signals

Validation should parse the JSON, confirm 45 unique event names, verify the expected family counts, and ensure the three fixed-counter aliases reference fixed counters 0, 1, and 2. Additional checks should confirm PEBS/data-address fields remain on the precise events that need them. Integration tests should verify `perf list` exposes branch, cycle, instruction, recycle-queue, and no-allocation aliases and that representative fixed plus programmable events can be opened together within KNL counter constraints.
