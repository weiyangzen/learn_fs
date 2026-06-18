<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen2/cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen2/cache.json

## Purpose
Defines AMD `amdzen2` L2 request, latency, write-combine, cache-state, fill, prefetch, probe, and L3PMC aliases for cache hierarchy analysis in perf.

## APIs, Types, and Functions
The data contract is a perf PMU JSON array with 60 records: 60 raw event aliases and 0 derived metrics. Schema fields present are `BriefDescription`, `EventCode`, `EventName`, `UMask`, `Unit`. `jevents.py` maps `EventCode`, `UMask`, `CounterMask`, `MSRIndex`, `MSRValue`, `PerPkg`, `Deprecated`, `MetricExpr`, `MetricGroup`, and `ScaleUnit` into `struct pmu_event` or `struct pmu_metric` entries declared in `pmu-events.h`. Units resolve to `L3PMC`, `default_core`. Representative names: `l2_request_g1.rd_blk_l`, `l2_request_g1.rd_blk_x`, `l2_request_g1.ls_rd_blk_c_s`, `l2_request_g1.cacheable_ic_read`, `l2_request_g1.change_to_x`, `l2_request_g1.prefetch_l2_cmd`, `l2_request_g1.l2_hw_pf`, `l2_request_g1.group2`, `l2_request_g1.all_no_prefetch`, `l2_request_g2.group1`, plus 50 more.

## Control Flow
Build control flow is data-driven: `jevents.py` reads this `cache` file, lowercases event aliases, converts `Unit` through `unit_to_pmu()`, canonicalizes event and umask encodings, and appends generated C strings to the model event table. Runtime perf reaches the records through `find_core_events_table()`, `find_sys_events_table()`, `pmu_events_table__find_event()`, and `pmu_events_table__for_each_event()` when `perf list`, `perf stat -e`, or metrics request the aliases.

## State and Persistence
The file has no executable state, locks, persistence layer, or runtime mutation. Its durable behavior is the generated perf event/metric table selected by x86 mapfile CPUID matching; kernel PMU drivers own counter state once a user selects an alias.

## Dependencies and Integration
Integrated by `tools/perf/pmu-events/arch/x86/mapfile.csv` selecting the `amdzen2` directory for matching x86 CPU identifiers. Consumed by `jevents.py`, `pmu-events.h`, `builtin-list.c`, metric parsing, and PMU table lookup helpers. Unit-specific routing depends on `unit_to_pmu()` mappings for `L3PMC`; missing `Unit` means the default core PMU.

## Risks
The main risk is semantic drift from the vendor performance-monitoring documentation: a wrong event code, umask, MSR filter, or PMU unit can make a friendly alias count the wrong hardware condition. AMD uncore-style units such as `L3PMC` and `DFPMC` depend on kernel PMU naming and package aggregation support; unsupported systems may list aliases that cannot be scheduled.

## Test Signals
Run the perf pmu-events generator over `arch/x86` and the `tools/perf/tests/pmu-events.c` generated-table checks. Inspect `perf list --json` or generated C tables for representative aliases `l2_request_g1.rd_blk_l`, `l2_request_g1.rd_blk_x`, `l2_request_g1.ls_rd_blk_c_s`, `l2_request_g1.cacheable_ic_read`, `l2_request_g1.change_to_x`, `l2_request_g1.prefetch_l2_cmd`, plus 54 more. On matching hardware, run `perf stat -e` for events such as `l2_request_g1.rd_blk_l`, `l2_request_g1.rd_blk_x`, `l2_request_g1.ls_rd_blk_c_s`, `l2_request_g1.cacheable_ic_read`, `l2_request_g1.change_to_x`, plus 55 more and verify the kernel accepts the encoding and returns plausible non-negative counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen2/cache.json -->
