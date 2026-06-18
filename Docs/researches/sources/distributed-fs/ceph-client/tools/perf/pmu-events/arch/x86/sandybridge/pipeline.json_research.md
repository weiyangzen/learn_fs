## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sandybridge/pipeline.json

### Purpose
`pipeline.json` defines 128 Sandy Bridge core pipeline events. It covers branch execution and retirement, branch misprediction, clock and fixed counter events, cycle activity, instruction retirement, RAT/recovery stalls, load blocking, LSD, machine clears, resource stalls, reservation station state, dispatched/executed/issued/retired uops, and per-port dispatch.

### Important APIs, Types, And Data Fields
The file is a JSON event array using:

- `EventName` for user-facing names such as `BR_INST_EXEC.ALL_BRANCHES`, `BR_MISP_RETIRED.ALL_BRANCHES`, `CPU_CLK_UNHALTED.THREAD`, `INST_RETIRED.ANY`, `UOPS_RETIRED.RETIRE_SLOTS`, and `UOPS_DISPATCHED_PORT.PORT_0`.
- `EventCode`/`UMask` for programmable selectors, plus fixed-counter `Counter` values for fixed events (`Fixed counter 0`, `Fixed counter 1`, `Fixed counter 2`).
- `Counter`, `CounterMask`, `AnyThread`, `EdgeDetect`, `Invert`, and `PEBS` modifiers for scheduling, threshold cycles, any-thread counting, edge detection, inverted masks, and precise sampling.
- `BriefDescription`, `PublicDescription`, and `SampleAfterValue` for help and sampling defaults.

No functions/classes exist; the PMU event schema is the integration interface.

### Control Flow And Data Flow
Perf's generator reads this file and creates event records. Runtime perf resolves names to either programmable events or fixed counters. `snb-metrics.json` is heavily dependent on these names: top-down slots use `UOPS_RETIRED.RETIRE_SLOTS`, `UOPS_ISSUED.ANY`, and `CPU_CLK_UNHALTED.THREAD`; branch and bad-speculation metrics use `BR_MISP_RETIRED.*`, `BR_INST_RETIRED.*`, and `MACHINE_CLEARS.COUNT`; backend and port metrics use `UOPS_DISPATCHED.*`, `RESOURCE_STALLS.*`, `RS_EVENTS.EMPTY_CYCLES`, and `CYCLE_ACTIVITY.*`.

### State And Persistence
The file persists static PMU metadata and default sampling periods. Runtime counts are hardware state, not stored here. Build-generated perf tables persist a compiled copy of this data.

### Dependencies And Integration Points
The file depends on Sandy Bridge core PMU and fixed counter behavior. It integrates with `counter.json` for counter inventory, `snb-metrics.json` for most top-down formulas, `frontend.json` for fetch-latency formulas, `floating-point.json` for compute formulas, and `metricgroups.json` for metric taxonomy.

### Risks
This is one of the highest-blast-radius files because many metrics depend on exact event names and semantics. Fixed-counter metadata must be correct for basic IPC/CPI calculations. Any-thread variants, PEBS flags, and counter masks must be preserved. Several cycle-style events share selectors but differ by `CounterMask`, `Invert`, or `EdgeDetect`, so review should inspect modifiers, not just event code and umask.

### Test Signals
Validation should include JSON parsing, generated perf table diffing, `perf list` checks for fixed and programmable events, metric parser tests for top-down level 1 and 2 metrics, and smoke tests using `INST_RETIRED.ANY`, `CPU_CLK_UNHALTED.THREAD`, `UOPS_RETIRED.RETIRE_SLOTS`, and branch misprediction events.
