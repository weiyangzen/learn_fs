<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlaken/uncore-memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlaken/uncore-memory.json

## Purpose
Defines Alder Lake-N integrated memory-controller and free-running memory-controller events for CAS counts, activation/precharge behavior, DRAM page hits/misses, thermal state, prefetches, and VC requests.

## APIs, Types, and Functions
The data contract is a perf PMU JSON array with 25 records: 25 raw event aliases and 0 derived metrics. Schema fields present are `BriefDescription`, `Counter`, `EventCode`, `EventName`, `PerPkg`, `PublicDescription`, `UMask`, `Unit`. `jevents.py` maps `EventCode`, `UMask`, `CounterMask`, `MSRIndex`, `MSRValue`, `PerPkg`, `Deprecated`, `MetricExpr`, `MetricGroup`, and `ScaleUnit` into `struct pmu_event` or `struct pmu_metric` entries declared in `pmu-events.h`. Units resolve to `iMC`, `imc_free_running_0`, `imc_free_running_1`. Representative names: `UNC_MC0_RDCAS_COUNT_FREERUN`, `UNC_MC0_WRCAS_COUNT_FREERUN`, `UNC_MC1_RDCAS_COUNT_FREERUN`, `UNC_MC1_WRCAS_COUNT_FREERUN`, `UNC_M_ACT_COUNT_RD`, `UNC_M_ACT_COUNT_TOTAL`, `UNC_M_ACT_COUNT_WR`, `UNC_M_CAS_COUNT_RD`, `UNC_M_CAS_COUNT_WR`, `UNC_M_CLOCKTICKS`, plus 15 more.

## Control Flow
Build control flow is data-driven: `jevents.py` reads this `uncore-memory` file, lowercases event aliases, converts `Unit` through `unit_to_pmu()`, canonicalizes event and umask encodings, and appends generated C strings to the model event table. Runtime perf reaches the records through `find_core_events_table()`, `find_sys_events_table()`, `pmu_events_table__find_event()`, and `pmu_events_table__for_each_event()` when `perf list`, `perf stat -e`, or metrics request the aliases.

## State and Persistence
The file has no executable state, locks, persistence layer, or runtime mutation. Its durable behavior is the generated perf event/metric table selected by x86 mapfile CPUID matching; kernel PMU drivers own counter state once a user selects an alias.

## Dependencies and Integration
Integrated by `tools/perf/pmu-events/arch/x86/mapfile.csv` selecting the `alderlaken` directory for matching x86 CPU identifiers. Consumed by `jevents.py`, `pmu-events.h`, `builtin-list.c`, metric parsing, and PMU table lookup helpers. Unit-specific routing depends on `unit_to_pmu()` mappings for `iMC`, `imc_free_running_0`, `imc_free_running_1`; missing `Unit` means the default core PMU. Entries with `PerPkg` require package-level aggregation behavior in perf's uncore/sys PMU handling.

## Risks
The main risk is semantic drift from the vendor performance-monitoring documentation: a wrong event code, umask, MSR filter, or PMU unit can make a friendly alias count the wrong hardware condition. Uncore events need package/socket aggregation checks because counter availability and naming can differ from core PMU events.

## Test Signals
Run the perf pmu-events generator over `arch/x86` and the `tools/perf/tests/pmu-events.c` generated-table checks. Inspect `perf list --json` or generated C tables for representative aliases `UNC_MC0_RDCAS_COUNT_FREERUN`, `UNC_MC0_WRCAS_COUNT_FREERUN`, `UNC_MC1_RDCAS_COUNT_FREERUN`, `UNC_MC1_WRCAS_COUNT_FREERUN`, `UNC_M_ACT_COUNT_RD`, `UNC_M_ACT_COUNT_TOTAL`, plus 19 more. On matching hardware, run `perf stat -e` for events such as `UNC_MC0_RDCAS_COUNT_FREERUN`, `UNC_MC0_WRCAS_COUNT_FREERUN`, `UNC_MC1_RDCAS_COUNT_FREERUN`, `UNC_MC1_WRCAS_COUNT_FREERUN`, `UNC_M_ACT_COUNT_RD`, plus 20 more and verify the kernel accepts the encoding and returns plausible non-negative counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlaken/uncore-memory.json -->
