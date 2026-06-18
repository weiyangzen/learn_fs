## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sandybridge/frontend.json

### Purpose
`frontend.json` defines 33 Sandy Bridge front-end PMU events. It describes branch resteers, DSB-to-MITE switches, Decode Stream Buffer fill cancellation, instruction cache hits/misses, IDQ delivery by DSB/MITE/MS paths, uops-not-delivered events, and instructions written to the instruction queue.

### Important APIs, Types, And Data Fields
The file uses the core event schema:

- `EventName` covers `BACLEARS.ANY`, `DSB2MITE_SWITCHES.*`, `DSB_FILL.*`, `ICACHE.*`, `IDQ.*`, `IDQ_UOPS_NOT_DELIVERED.*`, and `INSTS_WRITTEN_TO_IQ.INSTS`.
- `EventCode`, `UMask`, and `Counter` provide PMU selectors and scheduling constraints.
- `CounterMask`, `EdgeDetect`, and `Invert` are used by cycle-threshold events such as `IDQ.ALL_DSB_CYCLES_4_UOPS`, edge-detected microcode switch events, and not-delivered cycle variants.
- `BriefDescription` and `PublicDescription` feed event help.
- `SampleAfterValue` supplies sampling defaults.

There are no executable functions. The event objects are the public data interface.

### Control Flow And Data Flow
Perf reads each object and exposes symbolic front-end events. Derived top-down metrics consume these names: `tma_frontend_bound` uses `IDQ_UOPS_NOT_DELIVERED.CORE`, `tma_fetch_latency` uses `IDQ_UOPS_NOT_DELIVERED.CYCLES_0_UOPS_DELIV.CORE`, `tma_dsb_switches` uses `DSB2MITE_SWITCHES.PENALTY_CYCLES`, `tma_ms_switches` uses `IDQ.MS_SWITCHES`, and `tma_info_frontend_dsb_coverage` combines `IDQ.DSB_UOPS`, `LSD.UOPS`, `IDQ.MITE_UOPS`, and `IDQ.MS_UOPS`.

### State And Persistence
The file persists static selector and modifier metadata. Runtime front-end event counts are read from hardware counters and are not persisted by this JSON.

### Dependencies And Integration Points
The definitions depend on Sandy Bridge front-end pipeline concepts: DSB, MITE, IDQ, microcode sequencer, BPU resteers, and instruction cache. Integration points include perf event generation, `snb-metrics.json` top-down formulas, and `metricgroups.json` groups such as `Frontend`, `FetchBW`, `FetchLat`, `DSB`, `DSBmiss`, and `Fed`.

### Risks
Cycle events using `CounterMask`, `Invert`, or `EdgeDetect` are easy to misencode. A wrong modifier can invert the metric meaning while still producing plausible numbers. Formula references are name-sensitive, so renames must be coordinated with `snb-metrics.json`. Descriptions should continue distinguishing DSB, MITE, IDQ, and MS paths because users rely on perf help text to interpret front-end bottlenecks.

### Test Signals
Validate JSON syntax and schema, inspect generated perf entries for modifiers on `IDQ_UOPS_NOT_DELIVERED.*` and `IDQ.MS_SWITCHES`, run metric parser tests for `tma_frontend_bound`, `tma_fetch_latency`, `tma_dsb_switches`, and `tma_ms_switches`, and smoke-test `perf list` output for the front-end group.
