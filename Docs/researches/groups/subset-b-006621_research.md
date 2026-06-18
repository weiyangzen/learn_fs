# subset-b-006621 Research

Grouped research for `subset-b-006621`. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlaken/adln-metrics.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlaken/adln-metrics.json

## Purpose
Defines derived Intel Alder Lake-N metrics for perf, including package/core C-state residency, SMI accounting, topdown TMA levels, frontend/backend bottlenecks, memory execution ratios, load/store miss accounting, and floating-point operation mix.

## APIs, Types, and Functions
The data contract is a perf PMU JSON array with 94 records: 0 raw event aliases and 94 derived metrics. Schema fields present are `BriefDescription`, `DefaultMetricgroupName`, `MetricExpr`, `MetricGroup`, `MetricName`, `MetricThreshold`, `MetricgroupNoGroup`, `PublicDescription`, `ScaleUnit`. `jevents.py` maps `EventCode`, `UMask`, `CounterMask`, `MSRIndex`, `MSRValue`, `PerPkg`, `Deprecated`, `MetricExpr`, `MetricGroup`, and `ScaleUnit` into `struct pmu_event` or `struct pmu_metric` entries declared in `pmu-events.h`. Units resolve to `default_core`. Representative names: `C10_Pkg_Residency`, `C1_Core_Residency`, `C2_Pkg_Residency`, `C3_Pkg_Residency`, `C6_Core_Residency`, `C6_Pkg_Residency`, `C7_Core_Residency`, `C8_Pkg_Residency`, `smi_cycles`, `smi_num`, plus 84 more.

## Control Flow
Build control flow is data-driven: `process_one_file()` assigns a model table for the leaf x86 directory, `read_json_events()` creates one `PmuEvent` per JSON object, and metric expressions are parsed by `metric.ParsePerfJson(...).Simplify()`. The 94 metrics reference tokens such as `BACLEARS.ANY`, `BR_INST_RETIRED.ALL_BRANCHES`, `BR_INST_RETIRED.CALL`, `BR_INST_RETIRED.FAR_BRANCH`, `BR_MISP_RETIRED.ALL_BRANCHES`, `BR_MISP_RETIRED.COND`, `BR_MISP_RETIRED.COND_TAKEN`, `BR_MISP_RETIRED.INDIRECT`, `BR_MISP_RETIRED.RETURN`, `CPU_CLK_UNHALTED.CORE`, `CPU_CLK_UNHALTED.CORE_P`, `CPU_CLK_UNHALTED.REF_TSC`, plus 79 more; at runtime `perf stat -M` resolves those names against generated PMU tables and evaluates the formulas over counter groups selected for the matching CPUID.

## State and Persistence
The file has no executable state, locks, persistence layer, or runtime mutation. Its durable behavior is the generated perf event/metric table selected by x86 mapfile CPUID matching; kernel PMU drivers own counter state once a user selects an alias.

## Dependencies and Integration
Integrated by `tools/perf/pmu-events/arch/x86/mapfile.csv` selecting the `alderlaken` directory for matching x86 CPU identifiers. Consumed by `jevents.py`, `pmu-events.h`, `builtin-list.c`, metric parsing, and PMU table lookup helpers. All entries omit `Unit`, so `jevents.py` routes them to the default core PMU for this model. Metric integration also depends on expression-token resolution, `MetricConstraint` grouping policy, `ScaleUnit`, `MetricThreshold`, and metric groups `Default;TopdownL1;tma_L1_group`, `Ifetch`, `Load_Store_Miss`, `Mem_Exec`, `Power`, `Summary`, `TopdownL2;tma_L2_group;tma_backend_bound_group`, `TopdownL2;tma_L2_group;tma_bad_speculation_group`, plus 8 more.

## Risks
The main risk is semantic drift from the vendor performance-monitoring documentation: a wrong event code, umask, MSR filter, or PMU unit can make a friendly alias count the wrong hardware condition. Metric formulas can fail or mislead if referenced aliases are unavailable, event grouping cannot be scheduled, `#slots` or topdown constants are wrong for the CPU, or denominators are zero on short samples. The `MetricThreshold` strings are carried as text rather than parsed like `MetricExpr`, so threshold syntax changes need explicit perf UI validation.

## Test Signals
Run the perf pmu-events generator over `arch/x86` and the `tools/perf/tests/pmu-events.c` generated-table checks. Inspect `perf list --json` or generated C tables for representative aliases `C10_Pkg_Residency`, `C1_Core_Residency`, `C2_Pkg_Residency`, `C3_Pkg_Residency`, `C6_Core_Residency`, `C6_Pkg_Residency`, plus 88 more. On matching hardware, run `perf stat -M` for metrics such as `C10_Pkg_Residency`, `C1_Core_Residency`, `C2_Pkg_Residency`, `C3_Pkg_Residency`, `C6_Core_Residency`, plus 89 more and verify expression parsing, grouping, scaling, and thresholds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlaken/adln-metrics.json -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlaken/floating-point.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlaken/floating-point.json

## Purpose
Defines Alder Lake-N floating-point divider, FP assist, and retired FP division aliases.

## APIs, Types, and Functions
The data contract is a perf PMU JSON array with 4 records: 4 raw event aliases and 0 derived metrics. Schema fields present are `BriefDescription`, `Counter`, `EventCode`, `EventName`, `PublicDescription`, `SampleAfterValue`, `UMask`. `jevents.py` maps `EventCode`, `UMask`, `CounterMask`, `MSRIndex`, `MSRValue`, `PerPkg`, `Deprecated`, `MetricExpr`, `MetricGroup`, and `ScaleUnit` into `struct pmu_event` or `struct pmu_metric` entries declared in `pmu-events.h`. Units resolve to `default_core`. Representative names: `ARITH.FPDIV_ACTIVE`, `ARITH.FPDIV_UOPS`, `MACHINE_CLEARS.FP_ASSIST`, `UOPS_RETIRED.FPDIV`.

## Control Flow
Build control flow is data-driven: `jevents.py` reads this `floating-point` file, lowercases event aliases, converts `Unit` through `unit_to_pmu()`, canonicalizes event and umask encodings, and appends generated C strings to the model event table. Runtime perf reaches the records through `find_core_events_table()`, `find_sys_events_table()`, `pmu_events_table__find_event()`, and `pmu_events_table__for_each_event()` when `perf list`, `perf stat -e`, or metrics request the aliases.

## State and Persistence
The file has no executable state, locks, persistence layer, or runtime mutation. Its durable behavior is the generated perf event/metric table selected by x86 mapfile CPUID matching; kernel PMU drivers own counter state once a user selects an alias.

## Dependencies and Integration
Integrated by `tools/perf/pmu-events/arch/x86/mapfile.csv` selecting the `alderlaken` directory for matching x86 CPU identifiers. Consumed by `jevents.py`, `pmu-events.h`, `builtin-list.c`, metric parsing, and PMU table lookup helpers. All entries omit `Unit`, so `jevents.py` routes them to the default core PMU for this model.

## Risks
The main risk is semantic drift from the vendor performance-monitoring documentation: a wrong event code, umask, MSR filter, or PMU unit can make a friendly alias count the wrong hardware condition.

## Test Signals
Run the perf pmu-events generator over `arch/x86` and the `tools/perf/tests/pmu-events.c` generated-table checks. Inspect `perf list --json` or generated C tables for representative aliases `ARITH.FPDIV_ACTIVE`, `ARITH.FPDIV_UOPS`, `MACHINE_CLEARS.FP_ASSIST`, `UOPS_RETIRED.FPDIV`. On matching hardware, run `perf stat -e` for events such as `ARITH.FPDIV_ACTIVE`, `ARITH.FPDIV_UOPS`, `MACHINE_CLEARS.FP_ASSIST`, `UOPS_RETIRED.FPDIV` and verify the kernel accepts the encoding and returns plausible non-negative counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlaken/floating-point.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlaken/frontend.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlaken/frontend.json

## Purpose
Defines Alder Lake-N frontend aliases for BACLEARs and instruction-cache access/miss accounting.

## APIs, Types, and Functions
The data contract is a perf PMU JSON array with 3 records: 3 raw event aliases and 0 derived metrics. Schema fields present are `BriefDescription`, `Counter`, `EventCode`, `EventName`, `PublicDescription`, `SampleAfterValue`, `UMask`. `jevents.py` maps `EventCode`, `UMask`, `CounterMask`, `MSRIndex`, `MSRValue`, `PerPkg`, `Deprecated`, `MetricExpr`, `MetricGroup`, and `ScaleUnit` into `struct pmu_event` or `struct pmu_metric` entries declared in `pmu-events.h`. Units resolve to `default_core`. Representative names: `BACLEARS.ANY`, `ICACHE.ACCESSES`, `ICACHE.MISSES`.

## Control Flow
Build control flow is data-driven: `jevents.py` reads this `frontend` file, lowercases event aliases, converts `Unit` through `unit_to_pmu()`, canonicalizes event and umask encodings, and appends generated C strings to the model event table. Runtime perf reaches the records through `find_core_events_table()`, `find_sys_events_table()`, `pmu_events_table__find_event()`, and `pmu_events_table__for_each_event()` when `perf list`, `perf stat -e`, or metrics request the aliases.

## State and Persistence
The file has no executable state, locks, persistence layer, or runtime mutation. Its durable behavior is the generated perf event/metric table selected by x86 mapfile CPUID matching; kernel PMU drivers own counter state once a user selects an alias.

## Dependencies and Integration
Integrated by `tools/perf/pmu-events/arch/x86/mapfile.csv` selecting the `alderlaken` directory for matching x86 CPU identifiers. Consumed by `jevents.py`, `pmu-events.h`, `builtin-list.c`, metric parsing, and PMU table lookup helpers. All entries omit `Unit`, so `jevents.py` routes them to the default core PMU for this model.

## Risks
The main risk is semantic drift from the vendor performance-monitoring documentation: a wrong event code, umask, MSR filter, or PMU unit can make a friendly alias count the wrong hardware condition.

## Test Signals
Run the perf pmu-events generator over `arch/x86` and the `tools/perf/tests/pmu-events.c` generated-table checks. Inspect `perf list --json` or generated C tables for representative aliases `BACLEARS.ANY`, `ICACHE.ACCESSES`, `ICACHE.MISSES`. On matching hardware, run `perf stat -e` for events such as `BACLEARS.ANY`, `ICACHE.ACCESSES`, `ICACHE.MISSES` and verify the kernel accepts the encoding and returns plausible non-negative counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlaken/frontend.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlaken/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlaken/memory.json

## Purpose
Defines Alder Lake-N load-head retirement classifications, memory-ordering machine clears, and offcore-response demand/code/RFO/software-prefetch DRAM and L3-miss events.

## APIs, Types, and Functions
The data contract is a perf PMU JSON array with 17 records: 17 raw event aliases and 0 derived metrics. Schema fields present are `BriefDescription`, `Counter`, `EventCode`, `EventName`, `MSRIndex`, `MSRValue`, `PublicDescription`, `SampleAfterValue`, `UMask`. `jevents.py` maps `EventCode`, `UMask`, `CounterMask`, `MSRIndex`, `MSRValue`, `PerPkg`, `Deprecated`, `MetricExpr`, `MetricGroup`, and `ScaleUnit` into `struct pmu_event` or `struct pmu_metric` entries declared in `pmu-events.h`. Units resolve to `default_core`. Representative names: `LD_HEAD.ANY_AT_RET`, `LD_HEAD.L1_BOUND_AT_RET`, `LD_HEAD.L1_MISS_AT_RET`, `LD_HEAD.OTHER_AT_RET`, `LD_HEAD.PGWALK_AT_RET`, `LD_HEAD.ST_ADDR_AT_RET`, `MACHINE_CLEARS.MEMORY_ORDERING`, `OCR.DEMAND_CODE_RD.DRAM`, `OCR.DEMAND_CODE_RD.L3_MISS`, `OCR.DEMAND_DATA_RD.DRAM`, plus 7 more. It also has 10 entries with MSR filters.

## Control Flow
Build control flow is data-driven: `jevents.py` reads this `memory` file, lowercases event aliases, converts `Unit` through `unit_to_pmu()`, canonicalizes event and umask encodings, and appends generated C strings to the model event table. Runtime perf reaches the records through `find_core_events_table()`, `find_sys_events_table()`, `pmu_events_table__find_event()`, and `pmu_events_table__for_each_event()` when `perf list`, `perf stat -e`, or metrics request the aliases.

## State and Persistence
The file has no executable state, locks, persistence layer, or runtime mutation. Its durable behavior is the generated perf event/metric table selected by x86 mapfile CPUID matching; kernel PMU drivers own counter state once a user selects an alias.

## Dependencies and Integration
Integrated by `tools/perf/pmu-events/arch/x86/mapfile.csv` selecting the `alderlaken` directory for matching x86 CPU identifiers. Consumed by `jevents.py`, `pmu-events.h`, `builtin-list.c`, metric parsing, and PMU table lookup helpers. All entries omit `Unit`, so `jevents.py` routes them to the default core PMU for this model.

## Risks
The main risk is semantic drift from the vendor performance-monitoring documentation: a wrong event code, umask, MSR filter, or PMU unit can make a friendly alias count the wrong hardware condition. MSR-filtered offcore response records are sensitive to exact `MSRIndex` and `MSRValue` encodings and can silently overlap if copied from a neighboring Intel model.

## Test Signals
Run the perf pmu-events generator over `arch/x86` and the `tools/perf/tests/pmu-events.c` generated-table checks. Inspect `perf list --json` or generated C tables for representative aliases `LD_HEAD.ANY_AT_RET`, `LD_HEAD.L1_BOUND_AT_RET`, `LD_HEAD.L1_MISS_AT_RET`, `LD_HEAD.OTHER_AT_RET`, `LD_HEAD.PGWALK_AT_RET`, `LD_HEAD.ST_ADDR_AT_RET`, plus 11 more. On matching hardware, run `perf stat -e` for events such as `LD_HEAD.ANY_AT_RET`, `LD_HEAD.L1_BOUND_AT_RET`, `LD_HEAD.L1_MISS_AT_RET`, `LD_HEAD.OTHER_AT_RET`, `LD_HEAD.PGWALK_AT_RET`, plus 12 more and verify the kernel accepts the encoding and returns plausible non-negative counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlaken/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlaken/metricgroups.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlaken/metricgroups.json

## Purpose
Documents the metric-group descriptions for the Intel `alderlaken` perf model. The file is not a counter table; it gives human-readable help for metric group names that appear in sibling `MetricGroup` fields and in `perf list metricgroups` output.

## APIs, Types, and Functions
This file is a JSON object rather than a JSON event array. `jevents.py` detects the `metricgroups.json` suffix, loads each key/value pair into `_metricgroups`, stores the strings in the generated big C string table, and emits them through `describe_metricgroup()`. It defines 21 groups: `Flops`, `Ifetch`, `Load_Store_Miss`, `Mem_Exec`, `Power`, `Summary`, `TopdownL1`, `TopdownL2`, `TopdownL3`, `load_store_bound`, `tma_L1_group`, `tma_L2_group`, plus 9 more.

## Control Flow
During the pmu-events build, directory walking sees this file before normal event insertion for the model. The generator does not create counters from it; it only records sorted group descriptions that runtime perf queries when listing or explaining metric groups.

## State and Persistence
The JSON object has no mutable runtime state. Its persistent state is the group-name-to-description mapping compiled into generated perf tables; changes are visible only after rebuilding perf's pmu-events output.

## Dependencies and Integration
Depends on sibling `alderlaken` metric files that name these groups, on `jevents.py` metric-group handling, and on `describe_metricgroup()` consumers in perf list/stat UI code. The group names must remain byte-for-byte stable with `MetricGroup`, `DefaultMetricgroupName`, and related fields.

## Risks
Risks are name drift and stale documentation: if a metric moves groups or a group is renamed without updating this object, `perf list metricgroups` and metric help become misleading while metrics still parse. Sorting and duplicate group names should also be watched because `describe_metricgroup()` uses generated lookup tables.

## Test Signals
Test by rebuilding generated pmu-events output, running the pmu-events unit tests that exercise `describe_metricgroup()`, and checking `perf list metricgroups` on an x86 build for representative groups such as `TopdownL1`, `Power`, and `tma_backend_bound_group`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlaken/metricgroups.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlaken/other.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlaken/other.json

## Purpose
Defines Alder Lake-N miscellaneous LBR insertion and streaming-write offcore response aliases.

## APIs, Types, and Functions
The data contract is a perf PMU JSON array with 4 records: 4 raw event aliases and 0 derived metrics. Schema fields present are `BriefDescription`, `Counter`, `Deprecated`, `EventCode`, `EventName`, `MSRIndex`, `MSRValue`, `PublicDescription`, `SampleAfterValue`, `UMask`. `jevents.py` maps `EventCode`, `UMask`, `CounterMask`, `MSRIndex`, `MSRValue`, `PerPkg`, `Deprecated`, `MetricExpr`, `MetricGroup`, and `ScaleUnit` into `struct pmu_event` or `struct pmu_metric` entries declared in `pmu-events.h`. Units resolve to `default_core`. Representative names: `LBR_INSERTS.ANY`, `OCR.FULL_STREAMING_WR.ANY_RESPONSE`, `OCR.PARTIAL_STREAMING_WR.ANY_RESPONSE`, `OCR.STREAMING_WR.ANY_RESPONSE`. It also has 1 deprecated entries, 3 entries with MSR filters.

## Control Flow
Build control flow is data-driven: `jevents.py` reads this `other` file, lowercases event aliases, converts `Unit` through `unit_to_pmu()`, canonicalizes event and umask encodings, and appends generated C strings to the model event table. Runtime perf reaches the records through `find_core_events_table()`, `find_sys_events_table()`, `pmu_events_table__find_event()`, and `pmu_events_table__for_each_event()` when `perf list`, `perf stat -e`, or metrics request the aliases.

## State and Persistence
The file has no executable state, locks, persistence layer, or runtime mutation. Its durable behavior is the generated perf event/metric table selected by x86 mapfile CPUID matching; kernel PMU drivers own counter state once a user selects an alias. Deprecated records persist in the generated tables so old event names can still be listed or redirected with deprecation metadata.

## Dependencies and Integration
Integrated by `tools/perf/pmu-events/arch/x86/mapfile.csv` selecting the `alderlaken` directory for matching x86 CPU identifiers. Consumed by `jevents.py`, `pmu-events.h`, `builtin-list.c`, metric parsing, and PMU table lookup helpers. All entries omit `Unit`, so `jevents.py` routes them to the default core PMU for this model.

## Risks
The main risk is semantic drift from the vendor performance-monitoring documentation: a wrong event code, umask, MSR filter, or PMU unit can make a friendly alias count the wrong hardware condition. This file has 1 deprecated entries, so consumers must prefer replacement names while preserving compatibility for older scripts. MSR-filtered offcore response records are sensitive to exact `MSRIndex` and `MSRValue` encodings and can silently overlap if copied from a neighboring Intel model.

## Test Signals
Run the perf pmu-events generator over `arch/x86` and the `tools/perf/tests/pmu-events.c` generated-table checks. Inspect `perf list --json` or generated C tables for representative aliases `LBR_INSERTS.ANY`, `OCR.FULL_STREAMING_WR.ANY_RESPONSE`, `OCR.PARTIAL_STREAMING_WR.ANY_RESPONSE`, `OCR.STREAMING_WR.ANY_RESPONSE`. On matching hardware, run `perf stat -e` for events such as `LBR_INSERTS.ANY`, `OCR.FULL_STREAMING_WR.ANY_RESPONSE`, `OCR.PARTIAL_STREAMING_WR.ANY_RESPONSE`, `OCR.STREAMING_WR.ANY_RESPONSE` and verify the kernel accepts the encoding and returns plausible non-negative counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlaken/other.json -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlaken/uncore-interconnect.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlaken/uncore-interconnect.json

## Purpose
Defines Alder Lake-N uncore ARB interconnect occupancy/request events for package-level fabric tracking.

## APIs, Types, and Functions
The data contract is a perf PMU JSON array with 11 records: 11 raw event aliases and 0 derived metrics. Schema fields present are `BriefDescription`, `Counter`, `Deprecated`, `EventCode`, `EventName`, `Experimental`, `PerPkg`, `UMask`, `Unit`. `jevents.py` maps `EventCode`, `UMask`, `CounterMask`, `MSRIndex`, `MSRValue`, `PerPkg`, `Deprecated`, `MetricExpr`, `MetricGroup`, and `ScaleUnit` into `struct pmu_event` or `struct pmu_metric` entries declared in `pmu-events.h`. Units resolve to `ARB`. Representative names: `UNC_ARB_COH_TRK_REQUESTS.ALL`, `UNC_ARB_DAT_OCCUPANCY.ALL`, `UNC_ARB_DAT_OCCUPANCY.RD`, `UNC_ARB_DAT_REQUESTS.RD`, `UNC_ARB_IFA_OCCUPANCY.ALL`, `UNC_ARB_REQ_TRK_OCCUPANCY.DRD`, `UNC_ARB_REQ_TRK_REQUEST.DRD`, `UNC_ARB_TRK_OCCUPANCY.ALL`, `UNC_ARB_TRK_OCCUPANCY.RD`, `UNC_ARB_TRK_REQUESTS.ALL`, plus 1 more. It also has 2 deprecated entries.

## Control Flow
Build control flow is data-driven: `jevents.py` reads this `uncore-interconnect` file, lowercases event aliases, converts `Unit` through `unit_to_pmu()`, canonicalizes event and umask encodings, and appends generated C strings to the model event table. Runtime perf reaches the records through `find_core_events_table()`, `find_sys_events_table()`, `pmu_events_table__find_event()`, and `pmu_events_table__for_each_event()` when `perf list`, `perf stat -e`, or metrics request the aliases.

## State and Persistence
The file has no executable state, locks, persistence layer, or runtime mutation. Its durable behavior is the generated perf event/metric table selected by x86 mapfile CPUID matching; kernel PMU drivers own counter state once a user selects an alias. Deprecated records persist in the generated tables so old event names can still be listed or redirected with deprecation metadata.

## Dependencies and Integration
Integrated by `tools/perf/pmu-events/arch/x86/mapfile.csv` selecting the `alderlaken` directory for matching x86 CPU identifiers. Consumed by `jevents.py`, `pmu-events.h`, `builtin-list.c`, metric parsing, and PMU table lookup helpers. Unit-specific routing depends on `unit_to_pmu()` mappings for `ARB`; missing `Unit` means the default core PMU. Entries with `PerPkg` require package-level aggregation behavior in perf's uncore/sys PMU handling.

## Risks
The main risk is semantic drift from the vendor performance-monitoring documentation: a wrong event code, umask, MSR filter, or PMU unit can make a friendly alias count the wrong hardware condition. This file has 2 deprecated entries, so consumers must prefer replacement names while preserving compatibility for older scripts. Uncore events need package/socket aggregation checks because counter availability and naming can differ from core PMU events.

## Test Signals
Run the perf pmu-events generator over `arch/x86` and the `tools/perf/tests/pmu-events.c` generated-table checks. Inspect `perf list --json` or generated C tables for representative aliases `UNC_ARB_COH_TRK_REQUESTS.ALL`, `UNC_ARB_DAT_OCCUPANCY.ALL`, `UNC_ARB_DAT_OCCUPANCY.RD`, `UNC_ARB_DAT_REQUESTS.RD`, `UNC_ARB_IFA_OCCUPANCY.ALL`, `UNC_ARB_REQ_TRK_OCCUPANCY.DRD`, plus 5 more. On matching hardware, run `perf stat -e` for events such as `UNC_ARB_COH_TRK_REQUESTS.ALL`, `UNC_ARB_DAT_OCCUPANCY.ALL`, `UNC_ARB_DAT_OCCUPANCY.RD`, `UNC_ARB_DAT_REQUESTS.RD`, `UNC_ARB_IFA_OCCUPANCY.ALL`, plus 6 more and verify the kernel accepts the encoding and returns plausible non-negative counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlaken/uncore-interconnect.json -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlaken/uncore-other.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlaken/uncore-other.json

## Purpose
Defines the Alder Lake-N package clock uncore event `UNC_CLOCK.SOCKET`.

## APIs, Types, and Functions
The data contract is a perf PMU JSON array with 1 records: 1 raw event aliases and 0 derived metrics. Schema fields present are `BriefDescription`, `Counter`, `EventCode`, `EventName`, `PerPkg`, `Unit`. `jevents.py` maps `EventCode`, `UMask`, `CounterMask`, `MSRIndex`, `MSRValue`, `PerPkg`, `Deprecated`, `MetricExpr`, `MetricGroup`, and `ScaleUnit` into `struct pmu_event` or `struct pmu_metric` entries declared in `pmu-events.h`. Units resolve to `CLOCK`. Representative names: `UNC_CLOCK.SOCKET`.

## Control Flow
Build control flow is data-driven: `jevents.py` reads this `uncore-other` file, lowercases event aliases, converts `Unit` through `unit_to_pmu()`, canonicalizes event and umask encodings, and appends generated C strings to the model event table. Runtime perf reaches the records through `find_core_events_table()`, `find_sys_events_table()`, `pmu_events_table__find_event()`, and `pmu_events_table__for_each_event()` when `perf list`, `perf stat -e`, or metrics request the aliases.

## State and Persistence
The file has no executable state, locks, persistence layer, or runtime mutation. Its durable behavior is the generated perf event/metric table selected by x86 mapfile CPUID matching; kernel PMU drivers own counter state once a user selects an alias.

## Dependencies and Integration
Integrated by `tools/perf/pmu-events/arch/x86/mapfile.csv` selecting the `alderlaken` directory for matching x86 CPU identifiers. Consumed by `jevents.py`, `pmu-events.h`, `builtin-list.c`, metric parsing, and PMU table lookup helpers. Unit-specific routing depends on `unit_to_pmu()` mappings for `CLOCK`; missing `Unit` means the default core PMU. Entries with `PerPkg` require package-level aggregation behavior in perf's uncore/sys PMU handling.

## Risks
The main risk is semantic drift from the vendor performance-monitoring documentation: a wrong event code, umask, MSR filter, or PMU unit can make a friendly alias count the wrong hardware condition. Uncore events need package/socket aggregation checks because counter availability and naming can differ from core PMU events.

## Test Signals
Run the perf pmu-events generator over `arch/x86` and the `tools/perf/tests/pmu-events.c` generated-table checks. Inspect `perf list --json` or generated C tables for representative aliases `UNC_CLOCK.SOCKET`. On matching hardware, run `perf stat -e` for events such as `UNC_CLOCK.SOCKET` and verify the kernel accepts the encoding and returns plausible non-negative counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlaken/uncore-other.json -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen1/cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen1/cache.json

## Purpose
Defines AMD `amdzen1` L2 request, latency, write-combine, cache-state, fill, prefetch, probe, and L3PMC aliases for cache hierarchy analysis in perf.

## APIs, Types, and Functions
The data contract is a perf PMU JSON array with 56 records: 56 raw event aliases and 0 derived metrics. Schema fields present are `BriefDescription`, `EventCode`, `EventName`, `UMask`, `Unit`. `jevents.py` maps `EventCode`, `UMask`, `CounterMask`, `MSRIndex`, `MSRValue`, `PerPkg`, `Deprecated`, `MetricExpr`, `MetricGroup`, and `ScaleUnit` into `struct pmu_event` or `struct pmu_metric` entries declared in `pmu-events.h`. Units resolve to `L3PMC`, `default_core`. Representative names: `ic_fw32`, `ic_fw32_miss`, `ic_cache_fill_l2`, `ic_cache_fill_sys`, `bp_l1_tlb_miss_l2_hit`, `bp_l1_tlb_miss_l2_miss`, `bp_snp_re_sync`, `ic_fetch_stall.ic_stall_any`, `ic_fetch_stall.ic_stall_dq_empty`, `ic_fetch_stall.ic_stall_back_pressure`, plus 46 more.

## Control Flow
Build control flow is data-driven: `jevents.py` reads this `cache` file, lowercases event aliases, converts `Unit` through `unit_to_pmu()`, canonicalizes event and umask encodings, and appends generated C strings to the model event table. Runtime perf reaches the records through `find_core_events_table()`, `find_sys_events_table()`, `pmu_events_table__find_event()`, and `pmu_events_table__for_each_event()` when `perf list`, `perf stat -e`, or metrics request the aliases.

## State and Persistence
The file has no executable state, locks, persistence layer, or runtime mutation. Its durable behavior is the generated perf event/metric table selected by x86 mapfile CPUID matching; kernel PMU drivers own counter state once a user selects an alias.

## Dependencies and Integration
Integrated by `tools/perf/pmu-events/arch/x86/mapfile.csv` selecting the `amdzen1` directory for matching x86 CPU identifiers. Consumed by `jevents.py`, `pmu-events.h`, `builtin-list.c`, metric parsing, and PMU table lookup helpers. Unit-specific routing depends on `unit_to_pmu()` mappings for `L3PMC`; missing `Unit` means the default core PMU.

## Risks
The main risk is semantic drift from the vendor performance-monitoring documentation: a wrong event code, umask, MSR filter, or PMU unit can make a friendly alias count the wrong hardware condition. AMD uncore-style units such as `L3PMC` and `DFPMC` depend on kernel PMU naming and package aggregation support; unsupported systems may list aliases that cannot be scheduled.

## Test Signals
Run the perf pmu-events generator over `arch/x86` and the `tools/perf/tests/pmu-events.c` generated-table checks. Inspect `perf list --json` or generated C tables for representative aliases `ic_fw32`, `ic_fw32_miss`, `ic_cache_fill_l2`, `ic_cache_fill_sys`, `bp_l1_tlb_miss_l2_hit`, `bp_l1_tlb_miss_l2_miss`, plus 50 more. On matching hardware, run `perf stat -e` for events such as `ic_fw32`, `ic_fw32_miss`, `ic_cache_fill_l2`, `ic_cache_fill_sys`, `bp_l1_tlb_miss_l2_hit`, plus 51 more and verify the kernel accepts the encoding and returns plausible non-negative counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen1/cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen1/core.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen1/core.json

## Purpose
Defines AMD `amdzen1` core retirement and execution aliases for retired instructions/uops/branches, mispredictions, returns, conditional branches, divide activity, IBS-tagged ops, and fused branches.

## APIs, Types, and Functions
The data contract is a perf PMU JSON array with 21 records: 21 raw event aliases and 0 derived metrics. Schema fields present are `BriefDescription`, `EventCode`, `EventName`, `PublicDescription`, `UMask`. `jevents.py` maps `EventCode`, `UMask`, `CounterMask`, `MSRIndex`, `MSRValue`, `PerPkg`, `Deprecated`, `MetricExpr`, `MetricGroup`, and `ScaleUnit` into `struct pmu_event` or `struct pmu_metric` entries declared in `pmu-events.h`. Units resolve to `default_core`. Representative names: `ex_ret_instr`, `ex_ret_cops`, `ex_ret_brn`, `ex_ret_brn_misp`, `ex_ret_brn_tkn`, `ex_ret_brn_tkn_misp`, `ex_ret_brn_far`, `ex_ret_brn_resync`, `ex_ret_near_ret`, `ex_ret_near_ret_mispred`, plus 11 more.

## Control Flow
Build control flow is data-driven: `jevents.py` reads this `core` file, lowercases event aliases, converts `Unit` through `unit_to_pmu()`, canonicalizes event and umask encodings, and appends generated C strings to the model event table. Runtime perf reaches the records through `find_core_events_table()`, `find_sys_events_table()`, `pmu_events_table__find_event()`, and `pmu_events_table__for_each_event()` when `perf list`, `perf stat -e`, or metrics request the aliases.

## State and Persistence
The file has no executable state, locks, persistence layer, or runtime mutation. Its durable behavior is the generated perf event/metric table selected by x86 mapfile CPUID matching; kernel PMU drivers own counter state once a user selects an alias.

## Dependencies and Integration
Integrated by `tools/perf/pmu-events/arch/x86/mapfile.csv` selecting the `amdzen1` directory for matching x86 CPU identifiers. Consumed by `jevents.py`, `pmu-events.h`, `builtin-list.c`, metric parsing, and PMU table lookup helpers. All entries omit `Unit`, so `jevents.py` routes them to the default core PMU for this model.

## Risks
The main risk is semantic drift from the vendor performance-monitoring documentation: a wrong event code, umask, MSR filter, or PMU unit can make a friendly alias count the wrong hardware condition.

## Test Signals
Run the perf pmu-events generator over `arch/x86` and the `tools/perf/tests/pmu-events.c` generated-table checks. Inspect `perf list --json` or generated C tables for representative aliases `ex_ret_instr`, `ex_ret_cops`, `ex_ret_brn`, `ex_ret_brn_misp`, `ex_ret_brn_tkn`, `ex_ret_brn_tkn_misp`, plus 15 more. On matching hardware, run `perf stat -e` for events such as `ex_ret_instr`, `ex_ret_cops`, `ex_ret_brn`, `ex_ret_brn_misp`, `ex_ret_brn_tkn`, plus 16 more and verify the kernel accepts the encoding and returns plausible non-negative counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen1/core.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen1/data-fabric.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen1/data-fabric.json

## Purpose
Defines AMD `amdzen1` DFPMC per-package data-fabric aliases for remote outbound traffic and DRAM-channel controller traffic selection.

## APIs, Types, and Functions
The data contract is a perf PMU JSON array with 12 records: 12 raw event aliases and 0 derived metrics. Schema fields present are `EventCode`, `EventName`, `PerPkg`, `PublicDescription`, `UMask`, `Unit`. `jevents.py` maps `EventCode`, `UMask`, `CounterMask`, `MSRIndex`, `MSRValue`, `PerPkg`, `Deprecated`, `MetricExpr`, `MetricGroup`, and `ScaleUnit` into `struct pmu_event` or `struct pmu_metric` entries declared in `pmu-events.h`. Units resolve to `DFPMC`. Representative names: `remote_outbound_data_controller_0`, `remote_outbound_data_controller_1`, `remote_outbound_data_controller_2`, `remote_outbound_data_controller_3`, `dram_channel_data_controller_0`, `dram_channel_data_controller_1`, `dram_channel_data_controller_2`, `dram_channel_data_controller_3`, `dram_channel_data_controller_4`, `dram_channel_data_controller_5`, plus 2 more.

## Control Flow
Build control flow is data-driven: `jevents.py` reads this `data-fabric` file, lowercases event aliases, converts `Unit` through `unit_to_pmu()`, canonicalizes event and umask encodings, and appends generated C strings to the model event table. Runtime perf reaches the records through `find_core_events_table()`, `find_sys_events_table()`, `pmu_events_table__find_event()`, and `pmu_events_table__for_each_event()` when `perf list`, `perf stat -e`, or metrics request the aliases.

## State and Persistence
The file has no executable state, locks, persistence layer, or runtime mutation. Its durable behavior is the generated perf event/metric table selected by x86 mapfile CPUID matching; kernel PMU drivers own counter state once a user selects an alias.

## Dependencies and Integration
Integrated by `tools/perf/pmu-events/arch/x86/mapfile.csv` selecting the `amdzen1` directory for matching x86 CPU identifiers. Consumed by `jevents.py`, `pmu-events.h`, `builtin-list.c`, metric parsing, and PMU table lookup helpers. Unit-specific routing depends on `unit_to_pmu()` mappings for `DFPMC`; missing `Unit` means the default core PMU. Entries with `PerPkg` require package-level aggregation behavior in perf's uncore/sys PMU handling.

## Risks
The main risk is semantic drift from the vendor performance-monitoring documentation: a wrong event code, umask, MSR filter, or PMU unit can make a friendly alias count the wrong hardware condition. AMD uncore-style units such as `L3PMC` and `DFPMC` depend on kernel PMU naming and package aggregation support; unsupported systems may list aliases that cannot be scheduled.

## Test Signals
Run the perf pmu-events generator over `arch/x86` and the `tools/perf/tests/pmu-events.c` generated-table checks. Inspect `perf list --json` or generated C tables for representative aliases `remote_outbound_data_controller_0`, `remote_outbound_data_controller_1`, `remote_outbound_data_controller_2`, `remote_outbound_data_controller_3`, `dram_channel_data_controller_0`, `dram_channel_data_controller_1`, plus 6 more. On matching hardware, run `perf stat -e` for events such as `remote_outbound_data_controller_0`, `remote_outbound_data_controller_1`, `remote_outbound_data_controller_2`, `remote_outbound_data_controller_3`, `dram_channel_data_controller_0`, plus 7 more and verify the kernel accepts the encoding and returns plausible non-negative counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen1/data-fabric.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen1/floating-point.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen1/floating-point.json

## Purpose
Defines AMD `amdzen1` floating-point pipe, retired x87/SSE/AVX operation, move-elimination, serialization, and FP fill/spill fault aliases for operation-mix analysis.

## APIs, Types, and Functions
The data contract is a perf PMU JSON array with 32 records: 32 raw event aliases and 0 derived metrics. Schema fields present are `BriefDescription`, `EventCode`, `EventName`, `PublicDescription`, `UMask`. `jevents.py` maps `EventCode`, `UMask`, `CounterMask`, `MSRIndex`, `MSRValue`, `PerPkg`, `Deprecated`, `MetricExpr`, `MetricGroup`, and `ScaleUnit` into `struct pmu_event` or `struct pmu_metric` entries declared in `pmu-events.h`. Units resolve to `default_core`. Representative names: `fpu_pipe_assignment.dual`, `fpu_pipe_assignment.dual3`, `fpu_pipe_assignment.dual2`, `fpu_pipe_assignment.dual1`, `fpu_pipe_assignment.dual0`, `fpu_pipe_assignment.total`, `fpu_pipe_assignment.total3`, `fpu_pipe_assignment.total2`, `fpu_pipe_assignment.total1`, `fpu_pipe_assignment.total0`, plus 22 more.

## Control Flow
Build control flow is data-driven: `jevents.py` reads this `floating-point` file, lowercases event aliases, converts `Unit` through `unit_to_pmu()`, canonicalizes event and umask encodings, and appends generated C strings to the model event table. Runtime perf reaches the records through `find_core_events_table()`, `find_sys_events_table()`, `pmu_events_table__find_event()`, and `pmu_events_table__for_each_event()` when `perf list`, `perf stat -e`, or metrics request the aliases.

## State and Persistence
The file has no executable state, locks, persistence layer, or runtime mutation. Its durable behavior is the generated perf event/metric table selected by x86 mapfile CPUID matching; kernel PMU drivers own counter state once a user selects an alias.

## Dependencies and Integration
Integrated by `tools/perf/pmu-events/arch/x86/mapfile.csv` selecting the `amdzen1` directory for matching x86 CPU identifiers. Consumed by `jevents.py`, `pmu-events.h`, `builtin-list.c`, metric parsing, and PMU table lookup helpers. All entries omit `Unit`, so `jevents.py` routes them to the default core PMU for this model.

## Risks
The main risk is semantic drift from the vendor performance-monitoring documentation: a wrong event code, umask, MSR filter, or PMU unit can make a friendly alias count the wrong hardware condition.

## Test Signals
Run the perf pmu-events generator over `arch/x86` and the `tools/perf/tests/pmu-events.c` generated-table checks. Inspect `perf list --json` or generated C tables for representative aliases `fpu_pipe_assignment.dual`, `fpu_pipe_assignment.dual3`, `fpu_pipe_assignment.dual2`, `fpu_pipe_assignment.dual1`, `fpu_pipe_assignment.dual0`, `fpu_pipe_assignment.total`, plus 26 more. On matching hardware, run `perf stat -e` for events such as `fpu_pipe_assignment.dual`, `fpu_pipe_assignment.dual3`, `fpu_pipe_assignment.dual2`, `fpu_pipe_assignment.dual1`, `fpu_pipe_assignment.dual0`, plus 27 more and verify the kernel accepts the encoding and returns plausible non-negative counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen1/floating-point.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen1/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen1/memory.json

## Purpose
Defines AMD `amdzen1` load/store, lock, dispatch, store-to-load-forwarding, data-cache, MAB allocation, TLB miss, table-walker, misalignment, and memory-side activity aliases.

## APIs, Types, and Functions
The data contract is a perf PMU JSON array with 31 records: 31 raw event aliases and 0 derived metrics. Schema fields present are `BriefDescription`, `EventCode`, `EventName`, `UMask`. `jevents.py` maps `EventCode`, `UMask`, `CounterMask`, `MSRIndex`, `MSRValue`, `PerPkg`, `Deprecated`, `MetricExpr`, `MetricGroup`, and `ScaleUnit` into `struct pmu_event` or `struct pmu_metric` entries declared in `pmu-events.h`. Units resolve to `default_core`. Representative names: `ls_locks.bus_lock`, `ls_dispatch.ld_st_dispatch`, `ls_dispatch.store_dispatch`, `ls_dispatch.ld_dispatch`, `ls_stlf`, `ls_dc_accesses`, `ls_mab_alloc.dc_prefetcher`, `ls_mab_alloc.stores`, `ls_mab_alloc.loads`, `ls_l1_d_tlb_miss.all`, plus 21 more.

## Control Flow
Build control flow is data-driven: `jevents.py` reads this `memory` file, lowercases event aliases, converts `Unit` through `unit_to_pmu()`, canonicalizes event and umask encodings, and appends generated C strings to the model event table. Runtime perf reaches the records through `find_core_events_table()`, `find_sys_events_table()`, `pmu_events_table__find_event()`, and `pmu_events_table__for_each_event()` when `perf list`, `perf stat -e`, or metrics request the aliases.

## State and Persistence
The file has no executable state, locks, persistence layer, or runtime mutation. Its durable behavior is the generated perf event/metric table selected by x86 mapfile CPUID matching; kernel PMU drivers own counter state once a user selects an alias.

## Dependencies and Integration
Integrated by `tools/perf/pmu-events/arch/x86/mapfile.csv` selecting the `amdzen1` directory for matching x86 CPU identifiers. Consumed by `jevents.py`, `pmu-events.h`, `builtin-list.c`, metric parsing, and PMU table lookup helpers. All entries omit `Unit`, so `jevents.py` routes them to the default core PMU for this model.

## Risks
The main risk is semantic drift from the vendor performance-monitoring documentation: a wrong event code, umask, MSR filter, or PMU unit can make a friendly alias count the wrong hardware condition.

## Test Signals
Run the perf pmu-events generator over `arch/x86` and the `tools/perf/tests/pmu-events.c` generated-table checks. Inspect `perf list --json` or generated C tables for representative aliases `ls_locks.bus_lock`, `ls_dispatch.ld_st_dispatch`, `ls_dispatch.store_dispatch`, `ls_dispatch.ld_dispatch`, `ls_stlf`, `ls_dc_accesses`, plus 25 more. On matching hardware, run `perf stat -e` for events such as `ls_locks.bus_lock`, `ls_dispatch.ld_st_dispatch`, `ls_dispatch.store_dispatch`, `ls_dispatch.ld_dispatch`, `ls_stlf`, plus 26 more and verify the kernel accepts the encoding and returns plausible non-negative counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen1/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen1/other.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen1/other.json

## Purpose
Defines AMD `amdzen1` miscellaneous frontend/dispatch resource aliases, mainly op-cache, decoder, and dispatch-token stall breakdowns that do not fit branch, cache, memory, or FP groups.

## APIs, Types, and Functions
The data contract is a perf PMU JSON array with 9 records: 9 raw event aliases and 0 derived metrics. Schema fields present are `BriefDescription`, `EventCode`, `EventName`, `UMask`. `jevents.py` maps `EventCode`, `UMask`, `CounterMask`, `MSRIndex`, `MSRValue`, `PerPkg`, `Deprecated`, `MetricExpr`, `MetricGroup`, and `ScaleUnit` into `struct pmu_event` or `struct pmu_metric` entries declared in `pmu-events.h`. Units resolve to `default_core`. Representative names: `ic_oc_mode_switch.oc_ic_mode_switch`, `ic_oc_mode_switch.ic_oc_mode_switch`, `de_dis_dispatch_token_stalls0.retire_token_stall`, `de_dis_dispatch_token_stalls0.agsq_token_stall`, `de_dis_dispatch_token_stalls0.alu_token_stall`, `de_dis_dispatch_token_stalls0.alsq3_0_token_stall`, `de_dis_dispatch_token_stalls0.alsq3_token_stall`, `de_dis_dispatch_token_stalls0.alsq2_token_stall`, `de_dis_dispatch_token_stalls0.alsq1_token_stall`.

## Control Flow
Build control flow is data-driven: `jevents.py` reads this `other` file, lowercases event aliases, converts `Unit` through `unit_to_pmu()`, canonicalizes event and umask encodings, and appends generated C strings to the model event table. Runtime perf reaches the records through `find_core_events_table()`, `find_sys_events_table()`, `pmu_events_table__find_event()`, and `pmu_events_table__for_each_event()` when `perf list`, `perf stat -e`, or metrics request the aliases.

## State and Persistence
The file has no executable state, locks, persistence layer, or runtime mutation. Its durable behavior is the generated perf event/metric table selected by x86 mapfile CPUID matching; kernel PMU drivers own counter state once a user selects an alias.

## Dependencies and Integration
Integrated by `tools/perf/pmu-events/arch/x86/mapfile.csv` selecting the `amdzen1` directory for matching x86 CPU identifiers. Consumed by `jevents.py`, `pmu-events.h`, `builtin-list.c`, metric parsing, and PMU table lookup helpers. All entries omit `Unit`, so `jevents.py` routes them to the default core PMU for this model.

## Risks
The main risk is semantic drift from the vendor performance-monitoring documentation: a wrong event code, umask, MSR filter, or PMU unit can make a friendly alias count the wrong hardware condition.

## Test Signals
Run the perf pmu-events generator over `arch/x86` and the `tools/perf/tests/pmu-events.c` generated-table checks. Inspect `perf list --json` or generated C tables for representative aliases `ic_oc_mode_switch.oc_ic_mode_switch`, `ic_oc_mode_switch.ic_oc_mode_switch`, `de_dis_dispatch_token_stalls0.retire_token_stall`, `de_dis_dispatch_token_stalls0.agsq_token_stall`, `de_dis_dispatch_token_stalls0.alu_token_stall`, `de_dis_dispatch_token_stalls0.alsq3_0_token_stall`, plus 3 more. On matching hardware, run `perf stat -e` for events such as `ic_oc_mode_switch.oc_ic_mode_switch`, `ic_oc_mode_switch.ic_oc_mode_switch`, `de_dis_dispatch_token_stalls0.retire_token_stall`, `de_dis_dispatch_token_stalls0.agsq_token_stall`, `de_dis_dispatch_token_stalls0.alu_token_stall`, plus 4 more and verify the kernel accepts the encoding and returns plausible non-negative counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen1/other.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen1/recommended.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen1/recommended.json

## Purpose
Defines AMD `amdzen1` recommended perf aliases and derived metrics for branch misprediction, cache access/hit/miss breakdowns, L3 latency, instruction-cache miss ratio, ITLB/DTLB misses, TLB flushes, dispatched uops, and SSE/AVX stalls.

## APIs, Types, and Functions
The data contract is a perf PMU JSON array with 28 records: 17 raw event aliases and 11 derived metrics. Schema fields present are `BriefDescription`, `EventCode`, `EventName`, `MetricConstraint`, `MetricExpr`, `MetricGroup`, `MetricName`, `PerPkg`, `ScaleUnit`, `UMask`, `Unit`. `jevents.py` maps `EventCode`, `UMask`, `CounterMask`, `MSRIndex`, `MSRValue`, `PerPkg`, `Deprecated`, `MetricExpr`, `MetricGroup`, and `ScaleUnit` into `struct pmu_event` or `struct pmu_metric` entries declared in `pmu-events.h`. Units resolve to `L3PMC`, `default_core`. Representative names: `branch_misprediction_ratio`, `all_dc_accesses`, `all_l2_cache_accesses`, `l2_cache_accesses_from_ic_misses`, `l2_cache_accesses_from_dc_misses`, `l2_cache_accesses_from_l2_hwpf`, `all_l2_cache_misses`, `l2_cache_misses_from_ic_miss`, `l2_cache_misses_from_dc_misses`, `l2_cache_misses_from_l2_hwpf`, plus 18 more.

## Control Flow
Build control flow is data-driven: `process_one_file()` assigns a model table for the leaf x86 directory, `read_json_events()` creates one `PmuEvent` per JSON object, and metric expressions are parsed by `metric.ParsePerfJson(...).Simplify()`. The 11 metrics reference tokens such as `bp_l1_tlb_fetch_hit`, `bp_l1_tlb_miss_l2_hit`, `bp_l1_tlb_miss_l2_miss`, `dram_channel_data_controller_0`, `dram_channel_data_controller_1`, `dram_channel_data_controller_2`, `dram_channel_data_controller_3`, `dram_channel_data_controller_4`, `dram_channel_data_controller_5`, `dram_channel_data_controller_6`, `dram_channel_data_controller_7`, `ex_ret_brn`, plus 14 more; at runtime `perf stat -M` resolves those names against generated PMU tables and evaluates the formulas over counter groups selected for the matching CPUID.

## State and Persistence
The file has no executable state, locks, persistence layer, or runtime mutation. Its durable behavior is the generated perf event/metric table selected by x86 mapfile CPUID matching; kernel PMU drivers own counter state once a user selects an alias.

## Dependencies and Integration
Integrated by `tools/perf/pmu-events/arch/x86/mapfile.csv` selecting the `amdzen1` directory for matching x86 CPU identifiers. Consumed by `jevents.py`, `pmu-events.h`, `builtin-list.c`, metric parsing, and PMU table lookup helpers. Unit-specific routing depends on `unit_to_pmu()` mappings for `L3PMC`; missing `Unit` means the default core PMU. Metric integration also depends on expression-token resolution, `MetricConstraint` grouping policy, `ScaleUnit`, `MetricThreshold`, and metric groups `branch_prediction`, `data_fabric`, `l2_cache`, `l3_cache`, `tlb`. Entries with `PerPkg` require package-level aggregation behavior in perf's uncore/sys PMU handling.

## Risks
The main risk is semantic drift from the vendor performance-monitoring documentation: a wrong event code, umask, MSR filter, or PMU unit can make a friendly alias count the wrong hardware condition. Metric formulas can fail or mislead if referenced aliases are unavailable, event grouping cannot be scheduled, `#slots` or topdown constants are wrong for the CPU, or denominators are zero on short samples. AMD uncore-style units such as `L3PMC` and `DFPMC` depend on kernel PMU naming and package aggregation support; unsupported systems may list aliases that cannot be scheduled.

## Test Signals
Run the perf pmu-events generator over `arch/x86` and the `tools/perf/tests/pmu-events.c` generated-table checks. Inspect `perf list --json` or generated C tables for representative aliases `branch_misprediction_ratio`, `all_dc_accesses`, `all_l2_cache_accesses`, `l2_cache_accesses_from_ic_misses`, `l2_cache_accesses_from_dc_misses`, `l2_cache_accesses_from_l2_hwpf`, plus 22 more. On matching hardware, run `perf stat -M` for metrics such as `branch_misprediction_ratio`, `all_l2_cache_accesses`, `l2_cache_accesses_from_l2_hwpf`, `all_l2_cache_misses`, `l2_cache_misses_from_l2_hwpf`, plus 6 more and verify expression parsing, grouping, scaling, and thresholds. On matching hardware, run `perf stat -e` for events such as `all_dc_accesses`, `l2_cache_accesses_from_ic_misses`, `l2_cache_accesses_from_dc_misses`, `l2_cache_misses_from_ic_miss`, `l2_cache_misses_from_dc_misses`, plus 12 more and verify the kernel accepts the encoding and returns plausible non-negative counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen1/recommended.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen2/branch.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen2/branch.json

## Purpose
Defines AMD `amdzen2` branch-prediction and instruction-side TLB aliases, including BTB corrections, dynamic indirect prediction, redirect activity, fetch TLB hits, and ITLB reload requests.

## APIs, Types, and Functions
The data contract is a perf PMU JSON array with 9 records: 9 raw event aliases and 0 derived metrics. Schema fields present are `BriefDescription`, `EventCode`, `EventName`, `PublicDescription`, `UMask`. `jevents.py` maps `EventCode`, `UMask`, `CounterMask`, `MSRIndex`, `MSRValue`, `PerPkg`, `Deprecated`, `MetricExpr`, `MetricGroup`, and `ScaleUnit` into `struct pmu_event` or `struct pmu_metric` entries declared in `pmu-events.h`. Units resolve to `default_core`. Representative names: `bp_l1_btb_correct`, `bp_l2_btb_correct`, `bp_dyn_ind_pred`, `bp_de_redirect`, `bp_l1_tlb_fetch_hit`, `bp_l1_tlb_fetch_hit.if1g`, `bp_l1_tlb_fetch_hit.if2m`, `bp_l1_tlb_fetch_hit.if4k`, `bp_tlb_rel`.

## Control Flow
Build control flow is data-driven: `jevents.py` reads this `branch` file, lowercases event aliases, converts `Unit` through `unit_to_pmu()`, canonicalizes event and umask encodings, and appends generated C strings to the model event table. Runtime perf reaches the records through `find_core_events_table()`, `find_sys_events_table()`, `pmu_events_table__find_event()`, and `pmu_events_table__for_each_event()` when `perf list`, `perf stat -e`, or metrics request the aliases.

## State and Persistence
The file has no executable state, locks, persistence layer, or runtime mutation. Its durable behavior is the generated perf event/metric table selected by x86 mapfile CPUID matching; kernel PMU drivers own counter state once a user selects an alias.

## Dependencies and Integration
Integrated by `tools/perf/pmu-events/arch/x86/mapfile.csv` selecting the `amdzen2` directory for matching x86 CPU identifiers. Consumed by `jevents.py`, `pmu-events.h`, `builtin-list.c`, metric parsing, and PMU table lookup helpers. All entries omit `Unit`, so `jevents.py` routes them to the default core PMU for this model.

## Risks
The main risk is semantic drift from the vendor performance-monitoring documentation: a wrong event code, umask, MSR filter, or PMU unit can make a friendly alias count the wrong hardware condition.

## Test Signals
Run the perf pmu-events generator over `arch/x86` and the `tools/perf/tests/pmu-events.c` generated-table checks. Inspect `perf list --json` or generated C tables for representative aliases `bp_l1_btb_correct`, `bp_l2_btb_correct`, `bp_dyn_ind_pred`, `bp_de_redirect`, `bp_l1_tlb_fetch_hit`, `bp_l1_tlb_fetch_hit.if1g`, plus 3 more. On matching hardware, run `perf stat -e` for events such as `bp_l1_btb_correct`, `bp_l2_btb_correct`, `bp_dyn_ind_pred`, `bp_de_redirect`, `bp_l1_tlb_fetch_hit`, plus 4 more and verify the kernel accepts the encoding and returns plausible non-negative counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen2/branch.json -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen2/core.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen2/core.json

## Purpose
Defines AMD `amdzen2` core retirement and execution aliases for retired instructions/uops/branches, mispredictions, returns, conditional branches, divide activity, IBS-tagged ops, and fused branches.

## APIs, Types, and Functions
The data contract is a perf PMU JSON array with 22 records: 22 raw event aliases and 0 derived metrics. Schema fields present are `BriefDescription`, `EventCode`, `EventName`, `PublicDescription`, `UMask`. `jevents.py` maps `EventCode`, `UMask`, `CounterMask`, `MSRIndex`, `MSRValue`, `PerPkg`, `Deprecated`, `MetricExpr`, `MetricGroup`, and `ScaleUnit` into `struct pmu_event` or `struct pmu_metric` entries declared in `pmu-events.h`. Units resolve to `default_core`. Representative names: `ex_ret_instr`, `ex_ret_cops`, `ex_ret_brn`, `ex_ret_brn_misp`, `ex_ret_brn_tkn`, `ex_ret_brn_tkn_misp`, `ex_ret_brn_far`, `ex_ret_brn_resync`, `ex_ret_near_ret`, `ex_ret_near_ret_mispred`, plus 12 more.

## Control Flow
Build control flow is data-driven: `jevents.py` reads this `core` file, lowercases event aliases, converts `Unit` through `unit_to_pmu()`, canonicalizes event and umask encodings, and appends generated C strings to the model event table. Runtime perf reaches the records through `find_core_events_table()`, `find_sys_events_table()`, `pmu_events_table__find_event()`, and `pmu_events_table__for_each_event()` when `perf list`, `perf stat -e`, or metrics request the aliases.

## State and Persistence
The file has no executable state, locks, persistence layer, or runtime mutation. Its durable behavior is the generated perf event/metric table selected by x86 mapfile CPUID matching; kernel PMU drivers own counter state once a user selects an alias.

## Dependencies and Integration
Integrated by `tools/perf/pmu-events/arch/x86/mapfile.csv` selecting the `amdzen2` directory for matching x86 CPU identifiers. Consumed by `jevents.py`, `pmu-events.h`, `builtin-list.c`, metric parsing, and PMU table lookup helpers. All entries omit `Unit`, so `jevents.py` routes them to the default core PMU for this model.

## Risks
The main risk is semantic drift from the vendor performance-monitoring documentation: a wrong event code, umask, MSR filter, or PMU unit can make a friendly alias count the wrong hardware condition.

## Test Signals
Run the perf pmu-events generator over `arch/x86` and the `tools/perf/tests/pmu-events.c` generated-table checks. Inspect `perf list --json` or generated C tables for representative aliases `ex_ret_instr`, `ex_ret_cops`, `ex_ret_brn`, `ex_ret_brn_misp`, `ex_ret_brn_tkn`, `ex_ret_brn_tkn_misp`, plus 16 more. On matching hardware, run `perf stat -e` for events such as `ex_ret_instr`, `ex_ret_cops`, `ex_ret_brn`, `ex_ret_brn_misp`, `ex_ret_brn_tkn`, plus 17 more and verify the kernel accepts the encoding and returns plausible non-negative counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen2/core.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen2/data-fabric.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen2/data-fabric.json

## Purpose
Defines AMD `amdzen2` DFPMC per-package data-fabric aliases for remote outbound traffic and DRAM-channel controller traffic selection.

## APIs, Types, and Functions
The data contract is a perf PMU JSON array with 12 records: 12 raw event aliases and 0 derived metrics. Schema fields present are `EventCode`, `EventName`, `PerPkg`, `PublicDescription`, `UMask`, `Unit`. `jevents.py` maps `EventCode`, `UMask`, `CounterMask`, `MSRIndex`, `MSRValue`, `PerPkg`, `Deprecated`, `MetricExpr`, `MetricGroup`, and `ScaleUnit` into `struct pmu_event` or `struct pmu_metric` entries declared in `pmu-events.h`. Units resolve to `DFPMC`. Representative names: `remote_outbound_data_controller_0`, `remote_outbound_data_controller_1`, `remote_outbound_data_controller_2`, `remote_outbound_data_controller_3`, `dram_channel_data_controller_0`, `dram_channel_data_controller_1`, `dram_channel_data_controller_2`, `dram_channel_data_controller_3`, `dram_channel_data_controller_4`, `dram_channel_data_controller_5`, plus 2 more.

## Control Flow
Build control flow is data-driven: `jevents.py` reads this `data-fabric` file, lowercases event aliases, converts `Unit` through `unit_to_pmu()`, canonicalizes event and umask encodings, and appends generated C strings to the model event table. Runtime perf reaches the records through `find_core_events_table()`, `find_sys_events_table()`, `pmu_events_table__find_event()`, and `pmu_events_table__for_each_event()` when `perf list`, `perf stat -e`, or metrics request the aliases.

## State and Persistence
The file has no executable state, locks, persistence layer, or runtime mutation. Its durable behavior is the generated perf event/metric table selected by x86 mapfile CPUID matching; kernel PMU drivers own counter state once a user selects an alias.

## Dependencies and Integration
Integrated by `tools/perf/pmu-events/arch/x86/mapfile.csv` selecting the `amdzen2` directory for matching x86 CPU identifiers. Consumed by `jevents.py`, `pmu-events.h`, `builtin-list.c`, metric parsing, and PMU table lookup helpers. Unit-specific routing depends on `unit_to_pmu()` mappings for `DFPMC`; missing `Unit` means the default core PMU. Entries with `PerPkg` require package-level aggregation behavior in perf's uncore/sys PMU handling.

## Risks
The main risk is semantic drift from the vendor performance-monitoring documentation: a wrong event code, umask, MSR filter, or PMU unit can make a friendly alias count the wrong hardware condition. AMD uncore-style units such as `L3PMC` and `DFPMC` depend on kernel PMU naming and package aggregation support; unsupported systems may list aliases that cannot be scheduled.

## Test Signals
Run the perf pmu-events generator over `arch/x86` and the `tools/perf/tests/pmu-events.c` generated-table checks. Inspect `perf list --json` or generated C tables for representative aliases `remote_outbound_data_controller_0`, `remote_outbound_data_controller_1`, `remote_outbound_data_controller_2`, `remote_outbound_data_controller_3`, `dram_channel_data_controller_0`, `dram_channel_data_controller_1`, plus 6 more. On matching hardware, run `perf stat -e` for events such as `remote_outbound_data_controller_0`, `remote_outbound_data_controller_1`, `remote_outbound_data_controller_2`, `remote_outbound_data_controller_3`, `dram_channel_data_controller_0`, plus 7 more and verify the kernel accepts the encoding and returns plausible non-negative counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen2/data-fabric.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen2/floating-point.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen2/floating-point.json

## Purpose
Defines AMD `amdzen2` floating-point pipe, retired x87/SSE/AVX operation, move-elimination, serialization, and FP fill/spill fault aliases for operation-mix analysis.

## APIs, Types, and Functions
The data contract is a perf PMU JSON array with 22 records: 22 raw event aliases and 0 derived metrics. Schema fields present are `BriefDescription`, `EventCode`, `EventName`, `PublicDescription`, `UMask`. `jevents.py` maps `EventCode`, `UMask`, `CounterMask`, `MSRIndex`, `MSRValue`, `PerPkg`, `Deprecated`, `MetricExpr`, `MetricGroup`, and `ScaleUnit` into `struct pmu_event` or `struct pmu_metric` entries declared in `pmu-events.h`. Units resolve to `default_core`. Representative names: `fpu_pipe_assignment.total`, `fpu_pipe_assignment.total3`, `fpu_pipe_assignment.total2`, `fpu_pipe_assignment.total1`, `fpu_pipe_assignment.total0`, `fp_ret_sse_avx_ops.all`, `fp_ret_sse_avx_ops.mac_flops`, `fp_ret_sse_avx_ops.div_flops`, `fp_ret_sse_avx_ops.mult_flops`, `fp_ret_sse_avx_ops.add_sub_flops`, plus 12 more.

## Control Flow
Build control flow is data-driven: `jevents.py` reads this `floating-point` file, lowercases event aliases, converts `Unit` through `unit_to_pmu()`, canonicalizes event and umask encodings, and appends generated C strings to the model event table. Runtime perf reaches the records through `find_core_events_table()`, `find_sys_events_table()`, `pmu_events_table__find_event()`, and `pmu_events_table__for_each_event()` when `perf list`, `perf stat -e`, or metrics request the aliases.

## State and Persistence
The file has no executable state, locks, persistence layer, or runtime mutation. Its durable behavior is the generated perf event/metric table selected by x86 mapfile CPUID matching; kernel PMU drivers own counter state once a user selects an alias.

## Dependencies and Integration
Integrated by `tools/perf/pmu-events/arch/x86/mapfile.csv` selecting the `amdzen2` directory for matching x86 CPU identifiers. Consumed by `jevents.py`, `pmu-events.h`, `builtin-list.c`, metric parsing, and PMU table lookup helpers. All entries omit `Unit`, so `jevents.py` routes them to the default core PMU for this model.

## Risks
The main risk is semantic drift from the vendor performance-monitoring documentation: a wrong event code, umask, MSR filter, or PMU unit can make a friendly alias count the wrong hardware condition.

## Test Signals
Run the perf pmu-events generator over `arch/x86` and the `tools/perf/tests/pmu-events.c` generated-table checks. Inspect `perf list --json` or generated C tables for representative aliases `fpu_pipe_assignment.total`, `fpu_pipe_assignment.total3`, `fpu_pipe_assignment.total2`, `fpu_pipe_assignment.total1`, `fpu_pipe_assignment.total0`, `fp_ret_sse_avx_ops.all`, plus 16 more. On matching hardware, run `perf stat -e` for events such as `fpu_pipe_assignment.total`, `fpu_pipe_assignment.total3`, `fpu_pipe_assignment.total2`, `fpu_pipe_assignment.total1`, `fpu_pipe_assignment.total0`, plus 17 more and verify the kernel accepts the encoding and returns plausible non-negative counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen2/floating-point.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen2/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen2/memory.json

## Purpose
Defines AMD `amdzen2` load/store, lock, dispatch, store-to-load-forwarding, data-cache, MAB allocation, TLB miss, table-walker, misalignment, and memory-side activity aliases.

## APIs, Types, and Functions
The data contract is a perf PMU JSON array with 58 records: 58 raw event aliases and 0 derived metrics. Schema fields present are `BriefDescription`, `EventCode`, `EventName`, `PublicDescription`, `UMask`. `jevents.py` maps `EventCode`, `UMask`, `CounterMask`, `MSRIndex`, `MSRValue`, `PerPkg`, `Deprecated`, `MetricExpr`, `MetricGroup`, and `ScaleUnit` into `struct pmu_event` or `struct pmu_metric` entries declared in `pmu-events.h`. Units resolve to `default_core`. Representative names: `ls_bad_status2.stli_other`, `ls_locks.spec_lock_hi_spec`, `ls_locks.spec_lock_lo_spec`, `ls_locks.non_spec_lock`, `ls_locks.bus_lock`, `ls_ret_cl_flush`, `ls_ret_cpuid`, `ls_dispatch.ld_st_dispatch`, `ls_dispatch.store_dispatch`, `ls_dispatch.ld_dispatch`, plus 48 more.

## Control Flow
Build control flow is data-driven: `jevents.py` reads this `memory` file, lowercases event aliases, converts `Unit` through `unit_to_pmu()`, canonicalizes event and umask encodings, and appends generated C strings to the model event table. Runtime perf reaches the records through `find_core_events_table()`, `find_sys_events_table()`, `pmu_events_table__find_event()`, and `pmu_events_table__for_each_event()` when `perf list`, `perf stat -e`, or metrics request the aliases.

## State and Persistence
The file has no executable state, locks, persistence layer, or runtime mutation. Its durable behavior is the generated perf event/metric table selected by x86 mapfile CPUID matching; kernel PMU drivers own counter state once a user selects an alias.

## Dependencies and Integration
Integrated by `tools/perf/pmu-events/arch/x86/mapfile.csv` selecting the `amdzen2` directory for matching x86 CPU identifiers. Consumed by `jevents.py`, `pmu-events.h`, `builtin-list.c`, metric parsing, and PMU table lookup helpers. All entries omit `Unit`, so `jevents.py` routes them to the default core PMU for this model.

## Risks
The main risk is semantic drift from the vendor performance-monitoring documentation: a wrong event code, umask, MSR filter, or PMU unit can make a friendly alias count the wrong hardware condition.

## Test Signals
Run the perf pmu-events generator over `arch/x86` and the `tools/perf/tests/pmu-events.c` generated-table checks. Inspect `perf list --json` or generated C tables for representative aliases `ls_bad_status2.stli_other`, `ls_locks.spec_lock_hi_spec`, `ls_locks.spec_lock_lo_spec`, `ls_locks.non_spec_lock`, `ls_locks.bus_lock`, `ls_ret_cl_flush`, plus 52 more. On matching hardware, run `perf stat -e` for events such as `ls_bad_status2.stli_other`, `ls_locks.spec_lock_hi_spec`, `ls_locks.spec_lock_lo_spec`, `ls_locks.non_spec_lock`, `ls_locks.bus_lock`, plus 53 more and verify the kernel accepts the encoding and returns plausible non-negative counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen2/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen2/other.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen2/other.json

## Purpose
Defines AMD `amdzen2` miscellaneous frontend/dispatch resource aliases, mainly op-cache, decoder, and dispatch-token stall breakdowns that do not fit branch, cache, memory, or FP groups.

## APIs, Types, and Functions
The data contract is a perf PMU JSON array with 19 records: 19 raw event aliases and 0 derived metrics. Schema fields present are `BriefDescription`, `EventCode`, `EventName`, `UMask`. `jevents.py` maps `EventCode`, `UMask`, `CounterMask`, `MSRIndex`, `MSRValue`, `PerPkg`, `Deprecated`, `MetricExpr`, `MetricGroup`, and `ScaleUnit` into `struct pmu_event` or `struct pmu_metric` entries declared in `pmu-events.h`. Units resolve to `default_core`. Representative names: `de_dis_uop_queue_empty_di0`, `de_dis_uops_from_decoder`, `de_dis_uops_from_decoder.opcache_dispatched`, `de_dis_uops_from_decoder.decoder_dispatched`, `de_dis_dispatch_token_stalls1.fp_misc_rsrc_stall`, `de_dis_dispatch_token_stalls1.fp_sch_rsrc_stall`, `de_dis_dispatch_token_stalls1.fp_reg_file_rsrc_stall`, `de_dis_dispatch_token_stalls1.taken_branch_buffer_rsrc_stall`, `de_dis_dispatch_token_stalls1.int_sched_misc_token_stall`, `de_dis_dispatch_token_stalls1.store_queue_token_stall`, plus 9 more.

## Control Flow
Build control flow is data-driven: `jevents.py` reads this `other` file, lowercases event aliases, converts `Unit` through `unit_to_pmu()`, canonicalizes event and umask encodings, and appends generated C strings to the model event table. Runtime perf reaches the records through `find_core_events_table()`, `find_sys_events_table()`, `pmu_events_table__find_event()`, and `pmu_events_table__for_each_event()` when `perf list`, `perf stat -e`, or metrics request the aliases.

## State and Persistence
The file has no executable state, locks, persistence layer, or runtime mutation. Its durable behavior is the generated perf event/metric table selected by x86 mapfile CPUID matching; kernel PMU drivers own counter state once a user selects an alias.

## Dependencies and Integration
Integrated by `tools/perf/pmu-events/arch/x86/mapfile.csv` selecting the `amdzen2` directory for matching x86 CPU identifiers. Consumed by `jevents.py`, `pmu-events.h`, `builtin-list.c`, metric parsing, and PMU table lookup helpers. All entries omit `Unit`, so `jevents.py` routes them to the default core PMU for this model.

## Risks
The main risk is semantic drift from the vendor performance-monitoring documentation: a wrong event code, umask, MSR filter, or PMU unit can make a friendly alias count the wrong hardware condition.

## Test Signals
Run the perf pmu-events generator over `arch/x86` and the `tools/perf/tests/pmu-events.c` generated-table checks. Inspect `perf list --json` or generated C tables for representative aliases `de_dis_uop_queue_empty_di0`, `de_dis_uops_from_decoder`, `de_dis_uops_from_decoder.opcache_dispatched`, `de_dis_uops_from_decoder.decoder_dispatched`, `de_dis_dispatch_token_stalls1.fp_misc_rsrc_stall`, `de_dis_dispatch_token_stalls1.fp_sch_rsrc_stall`, plus 13 more. On matching hardware, run `perf stat -e` for events such as `de_dis_uop_queue_empty_di0`, `de_dis_uops_from_decoder`, `de_dis_uops_from_decoder.opcache_dispatched`, `de_dis_uops_from_decoder.decoder_dispatched`, `de_dis_dispatch_token_stalls1.fp_misc_rsrc_stall`, plus 14 more and verify the kernel accepts the encoding and returns plausible non-negative counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen2/other.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen2/recommended.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen2/recommended.json

## Purpose
Defines AMD `amdzen2` recommended perf aliases and derived metrics for branch misprediction, cache access/hit/miss breakdowns, L3 latency, instruction-cache miss ratio, ITLB/DTLB misses, TLB flushes, dispatched uops, and SSE/AVX stalls.

## APIs, Types, and Functions
The data contract is a perf PMU JSON array with 28 records: 17 raw event aliases and 11 derived metrics. Schema fields present are `BriefDescription`, `EventCode`, `EventName`, `MetricConstraint`, `MetricExpr`, `MetricGroup`, `MetricName`, `PerPkg`, `ScaleUnit`, `UMask`, `Unit`. `jevents.py` maps `EventCode`, `UMask`, `CounterMask`, `MSRIndex`, `MSRValue`, `PerPkg`, `Deprecated`, `MetricExpr`, `MetricGroup`, and `ScaleUnit` into `struct pmu_event` or `struct pmu_metric` entries declared in `pmu-events.h`. Units resolve to `L3PMC`, `default_core`. Representative names: `branch_misprediction_ratio`, `all_dc_accesses`, `all_l2_cache_accesses`, `l2_cache_accesses_from_ic_misses`, `l2_cache_accesses_from_dc_misses`, `l2_cache_accesses_from_l2_hwpf`, `all_l2_cache_misses`, `l2_cache_misses_from_ic_miss`, `l2_cache_misses_from_dc_misses`, `l2_cache_misses_from_l2_hwpf`, plus 18 more.

## Control Flow
Build control flow is data-driven: `process_one_file()` assigns a model table for the leaf x86 directory, `read_json_events()` creates one `PmuEvent` per JSON object, and metric expressions are parsed by `metric.ParsePerfJson(...).Simplify()`. The 11 metrics reference tokens such as `bp_l1_tlb_fetch_hit`, `bp_l1_tlb_miss_l2_hit`, `bp_l1_tlb_miss_l2_tlb_miss`, `dram_channel_data_controller_0`, `dram_channel_data_controller_1`, `dram_channel_data_controller_2`, `dram_channel_data_controller_3`, `dram_channel_data_controller_4`, `dram_channel_data_controller_5`, `dram_channel_data_controller_6`, `dram_channel_data_controller_7`, `ex_ret_brn`, plus 14 more; at runtime `perf stat -M` resolves those names against generated PMU tables and evaluates the formulas over counter groups selected for the matching CPUID.

## State and Persistence
The file has no executable state, locks, persistence layer, or runtime mutation. Its durable behavior is the generated perf event/metric table selected by x86 mapfile CPUID matching; kernel PMU drivers own counter state once a user selects an alias.

## Dependencies and Integration
Integrated by `tools/perf/pmu-events/arch/x86/mapfile.csv` selecting the `amdzen2` directory for matching x86 CPU identifiers. Consumed by `jevents.py`, `pmu-events.h`, `builtin-list.c`, metric parsing, and PMU table lookup helpers. Unit-specific routing depends on `unit_to_pmu()` mappings for `L3PMC`; missing `Unit` means the default core PMU. Metric integration also depends on expression-token resolution, `MetricConstraint` grouping policy, `ScaleUnit`, `MetricThreshold`, and metric groups `branch_prediction`, `data_fabric`, `l2_cache`, `l3_cache`, `tlb`. Entries with `PerPkg` require package-level aggregation behavior in perf's uncore/sys PMU handling.

## Risks
The main risk is semantic drift from the vendor performance-monitoring documentation: a wrong event code, umask, MSR filter, or PMU unit can make a friendly alias count the wrong hardware condition. Metric formulas can fail or mislead if referenced aliases are unavailable, event grouping cannot be scheduled, `#slots` or topdown constants are wrong for the CPU, or denominators are zero on short samples. AMD uncore-style units such as `L3PMC` and `DFPMC` depend on kernel PMU naming and package aggregation support; unsupported systems may list aliases that cannot be scheduled.

## Test Signals
Run the perf pmu-events generator over `arch/x86` and the `tools/perf/tests/pmu-events.c` generated-table checks. Inspect `perf list --json` or generated C tables for representative aliases `branch_misprediction_ratio`, `all_dc_accesses`, `all_l2_cache_accesses`, `l2_cache_accesses_from_ic_misses`, `l2_cache_accesses_from_dc_misses`, `l2_cache_accesses_from_l2_hwpf`, plus 22 more. On matching hardware, run `perf stat -M` for metrics such as `branch_misprediction_ratio`, `all_l2_cache_accesses`, `l2_cache_accesses_from_l2_hwpf`, `all_l2_cache_misses`, `l2_cache_misses_from_l2_hwpf`, plus 6 more and verify expression parsing, grouping, scaling, and thresholds. On matching hardware, run `perf stat -e` for events such as `all_dc_accesses`, `l2_cache_accesses_from_ic_misses`, `l2_cache_accesses_from_dc_misses`, `l2_cache_misses_from_ic_miss`, `l2_cache_misses_from_dc_misses`, plus 12 more and verify the kernel accepts the encoding and returns plausible non-negative counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen2/recommended.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen3/branch.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen3/branch.json

## Purpose
Defines AMD `amdzen3` branch-prediction and instruction-side TLB aliases, including BTB corrections, dynamic indirect prediction, redirect activity, fetch TLB hits, and ITLB reload requests.

## APIs, Types, and Functions
The data contract is a perf PMU JSON array with 9 records: 9 raw event aliases and 0 derived metrics. Schema fields present are `BriefDescription`, `EventCode`, `EventName`, `PublicDescription`, `UMask`. `jevents.py` maps `EventCode`, `UMask`, `CounterMask`, `MSRIndex`, `MSRValue`, `PerPkg`, `Deprecated`, `MetricExpr`, `MetricGroup`, and `ScaleUnit` into `struct pmu_event` or `struct pmu_metric` entries declared in `pmu-events.h`. Units resolve to `default_core`. Representative names: `bp_l1_btb_correct`, `bp_l2_btb_correct`, `bp_dyn_ind_pred`, `bp_de_redirect`, `bp_l1_tlb_fetch_hit`, `bp_l1_tlb_fetch_hit.if1g`, `bp_l1_tlb_fetch_hit.if2m`, `bp_l1_tlb_fetch_hit.if4k`, `bp_tlb_rel`.

## Control Flow
Build control flow is data-driven: `jevents.py` reads this `branch` file, lowercases event aliases, converts `Unit` through `unit_to_pmu()`, canonicalizes event and umask encodings, and appends generated C strings to the model event table. Runtime perf reaches the records through `find_core_events_table()`, `find_sys_events_table()`, `pmu_events_table__find_event()`, and `pmu_events_table__for_each_event()` when `perf list`, `perf stat -e`, or metrics request the aliases.

## State and Persistence
The file has no executable state, locks, persistence layer, or runtime mutation. Its durable behavior is the generated perf event/metric table selected by x86 mapfile CPUID matching; kernel PMU drivers own counter state once a user selects an alias.

## Dependencies and Integration
Integrated by `tools/perf/pmu-events/arch/x86/mapfile.csv` selecting the `amdzen3` directory for matching x86 CPU identifiers. Consumed by `jevents.py`, `pmu-events.h`, `builtin-list.c`, metric parsing, and PMU table lookup helpers. All entries omit `Unit`, so `jevents.py` routes them to the default core PMU for this model.

## Risks
The main risk is semantic drift from the vendor performance-monitoring documentation: a wrong event code, umask, MSR filter, or PMU unit can make a friendly alias count the wrong hardware condition.

## Test Signals
Run the perf pmu-events generator over `arch/x86` and the `tools/perf/tests/pmu-events.c` generated-table checks. Inspect `perf list --json` or generated C tables for representative aliases `bp_l1_btb_correct`, `bp_l2_btb_correct`, `bp_dyn_ind_pred`, `bp_de_redirect`, `bp_l1_tlb_fetch_hit`, `bp_l1_tlb_fetch_hit.if1g`, plus 3 more. On matching hardware, run `perf stat -e` for events such as `bp_l1_btb_correct`, `bp_l2_btb_correct`, `bp_dyn_ind_pred`, `bp_de_redirect`, `bp_l1_tlb_fetch_hit`, plus 4 more and verify the kernel accepts the encoding and returns plausible non-negative counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/amdzen3/branch.json -->
