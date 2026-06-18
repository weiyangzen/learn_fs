<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlake/virtual-memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlake/virtual-memory.json

## Purpose
Defines Intel Alder Lake hybrid DTLB/ITLB miss and page-walk events for both `cpu_core` and `cpu_atom` PMUs, letting perf expose separate aliases for P-core and E-core virtual-memory behavior.

## APIs, Types, and Functions
The data contract is a perf PMU JSON array with 29 records: 29 raw event aliases and 0 derived metrics. Schema fields present are `BriefDescription`, `Counter`, `CounterMask`, `Data_LA`, `Deprecated`, `EventCode`, `EventName`, `PublicDescription`, `SampleAfterValue`, `UMask`, `Unit`. `jevents.py` maps `EventCode`, `UMask`, `CounterMask`, `MSRIndex`, `MSRValue`, `PerPkg`, `Deprecated`, `MetricExpr`, `MetricGroup`, and `ScaleUnit` into `struct pmu_event` or `struct pmu_metric` entries declared in `pmu-events.h`. Units resolve to `cpu_atom`, `cpu_core`. Representative names: `DTLB_LOAD_MISSES.STLB_HIT`, `DTLB_LOAD_MISSES.WALK_ACTIVE`, `DTLB_LOAD_MISSES.WALK_COMPLETED`, `DTLB_LOAD_MISSES.WALK_COMPLETED`, `DTLB_LOAD_MISSES.WALK_COMPLETED_1G`, `DTLB_LOAD_MISSES.WALK_COMPLETED_2M_4M`, `DTLB_LOAD_MISSES.WALK_COMPLETED_4K`, `DTLB_LOAD_MISSES.WALK_PENDING`, `DTLB_STORE_MISSES.STLB_HIT`, `DTLB_STORE_MISSES.WALK_ACTIVE`, plus 19 more. It also has 3 deprecated entries, 3 entries marked with `Data_LA`.

## Control Flow
Build control flow is data-driven: `jevents.py` reads this `virtual-memory` file, lowercases event aliases, converts `Unit` through `unit_to_pmu()`, canonicalizes event and umask encodings, and appends generated C strings to the model event table. Runtime perf reaches the records through `find_core_events_table()`, `find_sys_events_table()`, `pmu_events_table__find_event()`, and `pmu_events_table__for_each_event()` when `perf list`, `perf stat -e`, or metrics request the aliases.

## State and Persistence
The file has no executable state, locks, persistence layer, or runtime mutation. Its durable behavior is the generated perf event/metric table selected by x86 mapfile CPUID matching; kernel PMU drivers own counter state once a user selects an alias. Duplicate logical names exist for `DTLB_LOAD_MISSES.WALK_COMPLETED`, `DTLB_STORE_MISSES.WALK_COMPLETED`, `ITLB_MISSES.WALK_COMPLETED`, usually because separate PMUs or masks share a visible alias. Deprecated records persist in the generated tables so old event names can still be listed or redirected with deprecation metadata.

## Dependencies and Integration
Integrated by `tools/perf/pmu-events/arch/x86/mapfile.csv` selecting the `alderlake` directory for matching x86 CPU identifiers. Consumed by `jevents.py`, `pmu-events.h`, `builtin-list.c`, metric parsing, and PMU table lookup helpers. Unit-specific routing depends on `unit_to_pmu()` mappings for `cpu_atom`, `cpu_core`; missing `Unit` means the default core PMU.

## Risks
The main risk is semantic drift from the vendor performance-monitoring documentation: a wrong event code, umask, MSR filter, or PMU unit can make a friendly alias count the wrong hardware condition. This file has 3 deprecated entries, so consumers must prefer replacement names while preserving compatibility for older scripts. Hybrid `cpu_core` and `cpu_atom` entries intentionally share some names; tests must verify PMU disambiguation rather than treating duplicates as accidental.

## Test Signals
Run the perf pmu-events generator over `arch/x86` and the `tools/perf/tests/pmu-events.c` generated-table checks. Inspect `perf list --json` or generated C tables for representative aliases `DTLB_LOAD_MISSES.STLB_HIT`, `DTLB_LOAD_MISSES.WALK_ACTIVE`, `DTLB_LOAD_MISSES.WALK_COMPLETED`, `DTLB_LOAD_MISSES.WALK_COMPLETED`, `DTLB_LOAD_MISSES.WALK_COMPLETED_1G`, `DTLB_LOAD_MISSES.WALK_COMPLETED_2M_4M`, plus 23 more. On matching hardware, run `perf stat -e` for events such as `DTLB_LOAD_MISSES.STLB_HIT`, `DTLB_LOAD_MISSES.WALK_ACTIVE`, `DTLB_LOAD_MISSES.WALK_COMPLETED`, `DTLB_LOAD_MISSES.WALK_COMPLETED`, `DTLB_LOAD_MISSES.WALK_COMPLETED_1G`, plus 24 more and verify the kernel accepts the encoding and returns plausible non-negative counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlake/virtual-memory.json -->
