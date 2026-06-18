# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/lunarlake/pipeline.json

## Purpose

`pipeline.json` is the main Lunar Lake pipeline event catalog. It contains 239 event records spanning divider activity, retired branches and mispredictions, fixed and programmable clock counters, dependency and execution stalls, retired instructions and uops, integer vector events, load blocking, loop-stream detector activity, machine clears, memory stalls, serialization, top-down slots, frontend/backend slot breakdowns, and uop issue, dispatch, execution, and retirement. It is central to `perf stat` top-down analysis and low-level pipeline diagnosis on Lunar Lake hybrid systems.

## Important APIs, Types, And Data Shape

The array uses the standard perf event JSON object schema with keys such as `EventName`, `Unit`, `EventCode`, `UMask`, `Counter`, `CounterMask`, `BriefDescription`, `PublicDescription`, `SampleAfterValue`, `Deprecated`, `MSRIndex`, `MSRValue`, `EdgeDetect`, and `Invert`. The file intentionally duplicates many event names by `Unit`, for example `ARITH.DIV_ACTIVE`, `BR_INST_RETIRED.ALL_BRANCHES`, `CPU_CLK_UNHALTED.THREAD`, `INST_RETIRED.ANY`, and `TOPDOWN.*` variants differ between `cpu_core` and `cpu_atom`. Fixed counters are represented by `Counter` strings such as `Fixed counter 0` through `Fixed counter 6`; programmable events list available counters.

## Control Flow

`jevents.py` parses each object into `JsonEvent`, converts the topic from the filename to `pipeline`, lowers the event name for perf alias lookup, and emits generated event table entries. At runtime, perf resolves aliases per PMU unit. Top-down metric code and `perf stat --topdown` use events such as `TOPDOWN.SLOTS`, `TOPDOWN.BAD_SPEC_SLOTS`, `TOPDOWN_BE_BOUND.*`, `TOPDOWN_FE_BOUND.*`, `TOPDOWN_RETIRING.*`, and `UOPS_RETIRED.SLOTS` as building blocks for derived metrics.

## State And Persistence

The file is static build-time input. Persistent state is the generated event table and any downstream metric expressions that rely on these names. Runtime counter programming is transient. MSR-backed entries such as `INT_MISC.BPCLEAR_CYCLES`, `INT_MISC.UNKNOWN_BRANCH_CYCLES`, and `UOPS_RETIRED.MS` carry filter state through generated `MSRIndex` and `MSRValue` fields.

## Dependencies And Integration Points

Dependencies include Intel hybrid PMU units, fixed counter semantics, top-down slot architecture, and perf's JSON-to-C generator. Integration points are `tools/perf/pmu-events/jevents.py`, `pmu-events.h`, generated `pmu-events.c`, `util/metricgroup.c`, `builtin-stat.c`, `perf list`, `perf stat`, and PMU-event tests. It also coordinates with `metricgroups.json` because many pipeline events feed top-down metric groups.

## Risks

Hybrid duplication is the dominant maintenance risk: the same alias can have different event codes, masks, counters, or fixed-counter meanings on P-core and E-core PMUs. Deprecated atom events such as `ARITH.DIV_OCCUPANCY`, `ARITH.DIV_UOPS`, `LOAD_HIT_PREFETCH.HW_PF`, and `MACHINE_CLEARS.SLOW` should remain visible for compatibility but not be preferred in new metrics. Top-down fixed counters must line up with kernel support and CPU model capabilities. Counter masks and MSR filters are easy to mistype and can change a count from cycles to periods.

## Test Signals

Checks should include JSON validity, length 239, presence of both `cpu_core` and `cpu_atom` records, and generator success. Representative runtime checks are `perf list pipeline`, `perf stat -e cycles,instructions,topdown.slots`, and explicit hybrid aliases such as `cpu_core/uops_retired.slots/` and `cpu_atom/topdown_fe_bound.all/`. Tests should also verify deprecated entries remain marked, not removed silently.
