<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen1/branch.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen1/branch.json

## Purpose
Defines AMD `amdzen1` branch-prediction and instruction-side TLB aliases, including BTB corrections, dynamic indirect prediction, redirect activity, fetch TLB hits, and ITLB reload requests.

## APIs, Types, and Functions
The data contract is a perf PMU JSON array with 5 records: 5 raw event aliases and 0 derived metrics. Schema fields present are `BriefDescription`, `EventCode`, `EventName`, `PublicDescription`. `jevents.py` maps `EventCode`, `UMask`, `CounterMask`, `MSRIndex`, `MSRValue`, `PerPkg`, `Deprecated`, `MetricExpr`, `MetricGroup`, and `ScaleUnit` into `struct pmu_event` or `struct pmu_metric` entries declared in `pmu-events.h`. Units resolve to `default_core`. Representative names: `bp_l1_btb_correct`, `bp_l2_btb_correct`, `bp_dyn_ind_pred`, `bp_de_redirect`, `bp_l1_tlb_fetch_hit`.

## Control Flow
Build control flow is data-driven: `jevents.py` reads this `branch` file, lowercases event aliases, converts `Unit` through `unit_to_pmu()`, canonicalizes event and umask encodings, and appends generated C strings to the model event table. Runtime perf reaches the records through `find_core_events_table()`, `find_sys_events_table()`, `pmu_events_table__find_event()`, and `pmu_events_table__for_each_event()` when `perf list`, `perf stat -e`, or metrics request the aliases.

## State and Persistence
The file has no executable state, locks, persistence layer, or runtime mutation. Its durable behavior is the generated perf event/metric table selected by x86 mapfile CPUID matching; kernel PMU drivers own counter state once a user selects an alias.

## Dependencies and Integration
Integrated by `tools/perf/pmu-events/arch/x86/mapfile.csv` selecting the `amdzen1` directory for matching x86 CPU identifiers. Consumed by `jevents.py`, `pmu-events.h`, `builtin-list.c`, metric parsing, and PMU table lookup helpers. All entries omit `Unit`, so `jevents.py` routes them to the default core PMU for this model.

## Risks
The main risk is semantic drift from the vendor performance-monitoring documentation: a wrong event code, umask, MSR filter, or PMU unit can make a friendly alias count the wrong hardware condition.

## Test Signals
Run the perf pmu-events generator over `arch/x86` and the `tools/perf/tests/pmu-events.c` generated-table checks. Inspect `perf list --json` or generated C tables for representative aliases `bp_l1_btb_correct`, `bp_l2_btb_correct`, `bp_dyn_ind_pred`, `bp_de_redirect`, `bp_l1_tlb_fetch_hit`. On matching hardware, run `perf stat -e` for events such as `bp_l1_btb_correct`, `bp_l2_btb_correct`, `bp_dyn_ind_pred`, `bp_de_redirect`, `bp_l1_tlb_fetch_hit` and verify the kernel accepts the encoding and returns plausible non-negative counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen1/branch.json -->
