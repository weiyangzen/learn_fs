<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlaken/pipeline.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlaken/pipeline.json

## Purpose
Defines Alder Lake-N pipeline, branch-retirement, misprediction, machine-clear, uop, recovery-cycle, topdown slot, and execution-port aliases used for pipeline and topdown bottleneck analysis.

## APIs, Types, and Functions
The data contract is a perf PMU JSON array with 87 records: 87 raw event aliases and 0 derived metrics. Schema fields present are `BriefDescription`, `Counter`, `CounterMask`, `Deprecated`, `EventCode`, `EventName`, `PublicDescription`, `SampleAfterValue`, `UMask`. `jevents.py` maps `EventCode`, `UMask`, `CounterMask`, `MSRIndex`, `MSRValue`, `PerPkg`, `Deprecated`, `MetricExpr`, `MetricGroup`, and `ScaleUnit` into `struct pmu_event` or `struct pmu_metric` entries declared in `pmu-events.h`. Units resolve to `default_core`. Representative names: `ARITH.DIV_ACTIVE`, `ARITH.DIV_OCCUPANCY`, `ARITH.DIV_UOPS`, `ARITH.IDIV_ACTIVE`, `ARITH.IDIV_OCCUPANCY`, `ARITH.IDIV_UOPS`, `BR_INST_RETIRED.ALL_BRANCHES`, `BR_INST_RETIRED.CALL`, `BR_INST_RETIRED.COND`, `BR_INST_RETIRED.COND_TAKEN`, plus 77 more. It also has 15 deprecated entries.

## Control Flow
Build control flow is data-driven: `jevents.py` reads this `pipeline` file, lowercases event aliases, converts `Unit` through `unit_to_pmu()`, canonicalizes event and umask encodings, and appends generated C strings to the model event table. Runtime perf reaches the records through `find_core_events_table()`, `find_sys_events_table()`, `pmu_events_table__find_event()`, and `pmu_events_table__for_each_event()` when `perf list`, `perf stat -e`, or metrics request the aliases.

## State and Persistence
The file has no executable state, locks, persistence layer, or runtime mutation. Its durable behavior is the generated perf event/metric table selected by x86 mapfile CPUID matching; kernel PMU drivers own counter state once a user selects an alias. Deprecated records persist in the generated tables so old event names can still be listed or redirected with deprecation metadata.

## Dependencies and Integration
Integrated by `tools/perf/pmu-events/arch/x86/mapfile.csv` selecting the `alderlaken` directory for matching x86 CPU identifiers. Consumed by `jevents.py`, `pmu-events.h`, `builtin-list.c`, metric parsing, and PMU table lookup helpers. All entries omit `Unit`, so `jevents.py` routes them to the default core PMU for this model.

## Risks
The main risk is semantic drift from the vendor performance-monitoring documentation: a wrong event code, umask, MSR filter, or PMU unit can make a friendly alias count the wrong hardware condition. This file has 15 deprecated entries, so consumers must prefer replacement names while preserving compatibility for older scripts.

## Test Signals
Run the perf pmu-events generator over `arch/x86` and the `tools/perf/tests/pmu-events.c` generated-table checks. Inspect `perf list --json` or generated C tables for representative aliases `ARITH.DIV_ACTIVE`, `ARITH.DIV_OCCUPANCY`, `ARITH.DIV_UOPS`, `ARITH.IDIV_ACTIVE`, `ARITH.IDIV_OCCUPANCY`, `ARITH.IDIV_UOPS`, plus 81 more. On matching hardware, run `perf stat -e` for events such as `ARITH.DIV_ACTIVE`, `ARITH.DIV_OCCUPANCY`, `ARITH.DIV_UOPS`, `ARITH.IDIV_ACTIVE`, `ARITH.IDIV_OCCUPANCY`, plus 82 more and verify the kernel accepts the encoding and returns plausible non-negative counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlaken/pipeline.json -->
