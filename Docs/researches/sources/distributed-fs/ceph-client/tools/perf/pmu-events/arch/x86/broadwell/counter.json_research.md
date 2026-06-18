# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwell/counter.json

## Purpose
Broadwell PMU counter topology declaration for Linux `perf`. The file is a compact JSON array of four unit records describing how many generic and fixed counters are available for core and selected uncore-like Broadwell PMU units.

The records declare `core` with four generic and three fixed counters, `CBOX` with two generic and zero fixed counters, `ARB` with two generic and zero fixed counters, and `cbox_0` with zero generic and one fixed counter.

## Important APIs, Types, and Functions
The schema is a counter-unit object:

- `Unit`: PMU unit name, such as `core`, `CBOX`, `ARB`, or `cbox_0`.
- `CountersNumGeneric`: number of programmable generic counters for that unit.
- `CountersNumFixed`: number of fixed counters for that unit.

There are no functions or executable types. The file acts as metadata consumed by perf tooling when modeling event scheduling capacity for Broadwell PMU units.

## Control Flow
Perf tooling reads this file during PMU-events table generation or event-map loading. At runtime, scheduling logic can use the declared counter counts to understand how many events can be placed on each unit without multiplexing. The file does not decide scheduling itself; it supplies capacity data to the perf infrastructure.

The effective flow is: parse unit records, attach counter capacity to the architecture PMU map, then combine this capacity with per-event `Counter` constraints from event JSON files such as `cache.json`, `floating-point.json`, and `frontend.json`.

## State and Persistence Behavior
The only persistent state is the checked-in counter metadata. Runtime state is the allocation of perf events to hardware counters during a perf session. No collection data is persisted here, and the file is not mutated by perf.

Changing values in this file changes scheduling assumptions. For example, reducing `core` generic counter count would increase expected multiplexing, while incorrect uncore counts could make generated maps advertise unsupported schedules.

## Dependencies and Integration Points
This file integrates with the Broadwell PMU-events architecture directory and complements event definition files. Core event files typically constrain events to counters `0,1,2,3`, matching `core`'s four generic counters. The fixed counter count is relevant to standard fixed-function events such as cycles, instructions, and reference cycles used by metrics in `bdw-metrics.json`.

The `CBOX`, `ARB`, and `cbox_0` records integrate with uncore event tables and metrics that reference uncore/system events such as socket clocks and memory bandwidth. This file is part of the same generated PMU map used by `perf list` and `perf stat`.

## Risks
Risks are small but high impact:

- Incorrect counter counts can make perf over-schedule events, underuse available counters, or report misleading multiplexing pressure.
- Unit naming must match event tables and PMU discovery names. Case differences such as `CBOX` versus `cbox_0` are semantically meaningful in the JSON and tooling.
- Fixed-counter declarations must align with kernel PMU support; otherwise metrics that rely on fixed events can appear schedulable but fail at runtime.
- The file is too small to catch errors through internal redundancy, so validation must come from integration tests.

## Test Signals
Useful checks include JSON syntax validation, generated PMU map inspection, `perf list` on Broadwell systems, and scheduling smoke tests that collect four generic core events without multiplexing and a fifth with expected multiplexing. Fixed-counter availability can be checked with cycles/instructions/reference-cycle style events. Uncore counter declarations should be validated with representative CBOX and ARB events from the same Broadwell PMU-events tree.
