# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/rocketlake/pipeline.json

## Purpose
This JSON file defines Rocket Lake core pipeline PMU events for Linux perf. It supplies the symbolic event aliases used for instruction retirement, branch retirement and misprediction, clocks, front-end/back-end activity, dispatch port utilization, issued/executed/retired uops, resource stalls, machine clears, assists, divider activity, and topdown slot accounting.

The file is one of the central event providers for `rkl-metrics.json`: many Topdown Microarchitecture Analysis metrics use its aliases directly, including `TOPDOWN.SLOTS`, `UOPS_RETIRED.SLOTS`, `BR_MISP_RETIRED.*`, `CYCLE_ACTIVITY.*`, `EXE_ACTIVITY.*`, and `UOPS_DISPATCHED.*`.

## Data shape and important fields
The file is a JSON array of 95 event objects. The observed keys are `EventName`, `BriefDescription`, `PublicDescription`, `EventCode`, `UMask`, `Counter`, `CounterMask`, `Invert`, `EdgeDetect`, and `SampleAfterValue`.

The event-name families are:

- `ARITH`: 2 divider activity events.
- `ASSISTS`: 1 microcode assist event.
- `BR_INST_RETIRED`: 9 retired branch classifications.
- `BR_MISP_RETIRED`: 8 mispredicted branch classifications.
- `CPU_CLK_UNHALTED`: 7 clock events, including fixed-counter aliases.
- `CYCLE_ACTIVITY`: 7 load/memory outstanding and stall events.
- `EXE_ACTIVITY`: 5 port-utilization and store-bound events.
- `INST_RETIRED`: 5 retired instruction events.
- `INT_MISC`: 5 recovery, clear/resteer, and uop-dropping events.
- `UOPS_DISPATCHED`: 7 execution port groups.
- `UOPS_EXECUTED`: 12 executed-uop and occupancy events.
- `UOPS_ISSUED` and `UOPS_RETIRED`: 3 events each.
- Smaller families for decode, LSD, machine clears, load blocking, resource stalls, reservation station emptiness, and topdown slots.

Most entries target programmable counters `0,1,2,3,4,5,6,7`; 14 entries are restricted to `0,1,2,3`; fixed counter aliases cover retired instructions and clocks. The file uses `CounterMask` on 29 entries, `Invert` on 6 entries, and `EdgeDetect` on 3 entries, which means tests must cover more than simple event-code/umask emission.

## Control flow and integration
The JSON is consumed by the generic perf PMU event generation flow:

1. `jevents.py` scans `arch/x86/rocketlake/pipeline.json` as a topic file.
2. Each object is converted into a `JsonEvent`; names, descriptions, topic, event encodings, counter constraints, cmasks, invert flags, edge-detect flags, and sample periods are emitted into generated C data.
3. `pmu-events.h` exposes the generated events through `pmu_events_table__for_each_event()` and `pmu_events_table__find_event()`.
4. Runtime perf command paths use the generated table selected by the x86 mapfile to resolve symbolic names.

There are no local functions or branches in the JSON file itself. The control behavior is in perf's parser and event scheduler. Counter restrictions and cmask/invert/edge flags alter how perf programs the PMU and how events can be grouped.

## State, persistence, and dependencies
The file is static declarative input. Its persistent artifact is generated perf event-table C code. It depends on the Rocket Lake PMU programming model, fixed counter availability, topdown slot support, and perf's JSON schema. It also depends on sibling event files because the metrics layer combines pipeline aliases with memory, frontend, cache, offcore, and virtual-memory aliases.

The file has no runtime state, but its event definitions influence perf's runtime PMU programming state when users request the aliases. Fixed-counter aliases such as `CPU_CLK_UNHALTED.THREAD`, `CPU_CLK_UNHALTED.REF_TSC`, and `INST_RETIRED.ANY` affect counter scheduling because they do not consume the same programmable counters as normal events.

## Risks
Incorrect event encodings here have broad blast radius because these events are foundational to TMA and common `perf stat` workflows. Errors in `TOPDOWN.SLOTS`, retired instruction counts, clocks, or branch events will distort high-level metrics rather than only one low-level counter.

Counter-mask and invert semantics are easy to break during maintenance. For example, occupancy-style or "cycles with at least N" events rely on `CounterMask`, and some pipeline utilization events rely on inverted threshold tests. A JSON syntax check will not catch a swapped cmask, missing invert flag, or bad fixed-counter designation.

Cross-file metric consistency is another risk. `rkl-metrics.json` references both present aliases and aliases from other Rocket Lake files. Renaming pipeline aliases or changing their case will break metric formulas because metric expressions match symbolic event names.

## Test signals
Useful signals include `jq empty pipeline.json`, full `jevents.py` generation, and perf's PMU event unit tests. Runtime-facing checks should include `perf list --json` to verify representative aliases from each family, plus `perf stat` smoke tests for fixed counters, programmable events, cmask/invert events, and topdown metrics. Metric parser tests should include formulas using `TOPDOWN.SLOTS`, `BR_MISP_RETIRED.ALL_BRANCHES`, `CYCLE_ACTIVITY.STALLS_MEM_ANY`, `EXE_ACTIVITY.BOUND_ON_STORES`, and `UOPS_RETIRED.SLOTS`.
