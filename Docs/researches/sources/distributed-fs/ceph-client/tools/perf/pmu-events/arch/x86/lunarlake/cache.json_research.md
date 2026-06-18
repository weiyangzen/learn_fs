<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/lunarlake/cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/lunarlake/cache.json

## Purpose
This JSON file defines Lunar Lake cache, memory-access, offcore-response, L2, LLC, load/store retirement, prefetch, lock, and memory-bound stall PMU events for perf. The complete 1,694-line array was read and contains 166 records: 88 `cpu_core` records and 78 `cpu_atom` records for Lunar Lake's hybrid core/atom PMU model.

## Important APIs, Types, and Functions
The file uses perf event schema fields including `EventName`, `EventCode`, `UMask`, `Unit`, `Counter`, `SampleAfterValue`, `BriefDescription`, and frequent `PublicDescription`. Additional modifiers include `Data_LA` on 47 records, `MSRIndex`/`MSRValue` on 23 offcore-response or latency-threshold records, `CounterMask` on 5 records, and `Deprecated` on 2 records. There are no functions or classes; the exported API is the alias set generated from these records.

Major families include `MEM_UOPS_RETIRED` (21), `MEM_INST_RETIRED` (15), `OCR` offcore response events (15), `L2_RQSTS` (11), `MEM_LOAD_RETIRED` (9), `OFFCORE_REQUESTS_OUTSTANDING` (8), `L2_LINES_IN`/`L2_LINES_OUT`/`L2_REQUEST` (6 each), `SW_PREFETCH_ACCESS`, `OFFCORE_REQUESTS`, `MEM_LOAD_UOPS_RETIRED`, `MEM_BOUND_STALLS_LOAD`, `MEM_BOUND_STALLS_IFETCH`, and `LLC_PREFETCHES_THROTTLED` (5 each). Several event names intentionally appear twice with different `Unit` values, such as `OCR.DEMAND_DATA_RD.ANY_RESPONSE`, `L2_REQUEST.ALL`, and `LONGEST_LAT_CACHE.MISS`, so the unit is part of the public API.

## Control Flow
`tools/perf/pmu-events/Build` discovers this file and `jevents.py` parses it into generated perf tables. `jevents.py` maps `Unit` `cpu_core` and `cpu_atom` directly to those PMU names, turns `EventCode` into `event=`, `UMask` into `umask=`, `SampleAfterValue` into `period=`, `CounterMask` into `cmask=`, and `MSRIndex`/`MSRValue` into offcore or frontend MSR terms when supported by `lookup_msr`. The x86 map entry `GenuineIntel-6-BD,v1.21,lunarlake,core` selects this model's generated aliases. At runtime, perf resolves the same alias name separately for P-core and E-core PMUs when both units are present.

## State and Persistence
The JSON is static metadata. Persistent output is the generated `pmu-events.c` table with core/atom PMU names, periods, deprecation flags, offcore MSR encodings, and address-capable descriptions. Runtime state is limited to hardware counters, PMU scheduling, and offcore MSR programming performed by perf/kernel code. `Data_LA` marks address-capable precise-style memory events in generated descriptions, while `MSRIndex` and `MSRValue` are essential for offcore-response filtering and atom load-latency thresholds.

## Dependencies and Integration Points
Dependencies include the perf PMU JSON schema, `jevents.py`, `pmu-events.h`, x86 mapfile selection, hybrid PMU support for `cpu_core` and `cpu_atom`, and MSR filter support for offcore response registers `0x1a6/0x1a7` and latency threshold MSR `0x3F6`. The file integrates with top-down memory-bound analysis, cache hierarchy studies, prefetch tuning, offcore response attribution, and load/store retirement sampling. It is closely related to Lunar Lake virtual-memory, frontend, pipeline, and floating-point topics because memory stalls often need correlation with TLB walks, frontend fetch stalls, and vector workload intensity.

## Risks
Hybrid duplication is the largest risk: the same `EventName` can have different encodings, counters, descriptions, and units for `cpu_core` and `cpu_atom`, so tooling must not deduplicate by name alone. Offcore events depend on correct `MSRIndex`/`MSRValue` translation; wrong handling silently measures different response classes. `Data_LA` appears on many retired memory events, so dropping that field reduces sampling diagnostic value. Two deprecated records and several intentionally overlapping aggregate/detail aliases can lead to double counting or outdated usage if surfaced without deprecation metadata. Counter constraints differ sharply, including single-counter `L1D_PENDING.*` records and broader `0..9` P-core events.

## Test Signals
Validation should include `jq empty`, perf generation, and inspection of generated strings for `pmu=cpu_core` versus `pmu=cpu_atom`, `period=`, `cmask=`, and offcore MSR terms. `perf list` on Lunar Lake should show both unit-specific aliases where duplicates exist. Hardware smoke tests should cover P-core and E-core pinning separately, cache-hit/miss microbenchmarks, split/locked access tests, prefetch-heavy loops, and offcore DRAM/LLC response workloads. Regression tests should ensure deprecated flags remain attached and that duplicate alias names are preserved as unit-specific records rather than collapsed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/lunarlake/cache.json -->
