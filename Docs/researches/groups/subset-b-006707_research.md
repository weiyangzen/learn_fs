# Research: subset-b-006707 Sandy Bridge PMU event tables

This grouped report covers Sandy Bridge x86 PMU metadata under `sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sandybridge`. The files are declarative JSON consumed by the Linux perf PMU event tooling rather than executable code, so the relevant APIs are the JSON schemas, event and metric names, hardware selector fields, and integration contracts with perf's generated event database.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sandybridge/cache.json -->
## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sandybridge/cache.json

### Purpose
`cache.json` defines 173 Sandy Bridge core PMU events for cache hierarchy behavior: L1D allocation, eviction, replacement, bank conflicts, pending misses, L2 request/fill/writeback traffic, LLC reference/miss events, retired memory uops, offcore requests, offcore outstanding cycles, offcore responses, and split-lock/store-queue conditions. It is the largest file in this group and provides the low-level event names used by `perf stat -e`, `perf record -e`, and higher-level metrics in `snb-metrics.json`.

### Important APIs, Types, And Data Fields
The file is a JSON array of event objects. The effective API is the perf PMU event schema:

- `EventName` is the user-visible perf symbolic event, for example `L1D.REPLACEMENT`, `L2_RQSTS.ALL_DEMAND_DATA_RD`, `LONGEST_LAT_CACHE.MISS`, `MEM_LOAD_UOPS_RETIRED.L1_HIT`, and `OFFCORE_RESPONSE.DEMAND_DATA_RD.LLC_HIT.ANY_RESPONSE`.
- `EventCode` and `UMask` encode the architectural or model-specific event selector.
- `Counter` restricts usable programmable counters. Most events allow `0,1,2,3`; some require counter `2` or use fixed offcore-capable encodings.
- `CounterMask`, `AnyThread`, and `PEBS` add perf event modifiers for thresholded cycle counts, any-thread counting, and precise event sampling.
- `MSRIndex` and `MSRValue` appear on `OFFCORE_RESPONSE.*` events and program Sandy Bridge offcore response MSRs `0x1a6,0x1a7`.
- `BriefDescription` and `PublicDescription` feed perf event help output and generated documentation.
- `SampleAfterValue` supplies default sampling periods for record mode.

There are no local functions or classes. The data is parsed by perf's PMU-events build tools and transformed into generated C tables or runtime JSON event descriptions, depending on the perf version.

### Control Flow And Data Flow
At build time, perf's event tooling reads this array together with sibling Sandy Bridge files. Each object becomes one event record keyed by `EventName`. At runtime, perf resolves a symbolic event to the encoded selector fields, validates counter constraints, and programs the appropriate core PMU register. For offcore response events, perf must also program the offcore filter MSR with `MSRValue`; the same event selector `0xB7, 0xBB` and `UMask 0x1` is reused while the MSR filter distinguishes request/response/snoop classes.

The file also feeds derived metric evaluation indirectly. Metrics such as `tma_dram_bound`, `tma_l3_bound`, `tma_mem_bandwidth`, and `tma_memory_bound` reference events from this file (`MEM_LOAD_UOPS_RETIRED.LLC_HIT`, `MEM_LOAD_UOPS_MISC_RETIRED.LLC_MISS`, `CYCLE_ACTIVITY.*`, `OFFCORE_REQUESTS_OUTSTANDING.*`) and therefore rely on these names staying stable.

### State And Persistence
The file is static source data. It does not persist runtime state. Its persistent state is the set of hardware encodings, descriptions, PEBS flags, sampling periods, and offcore MSR filters committed in the repository. Generated perf artifacts cache these definitions after build, so changes require rebuilding or regenerating perf PMU event tables.

### Dependencies And Integration Points
The file depends on Intel Sandy Bridge PMU semantics: core counters, PEBS support, model-specific offcore response MSRs, and the mapping between event selector bits and cache states. It integrates with:

- perf PMU event parsers and `jevents` style table generation.
- `snb-metrics.json`, whose formulas reference cache and memory events by exact `EventName`.
- `metricgroups.json`, which labels derived metrics that use these events.
- The Linux perf user interface, where event names and descriptions are surfaced.

### Risks
The main risk is silent measurement corruption: incorrect `EventCode`, `UMask`, `Counter`, PEBS, `CounterMask`, `AnyThread`, `MSRIndex`, or `MSRValue` values can still parse but count the wrong hardware condition. Offcore response entries are particularly sensitive because many names share the same visible event selector and differ only by MSR filters. Counter restrictions also matter; events limited to counter `2` or requiring PEBS may fail scheduling or be multiplexed incorrectly if the metadata is wrong. Duplicate or renamed event names would break metrics that reference them.

### Test Signals
Useful validation signals include `jq` parse success, perf PMU schema validation, generated event table diffs, `perf list` showing the expected Sandy Bridge cache/offcore names, and smoke tests that run representative events such as `L1D.REPLACEMENT`, `L2_RQSTS.ALL_DEMAND_DATA_RD`, `MEM_LOAD_UOPS_RETIRED.L1_HIT`, and an `OFFCORE_RESPONSE.*` event on Sandy Bridge-family hardware or an event parser test fixture. Metric validation should check formulas in `snb-metrics.json` that reference cache events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sandybridge/cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sandybridge/counter.json -->
## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sandybridge/counter.json

### Purpose
`counter.json` declares the Sandy Bridge PMU counter inventory. It is a small metadata file that tells perf the `core` PMU has four generic programmable counters and three fixed counters.

### Important APIs, Types, And Data Fields
The file is a JSON array of three objects using the counter metadata schema:

- `Unit: "core"` identifies the PMU unit.
- `CountersNumGeneric: "4"` records the number of programmable core counters.
- `CountersNumFixed: "3"` records the number of fixed counters.

There are no event names, formulas, functions, or classes in this file. Its API is the counter-capability record consumed by the PMU events tooling.

### Control Flow And Data Flow
During PMU table generation, perf reads this file alongside the event tables. The counter counts inform event scheduling and metadata display. Runtime perf can then understand why events in sibling files refer to programmable counters `0,1,2,3` and fixed counters such as `Fixed counter 0`, `Fixed counter 1`, and `Fixed counter 2` in `pipeline.json`.

### State And Persistence
The file persists static hardware capability metadata only. There is no mutable state. Build output may embed these counts in generated perf data tables.

### Dependencies And Integration Points
The values must match Sandy Bridge PMU hardware. The file integrates with all sibling event files by giving context for their `Counter` fields, especially `pipeline.json` fixed-counter events like `INST_RETIRED.ANY`, `CPU_CLK_UNHALTED.THREAD`, and `CPU_CLK_UNHALTED.REF_TSC`.

### Risks
Incorrect generic or fixed counter counts can cause perf to schedule impossible events, reject valid events, or present misleading capability information. Because this file is tiny, formatting or schema errors are also high-impact: a malformed counter table can break PMU table generation for the whole Sandy Bridge event set.

### Test Signals
Validation should parse the JSON, check that the `core` unit has four generic and three fixed counters, verify generated perf metadata, and run `perf list`/event scheduling tests that include both programmable and fixed events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sandybridge/counter.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sandybridge/floating-point.json -->
## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sandybridge/floating-point.json

### Purpose
`floating-point.json` defines 15 Sandy Bridge floating-point and SIMD PMU events. It covers FP assists, SSE scalar and packed operations, x87 work, AVX/SSE transition assists, AVX store assists, and 256-bit SIMD FP operations.

### Important APIs, Types, And Data Fields
The file is an event-object array with standard core PMU fields:

- `EventName` includes `FP_ASSIST.*`, `FP_COMP_OPS_EXE.*`, `OTHER_ASSISTS.AVX_*`, and `SIMD_FP_256.*`.
- `EventCode` and `UMask` encode the event selectors.
- `Counter` is generally `0,1,2,3`.
- `CounterMask` appears on `FP_ASSIST.ANY` to count cycles with any FP assist.
- `BriefDescription` describes the visible perf event.
- `SampleAfterValue` supplies sampling defaults.

No functions or types are implemented locally; the data schema is the interface.

### Control Flow And Data Flow
Perf generation converts each event object into a named PMU event. Runtime users select the events directly or through metrics. `snb-metrics.json` consumes these names in formulas including `tma_fp_scalar`, `tma_fp_vector`, `tma_fp_vector_128b`, `tma_fp_vector_256b`, `tma_x87_use`, `tma_info_core_flopc`, and `tma_info_system_gflops`.

### State And Persistence
This file is static metadata. It persists Sandy Bridge FP event encodings and descriptions. Runtime counter values are produced by hardware and are not stored here.

### Dependencies And Integration Points
The definitions depend on Sandy Bridge's FP/SIMD event model and integrate with perf event parsing, top-down metric evaluation, and HPC-oriented metric groups such as `Compute`, `Flops`, and `HPC`.

### Risks
The main risk is formula drift: if an FP event is renamed or encoded incorrectly, derived FLOP and top-down compute metrics become invalid. The descriptions include legacy terminology around AVX/GSSE and should remain aligned with perf's accepted event names. `CounterMask` handling for `FP_ASSIST.ANY` should be preserved because it changes the meaning from occurrences to cycles.

### Test Signals
Check JSON validity, schema fields, generated `perf list` entries for `FP_COMP_OPS_EXE.SSE_PACKED_DOUBLE` and `SIMD_FP_256.PACKED_SINGLE`, and metric parser tests for formulas that reference FP event names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sandybridge/floating-point.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sandybridge/frontend.json -->
## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sandybridge/frontend.json

### Purpose
`frontend.json` defines 33 Sandy Bridge front-end PMU events. It describes branch resteers, DSB-to-MITE switches, Decode Stream Buffer fill cancellation, instruction cache hits/misses, IDQ delivery by DSB/MITE/MS paths, uops-not-delivered events, and instructions written to the instruction queue.

### Important APIs, Types, And Data Fields
The file uses the core event schema:

- `EventName` covers `BACLEARS.ANY`, `DSB2MITE_SWITCHES.*`, `DSB_FILL.*`, `ICACHE.*`, `IDQ.*`, `IDQ_UOPS_NOT_DELIVERED.*`, and `INSTS_WRITTEN_TO_IQ.INSTS`.
- `EventCode`, `UMask`, and `Counter` provide PMU selectors and scheduling constraints.
- `CounterMask`, `EdgeDetect`, and `Invert` are used by cycle-threshold events such as `IDQ.ALL_DSB_CYCLES_4_UOPS`, edge-detected microcode switch events, and not-delivered cycle variants.
- `BriefDescription` and `PublicDescription` feed event help.
- `SampleAfterValue` supplies sampling defaults.

There are no executable functions. The event objects are the public data interface.

### Control Flow And Data Flow
Perf reads each object and exposes symbolic front-end events. Derived top-down metrics consume these names: `tma_frontend_bound` uses `IDQ_UOPS_NOT_DELIVERED.CORE`, `tma_fetch_latency` uses `IDQ_UOPS_NOT_DELIVERED.CYCLES_0_UOPS_DELIV.CORE`, `tma_dsb_switches` uses `DSB2MITE_SWITCHES.PENALTY_CYCLES`, `tma_ms_switches` uses `IDQ.MS_SWITCHES`, and `tma_info_frontend_dsb_coverage` combines `IDQ.DSB_UOPS`, `LSD.UOPS`, `IDQ.MITE_UOPS`, and `IDQ.MS_UOPS`.

### State And Persistence
The file persists static selector and modifier metadata. Runtime front-end event counts are read from hardware counters and are not persisted by this JSON.

### Dependencies And Integration Points
The definitions depend on Sandy Bridge front-end pipeline concepts: DSB, MITE, IDQ, microcode sequencer, BPU resteers, and instruction cache. Integration points include perf event generation, `snb-metrics.json` top-down formulas, and `metricgroups.json` groups such as `Frontend`, `FetchBW`, `FetchLat`, `DSB`, `DSBmiss`, and `Fed`.

### Risks
Cycle events using `CounterMask`, `Invert`, or `EdgeDetect` are easy to misencode. A wrong modifier can invert the metric meaning while still producing plausible numbers. Formula references are name-sensitive, so renames must be coordinated with `snb-metrics.json`. Descriptions should continue distinguishing DSB, MITE, IDQ, and MS paths because users rely on perf help text to interpret front-end bottlenecks.

### Test Signals
Validate JSON syntax and schema, inspect generated perf entries for modifiers on `IDQ_UOPS_NOT_DELIVERED.*` and `IDQ.MS_SWITCHES`, run metric parser tests for `tma_frontend_bound`, `tma_fetch_latency`, `tma_dsb_switches`, and `tma_ms_switches`, and smoke-test `perf list` output for the front-end group.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sandybridge/frontend.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sandybridge/memory.json -->
## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sandybridge/memory.json

### Purpose
`memory.json` defines 37 Sandy Bridge memory latency, memory ordering, misalignment, offcore DRAM response, and page-walk events. It complements `cache.json` by focusing on load latency thresholds and LLC-miss-to-DRAM response classes.

### Important APIs, Types, And Data Fields
The file is a JSON array of PMU event objects:

- `EventName` includes `MACHINE_CLEARS.MEMORY_ORDERING`, `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_*`, `MEM_TRANS_RETIRED.PRECISE_STORE`, `MISALIGN_MEM_REF.*`, `OFFCORE_RESPONSE.*.LLC_MISS.*`, and `PAGE_WALKS.LLC_MISS`.
- `EventCode`, `UMask`, and `Counter` define core event selectors and counter constraints.
- `PEBS` marks precise memory events, including load latency thresholds and precise store sampling.
- `MSRIndex` and `MSRValue` program offcore response MSRs for DRAM/local-DRAM/LLC-hit response filters.
- `BriefDescription`, `PublicDescription`, and `SampleAfterValue` provide user-facing and sampling metadata.

No functions/classes are implemented; perf consumes this as declarative event metadata.

### Control Flow And Data Flow
During generation, perf turns each object into a named event. For `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_*`, the event uses PEBS and MSR latency threshold programming such as `MSRIndex 0x3F6` with threshold-specific `MSRValue` values. For `OFFCORE_RESPONSE.*` entries, perf programs the offcore response filter MSRs just as it does for cache offcore hit events. Metrics such as `tma_dram_bound`, `tma_mem_latency`, and bandwidth-oriented top-down views depend on this memory/offcore event family.

### State And Persistence
The file persists static event encodings and filter constants. It has no mutable state. Generated perf tables embed the metadata until regeneration.

### Dependencies And Integration Points
The file depends on Sandy Bridge PEBS memory latency facilities, offcore response filter MSRs, and memory-ordering machine-clear semantics. It integrates with `cache.json` offcore events, `virtual-memory.json` TLB/page-walk data, `snb-metrics.json` memory-bound formulas, and perf's precise sampling support.

### Risks
The highest-risk entries are PEBS latency threshold events and offcore response filters. Wrong `MSRValue` thresholds can shift latency buckets, and wrong offcore filters can classify traffic as DRAM/local DRAM/LLC hit incorrectly. Because many offcore entries share event code/umask, review must compare `MSRValue` rather than only visible event selector fields.

### Test Signals
Use JSON/schema validation, generated event table comparison, `perf list` checks for `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_64` and `OFFCORE_RESPONSE.DEMAND_DATA_RD.LLC_MISS.DRAM`, metric parser tests for memory-bound formulas, and hardware smoke tests for PEBS load-latency sampling where Sandy Bridge support is available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sandybridge/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sandybridge/metricgroups.json -->
## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sandybridge/metricgroups.json

### Purpose
`metricgroups.json` maps 117 metric group names to descriptions for Sandy Bridge. It supplies human-readable grouping metadata for top-down microarchitecture analysis, HPC summaries, memory, branch, power, OS, SMT, SoC, and issue-category metrics.

### Important APIs, Types, And Data Fields
Unlike the event files, this file is a JSON object, not an array. Each property name is a metric group key and each value is a description string. Key families include:

- Broad categories such as `Backend`, `Frontend`, `BadSpec`, `Retire`, `MemoryBound`, `MemoryBW`, `MemoryLat`, `Pipeline`, `Power`, `Summary`, `SMT`, `SoC`, and `HPC`.
- Top-down levels `TopdownL1` through `TopdownL6` and aliases such as `tma_L1_group` through `tma_L6_group`.
- Drill-down groups such as `tma_backend_bound_group`, `tma_fetch_latency_group`, `tma_fp_arith_group`, `tma_memory_bound_group`, and `tma_ports_utilization_group`.
- Issue tags such as `tma_issueBW`, `tma_issueFB`, `tma_issueMC`, `tma_issueMS`, `tma_issueTLB`, and related issue labels.

There are no event selectors, functions, or formulas. The API is the group-name-to-description map used by perf's metric display.

### Control Flow And Data Flow
Perf associates `MetricGroup` strings from `snb-metrics.json` with descriptions in this map. When users request metric groups or browse metric lists, perf can display group names and descriptions. Group names in `snb-metrics.json` are semicolon-separated; every group key here must remain compatible with those references.

### State And Persistence
This is static taxonomy metadata. It persists group descriptions but no runtime state or generated counters.

### Dependencies And Integration Points
The file depends on group names used in `snb-metrics.json`. It also reflects Intel's top-down microarchitecture analysis taxonomy. Integration points include perf metric listing, metric group filtering, documentation generation, and any tests that require group descriptions to exist for referenced groups.

### Risks
Because the schema differs from event arrays, tools that assume `.[].EventName` will fail. A missing or renamed group can degrade `perf list --details` output or make metric grouping less discoverable. Descriptions are generic for many groups, so the practical consistency risk is key coverage rather than prose precision.

### Test Signals
Validate the file as a JSON object, compare its keys against all semicolon-separated `MetricGroup` references in `snb-metrics.json`, and run perf metric-list tests to ensure groups such as `TopdownL1`, `MemoryBound`, `Flops`, and `tma_backend_bound_group` are discoverable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sandybridge/metricgroups.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sandybridge/other.json -->
## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sandybridge/other.json

### Purpose
`other.json` defines five Sandy Bridge events that do not fit cleanly into cache, front-end, pipeline, memory, or virtual-memory categories. They cover privilege-level cycles, ring transitions, hardware prefetch L1D misses, and split-lock/uncacheable-lock duration.

### Important APIs, Types, And Data Fields
The file is a JSON array of event objects:

- `EventName` values are `CPL_CYCLES.RING0`, `CPL_CYCLES.RING0_TRANS`, `CPL_CYCLES.RING123`, `HW_PRE_REQ.DL1_MISS`, and `LOCK_CYCLES.SPLIT_LOCK_UC_LOCK_DURATION`.
- `EventCode`, `UMask`, and `Counter` define selectors and counter availability.
- `CounterMask` and `EdgeDetect` are used by `CPL_CYCLES.RING0_TRANS` to count ring-0 transition-style events.
- `BriefDescription` and `SampleAfterValue` provide user-facing metadata.

There are no functions or persistent runtime objects.

### Control Flow And Data Flow
Perf exposes these entries as standalone events. The OS-oriented privilege cycle events can support kernel/user utilization investigations, while split-lock and prefetch miss events can support memory-system diagnostics. Some related OS metrics in `snb-metrics.json` use pipeline clock events rather than directly referencing these names, but these events remain available for manual perf sessions.

### State And Persistence
The file persists static event selector metadata. It does not store runtime counts.

### Dependencies And Integration Points
The definitions depend on Sandy Bridge PMU semantics for current privilege level, hardware prefetch requests, and lock cycles. Integration is primarily with perf event listing and manual event selection.

### Risks
The small event count makes omissions visible, but modifier mistakes on `CPL_CYCLES.RING0_TRANS` can alter semantics significantly. `LOCK_CYCLES.SPLIT_LOCK_UC_LOCK_DURATION` overlaps conceptually with `SQ_MISC.SPLIT_LOCK` in `cache.json`, so descriptions should stay clear about duration versus occurrence-style counting.

### Test Signals
Validate JSON, ensure all five names appear in generated perf output, and check encoded modifiers for `CPL_CYCLES.RING0_TRANS`. Manual smoke tests can use `perf stat -e CPL_CYCLES.RING0` on compatible hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sandybridge/other.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sandybridge/pipeline.json -->
## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sandybridge/pipeline.json

### Purpose
`pipeline.json` defines 128 Sandy Bridge core pipeline events. It covers branch execution and retirement, branch misprediction, clock and fixed counter events, cycle activity, instruction retirement, RAT/recovery stalls, load blocking, LSD, machine clears, resource stalls, reservation station state, dispatched/executed/issued/retired uops, and per-port dispatch.

### Important APIs, Types, And Data Fields
The file is a JSON event array using:

- `EventName` for user-facing names such as `BR_INST_EXEC.ALL_BRANCHES`, `BR_MISP_RETIRED.ALL_BRANCHES`, `CPU_CLK_UNHALTED.THREAD`, `INST_RETIRED.ANY`, `UOPS_RETIRED.RETIRE_SLOTS`, and `UOPS_DISPATCHED_PORT.PORT_0`.
- `EventCode`/`UMask` for programmable selectors, plus fixed-counter `Counter` values for fixed events (`Fixed counter 0`, `Fixed counter 1`, `Fixed counter 2`).
- `Counter`, `CounterMask`, `AnyThread`, `EdgeDetect`, `Invert`, and `PEBS` modifiers for scheduling, threshold cycles, any-thread counting, edge detection, inverted masks, and precise sampling.
- `BriefDescription`, `PublicDescription`, and `SampleAfterValue` for help and sampling defaults.

No functions/classes exist; the PMU event schema is the integration interface.

### Control Flow And Data Flow
Perf's generator reads this file and creates event records. Runtime perf resolves names to either programmable events or fixed counters. `snb-metrics.json` is heavily dependent on these names: top-down slots use `UOPS_RETIRED.RETIRE_SLOTS`, `UOPS_ISSUED.ANY`, and `CPU_CLK_UNHALTED.THREAD`; branch and bad-speculation metrics use `BR_MISP_RETIRED.*`, `BR_INST_RETIRED.*`, and `MACHINE_CLEARS.COUNT`; backend and port metrics use `UOPS_DISPATCHED.*`, `RESOURCE_STALLS.*`, `RS_EVENTS.EMPTY_CYCLES`, and `CYCLE_ACTIVITY.*`.

### State And Persistence
The file persists static PMU metadata and default sampling periods. Runtime counts are hardware state, not stored here. Build-generated perf tables persist a compiled copy of this data.

### Dependencies And Integration Points
The file depends on Sandy Bridge core PMU and fixed counter behavior. It integrates with `counter.json` for counter inventory, `snb-metrics.json` for most top-down formulas, `frontend.json` for fetch-latency formulas, `floating-point.json` for compute formulas, and `metricgroups.json` for metric taxonomy.

### Risks
This is one of the highest-blast-radius files because many metrics depend on exact event names and semantics. Fixed-counter metadata must be correct for basic IPC/CPI calculations. Any-thread variants, PEBS flags, and counter masks must be preserved. Several cycle-style events share selectors but differ by `CounterMask`, `Invert`, or `EdgeDetect`, so review should inspect modifiers, not just event code and umask.

### Test Signals
Validation should include JSON parsing, generated perf table diffing, `perf list` checks for fixed and programmable events, metric parser tests for top-down level 1 and 2 metrics, and smoke tests using `INST_RETIRED.ANY`, `CPU_CLK_UNHALTED.THREAD`, `UOPS_RETIRED.RETIRE_SLOTS`, and branch misprediction events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sandybridge/pipeline.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sandybridge/snb-metrics.json -->
## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sandybridge/snb-metrics.json

### Purpose
`snb-metrics.json` defines 69 Sandy Bridge derived metrics. It provides top-down microarchitecture analysis metrics, system summary metrics, power/C-state residency, SMT/core frequency helpers, floating-point throughput, memory bandwidth, SMI accounting, OS/kernel utilization, and metric thresholds.

### Important APIs, Types, And Data Fields
The file is a JSON array of metric objects:

- `MetricName` is the perf metric identifier, for example `tma_frontend_bound`, `tma_bad_speculation`, `tma_backend_bound`, `tma_retiring`, `tma_memory_bound`, `tma_fp_vector`, `tma_info_thread_ipc`, `tma_info_system_dram_bw_use`, `smi_cycles`, and C-state residency metrics.
- `MetricExpr` is the expression language consumed by perf. It references event names, other metrics, constants, runtime variables such as `#SMT_on`, `#core_wide`, `#num_cpus_online`, `#num_dies`, and special events like `duration_time`, `msr@tsc@`, `msr@aperf@`, and `cstate_*`.
- `MetricGroup` is a semicolon-separated taxonomy consumed with `metricgroups.json`.
- `MetricThreshold` encodes alert/display thresholds for many top-down metrics.
- `ScaleUnit` formats output, often `100%`, `1SMI#`, or blank for ratios.
- `MetricConstraint` and `MetricgroupNoGroup` constrain grouping for events that cannot be scheduled together or should not be auto-grouped in some modes.
- `BriefDescription` and `PublicDescription` provide user-facing metric explanations.

No local functions/classes exist, but metric expressions are executable by perf's metric evaluator.

### Control Flow And Data Flow
Perf loads event definitions from sibling files, then evaluates `MetricExpr` formulas by collecting referenced events and recursively resolving metric references. Top-down level 1 is built from `tma_frontend_bound`, `tma_bad_speculation`, `tma_retiring`, and derived `tma_backend_bound`. Lower-level metrics derive branch mispredicts, machine clears, fetch latency/bandwidth, core/memory bound, DRAM bound, L3 bound, store bound, port utilization, FP arithmetic mix, and microcode sequencing. System metrics use uncore events from `uncore-interconnect.json`, C-state pseudo-events, MSR pseudo-events, and duration/time pseudo-events.

### State And Persistence
The file persists formulas, thresholds, group membership, and display units. It stores no runtime measurements. Perf may compile or cache these expressions in generated event tables.

### Dependencies And Integration Points
This file depends on exact event names from `pipeline.json`, `frontend.json`, `cache.json`, `memory.json`, `floating-point.json`, `virtual-memory.json`, and `uncore-interconnect.json`. It depends on group keys in `metricgroups.json` and perf's expression evaluator features: conditional expressions, `min`, escaped raw event syntax such as `cpu@UOPS_DISPATCHED.CORE\\,cmask\\=1@`, MSR pseudo-events, C-state pseudo-events, and runtime topology variables.

### Risks
Metrics can fail or mislead if any referenced event is renamed, removed, or semantically changed. Expressions include scheduling-sensitive constraints and SMT/core-wide conditionals; mistakes can produce plausible but wrong top-down percentages. Escaping in raw event syntax is fragile because commas and backslashes must survive JSON parsing and perf expression parsing. Group and threshold metadata also affect how users discover and interpret bottlenecks.

### Test Signals
Run JSON validation, perf metric expression parser tests, reference checks ensuring every event and metric name resolves, group-key checks against `metricgroups.json`, and `perf stat -M` smoke tests for top-down groups on compatible systems. Important formulas to validate include `tma_info_thread_slots`, `tma_frontend_bound`, `tma_bad_speculation`, `tma_memory_bound`, `tma_dram_bound`, `tma_info_system_dram_bw_use`, and FP FLOP metrics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sandybridge/snb-metrics.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sandybridge/uncore-cache.json -->
## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sandybridge/uncore-cache.json

### Purpose
`uncore-cache.json` defines 25 Sandy Bridge uncore CBOX cache events. It covers LLC/CBOX lookup outcomes by request type and MESI state plus cross-snoop response categories for eviction, external snoop, and cross-core snoop traffic.

### Important APIs, Types, And Data Fields
The file uses the uncore event schema:

- `EventName` includes `UNC_CBO_CACHE_LOOKUP.*` and `UNC_CBO_XSNP_RESPONSE.*`.
- `Unit: "CBOX"` identifies the uncore PMU block.
- `EventCode` and `UMask` encode CBOX selectors.
- `Counter` generally allows `0,1`.
- `PerPkg: "1"` marks package-level uncore scope.
- `BriefDescription` provides user-facing help.

There are no functions or classes.

### Control Flow And Data Flow
Perf's uncore event handling maps these symbolic names to CBOX PMU events. Runtime counting occurs per package/CBOX rather than per core thread. Users can select lookup events such as read/write/any lookups in `I`, `M`, `E/S`, or `MESI` states, or snoop response events such as `HITM_XCORE` and `MISS_EXTERNAL`.

### State And Persistence
The file persists static uncore event metadata. Runtime uncore counter values are not stored here.

### Dependencies And Integration Points
Definitions depend on Sandy Bridge uncore CBOX PMU semantics and package-scoped perf uncore support. They integrate with perf list/stat uncore handling and with any metrics or user workflows that inspect LLC coherence behavior. This file is adjacent to, but distinct from, core cache events in `cache.json`.

### Risks
Uncore PMUs have different unit names, scopes, and counter constraints than core PMUs. Mislabeling `Unit`, `PerPkg`, or counter availability can cause perf to expose events under the wrong PMU or fail scheduling. MESI-state umasks are compact and easy to transpose, which would corrupt LLC/coherence diagnostics.

### Test Signals
Validate JSON, ensure `perf list` exposes CBOX events, check generated unit names and package scope, and smoke-test a representative lookup and snoop response event on supported Sandy Bridge uncore hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sandybridge/uncore-cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sandybridge/uncore-interconnect.json -->
## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sandybridge/uncore-interconnect.json

### Purpose
`uncore-interconnect.json` defines nine Sandy Bridge uncore ARB/interconnect events. It covers coherency tracker occupancy and requests, memory-data-return tracker occupancy and requests, write and eviction allocations, and the socket uncore clock fixed counter.

### Important APIs, Types, And Data Fields
The file is an uncore event array:

- `EventName` includes `UNC_ARB_COH_TRK_OCCUPANCY.ALL`, `UNC_ARB_COH_TRK_REQUESTS.ALL`, `UNC_ARB_TRK_OCCUPANCY.*`, `UNC_ARB_TRK_REQUESTS.*`, and `UNC_CLOCK.SOCKET`.
- `Unit: "ARB"` identifies the uncore arbiter/interconnect PMU.
- `EventCode`, `UMask`, and `Counter` encode selectors and counter constraints.
- `CounterMask` appears on occupancy cycle threshold variants.
- `PerPkg: "1"` marks package-level scope.
- `BriefDescription` describes the interconnect condition.

There are no local functions/classes.

### Control Flow And Data Flow
Perf exposes these as ARB uncore events. Runtime data is collected at package scope. `snb-metrics.json` references `UNC_ARB_TRK_REQUESTS.ALL`, `UNC_ARB_COH_TRK_REQUESTS.ALL`, and `UNC_CLOCK.SOCKET` in system-level metrics such as `tma_info_system_dram_bw_use`, `tma_info_system_socket_clks`, and `UNCORE_FREQ`.

### State And Persistence
The file persists static ARB PMU metadata only. Generated perf tables may embed it; runtime counter values are external hardware state.

### Dependencies And Integration Points
The definitions depend on Sandy Bridge uncore ARB PMU support and integrate directly with system-level metrics in `snb-metrics.json`, especially DRAM bandwidth and uncore frequency calculations. They also integrate with perf's uncore PMU discovery and package-scoped event scheduling.

### Risks
Metric formulas rely on exact event names, so renames or unit changes can break system metrics. Incorrect `CounterMask` values on occupancy threshold events would change cycle filtering. `UNC_CLOCK.SOCKET` is a fixed/socket clock signal; incorrect metadata would skew uncore frequency and time-normalized bandwidth metrics.

### Test Signals
Validate JSON and generated event tables, check reference resolution from `snb-metrics.json`, verify `perf list` exposes ARB events, and smoke-test `UNC_CLOCK.SOCKET` plus tracker request events on supported hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sandybridge/uncore-interconnect.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sandybridge/virtual-memory.json -->
## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sandybridge/virtual-memory.json

### Purpose
`virtual-memory.json` defines 16 Sandy Bridge virtual memory and TLB events. It covers DTLB load/store misses, STLB hits, page-walk completion and duration, EPT walk cycles, ITLB flush and miss behavior, and DTLB/STLB flush events.

### Important APIs, Types, And Data Fields
The file uses the standard event schema:

- `EventName` includes `DTLB_LOAD_MISSES.*`, `DTLB_STORE_MISSES.*`, `EPT.WALK_CYCLES`, `ITLB.ITLB_FLUSH`, `ITLB_MISSES.*`, and `TLB_FLUSH.*`.
- `EventCode`, `UMask`, and `Counter` define selector encoding and counter availability.
- `BriefDescription` and, for some entries, `PublicDescription` provide help text.
- `SampleAfterValue` provides sampling defaults.

There are no functions/classes; the JSON event records are consumed by perf.

### Control Flow And Data Flow
Perf generates named TLB/virtual-memory events from the array. Runtime users can count or sample TLB miss and page-walk behavior. `snb-metrics.json` references this file through metrics such as `tma_dtlb_load` and `tma_itlb_misses`, which combine STLB hit and walk-duration events with top-down fetch/memory bottleneck categories.

### State And Persistence
This file persists static PMU event metadata. Runtime TLB state and counter values are not stored here.

### Dependencies And Integration Points
The definitions depend on Sandy Bridge DTLB, STLB, ITLB, EPT, and page-walk PMU semantics. Integration points include perf event listing, top-down memory TLB and fetch-latency metrics, and group taxonomy keys such as `MemoryTLB`, `BigFootprint`, and `tma_issueTLB`.

### Risks
TLB metrics are sensitive to event-name stability and walk-duration semantics. If `DTLB_LOAD_MISSES.STLB_HIT`, `DTLB_LOAD_MISSES.WALK_DURATION`, `ITLB_MISSES.STLB_HIT`, or `ITLB_MISSES.WALK_DURATION` are renamed or misencoded, top-down TLB metrics can fail or misclassify bottlenecks. EPT-related events may be workload/hypervisor dependent, so tests should not assume nonzero counts.

### Test Signals
Validate JSON, ensure generated perf output includes DTLB/ITLB/STLB names, run metric expression tests for `tma_dtlb_load` and `tma_itlb_misses`, and use hardware smoke tests with TLB-stressing workloads where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sandybridge/virtual-memory.json -->
