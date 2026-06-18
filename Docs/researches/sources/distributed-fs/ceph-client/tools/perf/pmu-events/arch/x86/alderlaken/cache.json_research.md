<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlaken/cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlaken/cache.json

## Purpose
Defines Alder Lake-N core cache and memory-bound stall events, including L2 requests, LLC references, retired load hit/miss levels, scheduler blocking, split locks, and offcore-response cache outcomes.

## APIs, Types, and Functions
The data contract is a perf PMU JSON array with 64 records: 64 raw event aliases and 0 derived metrics. Schema fields present are `BriefDescription`, `Counter`, `Data_LA`, `EventCode`, `EventName`, `MSRIndex`, `MSRValue`, `PublicDescription`, `SampleAfterValue`, `UMask`. `jevents.py` maps `EventCode`, `UMask`, `CounterMask`, `MSRIndex`, `MSRValue`, `PerPkg`, `Deprecated`, `MetricExpr`, `MetricGroup`, and `ScaleUnit` into `struct pmu_event` or `struct pmu_metric` entries declared in `pmu-events.h`. Units resolve to `default_core`. Representative names: `L2_REQUEST.ALL`, `L2_REQUEST.HIT`, `L2_REQUEST.MISS`, `LONGEST_LAT_CACHE.MISS`, `LONGEST_LAT_CACHE.REFERENCE`, `MEM_BOUND_STALLS.IFETCH`, `MEM_BOUND_STALLS.IFETCH_DRAM_HIT`, `MEM_BOUND_STALLS.IFETCH_L2_HIT`, `MEM_BOUND_STALLS.IFETCH_LLC_HIT`, `MEM_BOUND_STALLS.LOAD`, plus 54 more. It also has 29 entries with MSR filters, 25 entries marked with `Data_LA`.

## Control Flow
Build control flow is data-driven: `jevents.py` reads this `cache` file, lowercases event aliases, converts `Unit` through `unit_to_pmu()`, canonicalizes event and umask encodings, and appends generated C strings to the model event table. Runtime perf reaches the records through `find_core_events_table()`, `find_sys_events_table()`, `pmu_events_table__find_event()`, and `pmu_events_table__for_each_event()` when `perf list`, `perf stat -e`, or metrics request the aliases.

## State and Persistence
The file has no executable state, locks, persistence layer, or runtime mutation. Its durable behavior is the generated perf event/metric table selected by x86 mapfile CPUID matching; kernel PMU drivers own counter state once a user selects an alias.

## Dependencies and Integration
Integrated by `tools/perf/pmu-events/arch/x86/mapfile.csv` selecting the `alderlaken` directory for matching x86 CPU identifiers. Consumed by `jevents.py`, `pmu-events.h`, `builtin-list.c`, metric parsing, and PMU table lookup helpers. All entries omit `Unit`, so `jevents.py` routes them to the default core PMU for this model.

## Risks
The main risk is semantic drift from the vendor performance-monitoring documentation: a wrong event code, umask, MSR filter, or PMU unit can make a friendly alias count the wrong hardware condition. MSR-filtered offcore response records are sensitive to exact `MSRIndex` and `MSRValue` encodings and can silently overlap if copied from a neighboring Intel model.

## Test Signals
Run the perf pmu-events generator over `arch/x86` and the `tools/perf/tests/pmu-events.c` generated-table checks. Inspect `perf list --json` or generated C tables for representative aliases `L2_REQUEST.ALL`, `L2_REQUEST.HIT`, `L2_REQUEST.MISS`, `LONGEST_LAT_CACHE.MISS`, `LONGEST_LAT_CACHE.REFERENCE`, `MEM_BOUND_STALLS.IFETCH`, plus 58 more. On matching hardware, run `perf stat -e` for events such as `L2_REQUEST.ALL`, `L2_REQUEST.HIT`, `L2_REQUEST.MISS`, `LONGEST_LAT_CACHE.MISS`, `LONGEST_LAT_CACHE.REFERENCE`, plus 59 more and verify the kernel accepts the encoding and returns plausible non-negative counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlaken/cache.json -->
