# subset-b-006689 grouped research

This grouped report covers the exact source files assigned to `subset-b-006689`. Each file section is delimited for reconciliation into the corresponding source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/ivybridge/pipeline.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/ivybridge/pipeline.json

Purpose: Defines 126 Ivy Bridge core PMU event aliases for pipeline, branch, execution, retirement, stall, and cycle accounting. This is data consumed by perf's PMU event table generator/resolver, not executable code, so the effective API is the JSON event schema and the stable `EventName` strings exposed to `perf stat`, `perf record`, and metric expressions.

Important APIs/types/functions: Entries use `EventName`, `EventCode`, `UMask`, `Counter`, `CounterMask`, `EdgeDetect`, `Invert`, `AnyThread`, `PEBS`, `SampleAfterValue`, `BriefDescription`, and `PublicDescription`. Major families include `BR_INST_EXEC`, `BR_INST_RETIRED`, `BR_MISP_EXEC`, `BR_MISP_RETIRED`, `CPU_CLK_UNHALTED`, `CYCLE_ACTIVITY`, `INST_RETIRED`, `INT_MISC`, `RESOURCE_STALLS`, `UOPS_DISPATCHED_PORT`, `UOPS_EXECUTED`, `UOPS_ISSUED`, and `UOPS_RETIRED`. Several fixed-counter aliases map retired instructions and unhalted cycles through pseudo `UMask` values such as fixed counters 0, 1, and 2.

Control flow: At build time the perf PMU tooling parses this array into architecture-specific event tables. At runtime CPU identification selects the Ivy Bridge table, user-supplied aliases are matched by `EventName`, and perf translates the JSON fields into perf event attributes such as event select, unit mask, counter mask, edge detection, PEBS eligibility, any-thread mode, and sampling period. Higher-level metrics can then reference these aliases by name.

State and persistence: The file is static source data. It persists event encodings in the repository and produces generated perf tables during build, but it has no runtime mutable state of its own. Runtime counts live in kernel/hardware PMU state and perf result buffers.

Dependencies/integration: Depends on Intel Ivy Bridge PMU semantics and perf's `pmu-events` JSON parser. It integrates with neighboring Ivy Bridge files for cache, memory, frontend, and uncore coverage, and with metric files that reference aliases such as `INST_RETIRED.ANY`, `UOPS_RETIRED.RETIRE_SLOTS`, `CYCLE_ACTIVITY.*`, and branch events.

Risks: Event accuracy depends on field correctness and Intel errata. Aliases with identical event select/unit mask but different `CounterMask`, `EdgeDetect`, or descriptions can be easy to confuse. Fixed-counter aliases and programmable-counter aliases for similar concepts must remain distinct. Counter constraints such as `Counter: 2` for some cycle-activity events can cause multiplexing or scheduling failures if changed. Description typos do not break parsing but can mislead performance diagnosis.

Test signals: Validate with `jq` schema checks, perf's pmu event table tests, alias lookup tests for representative branch/uop/stall events, and on-hardware smoke tests such as `perf stat -e INST_RETIRED.ANY,CPU_CLK_UNHALTED.THREAD,UOPS_RETIRED.RETIRE_SLOTS`. Metric tests should confirm Ivy Town/Ivy Bridge topdown expressions resolve every referenced core alias.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/ivybridge/pipeline.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/ivybridge/uncore-cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/ivybridge/uncore-cache.json

Purpose: Defines 25 Ivy Bridge uncore C-box cache/coherency aliases for LLC lookup state and cross-snoop response accounting. These names let perf users request package-level CBOX events without spelling raw uncore event encodings.

Important APIs/types/functions: Every entry is a PMU event object using `EventName`, `EventCode`, `UMask`, `Unit`, `Counter`, `PerPkg`, and `BriefDescription`. The file has two families: `UNC_CBO_CACHE_LOOKUP` with 16 variants covering request classes (`ANY`, `EXTSNP`, `READ`, `WRITE`) crossed with MESI hit states, and `UNC_CBO_XSNP_RESPONSE` with 9 variants covering snoop sources (`EVICTION`, `EXTERNAL`, `XCORE`) and responses (`MISS`, `HIT`, `HITM`). `Unit: CBOX` directs perf to uncore C-box PMUs, and `PerPkg: 1` marks package-level aggregation.

Control flow: Perf's generated event table maps these aliases into uncore PMU configurations. Runtime lookup selects Ivy Bridge by CPU model, resolves an alias such as `UNC_CBO_CACHE_LOOKUP.READ_MESI`, chooses the CBOX unit, applies event select and unit mask, and schedules the event on available CBOX counters. Counts are package/unit scoped rather than per-thread core PMU counts.

State and persistence: Static JSON preserves Intel uncore event encodings. There is no mutable state in the file. Hardware CBOX counters hold runtime state, and perf records or aggregates the resulting counts.

Dependencies/integration: Depends on the kernel exposing Ivy Bridge CBOX uncore PMUs with names understood by perf. Integrates with uncore interconnect events and with derived memory/coherency analysis outside this file. Its event names are not regular core aliases; consumers must respect the `Unit` and `PerPkg` fields.

Risks: Uncore topology varies by socket and SKU, so event availability and aggregation can differ across systems. `PerPkg` counts can be misread as per-core if UI layers drop unit context. MESI and snoop-response masks are dense; transposed `UMask` values would silently count a different cache state. Counter availability is limited to CBOX counters `0,1`, so broad event groups may multiplex.

Test signals: Run JSON validation, perf alias lookup for at least one lookup and one xsnp response event, and on-Ivy-Bridge hardware `perf stat -e uncore_cbox_*/event=.../` equivalence checks where possible. Tests should verify `Unit` remains `CBOX`, `PerPkg` remains set, and generated tables keep package scoping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/ivybridge/uncore-cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/ivybridge/uncore-interconnect.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/ivybridge/uncore-interconnect.json

Purpose: Defines 9 Ivy Bridge uncore ARB/interconnect aliases for tracker occupancy, tracker request allocation, and socket uncore clock counting. The file gives perf users named access to package interconnect pressure signals.

Important APIs/types/functions: Entries use the perf PMU event schema: `EventName`, `EventCode`, `UMask`, `Unit`, `Counter`, `CounterMask`, `PerPkg`, and `BriefDescription`. Families are `UNC_ARB_COH_TRK_OCCUPANCY`, `UNC_ARB_COH_TRK_REQUESTS`, `UNC_ARB_TRK_OCCUPANCY`, `UNC_ARB_TRK_REQUESTS`, and `UNC_CLOCK.SOCKET`. Occupancy aliases use `CounterMask` to distinguish all occupancy cycles, cycles with any request, and cycles over half full. `UNC_CLOCK.SOCKET` uses the ARB fixed counter.

Control flow: Build-time perf tooling includes these records in the Ivy Bridge PMU event table. Runtime alias resolution maps names to the ARB uncore PMU, applies event select/unit mask/counter mask, and schedules on ARB counters. Users can combine request counts and occupancy cycles to infer average outstanding interconnect or coherency pressure.

State and persistence: Static repository data only. It persists event encodings and descriptions; runtime state lives in ARB uncore counters and perf's measurement buffers.

Dependencies/integration: Depends on Intel Ivy Bridge ARB uncore event semantics and the kernel's uncore PMU driver exposing ARB counters. It complements `uncore-cache.json` CBOX events and memory-controller events in other Ivy Bridge files. Derived metrics may use `UNC_CLOCK.SOCKET` as an uncore time base.

Risks: Occupancy events are cycle-weighted and can be misinterpreted as simple request counts. `CounterMask` thresholds are semantically important; removing or changing them changes the meaning while leaving the event code stable. Fixed-counter `UNC_CLOCK.SOCKET` has a different scheduling model from programmable ARB events. As package-scoped events, counts may not compose cleanly with per-thread core counters in the same perf report.

Test signals: Validate JSON fields and generated table rows, including `Unit: ARB`, `PerPkg: 1`, and `CounterMask` on thresholded events. On hardware, compare `UNC_ARB_TRK_REQUESTS.ALL` and occupancy aliases under memory-load stress versus idle, and verify `UNC_CLOCK.SOCKET` increments as a package clock source.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/ivybridge/uncore-interconnect.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/ivybridge/virtual-memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/ivybridge/virtual-memory.json

Purpose: Defines 18 Ivy Bridge core PMU aliases for instruction/data TLB misses, page walks, TLB flushes, and EPT walk cycles. The file supports virtual-memory and address-translation analysis in perf.

Important APIs/types/functions: Entries expose `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, and occasional `PublicDescription`. Families include `DTLB_LOAD_MISSES`, `DTLB_STORE_MISSES`, `ITLB_MISSES`, `ITLB`, `TLB_FLUSH`, and `EPT`. The aliases distinguish first-level TLB misses that hit the second-level TLB, misses that cause page walks, completed walks, large-page walks, walk duration cycles, and thread/STLB flush events.

Control flow: Perf parses this JSON into the Ivy Bridge event table. At runtime, a requested alias such as `DTLB_LOAD_MISSES.WALK_DURATION` is resolved to event select/unit mask and scheduled on a core programmable counter. Sampling aliases use `SampleAfterValue` as a default period. Higher-level metrics can divide walk duration or walk counts by clocks or instructions.

State and persistence: Static PMU metadata only. The file has no mutable state; hardware PMU counters represent runtime translation behavior.

Dependencies/integration: Depends on Ivy Bridge core PMU definitions and perf's JSON parser. It integrates with topdown memory-TLB metrics in Ivy Town metric data, where expressions reference events like `DTLB_LOAD_MISSES.WALK_DURATION`, `DTLB_STORE_MISSES.WALK_DURATION`, and `ITLB_MISSES.WALK_DURATION`.

Risks: Similar names differ sharply between count and duration events. Some descriptions say STLB load misses for ITLB paths, so documentation wording should be checked before relying on it for user-facing education. Page-walk duration events are cycle-like and should not be summed with completed-walk counts without normalization. EPT events are virtualization-specific and may read as zero outside VM workloads.

Test signals: Schema checks should enforce valid event fields and unique names. Runtime smoke tests should request representative load, store, instruction, and flush aliases. Metric tests should ensure all TLB aliases referenced by Ivy Bridge/Ivy Town topdown formulas are present and resolvable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/ivybridge/virtual-memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/ivytown/cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/ivytown/cache.json

Purpose: Defines 118 Ivy Town core PMU aliases for data cache, L2, LLC, load-source, offcore request/response, split-lock, and memory-ordering-adjacent cache behavior. This is a central dependency for Ivy Town topdown and memory metrics.

Important APIs/types/functions: Entries use `EventName`, `EventCode`, `UMask`, `Counter`, `CounterMask`, `AnyThread`, `PEBS`, `MSRIndex`, `MSRValue`, `SampleAfterValue`, `BriefDescription`, and `PublicDescription`. Families include `L1D`, `L1D_PEND_MISS`, `L2_RQSTS`, `L2_TRANS`, `L2_LINES_IN`, `L2_LINES_OUT`, `LONGEST_LAT_CACHE`, `MEM_LOAD_UOPS_RETIRED`, `MEM_LOAD_UOPS_LLC_HIT_RETIRED`, `MEM_LOAD_UOPS_LLC_MISS_RETIRED`, `MEM_UOPS_RETIRED`, `OFFCORE_REQUESTS`, `OFFCORE_REQUESTS_OUTSTANDING`, `OFFCORE_REQUESTS_BUFFER`, `OFFCORE_RESPONSE`, and `SQ_MISC`.

Control flow: Perf's build tooling converts this JSON array into Ivy Town event aliases. Runtime alias lookup translates names into core PMU encodings. Offcore-response aliases are special: they share event select values such as `0xB7, 0xBB` and require offcore MSR filter programming through `MSRIndex`/`MSRValue` or equivalent generated metadata. PEBS-tagged load events can be used for precise sampling and data-source analysis.

State and persistence: Static metadata persists event names and raw encodings. Runtime state is in core PMU counters, offcore response MSRs, and PEBS records. There is no file-local mutable state.

Dependencies/integration: Depends on Ivy Town PMU/offcore response definitions and perf support for MSR filters. `ivt-metrics.json` references many aliases from this file, including `MEM_LOAD_UOPS_RETIRED.*`, LLC hit/miss retired events, `OFFCORE_REQUESTS_OUTSTANDING.*`, `L1D_PEND_MISS.*`, `L2_LINES_IN.ALL`, and `LONGEST_LAT_CACHE.MISS`.

Risks: Offcore-response descriptions and filters are easy to mismatch because many entries share visible event/umask fields while differing in hidden MSR filters. Some aliases require specific counters or PEBS support, affecting scheduling and sampling availability. Long derived metrics divide by combinations of these events, so missing or renamed aliases can break topdown formulas. Similar hit/miss wording should be audited; a few descriptions in this PMU family historically contain copy/paste mistakes.

Test signals: Validate JSON uniqueness and required offcore MSR fields, run perf PMU event tests for ordinary cache and offcore aliases, and verify topdown metric parsing resolves every referenced cache event. Hardware smoke tests should compare L1/L2/LLC miss counters under cache-thrashing workloads and exercise at least one precise load event.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/ivytown/cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/ivytown/counter.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/ivytown/counter.json

Purpose: Declares the Ivy Town PMU counter inventory by PMU unit. This file informs perf tooling how many fixed and generic counters exist for the core and each uncore unit.

Important APIs/types/functions: The JSON array contains 10 unit records with `Unit`, `CountersNumFixed`, and `CountersNumGeneric`. It lists `core` as 3 fixed counters and 4 generic counters, and uncore units `CBOX`, `HA`, `iMC`, `PCU`, and `QPI` as 4 generic counters each. `IRP` and `UBOX` have 2 generic counters, while `R3QPI` has 3. All uncore units list zero fixed counters.

Control flow: Perf PMU event table generation and validation can use this metadata to understand event scheduling capacity and unit capabilities. Runtime event grouping, multiplexing, and error reporting depend on the kernel PMU driver and perf's scheduler, but this file documents the expected Ivy Town hardware shape for generated metadata.

State and persistence: Static architecture metadata only. It has no event names and no runtime state. The persisted state is the counter-count contract for Ivy Town units.

Dependencies/integration: Integrates with all Ivy Town event files by providing the available counter context for `core`, CBOX, HA, iMC, IRP, PCU, QPI, R2PCIe, R3QPI, and UBOX events. It depends on unit names matching `Unit` fields in uncore event JSON files and perf's unit naming conventions.

Risks: If unit names drift from event files or kernel PMU names, generated metadata becomes misleading. Counter counts can vary by SKU or kernel exposure, so this file should be treated as model metadata rather than live discovery. Incorrect counts can cause overly optimistic grouping or missed multiplexing warnings.

Test signals: JSON validation should ensure every record has numeric string counts and unique `Unit` values. Cross-file tests should verify all Ivy Town `Unit` values used by event files appear here or are deliberately excluded. Runtime tests should compare perf-detected PMU counter capabilities against the expected model where Ivy Town hardware is available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/ivytown/counter.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/ivytown/floating-point.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/ivytown/floating-point.json

Purpose: Defines 17 Ivy Town core PMU aliases for floating-point assists, FP computational uops, SIMD move elimination, AVX/SSE transition assists, and 256-bit SIMD arithmetic. These aliases support HPC and topdown compute diagnostics.

Important APIs/types/functions: Entries use `EventName`, `EventCode`, `UMask`, `Counter`, `CounterMask`, `SampleAfterValue`, `BriefDescription`, and `PublicDescription`. Families include `FP_ASSIST`, `FP_COMP_OPS_EXE`, `MOVE_ELIMINATION`, `OTHER_ASSISTS`, and `SIMD_FP_256`. The FP computational aliases distinguish x87, SSE scalar single/double, SSE packed single/double, and AVX-256 packed single/double classes.

Control flow: Perf converts the JSON array into alias metadata. Runtime requests such as `FP_COMP_OPS_EXE.SSE_PACKED_DOUBLE` schedule core PMU counters using event select/unit mask values. Derived metrics in `ivt-metrics.json` combine these aliases to estimate scalar/vector FP fractions, x87 use, GFLOPS, FLOP/cycle, assists, and transition penalties.

State and persistence: Static event metadata only. Runtime counts are hardware PMU state and perf output; PEBS or sampling state is not managed by this file.

Dependencies/integration: Depends on Ivy Town core PMU definitions and perf alias parsing. It integrates tightly with metric expressions such as `tma_fp_scalar`, `tma_fp_vector`, `tma_fp_vector_128b`, `tma_fp_vector_256b`, `tma_info_core_flopc`, and `tma_info_system_gflops`.

Risks: These aliases count uops or assists, not necessarily architectural floating-point instructions, so derived FLOP estimates rely on assumptions about vector width and instruction mix. `FP_ASSIST.ANY` uses a counter mask and cycle-like semantics, while other FP assist aliases are count-like. AVX/SSE transition event descriptions are architecture-specific and can be mistaken for generic AVX penalties. Incorrect alias names break several topdown/HPC metrics.

Test signals: Validate schema and uniqueness, run metric parser tests for all FP-related expressions, and smoke-test `perf stat` on scalar, SSE, AVX, and x87 microbenchmarks. Tests should distinguish count events from `CounterMask`-qualified cycle events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/ivytown/floating-point.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/ivytown/frontend.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/ivytown/frontend.json

Purpose: Defines 30 Ivy Town frontend PMU aliases covering branch resteers, DSB-to-MITE switches, DSB fill pressure, instruction cache behavior, IDQ delivery paths, microcode sequencer delivery, and frontend under-delivery. These events feed topdown frontend-bound analysis.

Important APIs/types/functions: Entries use `EventName`, `EventCode`, `UMask`, `Counter`, `CounterMask`, `EdgeDetect`, `Invert`, `SampleAfterValue`, `BriefDescription`, and `PublicDescription`. Families include `BACLEARS`, `DSB2MITE_SWITCHES`, `DSB_FILL`, `ICACHE`, `IDQ`, and `IDQ_UOPS_NOT_DELIVERED`. Several aliases use `CounterMask` to count cycles with a delivery threshold; `IDQ.MS_DSB_OCCUR` and `IDQ.MS_SWITCHES` use edge detection to count occurrences.

Control flow: Perf's generated table exposes these aliases for core PMU scheduling. Runtime lookup maps frontend event names to event select/unit mask/counter-mask combinations. `ivt-metrics.json` uses them for `tma_frontend_bound`, `tma_fetch_latency`, `tma_fetch_bandwidth`, `tma_dsb`, `tma_dsb_switches`, `tma_mite`, `tma_ms_switches`, `tma_icache_misses`, and microcode sequencer metrics.

State and persistence: Static metadata only. Runtime frontend delivery and stall state is in hardware counters and perf samples.

Dependencies/integration: Depends on Ivy Town frontend PMU semantics and perf handling of `CounterMask`, `Invert`, and `EdgeDetect`. It integrates with pipeline events such as `UOPS_ISSUED` and with metric expressions that normalize frontend events by thread or core clocks.

Risks: Many aliases share event code `0x79` with different unit masks and counter masks; small field errors silently change the delivery path being counted. Cycle-threshold aliases should not be interpreted as raw uop totals. Edge-detected occurrence events and duration events have different units despite similar names. Topdown metrics are sensitive to these aliases because frontend-bound formulas subtract or normalize by delivery capacity.

Test signals: Validate event fields and generated aliases, especially `CounterMask`, `EdgeDetect`, and `Invert`. Run metric-resolution tests for frontend topdown formulas. On hardware, compare DSB/MITE/ICACHE counters with microbenchmarks that fit in the decoded-uop cache versus instruction-cache-thrashing or branch-heavy workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/ivytown/frontend.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/ivytown/ivt-metrics.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/ivytown/ivt-metrics.json

Purpose: Defines 137 derived Ivy Town perf metrics, including package/core C-state residency, SMI indicators, topdown microarchitecture levels, memory/cache diagnostics, frontend/backend breakdowns, FP/HPC summaries, power/system metrics, and helper `tma_info_*` values. This file is the main formula layer above raw PMU events.

Important APIs/types/functions: Entries use `MetricName`, `MetricExpr`, `MetricGroup`, `ScaleUnit`, `BriefDescription`, `PublicDescription`, `MetricThreshold`, `MetricConstraint`, and `MetricgroupNoGroup`. Expressions reference raw event aliases, other metrics, perf special terms (`duration_time`, `cycles`, `#SMT_on`, `#core_wide`, `#num_cpus_online`, `#num_dies`), MSR and sysfs-style events (`msr@tsc@`, `power@energy-pkg@`, `cstate_*`), and encoded event forms such as `cpu@...\\,cmask\\=1@`.

Control flow: Perf loads these metric definitions for Ivy Town, resolves dependencies recursively, schedules the raw events needed by each formula, evaluates `MetricExpr`, applies `ScaleUnit`, groups metrics through `MetricGroup`, and uses thresholds for UI/reporting hints. Level-1 topdown metrics derive from `tma_frontend_bound`, `tma_bad_speculation`, `tma_retiring`, and `tma_backend_bound`; deeper metrics refine those categories into branch, frontend, memory, core, port, FP, and system explanations.

State and persistence: Static formula metadata only. There is no mutable state in the file. Runtime state is the measured event values and evaluated metric results held by perf.

Dependencies/integration: Depends on raw aliases from Ivy Town cache, frontend, floating-point, memory, pipeline, virtual-memory, and uncore files. High-frequency dependencies include `INST_RETIRED.ANY`, `CPU_CLK_UNHALTED.THREAD`, `MEM_LOAD_UOPS_RETIRED.*`, LLC hit/miss retired events, `UOPS_RETIRED.RETIRE_SLOTS`, and `UOPS_EXECUTED.THREAD`. It also depends on `metricgroups.json` for readable group labels.

Risks: Formula breakage is easy when event aliases are renamed, removed, or moved between files. Expressions include divisions with workload-dependent zero denominators; perf's expression evaluator must handle these robustly. Some formulas embed architecture-specific latency constants, SMT adjustments, and heuristic thresholds, so values are diagnostic estimates rather than hardware invariants. Long offcore/memory expressions create large event groups that may multiplex or fail on counter constraints.

Test signals: Run perf metric parser tests, dependency-resolution checks for every `MetricExpr`, and group-label checks against `metricgroups.json`. On Ivy Town hardware, smoke-test topdown, memory, power, and FP metric groups under idle, CPU-bound, memory-bound, branch-mispredict, and FP workloads. Static tests should flag unknown aliases, cyclic metric dependencies, and invalid expression syntax.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/ivytown/ivt-metrics.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/ivytown/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/ivytown/memory.json

Purpose: Defines 41 Ivy Town memory-related core PMU aliases for memory-ordering machine clears, load latency sampling thresholds, precise store sampling, misaligned memory references, and LLC-miss offcore response classes. It extends the cache file's memory coverage with latency and remote/local DRAM attribution.

Important APIs/types/functions: Entries use `EventName`, `EventCode`, `UMask`, `Counter`, `MSRIndex`, `MSRValue`, `PEBS`, `SampleAfterValue`, `BriefDescription`, and `PublicDescription`. Families include `MACHINE_CLEARS`, `MEM_TRANS_RETIRED`, `MISALIGN_MEM_REF`, and many `OFFCORE_RESPONSE.*.LLC_MISS.*` aliases. `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_*` variants share event select `0xCD` and are constrained to counter 3 for PEBS-style latency sampling thresholds.

Control flow: Perf exposes these aliases after JSON table generation. Runtime use maps ordinary aliases to core event fields and maps offcore aliases to offcore response event select plus MSR filters. Precise load/store events can drive sampling workflows, while offcore LLC-miss aliases feed memory locality and remote-hit diagnostics.

State and persistence: Static metadata only. Runtime state is in PMU counters, offcore filter MSRs, and PEBS records. The file persists threshold alias names and filter encodings.

Dependencies/integration: Depends on Ivy Town PMU offcore response and PEBS support. It complements `cache.json`, which covers many LLC-hit and request-side aliases. Metrics such as remote memory/cache, false sharing, memory latency, and synchronization diagnostics can depend on these offcore response names.

Risks: Many offcore aliases share visible event fields and differ only by MSR filter values, so filter metadata correctness is critical. Some descriptions in the offcore family use hit/miss wording that should be audited carefully. Counter 3 constraints on latency events can conflict with other events in a group. PEBS availability may depend on kernel/hardware support and privilege settings.

Test signals: Static tests should verify required `MSRIndex`/`MSRValue` fields for every offcore response alias and counter constraints for `MEM_TRANS_RETIRED`. Runtime smoke tests should exercise load-latency sampling, misaligned access counters, and local versus remote memory workloads where Ivy Town NUMA hardware is available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/ivytown/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/ivytown/metricgroups.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/ivytown/metricgroups.json

Purpose: Provides 124 human-readable descriptions for Ivy Town metric group names used by `ivt-metrics.json`. This file is metadata for organizing and explaining perf metrics, especially topdown analysis groups and issue categories.

Important APIs/types/functions: Unlike most PMU event files, this JSON file is an object mapping group name to description. Keys include broad groups such as `Backend`, `Frontend`, `MemoryBound`, `MemoryBW`, `Offcore`, `Power`, `Summary`, and `SMT`; topdown levels `TopdownL1` through `TopdownL6`; mirrored internal groups like `tma_L1_group`; contributing-category groups like `tma_backend_bound_group`; and issue tags such as `tma_issueBW`, `tma_issueFB`, `tma_issueTLB`, and `tma_issueSyncxn`.

Control flow: Perf loads metric group descriptions when displaying or documenting metric groups. `ivt-metrics.json` entries list semicolon-separated `MetricGroup` values; those group IDs are resolved here for user-facing descriptions. The file does not schedule events or evaluate formulas.

State and persistence: Static descriptive metadata only. It persists labels and descriptions in the repository and has no runtime mutable state.

Dependencies/integration: Depends on group names matching the `MetricGroup` tokens in `ivt-metrics.json`. It also reflects naming from Intel's Top-down Microarchitecture Analysis spreadsheet, so consistency with imported metric definitions matters. Perf UI/help output depends on this file for readable grouping context.

Risks: Missing or misspelled group keys do not necessarily break metric computation, but they degrade discoverability and may leave groups undocumented. Because this file is object-shaped while event files are arrays, tooling that assumes arrays will fail. Generic descriptions repeated across many spreadsheet-derived groups are useful but not very specific, so users may need metric-level descriptions for interpretation.

Test signals: Validate JSON object shape, unique keys, and string descriptions. Cross-check every `MetricGroup` token from `ivt-metrics.json` against this object, allowing only deliberate built-in or legacy exceptions. UI tests should confirm `perf list --metricgroups` or equivalent help paths show these descriptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/ivytown/metricgroups.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/ivytown/other.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/ivytown/other.json

Purpose: Defines 4 Ivy Town miscellaneous core PMU aliases for current privilege level cycle accounting and split/uncacheable lock duration. These fill gaps not covered by cache, frontend, floating-point, or pipeline-specific files.

Important APIs/types/functions: Entries use `EventName`, `EventCode`, `UMask`, `Counter`, `CounterMask`, `EdgeDetect`, `SampleAfterValue`, `BriefDescription`, and `PublicDescription`. The `CPL_CYCLES` family includes `RING0`, `RING0_TRANS`, and `RING123`; `RING0_TRANS` uses `CounterMask: 1` and `EdgeDetect: 1` to count intervals/transitions rather than raw cycles. `LOCK_CYCLES.SPLIT_LOCK_UC_LOCK_DURATION` counts cycles with L1/L2 locked due to split or uncacheable locks.

Control flow: Perf's table generator includes these aliases in the Ivy Town core event map. Runtime lookup schedules the selected event on core programmable counters and applies edge/counter-mask qualifiers where present. System or OS metrics can use CPL cycle aliases to estimate kernel/user privilege activity, while lock-cycle aliases help diagnose pathological locked memory operations.

State and persistence: Static metadata only. Hardware PMU counters and perf outputs hold runtime counts.

Dependencies/integration: Depends on Ivy Town core PMU definitions and perf support for edge-detected events. It complements `ivt-metrics.json` OS/system metrics, which separately use privilege-qualified cycle and instruction aliases, and cache lock events from `cache.json`.

Risks: `CPL_CYCLES.RING123` combines rings 1, 2, and 3; most user workloads run ring 3, but the alias name should not be simplified to user-only in documentation. Transition counts and cycle counts have different units despite shared event code. Split/UC lock behavior can be rare and workload-specific, so zero counts are not necessarily a failure.

Test signals: Validate schema and generated aliases, including `EdgeDetect` on `RING0_TRANS`. Runtime smoke tests should compare ring0/ring123 counts under syscall-heavy versus user-space loops and trigger split-lock/UC-lock scenarios only in controlled tests where the platform permits them.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/ivytown/other.json -->
