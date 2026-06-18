# subset-b-006632 BroadwellX perf PMU JSON research

This grouped report covers the BroadwellX x86 PMU event and metric JSON files assigned to `subset-b-006632`. These files are data inputs to the Linux `tools/perf/pmu-events` build pipeline, not executable modules. The main consuming path is `pmu-events/Build`, which copies or generates JSON inputs, runs `pmu-events/jevents.py`, and emits `pmu-events.c`; runtime perf code then exposes the generated `struct pmu_event` and `struct pmu_metric` tables through aliases, `perf list`, and metric evaluation. The x86 mapfile maps `GenuineIntel-6-4F,v23,broadwellx,core` to this directory.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellx/bdx-metrics.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellx/bdx-metrics.json

## Purpose

`bdx-metrics.json` defines 186 BroadwellX core and system metrics for perf. It is the architectural metric layer above the raw event files in the same directory: formulas combine core events, uncore events, MSR pseudo-events, duration/time aliases, and perf expression conditionals to expose Top-down Microarchitecture Analysis categories, cache/memory ratios, power residency, bandwidth, IPC/CPI, SMT, kernel utilization, and instruction-mix diagnostics.

## Important APIs, types, and schema

Each array element is a metric dictionary consumed by `jevents.py` as a `JsonEvent` with `MetricName` set rather than `EventName`. Important fields are `MetricName`, `MetricExpr`, `MetricGroup`, `BriefDescription`, `PublicDescription`, `ScaleUnit`, `MetricThreshold`, `MetricConstraint`, and `MetricgroupNoGroup`. `jevents.py` maps these into `struct pmu_metric` fields: `metric_name`, `metric_expr`, `metric_group`, `metric_threshold`, `unit`, `desc`, `long_desc`, `metricgroup_no_group`, and `event_grouping`.

The metric expressions are parsed by `metric.ParsePerfJson(...).Simplify()` and may be rewritten by `metric.RewriteMetricsInTermsOfOthers()`. Expressions use perf JSON syntax such as `cpu@EVENT\\,cmask\\=1@`, `msr@tsc@`, arithmetic, `min`/`max`, and conditional expressions keyed by runtime variables like `#SMT_on`, `#core_wide`, and `#num_cpus_online`. Metric constraints such as `NO_GROUP_EVENTS` and `NO_GROUP_EVENTS_SMT` are converted to the `enum metric_event_groups` values in `pmu-events.h`; thresholds are stored as strings because `jevents.py` explicitly avoids parsing them.

## Control flow and integration

During the perf build, `Build` includes all x86 JSON files in `SRC_JSON`, optionally copies them to `$(OUTPUT)pmu-events/arch`, and runs `jevents.py`. `preprocess_one_file()` reads this file, adds compact metric strings to the global string table, and `process_one_file()` later appends unique metrics to the BroadwellX metric table. At runtime, `find_core_metrics_table("x86", cpuid)` resolves the BroadwellX table through `arch/x86/mapfile.csv`; `perf list` can print these metrics and `perf stat -M ...` can expand their event dependencies.

This file is tightly coupled to the adjacent raw event files. For example, Top-down and memory metrics reference cache events such as `MEM_LOAD_UOPS_RETIRED.*`, frontend events such as `IDQ_UOPS_NOT_DELIVERED.*`, floating-point events such as `FP_ARITH_INST_RETIRED.*`, memory transaction events such as `MEM_TRANS_RETIRED.*`, and offcore response events encoded in `cache.json` and `memory.json`. It also references other BroadwellX JSON files outside this work item, including pipeline, virtual-memory, uncore-memory, uncore-cache, uncore-interconnect, uncore-io, and power events.

## State and persistence behavior

There is no mutable runtime state in the JSON. Its persistent effect is the generated `pmu-events.c` metric table embedded into the perf binary. Runtime state is limited to perf's event scheduling and metric evaluation: constraints can change how event groups are scheduled, thresholds affect reporting, and formulas using `#SMT_on`, `duration_time`, or uncore counters vary by machine and workload.

## Dependencies

The file depends on the perf PMU JSON schema, `jevents.py`, `metric.py`, `pmu-events.h`, the x86 mapfile entry for BroadwellX, and the raw event names it references. It also depends on kernel/perf support for pseudo-events like `msr@tsc@`, `power@energy-pkg@`, `duration_time`, and named PMU instances such as `cbox_0`.

## Risks

The largest risk is stale or missing event references: because formulas span many files, a renamed event in cache, memory, frontend, floating-point, pipeline, virtual-memory, or uncore JSON will break metric expansion. Several metrics use `MetricConstraint` or `MetricgroupNoGroup` to avoid unsafe grouping; dropping those fields can lead to invalid multiplexing or misleading values under SMT/NMI constraints. Thresholds are not parsed by `jevents.py`, so syntax errors may survive generation and only surface in perf display behavior. Many formulas include division by event counts; zero-count workloads rely on perf metric handling to avoid noisy or undefined output. Some formulas mix core and uncore/system scope, so aggregation mode and PMU availability can materially affect interpretation.

## Test signals

Useful validation is `jq empty bdx-metrics.json`, a `tools/perf` build that regenerates `pmu-events.c`, `pmu-events/metric_test.py`, and a runtime smoke test on BroadwellX or compatible test fixtures with `perf list --json` and `perf stat -M TopdownL1,tma_backend_bound`. Targeted checks should verify that `MetricConstraint` strings map to `enum metric_event_groups`, that TopdownL1/TopdownL2 formulas expand without missing aliases, and that metric group descriptions from `metricgroups.json` cover the groups emitted here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellx/bdx-metrics.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellx/cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellx/cache.json

## Purpose

`cache.json` defines 88 BroadwellX core PMU events for L1D, L2, LLC, offcore request/response, memory uop retirement, and lock/cache behavior. It supplies the raw aliases that perf users can request directly and that higher-level BroadwellX metrics use for cache hit/miss, memory-bound, offcore snoop, false-sharing, bandwidth, and latency analysis.

## Important APIs, types, and schema

The file is an array of event dictionaries with fields such as `EventName`, `EventCode`, `UMask`, `Counter`, `CounterMask`, `SampleAfterValue`, `BriefDescription`, `PublicDescription`, `AnyThread`, `PEBS`, `Data_LA`, `Errata`, `MSRIndex`, and `MSRValue`. `jevents.py` converts each entry to a `struct pmu_event`: `EventName` becomes lowercase `name`, raw fields become an event encoding string, descriptions become `desc` and `long_desc`, `PEBS` appends precise-event notes, and `Errata` is appended to descriptions as a spec-update note.

Important event families include `L1D.REPLACEMENT`, `L1D_PEND_MISS.*`, `L2_LINES_IN.*`, `L2_RQSTS.*`, `L2_TRANS.*`, `LONGEST_LAT_CACHE.*`, `MEM_LOAD_UOPS_RETIRED.*`, `MEM_LOAD_UOPS_L3_HIT_RETIRED.*`, `MEM_LOAD_UOPS_L3_MISS_RETIRED.*`, `OFFCORE_REQUESTS.*`, `OFFCORE_REQUESTS_OUTSTANDING.*`, `OFFCORE_RESPONSE.*`, `SQ_MISC.SPLIT_LOCK`, and `LOCK_CYCLES.CACHE_LOCK_DURATION`. Offcore response entries use `MSRIndex` `0x1a6,0x1a7` and `MSRValue` masks, which `jevents.py` maps to `offcore_rsp=...`.

## Control flow and integration

The perf build treats `cache.json` as a topic file named `cache`; `get_topic()` turns the filename into the topic string that is stored on generated events. `read_json_events()` loads all entries, and `add_events_table_entries()` appends only records with `EventName` to the BroadwellX event table. At runtime these aliases are resolved by PMU name `default_core` unless a `Unit` field overrides it. Metrics in `bdx-metrics.json` rely heavily on this file for L1/L2/LLC MPKI, pending-miss cycles, offcore outstanding cycles, local/remote cache access, store latency, lock latency, and memory bandwidth decomposition.

## State and persistence behavior

The file has no mutable state. Its persistent output is a generated compact PMU event table in `pmu-events.c`. Runtime effects occur when perf programs the BroadwellX general-purpose counters and, for offcore events, the offcore response MSRs. `Counter` fields restrict scheduling to compatible hardware counters; `CounterMask`, `AnyThread`, and `PEBS` affect how the kernel configures the sampled event.

## Dependencies

Dependencies include Intel BroadwellX PMU semantics, perf's JSON schema, `jevents.py` MSR mapping for offcore response registers, and kernel support for the underlying core PMU events. Higher-level dependencies include `bdx-metrics.json`, which assumes these exact names, and `metricgroups.json`, which describes groups that include metrics built from these events.

## Risks

Offcore encodings are high risk because an incorrect `MSRValue` can silently count the wrong request/response class. Errata-marked events such as `MEM_LOAD_UOPS_L3_*`, `OFFCORE_REQUESTS_OUTSTANDING.*`, and several PEBS load events should be treated carefully in tests and documentation. Some events are constrained to counter 2 or require precise sampling/address support; ignoring `Counter` or `PEBS` can produce unschedulable groups or unexpected sampling behavior. Because metrics use many of these names verbatim, changing capitalization or suffixes breaks metric expansion even though JSON validation still passes.

## Test signals

Validation should include `jq empty cache.json`, a `jevents.py` generation run, and duplicate-alias checks from `print_pending_events()` assertions. Runtime or fixture tests should confirm `perf list cache` includes representative aliases such as `l1d.replacement`, `l2_rqsts.miss`, and `offcore_response.*`, and that metrics using `MEM_LOAD_UOPS_RETIRED.L3_MISS`, `L1D_PEND_MISS.PENDING`, and offcore response aliases expand without missing event errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellx/cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellx/counter.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellx/counter.json

## Purpose

`counter.json` documents the number of fixed and generic counters available for BroadwellX core and uncore PMU units. It records the counter capacity for `core`, `CBOX`, `HA`, `IRP`, `PCU`, `QPI`, `R2PCIe`, `R3QPI`, `SBOX`, `UBOX`, and `iMC` units.

## Important APIs, types, and schema

Each entry has `Unit`, `CountersNumFixed`, and `CountersNumGeneric`. The core entry declares 3 fixed counters and 4 generic counters. Most uncore units declare 0 fixed counters and 2 to 4 generic counters, with `UBOX` and `iMC` each declaring 1 fixed counter plus generic counters. This schema is metadata, not the normal `EventName`/`MetricName` event schema.

## Control flow and integration

In the current `jevents.py` path, records without `EventName` or `MetricName` instantiate `JsonEvent` objects but are not appended to `_pending_events` or `_pending_metrics`. As a result, this file is still read during preprocessing, but it does not create generated `struct pmu_event` or `struct pmu_metric` rows. Its practical integration value is as machine-readable PMU capacity documentation adjacent to the BroadwellX event lists; external tools or future perf logic could use it to reason about scheduling pressure across core and uncore PMUs.

## State and persistence behavior

The file contains static capability metadata only. It does not persist runtime state and, in the observed generator, has no generated-table side effect beyond successful JSON parsing.

## Dependencies

The file depends on BroadwellX PMU unit naming matching the surrounding uncore event files and perf's convention that `Unit` strings map to PMU names. It is adjacent to generated and hand-authored event JSON that may use unit names like CBOX, HA, PCU, QPI, SBOX, UBOX, and iMC.

## Risks

The main risk is assuming this file affects perf scheduling when the present generator ignores entries without `EventName` or `MetricName`. If downstream automation expects counter capacities from generated perf tables, it will not get them from this path. Another risk is stale capacity metadata: incorrect generic/fixed counts can mislead documentation or external scheduling analysis even though normal perf builds pass.

## Test signals

At minimum, `jq empty counter.json` should pass and a `jevents.py` build should continue to ignore these records without errors. A stronger guard is to assert that adding or editing this file does not change generated event/metric table counts unless generator support for counter-capacity records is intentionally added.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellx/counter.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellx/floating-point.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellx/floating-point.json

## Purpose

`floating-point.json` defines 22 BroadwellX floating-point and vector-assist events. It covers retired scalar, packed, 128-bit, and 256-bit FP arithmetic instructions; x87/SIMD assist conditions; SIMD move elimination; AVX/SSE transition assists; and canceled SIMD physical register file dispatches.

## Important APIs, types, and schema

Entries use the standard event schema: `EventName`, `EventCode`, `UMask`, `Counter`, `CounterMask`, `SampleAfterValue`, `BriefDescription`, `PublicDescription`, and occasional `Errata`. `jevents.py` converts these into generated `pmu_event` aliases with event encoding components such as `event=0xc7,umask=...` and `period=2000003`.

Important families are `FP_ARITH_INST_RETIRED.*` with 12 variants, `FP_ASSIST.*` with 5 variants, `MOVE_ELIMINATION.*`, `OTHER_ASSISTS.AVX_TO_SSE`, `OTHER_ASSISTS.SSE_TO_AVX`, and `UOP_DISPATCHES_CANCELLED.SIMD_PRF`. The arithmetic descriptions document operation multipliers, for example packed 128-bit and 256-bit events representing multiple floating-point operations per retired instruction. Public descriptions repeatedly call out DAZ/FTZ MXCSR requirements for arithmetic counts.

## Control flow and integration

The build assigns these entries to the `floating point` topic and includes them in the BroadwellX core event table. `bdx-metrics.json` consumes these aliases for Top-down FP categories and derived metrics such as `tma_fp_arith`, `tma_fp_scalar`, `tma_fp_vector`, `tma_info_core_flopc`, `tma_info_system_gflops`, and instruction-mix ratios. Because these are core PMU events, the generated PMU defaults to `default_core`.

## State and persistence behavior

The file has no mutable state. Its persistent effect is generated alias data in `pmu-events.c`; runtime state is the programmed counter configuration. `CounterMask` on assist events changes the event encoding and can distinguish cycles or occurrences depending on the Intel event definition. Errata `BDM30` on AVX/SSE transition assists is preserved in descriptions by `jevents.py`.

## Dependencies

Dependencies include BroadwellX FP PMU semantics, perf's event parser, the metric expression parser, and any runtime support for precise ratios that consume these counters. The file is tightly coupled to metric expressions in `bdx-metrics.json`; missing arithmetic aliases make the FP and GFLOPS metrics unusable.

## Risks

The biggest semantic risk is misinterpreting instruction counts as operation counts. Several events count one retired instruction while descriptions explain that each count represents multiple computations; metrics must apply the correct multipliers. DAZ/FTZ requirements can make workload comparisons misleading if floating-point environment state differs. Errata-marked transition assists should not be used as definitive diagnosis without checking the relevant Intel specification update. Event-name changes break Top-down FP metrics.

## Test signals

Useful checks are JSON validation, generated alias presence for `fp_arith_inst_retired.scalar`, `fp_arith_inst_retired.128b_packed_double`, and `other_assists.avx_to_sse`, plus metric expansion for `tma_fp_arith`, `tma_fp_vector_128b`, and `tma_info_system_gflops`. For runtime validation, compare simple scalar/vector FP microbenchmarks against expected relative counter movement rather than exact absolute counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellx/floating-point.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellx/frontend.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellx/frontend.json

## Purpose

`frontend.json` defines 28 BroadwellX frontend PMU events. It covers branch-address clears, DSB-to-MITE switch penalties, instruction-cache hits/misses/stalls, IDQ delivery paths, microcode sequencer delivery, and frontend undersupply cycles.

## Important APIs, types, and schema

Entries use `EventName`, `EventCode`, `UMask`, `Counter`, `CounterMask`, `EdgeDetect`, `Invert`, `SampleAfterValue`, `BriefDescription`, and `PublicDescription`. `jevents.py` converts `CounterMask` to `cmask=`, `EdgeDetect` to `edge=`, `Invert` to `inv=`, and `SampleAfterValue` to `period=` in the generated event string.

Important families include `BACLEARS.ANY`, `DSB2MITE_SWITCHES.PENALTY_CYCLES`, `ICACHE.HIT`, `ICACHE.MISSES`, `ICACHE.IFDATA_STALL`, 17 `IDQ.*` events, and 6 `IDQ_UOPS_NOT_DELIVERED.*` events. Several IDQ events distinguish all cycles with any uops, cycles with four uops, MITE delivery, DSB delivery, LSD delivery, and microcode sequencer delivery.

## Control flow and integration

The build assigns these records to the `frontend` topic and emits them into the BroadwellX core event table. `bdx-metrics.json` uses them in frontend Top-down formulas such as `tma_frontend_bound`, `tma_fetch_latency`, `tma_fetch_bandwidth`, `tma_dsb`, `tma_mite`, `tma_dsb_switches`, `tma_ms_switches`, `tma_icache_misses`, `tma_unknown_branches`, and DSB coverage diagnostics. Runtime perf users can also request these aliases directly to inspect instruction delivery behavior.

## State and persistence behavior

This is static event metadata. Persistent state is the generated alias table; runtime state is the PMU configuration derived from fields such as `cmask`, `edge`, and `inv`. Events with small sample periods, such as branch clears, can produce different sampling overhead characteristics from high-period counting events.

## Dependencies

Dependencies include BroadwellX frontend PMU definitions, the `jevents.py` event-field mapping, and metric expressions in `bdx-metrics.json`. The file also depends on other pipeline and branch events not in this work item for complete Top-down frontend formulas.

## Risks

Frontend events are easy to misread because many count cycles meeting a delivery condition rather than delivered uops. Incorrect `CounterMask`, `Invert`, or `EdgeDetect` values would change cycle classification while still producing syntactically valid JSON. DSB/MITE/LSD metrics combine multiple IDQ events; if any one alias changes, higher-level percentages become invalid. Public descriptions include detailed microarchitectural caveats that should be preserved because short descriptions alone can hide what is actually counted.

## Test signals

Validation should include JSON parsing, generated alias checks for `idq_uops_not_delivered.core`, `idq.all_dsb_cycles_4_uops`, `icache.misses`, and `dsb2mite_switches.penalty_cycles`, and metric expansion for `tma_frontend_bound`, `tma_fetch_latency`, `tma_dsb`, and `tma_mite`. A runtime smoke test can compare instruction-cache stress and tight-loop workloads to ensure frontend miss and DSB-related counters move plausibly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellx/frontend.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellx/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellx/memory.json

## Purpose

`memory.json` defines 58 BroadwellX memory and transactional-memory events. It covers HLE/RTM retired transaction states, transaction abort reasons, transactional memory execution/memory diagnostics, misaligned memory references, memory-ordering machine clears, PEBS load-latency thresholds, and LLC-miss offcore response categories.

## Important APIs, types, and schema

The standard event schema appears with `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, `PublicDescription`, `PEBS`, `Data_LA`, `Errata`, `MSRIndex`, and `MSRValue`. `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_*` entries use `MSRIndex` `0x3F6`, which `jevents.py` maps to `ldlat=...`, with `PEBS` value `2` and `Data_LA` indicating address support when precise. `OFFCORE_RESPONSE.*.LLC_MISS.*` entries use offcore response MSRs `0x1a6,0x1a7` and BroadwellX-specific response masks.

Important families are `HLE_RETIRED.*`, `RTM_RETIRED.*`, `TX_EXEC.*`, `TX_MEM.*`, `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_{4,8,16,32,64,128,256,512}`, `MISALIGN_MEM_REF.*`, `MACHINE_CLEARS.MEMORY_ORDERING`, and many `OFFCORE_RESPONSE.*.LLC_MISS.*` aliases for local DRAM, remote DRAM, remote HITM, remote hit-forward, demand RFO, all reads, all data reads, and code reads.

## Control flow and integration

The build assigns the topic `memory` and emits these as BroadwellX core events. `bdx-metrics.json` consumes the PEBS load-latency and offcore LLC-miss aliases in memory latency, NUMA, remote cache, remote memory, local memory, false-sharing, and store/lock latency formulas. Transactional-memory aliases are also used by generated Intel extra metrics in `intel_metrics.py` when TSX events are present.

## State and persistence behavior

The JSON is static; the generated perf binary stores the aliases. Runtime behavior is more stateful than simple events because PEBS load-latency entries program a latency MSR and require precise sampling support, while offcore events program offcore response MSRs. TSX/HLE events only produce meaningful counts on hardware and kernels where the transactional features are enabled and not disabled by microcode or policy.

## Dependencies

Dependencies include BroadwellX TSX/HLE PMU support, PEBS/Data Linear Address support, offcore response MSR support in `jevents.py`, and adjacent metric definitions. Several events carry errata labels such as `BDM100`, `BDM35`, and `BDE70`, so correct interpretation depends on Intel specification updates.

## Risks

The highest risk is semantic drift in offcore and latency MSR encodings: masks can be syntactically valid but count a different response class. PEBS latency events are constrained to counter 2 and precise sampling; using them in grouped metrics can fail or multiplex poorly if constraints are ignored. TSX events may be unavailable or misleading on systems where TSX is disabled. Errata-marked load-latency and offcore events need guarded interpretation in performance investigations.

## Test signals

Tests should validate JSON syntax, generated aliases for representative `mem_trans_retired.load_latency_gt_64`, `offcore_response.all_data_rd.llc_miss.local_dram`, `rtm_retired.aborted`, and `tx_mem.abort_conflict`, plus metric expansion for memory latency and NUMA metrics. Hardware smoke tests should verify PEBS load-latency events can be scheduled precisely and that offcore miss categories produce nonzero counts under memory-streaming workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellx/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellx/metricgroups.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellx/metricgroups.json

## Purpose

`metricgroups.json` maps 124 metric group names to human-readable group descriptions for BroadwellX. It provides display and discovery text for generic groups such as `Backend`, `Frontend`, `Mem`, `Power`, `TopdownL1`, and for detailed Top-down group identifiers such as `tma_backend_bound_group`, `tma_fetch_latency_group`, and `tma_ports_utilized_3m_group`.

## Important APIs, types, and schema

Unlike event files, this is a single JSON object whose keys are group names and whose values are descriptions. `jevents.py` treats files ending in `metricgroups.json` specially: `preprocess_one_file()` loads the object directly, adds each key and description to the compact metric string table, and stores them in the global `_metricgroups` mapping. These values back the generated `describe_metricgroup()` behavior declared in `pmu-events.h`.

## Control flow and integration

The file is read during the preprocessing phase before generated C output is emitted. It is not processed by `process_one_file()` as an event table and does not create `pmu_event` or `pmu_metric` rows. Instead, it supplements `MetricGroup` values used throughout `bdx-metrics.json`, enabling perf list/reporting paths to describe groups. The keys mirror both legacy group names and generated Top-down group names; this dual coverage allows metrics to be found by broad topics and by hierarchical Top-down categories.

## State and persistence behavior

The file contains static display metadata. Its persistent effect is generated string data and a metric-group description lookup in `pmu-events.c`. There is no runtime mutation.

## Dependencies

The file depends on group names in `bdx-metrics.json` remaining consistent. It also depends on `jevents.py` special-casing the `metricgroups.json` suffix and on perf display code using `describe_metricgroup()`.

## Risks

Missing group keys do not necessarily break metric generation, but they reduce discoverability and can cause blank or generic descriptions in user-facing output. Stale descriptions are a documentation risk: many values are generic, and detailed group names need to match the semantics of their associated metrics. Because the file is an object rather than an array, accidental conversion to event-list format would make `jevents.py` handle it incorrectly.

## Test signals

Validation should include `jq type metricgroups.json` returning `object`, a build that regenerates metric-group descriptions without assertion failures, and a comparison between all semicolon-delimited groups in `bdx-metrics.json` and keys present in this file. Runtime smoke tests should check `perf list` or JSON list output for representative group descriptions such as `TopdownL1`, `tma_memory_bound_group`, and `Power`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellx/metricgroups.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellx/other.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellx/other.json

## Purpose

`other.json` defines 4 BroadwellX core PMU events that do not fit the larger topic files: privilege-level cycle accounting and split/uncacheable lock duration. These events support operating-system overhead and lock-contention investigations.

## Important APIs, types, and schema

Entries use the standard event schema: `EventName`, `EventCode`, `UMask`, `Counter`, `CounterMask`, `EdgeDetect`, `SampleAfterValue`, `BriefDescription`, and `PublicDescription`. The three `CPL_CYCLES.*` events use event code `0x5C` with different umasks and, for `CPL_CYCLES.RING0_TRANS`, edge detection plus `cmask=1`. `LOCK_CYCLES.SPLIT_LOCK_UC_LOCK_DURATION` uses event code `0x63` and tracks cycles where L1/L2 are locked due to uncacheable or split lock behavior.

## Control flow and integration

The build assigns these records to the `other` topic and emits them into the BroadwellX core event table. The kernel/OS metrics in `bdx-metrics.json` use related privilege-cycle events such as kernel CPI/utilization formulas, while lock latency Top-down metrics rely on lock and memory events across this file and `cache.json`.

## State and persistence behavior

This file is static metadata. Its persistent effect is generated alias rows in `pmu-events.c`; runtime behavior is normal PMU counter programming with `edge` and `cmask` applied where present.

## Dependencies

Dependencies include BroadwellX core PMU support for CPL cycle and lock-cycle events, perf's event-field mapping, and higher-level metrics that interpret privileged cycles or lock latency.

## Risks

Privilege-level cycle events can be confused with process/kernel filtering because they count architectural ring state, while perf event modifiers such as `:k` and `:u` filter at a different layer. The split-lock event identifies expensive lock behavior but cannot by itself identify the offending address or instruction. Incorrect edge/cmask encoding on `RING0_TRANS` would change it from transition counting to duration-like counting.

## Test signals

Validation should include JSON parsing, generated aliases for `cpl_cycles.ring0`, `cpl_cycles.ring0_trans`, and `lock_cycles.split_lock_uc_lock_duration`, plus runtime smoke checks under syscall-heavy and lock-heavy workloads. Metric checks should verify OS/kernel utilization formulas that combine privileged-cycle aliases expand successfully.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellx/other.json -->
