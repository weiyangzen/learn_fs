<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlaken/virtual-memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlaken/virtual-memory.json

## Purpose
Defines Alder Lake-N DTLB, ITLB, load-head, and retired memory-uop virtual-memory events used to diagnose page walks, STLB misses, and address-translation retirement stalls.

## APIs, Types, and Functions
The data contract is a perf PMU JSON array with 9 records: 9 raw event aliases and 0 derived metrics. Schema fields present are `BriefDescription`, `Counter`, `Data_LA`, `Deprecated`, `EventCode`, `EventName`, `PublicDescription`, `SampleAfterValue`, `UMask`. `jevents.py` maps `EventCode`, `UMask`, `CounterMask`, `MSRIndex`, `MSRValue`, `PerPkg`, `Deprecated`, `MetricExpr`, `MetricGroup`, and `ScaleUnit` into `struct pmu_event` or `struct pmu_metric` entries declared in `pmu-events.h`. Units resolve to `default_core`. Representative names: `DTLB_LOAD_MISSES.WALK_COMPLETED`, `DTLB_STORE_MISSES.WALK_COMPLETED`, `ITLB_MISSES.MISS_CAUSED_WALK`, `ITLB_MISSES.PDE_CACHE_MISS`, `ITLB_MISSES.WALK_COMPLETED`, `LD_HEAD.DTLB_MISS_AT_RET`, `MEM_UOPS_RETIRED.DTLB_MISS`, `MEM_UOPS_RETIRED.DTLB_MISS_LOADS`, `MEM_UOPS_RETIRED.DTLB_MISS_STORES`. It also has 3 deprecated entries, 3 entries marked with `Data_LA`.

## Control Flow
Build control flow is data-driven: `jevents.py` reads this `virtual-memory` file, lowercases event aliases, converts `Unit` through `unit_to_pmu()`, canonicalizes event and umask encodings, and appends generated C strings to the model event table. Runtime perf reaches the records through `find_core_events_table()`, `find_sys_events_table()`, `pmu_events_table__find_event()`, and `pmu_events_table__for_each_event()` when `perf list`, `perf stat -e`, or metrics request the aliases.

## State and Persistence
The file has no executable state, locks, persistence layer, or runtime mutation. Its durable behavior is the generated perf event/metric table selected by x86 mapfile CPUID matching; kernel PMU drivers own counter state once a user selects an alias. Deprecated records persist in the generated tables so old event names can still be listed or redirected with deprecation metadata.

## Dependencies and Integration
Integrated by `tools/perf/pmu-events/arch/x86/mapfile.csv` selecting the `alderlaken` directory for matching x86 CPU identifiers. Consumed by `jevents.py`, `pmu-events.h`, `builtin-list.c`, metric parsing, and PMU table lookup helpers. All entries omit `Unit`, so `jevents.py` routes them to the default core PMU for this model.

## Risks
The main risk is semantic drift from the vendor performance-monitoring documentation: a wrong event code, umask, MSR filter, or PMU unit can make a friendly alias count the wrong hardware condition. This file has 3 deprecated entries, so consumers must prefer replacement names while preserving compatibility for older scripts.

## Test Signals
Run the perf pmu-events generator over `arch/x86` and the `tools/perf/tests/pmu-events.c` generated-table checks. Inspect `perf list --json` or generated C tables for representative aliases `DTLB_LOAD_MISSES.WALK_COMPLETED`, `DTLB_STORE_MISSES.WALK_COMPLETED`, `ITLB_MISSES.MISS_CAUSED_WALK`, `ITLB_MISSES.PDE_CACHE_MISS`, `ITLB_MISSES.WALK_COMPLETED`, `LD_HEAD.DTLB_MISS_AT_RET`, plus 3 more. On matching hardware, run `perf stat -e` for events such as `DTLB_LOAD_MISSES.WALK_COMPLETED`, `DTLB_STORE_MISSES.WALK_COMPLETED`, `ITLB_MISSES.MISS_CAUSED_WALK`, `ITLB_MISSES.PDE_CACHE_MISS`, `ITLB_MISSES.WALK_COMPLETED`, plus 4 more and verify the kernel accepts the encoding and returns plausible non-negative counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlaken/virtual-memory.json -->
