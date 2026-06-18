# subset-b-006668 grouped research

This grouped report covers Haswell and HaswellX x86 perf PMU metadata from the Ceph client copy of Linux `tools/perf`. The files are JSON event, metric, metric-group, and counter-capacity tables consumed at perf build time by the PMU event generator and exposed at runtime through generated perf aliases and metrics.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswell/hsw-metrics.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswell/hsw-metrics.json

## Purpose

This file defines 122 Haswell metric records for Linux perf. It is the Haswell top-down and system-metric catalog: package/core C-state residency, uncore frequency, SMI accounting, top-down microarchitecture levels, memory bandwidth and latency formulas, branch and instruction-mix ratios, SMT/core utilization helpers, pipeline throughput helpers, port-utilization breakdowns, and derived memory/cache/TLB indicators.

The x86 mapfile selects the `haswell` directory for `GenuineIntel-6-(3C|45|46)` models. Once compiled into perf, these metrics let users run `perf stat -M` or list metric groups without knowing the underlying raw events.

## Important APIs, Types, And Data

The file is declarative data. Its effective API is the perf metric JSON schema handled by `tools/perf/pmu-events/jevents.py`: `MetricName`, `MetricExpr`, `MetricGroup`, `BriefDescription`, and optional `ScaleUnit`. `MetricExpr` is parsed through perf's metric expression parser, simplified, then emitted into generated metric tables.

Important metric families include `tma_frontend_bound`, `tma_bad_speculation`, `tma_backend_bound`, `tma_retiring`, `tma_memory_bound`, `tma_core_bound`, `tma_fetch_latency`, `tma_fetch_bandwidth`, `tma_dram_bound`, `tma_ports_utilization`, `tma_ports_utilized_*`, `tma_port_0` through `tma_port_7`, `tma_info_memory_*`, `tma_info_system_*`, `tma_info_thread_*`, `C*_Residency`, `UNCORE_FREQ`, `smi_cycles`, and `smi_num`.

The expressions depend on aliases defined in sibling Haswell event files, including `CPU_CLK_UNHALTED.*`, `INST_RETIRED.*`, `UOPS_*`, `IDQ_*`, `BR_*`, `MACHINE_CLEARS.*`, `CYCLE_ACTIVITY.*`, `MEM_LOAD_UOPS_*`, `MEM_UOPS_RETIRED.*`, `OFFCORE_*`, `DTLB_*`, `ITLB_*`, and uncore `UNC_*` aliases. They also use perf expression variables such as `#SMT_on`, `#core_wide`, `#num_cpus_online`, `#num_dies`, and built-in events like `duration_time`, `msr@tsc@`, `msr@aperf@`, `msr@smi@`, and power/cstate PMUs.

## Control Flow

At build time, `jevents.py` scans the Haswell directory, skips only `metricgroups.json` for event loading, and creates `JsonEvent` objects for metric entries. `MetricExpr` is parsed by `metric.ParsePerfJson(...).Simplify()`, metric-group strings are preserved, descriptions are compacted into the generated string table, and metric records are emitted into generated `pmu-events.c`.

At runtime, perf metric expansion resolves metric names into event aliases, raw event specs, special PMUs, constants, and conditional expression branches. Metrics do not program counters directly; they expand into the event set needed by `perf stat`, then calculate ratios or percentages from measured counter values.

## State And Persistence Behavior

The JSON stores persistent metric formulas and display metadata only. It does not persist counter samples, derived values, or runtime state. Runtime state lives in perf evsels, kernel PMU file descriptors, and the measured workload. Formula conditionals such as `if #SMT_on else` adapt to detected topology at evaluation time.

## Dependencies And Integration Points

This file integrates with `arch/x86/mapfile.csv`, Haswell core and uncore event JSON files, `tools/perf/pmu-events/jevents.py`, `metric.py`, generated `pmu-events.c`, perf metric lookup and expression evaluation code, `perf list`, and `perf stat -M`. It depends on sibling event aliases staying stable because formulas reference event names textually. It also depends on kernel exposure of MSR, power, cstate, and uncore PMUs for system-level metrics.

## Risks And Edge Cases

Textual event references are the main risk: renaming or deleting an event alias in another JSON file can break metric expansion even when this file remains valid JSON. Several formulas divide by event counts such as branch counts, store counts, walk counts, or elapsed time; zero or multiplexed counts can produce undefined, capped, or misleading results. SMT-aware conditionals and hard-coded constants such as slot width, assist costs, and latency weights are Haswell-specific and should not be reused for HaswellX or later models without validation. Metrics that mix core, package, MSR, power, and uncore events can fail partially on kernels or systems that do not expose every required PMU.

## Test Signals

Useful checks include `jq empty`, running `jevents.py` generation for x86, building `tools/perf`, `perf test pmu-events`, `perf test expr`, and `perf list --details` for Haswell metric names. Runtime validation should include `perf stat -M tma_frontend_bound,tma_backend_bound,tma_retiring,tma_bad_speculation`, a memory-stress run for `tma_info_memory_*`, and a system-level run for `Power`, `SoC`, and `smi` groups on hardware or fixtures with the required MSR and uncore PMUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswell/hsw-metrics.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswell/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswell/memory.json

## Purpose

This file defines 60 Haswell core PMU memory and transactional-memory events. It covers HLE and RTM retirement, transactional abort causes, memory-ordering machine clears, misaligned memory references, load-latency thresholds, and offcore-response L3-miss/local-DRAM classifications.

## Important APIs, Types, And Data

The records use the perf event JSON schema: `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, optional `PEBS`, and descriptions. The file has no `Unit`, so entries are generated for the default core PMU selected by the Haswell mapfile.

Major event families are `HLE_RETIRED` with 8 entries, `RTM_RETIRED` with 8, `TX_EXEC` with 5, `TX_MEM` with 7, `MEM_TRANS_RETIRED` with 8 load-latency threshold events from greater-than-4 through greater-than-512 cycles, `MISALIGN_MEM_REF`, `MACHINE_CLEARS.MEMORY_ORDERING`, and 21 `OFFCORE_RESPONSE.*.L3_MISS.*` aliases covering demand, prefetch, code, data, RFO, all-reads, and all-requests views. PEBS is used where precise sampling is supported, notably memory transaction latency.

## Control Flow

During perf build generation, `jevents.py` reads each entry, lowercases the event alias, converts `EventCode` and nonzero `UMask` into perf event config strings, preserves sample periods, and records PEBS precision hints. The generated Haswell event table is then selected at runtime for matching Haswell CPU models.

At runtime, perf aliases from this file are used by direct `perf stat -e` or `perf record -e` requests and by metrics in `hsw-metrics.json`. Offcore response aliases are translated into event selectors plus offcore response match fields by the perf event generation path.

## State And Persistence Behavior

The file persists static event metadata. Transactional state, abort causes, load latencies, and offcore responses are measured by hardware during a perf run. `SampleAfterValue` persists as a default sampling period, while users may override sampling and counting behavior.

## Dependencies And Integration Points

Integration points include Haswell model selection, `jevents.py`, perf alias lookup, TSX/HLE hardware support, PEBS support for precise memory events, offcore response MSR encoding, and the Haswell metrics file. Memory-bound and data-sharing top-down metrics depend on aliases such as `MEM_TRANS_RETIRED.*`, `OFFCORE_RESPONSE.*`, `MEM_LOAD_UOPS_*`, and transactional abort events.

## Risks And Edge Cases

TSX/HLE events may be unavailable or disabled by microcode/kernel policy even on Haswell-family systems, so aliases can exist while counters are not useful. Offcore-response events are encoding-sensitive and can be easy to misclassify because request type and response type are both embedded in the alias. Load-latency threshold events are not equivalent to average latency; they count retired load events passing a threshold. PEBS hints must match hardware precision support or sampling users can get misleading expectations.

## Test Signals

Validate with `jq empty`, x86 PMU event generation, and `perf test pmu-events`. Runtime tests can use pointer-chasing or memory-load-latency workloads for `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_*`, TSX-capable microbenchmarks for `RTM_RETIRED` and `HLE_RETIRED`, and memory-locality workloads for `OFFCORE_RESPONSE.*.LOCAL_DRAM` versus `.ANY_RESPONSE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswell/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswell/metricgroups.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswell/metricgroups.json

## Purpose

This file maps 124 Haswell metric-group names to user-facing descriptions. It provides the descriptive catalog used by perf for top-down groups, spreadsheet-derived categories, issue-oriented subgroups, memory and frontend/backend groupings, power/system groups, and legacy aliases.

## Important APIs, Types, And Data

Unlike the event arrays, this file is a JSON object. Keys are metric group names and values are descriptions. `jevents.py` detects files ending in `metricgroups.json`, records each key/value in `_metricgroups`, and emits a generated lookup table for metric-group descriptions.

The keys include broad groups such as `Backend`, `Frontend`, `Mem`, `Pipeline`, `Power`, `Summary`, `SMT`, `SoC`, `Branches`, `CacheHits`, and `CacheMisses`; top-down levels `TopdownL1` through `TopdownL6` and `tma_L1_group` through `tma_L6_group`; and contribution groups like `tma_backend_bound_group`, `tma_frontend_bound_group`, `tma_memory_bound_group`, `tma_ports_utilization_group`, `tma_dtlb_load_group`, and `tma_store_bound_group`. Most spreadsheet-derived groups share the description "Grouping from Top-down Microarchitecture Analysis Metrics spreadsheet."

## Control Flow

At build time, this file follows a separate control path from event and metric arrays. `jevents.py` loads the object, stores group descriptions, excludes the file from normal event parsing, and later emits a sorted `metricgroups` lookup table into generated C. At runtime, perf uses the generated lookup to describe metric groups in list and metric-discovery paths.

## State And Persistence Behavior

The file persists display metadata only. It does not affect counter programming or metric expression evaluation directly. The generated lookup is static until perf is rebuilt.

## Dependencies And Integration Points

This file integrates with `hsw-metrics.json`, perf's metric listing UI, generated `pmu-events.c`, and any tooling that displays group descriptions. It depends on group names matching the semicolon-separated `MetricGroup` tokens used by metrics; a group description with no matching metric is harmless but stale, while a metric group with no description produces weaker help output.

## Risks And Edge Cases

Because the schema is object-shaped rather than array-shaped, treating this file like a normal event file would break generation. Duplicate or near-duplicate group names such as `MachineClears` and `Machine_Clears`, `MemoryBW` and `Memory_BW`, or legacy `TopdownL*` and newer `tma_L*_group` are intentional compatibility surfaces but can confuse consumers that normalize names. Descriptions are generic for many groups, so they help navigation more than semantic interpretation.

## Test Signals

Run `jq empty`, x86 `jevents.py` generation, and `perf test pmu-events`. `perf list --metricgroups` or equivalent list paths should show descriptions for representative groups such as `TopdownL1`, `tma_backend_bound_group`, `Power`, `SoC`, and `MemoryBW`. A consistency check can compare `MetricGroup` tokens in `hsw-metrics.json` with keys in this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswell/metricgroups.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswell/other.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswell/other.json

## Purpose

This file defines four Haswell core PMU events outside the main memory, pipeline, cache, frontend, and TLB categories. They cover privilege-level cycle accounting and split/uncacheable lock duration: `CPL_CYCLES.RING0`, `CPL_CYCLES.RING0_TRANS`, `CPL_CYCLES.RING123`, and `LOCK_CYCLES.SPLIT_LOCK_UC_LOCK_DURATION`.

## Important APIs, Types, And Data

Each record uses the standard event schema with `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, and for `LOCK_CYCLES...` a longer `PublicDescription`. All entries are default core-PMU aliases. `CPL_CYCLES` uses event `0x5C` with masks for ring 0 and non-ring-0 cycles; `LOCK_CYCLES` uses event `0x63`, mask `0x1`.

## Control Flow

`jevents.py` ingests the entries with the other Haswell arrays, converts selector and mask fields into generated perf alias configs, and emits them into the Haswell core event table. Runtime perf uses the aliases for direct event requests and as possible ingredients in OS/kernel-utilization analysis.

## State And Persistence Behavior

The file persists static alias metadata and sample periods. Privilege-cycle counts and lock-duration counts are hardware/runtime state measured during a perf session. No local mutable state exists in the JSON.

## Dependencies And Integration Points

The entries integrate with Haswell model matching, perf alias generation, privilege filter usage (`:k`, `:u`) in metrics, and lock-contention diagnostics. `CPL_CYCLES` is related to system/kernel metrics in `hsw-metrics.json`, while `LOCK_CYCLES...` supports split-lock and uncacheable-lock investigation.

## Risks And Edge Cases

The privilege-level naming can be misread: `RING123` is non-ring-0 rather than all user-only cycles under every perf filter combination. `RING0_TRANS` counts intervals between halts while in ring 0, not cycles. Lock-cycle events may be rare and workload-sensitive, and split-lock behavior can be affected by kernel mitigation or platform configuration.

## Test Signals

Validate JSON and generated aliases. Runtime checks include kernel-heavy versus user-heavy workloads for `CPL_CYCLES.*`, a lock-stress or split-lock test where available for `LOCK_CYCLES.SPLIT_LOCK_UC_LOCK_DURATION`, and `perf list` verification that the descriptions are visible under Haswell core events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswell/other.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswell/pipeline.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswell/pipeline.json

## Purpose

This file defines 130 Haswell core pipeline and execution events. It covers arithmetic divider uops, branch execution and retirement, mispredictions, unhalted clocks, cycle activity, instruction retirement, front/back-end stalls, load blocks, LSD behavior, machine clears, move elimination, resource stalls, reorder-buffer/LBR activity, reservation-station emptiness, uop issue/execution/retirement, and per-port dispatch/execution.

## Important APIs, Types, And Data

The records use `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, and descriptions. There is no explicit `Unit`, so entries target the default Haswell core PMU. Event families include `BR_INST_EXEC` with 13 entries, `BR_INST_RETIRED` with 9, `BR_MISP_EXEC` with 9, `BR_MISP_RETIRED` with 4, `CPU_CLK_UNHALTED` and `CPU_CLK_THREAD_UNHALTED`, `CYCLE_ACTIVITY`, `INST_RETIRED`, `IDQ`-related metrics via sibling frontend events, `LD_BLOCKS`, `LSD`, `MACHINE_CLEARS`, `RESOURCE_STALLS`, `UOPS_DISPATCHED_PORT`, `UOPS_EXECUTED`, `UOPS_EXECUTED_PORT`, `UOPS_ISSUED`, and `UOPS_RETIRED`.

The file contains several aliases that share selectors but differ in intended interpretation, such as cycles versus events using counter masks in raw use. Haswell top-down metrics depend heavily on these names.

## Control Flow

At generation time, `jevents.py` loads the array, lowercases aliases, converts event selector and umask into perf event strings, attaches sample periods, and emits compact event table rows. Runtime perf resolves aliases to hardware counter programming. Metrics in `hsw-metrics.json` then combine these counters into top-down ratios such as retiring, frontend bound, bad speculation, backend bound, ports utilization, and branch resteers.

## State And Persistence Behavior

The JSON persists PMU alias definitions. Pipeline occupancy, uop flow, branch behavior, and stall cycles are measured by hardware per run. Sample periods are static defaults but perf users can override them.

## Dependencies And Integration Points

Integration points include Haswell CPU model mapping, `jevents.py`, generated PMU tables, perf stat/record/list flows, and Haswell top-down metrics. The file also depends on Intel event semantics for counter masks and any-thread variants, especially for SMT-aware formulas that distinguish thread and core-wide behavior.

## Risks And Edge Cases

Several events represent cycles, slots, uops, or occurrences with similar names; mixing them in formulas requires careful denominators. SMT and any-thread variants can double-count or undercount if used with the wrong topology assumptions. Port events are particularly sensitive to microarchitecture-specific execution-port mapping. Branch execution events and retired branch events measure different pipeline stages, so ratios across them can be misleading without context.

## Test Signals

Use `jq empty`, x86 event generation, `perf test pmu-events`, and alias checks for representative `UOPS_*`, `BR_*`, `CPU_CLK_*`, and `CYCLE_ACTIVITY.*` events. Runtime validation can use branch-heavy code, divider-heavy code, port-pressure microbenchmarks, and stalled memory workloads to confirm directional changes in the expected counters and top-down metrics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswell/pipeline.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswell/uncore-cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswell/uncore-cache.json

## Purpose

This file defines 26 Haswell uncore cache/CBOX events. It exposes LLC/CBOX cache-lookup classifications by request source and MESI state, plus external snoop response classifications for hit, hitm, miss, eviction, external, and cross-core cases.

## Important APIs, Types, And Data

The entries use `EventName`, `EventCode`, `UMask`, `Counter`, `Unit`, `PerPkg`, and descriptions. `Unit` is `CBOX`, `PerPkg` is set, and counters are generally `0,1`, indicating package-level uncore CBOX programmable counters. `UNC_CBO_CACHE_LOOKUP` has 16 aliases spanning `ANY`, `READ`, `WRITE`, and `EXTSNP` crossed with MESI-style state masks. `UNC_CBO_XSNP_RESPONSE` has 9 aliases for HIT/HITM/MISS by eviction, external, and xcore response sources.

## Control Flow

During generation, `jevents.py` maps the `CBOX` unit to an uncore PMU table, converts event and umask fields to perf configs, and carries `PerPkg` metadata into generated entries. Runtime perf resolves these aliases against kernel-exposed uncore CBOX PMUs and programs package-scope counters rather than per-thread core counters.

## State And Persistence Behavior

The JSON stores static uncore alias metadata. Actual LLC lookup counts and snoop responses are maintained by uncore hardware during measurement. Package aggregation is driven by perf and kernel PMU topology, not by mutable state in this file.

## Dependencies And Integration Points

The file integrates with Haswell model selection, uncore PMU discovery, generated event tables, `perf list`, `perf stat`, and metrics that estimate data sharing, false sharing, L3 behavior, and memory traffic. It depends on the kernel naming and availability of CBOX PMUs matching perf's generated unit mapping.

## Risks And Edge Cases

Uncore PMU naming and package topology are the largest integration risks. Systems may expose multiple CBOX instances, so aggregation can differ from a single core event. MESI and snoop-response masks are easy to mix up; wrong masks would make cache-sharing diagnosis misleading. `PerPkg` events should not be interpreted as per-thread counts.

## Test Signals

Validate JSON and x86 generation. On compatible hardware or fixtures, `perf list` should show `unc_cbo_cache_lookup.*` and `unc_cbo_xsnp_response.*` under CBOX-style uncore PMUs. Runtime checks should compare lookup counts under read-heavy, write-heavy, and cross-core sharing workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswell/uncore-cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswell/uncore-interconnect.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswell/uncore-interconnect.json

## Purpose

This file defines six Haswell uncore interconnect/ARB events. They count ARB tracker occupancy and request allocations for coherent and non-coherent core outgoing traffic, including all requests, cycles with any outstanding request, coherency tracker requests, and write transactions.

## Important APIs, Types, And Data

The records use `EventName`, `EventCode`, `UMask`, `Counter`, `Unit`, `PerPkg`, `BriefDescription`, and some `PublicDescription` fields. `Unit` is `ARB`, `PerPkg` is set, and counters are `0` or `0,1`. Events include `UNC_ARB_COH_TRK_OCCUPANCY.All`, `UNC_ARB_COH_TRK_REQUESTS.ALL`, `UNC_ARB_TRK_OCCUPANCY.ALL`, `UNC_ARB_TRK_OCCUPANCY.CYCLES_WITH_ANY_REQUEST`, `UNC_ARB_TRK_REQUESTS.ALL`, and `UNC_ARB_TRK_REQUESTS.WRITES`.

## Control Flow

`jevents.py` generates uncore ARB aliases from this array, preserving package scope and converting selector/mask pairs into perf configs. At runtime, perf matches the generated aliases against ARB uncore PMU devices and aggregates package-level interconnect request tracking.

## State And Persistence Behavior

The file persists static metadata only. Queue occupancy, outstanding requests, and write allocation counts are runtime hardware state. Package-level persistence and aggregation are handled by perf's uncore PMU support.

## Dependencies And Integration Points

These events integrate with Haswell uncore discovery, generated PMU tables, `perf list`, `perf stat`, and Haswell system/memory metrics. `hsw-metrics.json` uses `UNC_ARB_TRK_REQUESTS.ALL` and `UNC_ARB_COH_TRK_REQUESTS.ALL` for DRAM bandwidth-use estimation.

## Risks And Edge Cases

Occupancy events and allocation-count events have different units; treating occupancy as requests can lead to incorrect bandwidth or pressure conclusions. `UNC_ARB_TRK_OCCUPANCY.ALL` and `.CYCLES_WITH_ANY_REQUEST` share event/mask fields but differ semantically through the counter configuration/description, so tests should verify generated aliases remain distinct. Multi-socket aggregation can make per-package traffic appear duplicated if users sum incorrectly.

## Test Signals

Run `jq empty`, x86 generation, and `perf test pmu-events`. On Haswell hardware or fixtures, verify `perf list` exposes ARB aliases and run memory/write-heavy workloads to check that request and write counts move in the expected direction. Metric validation should include `tma_info_system_dram_bw_use`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswell/uncore-interconnect.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswell/virtual-memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswell/virtual-memory.json

## Purpose

This file defines 49 Haswell core virtual-memory and TLB events. It covers DTLB load/store misses, ITLB misses, STLB hits by page size, page-walk completions and durations, PDE cache misses, EPT walk cycles, page-walker memory-source loads, TLB flushes, and ITLB flushes.

## Important APIs, Types, And Data

Records use the standard event schema with `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, and descriptions. Event families include 10 `DTLB_LOAD_MISSES`, 10 `DTLB_STORE_MISSES`, 9 `ITLB_MISSES`, 16 `PAGE_WALKER_LOADS`, `EPT.WALK_CYCLES`, `ITLB.ITLB_FLUSH`, and `TLB_FLUSH.DTLB_THREAD`/`TLB_FLUSH.STLB_ANY`.

The page-walk events distinguish completed walks for 4K, 2M/4M, and 1G pages from walk duration cycles and from memory-source loads in L1, L2, L3, or memory. EPT-prefixed page-walker load events support virtualization-related translation analysis.

## Control Flow

Build-time generation lowercases aliases and emits selector/mask/sample-period metadata into the Haswell core table. Runtime perf uses these aliases directly or through metrics such as `tma_dtlb_load`, `tma_dtlb_store`, `tma_itlb_misses`, and `tma_info_memory_tlb_page_walks_utilization`.

## State And Persistence Behavior

The JSON persists event definitions. TLB occupancy, page-walk behavior, EPT translation activity, and flushes are hardware/runtime state. Sample periods are static hints and do not store any measured state.

## Dependencies And Integration Points

The file depends on Haswell PMU semantics and integrates with `jevents.py`, generated perf tables, top-down memory/TLB metrics, huge-page diagnostics, virtualization/EPT analysis, and `perf stat`/`perf record` workflows. The metric file references `DTLB_LOAD_MISSES.WALK_DURATION`, `DTLB_STORE_MISSES.WALK_DURATION`, `ITLB_MISSES.WALK_DURATION`, and STLB-hit events by name.

## Risks And Edge Cases

Page-size-specific event names are easy to misinterpret on workloads that mix page sizes. Walk-completed events, miss-causes-walk events, walk-duration cycles, and page-walker memory-source loads are related but not interchangeable. EPT events require virtualization contexts and may be zero on ordinary host workloads. TLB flush counts can be dominated by OS behavior and CPU migration rather than application address locality.

## Test Signals

Validate JSON and generated aliases. Runtime checks should include pointer-chasing over large memory, huge-page versus 4K-page comparisons, instruction-footprint stress for ITLB events, and virtualization workloads for EPT/page-walker EPT aliases. Top-down TLB metrics should move with the DTLB/ITLB stressors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswell/virtual-memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswellx/cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswellx/cache.json

## Purpose

This file defines 97 HaswellX core cache, memory-request, and offcore events. HaswellX is selected for `GenuineIntel-6-3F`, and this file supplies server-oriented cache behavior aliases for L1D/L2/LLC behavior, fill-buffer pressure, outstanding offcore requests, retired memory uops, snoop outcomes, remote/local DRAM classifications, split locks, and store queue pressure.

## Important APIs, Types, And Data

Records use `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, and sometimes `PublicDescription`. There is no `Unit`, so entries belong to the HaswellX core PMU.

Major families include `L1D.REPLACEMENT`, five `L1D_PEND_MISS` events, `L2_LINES_IN/OUT`, 16 `L2_RQSTS`, 8 `L2_TRANS`, `LONGEST_LAT_CACHE`, `MEM_LOAD_UOPS_RETIRED`, `MEM_LOAD_UOPS_L3_HIT_RETIRED`, `MEM_LOAD_UOPS_L3_MISS_RETIRED`, `MEM_UOPS_RETIRED`, `OFFCORE_REQUESTS`, `OFFCORE_REQUESTS_OUTSTANDING`, `OFFCORE_REQUESTS_BUFFER.SQ_FULL`, 21 `OFFCORE_RESPONSE` aliases for LLC hit/snoop outcomes, `LOCK_CYCLES.CACHE_LOCK_DURATION`, and `SQ_MISC.SPLIT_LOCK`.

## Control Flow

`jevents.py` emits these records into the HaswellX model table based on the x86 mapfile. Runtime perf resolves aliases for direct use and for metrics that may be shared or generated for server Haswell variants. Offcore response aliases require the generator and runtime perf code to preserve the request/response encoding accurately.

## State And Persistence Behavior

The file stores static event metadata and sample periods. Cache line states, miss queues, fill buffers, snoop responses, and offcore request occupancy are measured by hardware during a run. No local state is persisted outside the generated perf tables.

## Dependencies And Integration Points

Integration points include HaswellX model matching, perf core PMU alias lookup, offcore response MSR handling, cache/memory performance workflows, and any metrics that use the names defined here. These aliases are especially relevant to server memory locality, snoop traffic, NUMA effects, and cache-sharing analysis.

## Risks And Edge Cases

Haswell and HaswellX share many names but not all event semantics; copying formulas or expectations between directories can be wrong. Offcore responses are dense encodings where request type, LLC hit/miss, snoop, local/remote, and prefetch distinctions must remain intact. Outstanding request events count occupancy or cycles with occupancy, not just request totals. Remote DRAM and HITM events require NUMA/cross-core conditions to be meaningful.

## Test Signals

Run `jq empty`, x86 `jevents.py` generation, `perf test pmu-events`, and representative `perf list` checks for `L2_RQSTS.*`, `MEM_LOAD_UOPS_RETIRED.*`, `OFFCORE_REQUESTS_OUTSTANDING.*`, and `OFFCORE_RESPONSE.*`. Runtime validation should use cache-fit versus cache-miss workloads, NUMA-local/remote memory placement, cross-core sharing, and store/write pressure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswellx/cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswellx/counter.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswellx/counter.json

## Purpose

This file defines the HaswellX PMU counter capacity table. It tells perf's generated PMU metadata how many fixed and generic counters are available for the core PMU and each listed uncore PMU unit.

## Important APIs, Types, And Data

The file is an array of records with `Unit`, `CountersNumFixed`, and `CountersNumGeneric`. It contains 11 units: `core` with 3 fixed and 4 generic counters; uncore `CBOX`, `HA`, `PCU`, `QPI`, `R2PCIe`, `SBOX`, and `iMC` with 4 generic counters; `IRP` and `UBOX` with 2 generic counters; and `R3QPI` with 3 generic counters. All uncore units list zero fixed counters.

This is metadata rather than an event list. Its effective API is the counter-info portion of the perf PMU event JSON schema.

## Control Flow

At build time, the PMU event generator reads counter records and emits generated counter-capacity metadata alongside event aliases. Runtime perf can use this metadata to understand PMU constraints, display PMU information, and reason about grouping pressure when scheduling events.

## State And Persistence Behavior

The file persists static hardware-capacity declarations. It does not represent allocated counters or active event groups. Runtime allocation, multiplexing, and scheduling state are maintained by perf and the kernel PMU subsystem.

## Dependencies And Integration Points

This file integrates with HaswellX model mapping, generated PMU metadata, event scheduling, and uncore unit naming. Its unit names must match event-file `Unit` values and kernel PMU naming conventions for HaswellX uncore devices.

## Risks And Edge Cases

Incorrect counter counts can make perf overestimate or underestimate how many events can be grouped without multiplexing. Unit-name mismatches can disconnect capacity metadata from the corresponding event aliases. The table is HaswellX-specific and should not be reused for desktop Haswell or later server generations.

## Test Signals

Validate JSON syntax and generation. Compare generated counter metadata against expected HaswellX PMU capacities, and run grouped `perf stat` workloads to check whether multiplexing behavior is plausible for core and uncore groups. Alias checks should confirm that units with events elsewhere in the HaswellX directory have matching counter-capacity entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswellx/counter.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswellx/floating-point.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswellx/floating-point.json

## Purpose

This file defines 10 HaswellX core floating-point, vector-transition, and SIMD move-elimination events. It covers AVX instruction counting, FP assists by SIMD/x87 input/output cause, SIMD move elimination success/failure, and AVX/SSE transition penalties.

## Important APIs, Types, And Data

Entries use `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, and `PublicDescription` where helpful. Event families are `AVX_INSTS.ALL`, `FP_ASSIST.ANY`, `FP_ASSIST.SIMD_INPUT`, `FP_ASSIST.SIMD_OUTPUT`, `FP_ASSIST.X87_INPUT`, `FP_ASSIST.X87_OUTPUT`, `MOVE_ELIMINATION.SIMD_ELIMINATED`, `MOVE_ELIMINATION.SIMD_NOT_ELIMINATED`, `OTHER_ASSISTS.AVX_TO_SSE`, and `OTHER_ASSISTS.SSE_TO_AVX`.

## Control Flow

The generator converts these core event records into HaswellX aliases. Runtime perf uses them directly for event selection or indirectly through floating-point and assist metrics. `AVX_INSTS.ALL` is event `0xC6` mask `0x7`; `FP_ASSIST` uses event `0xCA`; SIMD move elimination uses event `0x58`; AVX/SSE transition assists use event `0xC1`.

## State And Persistence Behavior

The JSON persists event definitions and sample periods. Floating-point assists, move-elimination outcomes, and transition penalties are workload-dependent hardware events measured during a perf run.

## Dependencies And Integration Points

This file integrates with HaswellX mapfile selection, perf PMU alias generation, floating-point performance investigations, compiler/vectorization diagnostics, and metric groups such as `Flops`, `FpScalar`, `FpVector`, and assist-related top-down categories when those metrics are available for the model.

## Risks And Edge Cases

`AVX_INSTS.ALL` notes that a whole `rep` string counts once, so it is not an instruction-throughput substitute in every case. FP assist events count exceptional microcode/help paths rather than normal FP operations. AVX/SSE transition events depend on code generation and upper-lane state, so they can be mitigated by compiler options or inserted `vzeroupper` instructions. Move-elimination events are candidate-uop outcomes, not architectural moves.

## Test Signals

Validate JSON and generated aliases. Runtime tests can use vectorized AVX loops, scalar/x87/SIMD exceptional inputs, code with and without `vzeroupper`, and move-heavy SIMD instruction sequences. `perf list` should show all ten aliases under the HaswellX core PMU.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswellx/floating-point.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswellx/frontend.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswellx/frontend.json

## Purpose

This file defines 29 HaswellX core frontend events. It covers branch-address clears, DSB-to-MITE switch penalties, instruction-cache hits/misses/stalls, IDQ delivery by DSB/MITE/microcode sequencer, and frontend under-delivery cycles for top-down analysis.

## Important APIs, Types, And Data

Records use `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, and sometimes `PublicDescription`. Families include `BACLEARS.ANY`, `DSB2MITE_SWITCHES.PENALTY_CYCLES`, four `ICACHE` aliases, 17 `IDQ` aliases, and six `IDQ_UOPS_NOT_DELIVERED` aliases.

Several aliases intentionally share event selector and mask values while representing different derived interpretations, such as DSB cycles versus DSB uops or MITE cycles versus MITE uops. Top-down frontend metrics use these names to distinguish decode-source coverage, microcode sequencer behavior, and delivery shortfall.

## Control Flow

At build time, `jevents.py` emits these entries into the HaswellX core event table. At runtime, perf programs the selected frontend counters or expands metrics that reference them. The aliases support both direct `perf stat -e` analysis and derived frontend-bound, fetch-bandwidth, fetch-latency, DSB, MITE, and microcode-sequencer metrics.

## State And Persistence Behavior

The file stores static alias definitions and sample periods. Instruction-cache state, decode-source usage, IDQ occupancy, and frontend delivery shortages are hardware/runtime behavior. No state is mutated or persisted by the JSON itself.

## Dependencies And Integration Points

Dependencies include HaswellX model matching, perf PMU event generation, generated alias lookup, top-down metric formulas, frontend performance workflows, and event semantics for DSB, MITE, LSD, and microcode sequencer paths. It overlaps conceptually with Haswell pipeline metrics but is HaswellX-specific.

## Risks And Edge Cases

Shared encodings with different names can confuse validation that looks only at event selector/mask pairs. The difference between cycles, uops, occurrences, and penalties is central; using the wrong alias in a formula changes the unit of analysis. Some frontend events are sensitive to SMT, instruction-cache footprint, branch predictor behavior, and microcode assists, so synthetic tests need controlled workloads.

## Test Signals

Validate JSON and generated aliases. Runtime tests should include instruction-cache footprint stress, branch-indirect or branch-clear workloads, decode-source comparisons that fit in DSB versus force MITE decode, and microcode-heavy instruction sequences. `perf list` should expose representative `ICACHE.*`, `IDQ.*`, and `IDQ_UOPS_NOT_DELIVERED.*` aliases for HaswellX.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswellx/frontend.json -->
