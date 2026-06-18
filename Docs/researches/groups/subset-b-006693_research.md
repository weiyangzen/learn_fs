# subset-b-006693 Research

Grouped code research for Ivy Town and Jake Town x86 perf PMU event metadata JSON files. Each section preserves the source path in its title and is bounded by reconciliation markers for source-tree-aligned splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/ivytown/uncore-io.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/ivytown/uncore-io.json

## Purpose
This JSON file defines Ivy Town uncore I/O PMU events for perf's generated event tables. It covers the R2PCIe uncore block, exposing clockticks, IIO credit acquisition/rejection/usage, ring utilization on AD/AK/BL/IV rings, receive-ring occupancy and inserts, and transmit-ring full/not-empty/NACK conditions. The data lets `perf list` and `perf stat -e` present symbolic names such as `UNC_R2_RING_AD_USED.CW_VR0_EVEN` instead of requiring users to hand-code event select and unit-mask values.

## Important APIs, Types, And Functions
The file is declarative and has no functions or exported types. The important schema fields are `EventName`, `EventCode`, `UMask`, `BriefDescription`, `PublicDescription`, `Counter`, `PerPkg`, and `Unit`. All 61 entries use `Unit: R2PCIe` and `PerPkg: 1`, with most events available on counters `0,1,2,3`; credit events are limited to `0,1`, and `UNC_R2_RxR_OCCUPANCY.DRS` is restricted to counter `0`. The event families are `UNC_R2_IIO_CREDITS_*`, `UNC_R2_RING_*_USED`, `UNC_R2_RxR_*`, `UNC_R2_TxR_*`, and `UNC_R2_CLOCKTICKS`.

## Control Flow
There is no runtime control flow in the file. At build or runtime, perf's PMU event tooling parses the JSON array, validates known keys, and emits or loads event aliases for the Ivy Town model. User selection of an alias resolves to the relevant uncore PMU unit, event code, unit mask, and counter constraints. The repeated ring entries encode the matrix of ring type, direction, virtual ring, and odd/even polarity as separate aliases rather than computing them dynamically.

## State And Persistence
The file persists static hardware metadata only. No counters are allocated or mutated by this JSON until perf opens a corresponding hardware event through the kernel PMU interface. The `PerPkg` values indicate package-scoped uncore measurement semantics, while `Counter` constrains which programmable counters can host each event. Counter values observed at runtime live in kernel perf events, not in this repository data.

## Dependencies And Integration Points
The file integrates with Linux perf's `pmu-events` JSON parser and architecture map for `arch/x86/ivytown`. It depends on perf's accepted event-field vocabulary and on kernel uncore PMU support for the R2PCIe unit. It complements other Ivy Town uncore files for memory and power and is consumed together with CPU model matching metadata when perf chooses the correct event table.

## Risks And Edge Cases
Because this is hardware metadata, small encoding errors can silently produce misleading performance data. Risk areas include incorrect `UMask` combinations for clockwise/counterclockwise and virtual-ring polarity filters, wrong counter restrictions for credit and occupancy events, duplicate names, missing `EventCode`, and stale descriptions copied from vendor documentation. Ring aliases that aggregate masks, such as `.CW`, `.CCW`, or `.ANY`, need consistency with the more specific odd/even aliases.

## Test Signals
Useful validation includes `jq empty` for syntax, schema checks against perf's `jevents` parser, `perf list` on Ivy Town class systems or forced table generation, and spot checks that aliases resolve to the expected `event`, `umask`, unit, and counter masks. Runtime signals include sane nonzero clockticks, ring activity under PCIe traffic, IIO credit rejection rising under contention, and no parser warnings during `tools/perf` builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/ivytown/uncore-io.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/ivytown/uncore-memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/ivytown/uncore-memory.json

## Purpose
This JSON file defines Ivy Town integrated memory controller uncore PMU events for perf. Its 198 entries expose DRAM activate, precharge, CAS, refresh, ECC, major-mode, queue occupancy, throttling, rank/bank read CAS, rank/bank write CAS, and memory power-management counters. It provides symbolic iMC event aliases that help diagnose memory bandwidth, page policy, write-drain behavior, rank/bank distribution, refresh pressure, throttling, and ECC activity.

## Important APIs, Types, And Functions
The file is a static array of event descriptors, not executable code. Important fields are `EventName`, `EventCode`, `UMask`, `Counter`, `PerPkg`, `Unit`, `BriefDescription`, and `PublicDescription`. Every entry uses `Unit: iMC`, `PerPkg: 1`, and counters `0,1,2,3`. Major families include `UNC_M_ACT_COUNT`, `UNC_M_CAS_COUNT`, `UNC_M_PRE_COUNT`, `UNC_M_MAJOR_MODES`, `UNC_M_POWER_*`, `UNC_M_RD_CAS_RANK{0..7}.BANK{0..7}`, `UNC_M_WR_CAS_RANK{0..7}.BANK{0..7}`, `UNC_M_RPQ_*`, `UNC_M_WPQ_*`, `UNC_M_WMM_TO_RMM`, and `UNC_M_VMSE_*`.

## Control Flow
There is no control flow in the JSON itself. Perf parses the array into model-specific iMC aliases, and a selected alias becomes a hardware event programmed on the appropriate uncore memory-controller PMU. The rank/bank sections are intentionally expanded into one descriptor per rank and bank so users can select a specific physical dimension directly. Aggregate aliases such as CAS read/write totals use broader unit masks than the rank/bank entries.

## State And Persistence
The persisted state is the metadata mapping from human-readable event names to hardware encodings and descriptions. Runtime memory-controller counter state is created by perf and the kernel uncore driver when a user opens an event. The file records package-scoped semantics through `PerPkg` and allows any iMC generic counter through `Counter: 0,1,2,3`; it does not store current memory-controller mode, rank population, or platform topology.

## Dependencies And Integration Points
This file depends on perf's x86 `pmu-events` parser and Ivy Town CPU model matching. It integrates with the Linux uncore iMC PMU driver, with perf alias generation, and with higher-level perf metric expressions that may reference memory event names. It also overlaps conceptually with Ivy Town power metadata because some `UNC_M_POWER_*` events live on the iMC unit rather than the package PCU unit.

## Risks And Edge Cases
The file is large and regular, making copy/paste or generated-table mistakes plausible. Rank/bank aliases must maintain correct mask progression for all eight ranks and eight banks. Some descriptions contain vendor terminology and minor textual issues, so tests should focus on encoding correctness rather than prose alone. Hardware may not expose all ranks, banks, or modes on every platform, so zero counts are not necessarily parser failures. Incorrect aggregate masks for `.ALL`, `.RD`, or `.WR` could mislead bandwidth calculations.

## Test Signals
Validation signals include JSON syntax checks, successful `jevents` generation, no duplicate event-name diagnostics, and `perf list` showing iMC aliases under Ivy Town. Runtime smoke tests should compare `UNC_M_CAS_COUNT.RD` and `.WR` against known memory bandwidth workloads, verify rank/bank events concentrate on populated channels, observe refresh and power-state counters during idle, and check ECC events only on ECC-capable systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/ivytown/uncore-memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/ivytown/uncore-power.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/ivytown/uncore-power.json

## Purpose
This JSON file defines Ivy Town PCU uncore power-management PMU events for perf. It covers package clockticks, per-core C-state transition cycles, delayed C-state aborts, demotions, frequency-band residency, max/min frequency limit causes, package C-state residency and exit latency, power-state occupancy, PROCHOT, voltage transitions, memory phase shedding, and VR hot cycles. These aliases support diagnosis of platform power policy and frequency throttling behavior.

## Important APIs, Types, And Functions
The file is declarative metadata. Important fields are `EventName`, `EventCode`, `Counter`, `PerPkg`, `Unit`, `BriefDescription`, `PublicDescription`, and for occupancy selectors, `Filter`. All 74 entries use `Unit: PCU`, `PerPkg: 1`, and counters `0,1,2,3`. Per-core families enumerate cores 0 through 14 for transition, delayed C-state abort, and demotion events. `UNC_P_POWER_STATE_OCCUPANCY.CORES_C0`, `.CORES_C3`, and `.CORES_C6` use filters `occ_sel=1`, `occ_sel=2`, and `occ_sel=3`.

## Control Flow
The file has no executable path. Perf loads the descriptors for Ivy Town, exposes the aliases, and programs the PCU uncore PMU when an event is requested. The per-core entries are explicit rows rather than parameterized aliases, so model changes in core count require separate metadata. The filter-backed occupancy rows demonstrate how the perf event table passes additional PMU filter terms beyond event code and counter selection.

## State And Persistence
Only static alias metadata is persisted. The JSON does not track current power state, residency, or throttling; those values are sampled from hardware counters at runtime. `PerPkg` indicates package-level accounting, which matters because PCU measurements are not per logical CPU. Counter constraints permit all four PCU generic counters, so multiplexing behavior is controlled by perf when users request more events than hardware can count concurrently.

## Dependencies And Integration Points
The file integrates with perf's Ivy Town `pmu-events` table and the kernel PCU uncore PMU driver. It is closely related to CPU idle, P-state, thermal, and power-limit analysis workflows, and its aliases can be referenced from perf metrics or user scripts. The `Filter` field depends on parser support for passing PCU-specific filter syntax through to the PMU event selector.

## Risks And Edge Cases
The per-core rows assume the Ivy Town PCU event layout and core index set; an incorrect row can make one core's state appear under another alias. Frequency and throttling counters are easy to misinterpret without package topology and policy context. Filter typos for occupancy selectors can produce rejected events or valid events that count the wrong C-state bucket. Package-level counters should not be treated as per-thread measurements in metrics.

## Test Signals
Test signals include JSON syntax validation, successful perf event-table generation, `perf list` exposing PCU aliases, and ability to open representative events such as package clockticks, C-state residency, and frequency limit cycles on supported hardware. Runtime sanity checks include higher C-state residency while idle, increased PROCHOT or limit-cause counters under thermal or power stress, and stable parser handling of the `occ_sel` filters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/ivytown/uncore-power.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/ivytown/virtual-memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/ivytown/virtual-memory.json

## Purpose
This JSON file defines Ivy Town core PMU events related to virtual memory translation. Its 20 entries cover DTLB load misses, DTLB store misses, ITLB misses, second-level TLB hits, page-walk completions and durations, TLB flushes, instruction TLB flushes, and EPT walk cycles. It gives perf users symbolic names for translation overhead analysis on Ivy Town processors.

## Important APIs, Types, And Functions
The file contains event descriptors, not functions. Important fields are `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, and `PublicDescription`. All entries use programmable counters `0,1,2,3` and omit an uncore `Unit`, which means they are core PMU events. Families include `DTLB_LOAD_MISSES`, `DTLB_STORE_MISSES`, `ITLB_MISSES`, `TLB_FLUSH`, `ITLB.ITLB_FLUSH`, and `EPT.WALK_CYCLES`.

## Control Flow
There is no in-file control flow. Perf parses the JSON into Ivy Town core event aliases. When a user selects an alias, perf programs the core PMU with the specified event code and unit mask. Duration events count page-walk cycles, while completed or miss-cause aliases count occurrences; metrics and users must choose the appropriate form for rate versus latency analysis.

## State And Persistence
The JSON persists only event metadata and sampling defaults. Runtime TLB miss, walk, and flush counts are maintained by hardware counters and read through perf events. `SampleAfterValue` gives perf a default sampling period for some aliases but does not imply persistence in the source tree. Because these are core events, counts are scoped to selected CPUs, threads, or tasks according to normal perf event placement.

## Dependencies And Integration Points
The file integrates with perf's Ivy Town model event map and the kernel core PMU driver. The aliases are often consumed by top-down or memory-latency metrics, profiler recipes, and manual `perf stat` runs. `EPT.WALK_CYCLES` ties the table to virtualization analysis, where nested address translation can be a separate translation-cost source.

## Risks And Edge Cases
Load, store, and instruction TLB events have similar names but different event codes and masks; swapping masks would produce plausible but incorrect data. Page-walk duration events are cycle counts, not miss counts, so metric formulas must avoid treating them as occurrences. Some aliases distinguish demand-load walks from broader load walks, which affects workload interpretation. Virtualization-specific EPT events may be zero on non-virtualized workloads.

## Test Signals
Useful checks include JSON validation, successful perf table generation, `perf list` visibility, and opening representative load, store, instruction, and flush aliases. Runtime sanity tests include increased DTLB walk events under large random memory footprints, lower miss rates with huge pages, ITLB activity under instruction-cache stress, and EPT walk activity in virtualized workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/ivytown/virtual-memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/jaketown/cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/jaketown/cache.json

## Purpose
This JSON file defines Jake Town cache, memory-access, and offcore-response core PMU events for perf. Its 123 entries cover L1D allocation, replacement, eviction, pending misses, L2 lines and requests, lock cycles, retired memory uops, LLC hit and miss retirement, offcore requests, offcore outstanding requests, offcore response filters, and split lock signals. It supports cache hierarchy and memory-access analysis on Sandy Bridge-EP/Jake Town systems.

## Important APIs, Types, And Functions
The file is a declarative event table. Important fields include `EventName`, `EventCode`, `UMask`, `Counter`, `CounterMask`, `AnyThread`, `PEBS`, `MSRIndex`, `MSRValue`, `SampleAfterValue`, `BriefDescription`, and `PublicDescription`. Most entries use counters `0,1,2,3`, while `OFFCORE_RESPONSE` entries are constrained to counter `2` and program MSRs `0x1a6,0x1a7` with per-alias `MSRValue` filters. Families include `L1D*`, `L2_*`, `MEM_*`, `LONGEST_LAT_CACHE`, `OFFCORE_REQUESTS*`, `OFFCORE_RESPONSE*`, `LOCK_CYCLES`, and `SQ_MISC`.

## Control Flow
There is no executable flow in the file. Perf parses the descriptors into Jake Town aliases and, for ordinary events, programs the core PMU with event code and unit mask. For offcore response aliases, perf also programs the offcore response MSR filter indicated by `MSRIndex` and `MSRValue`; this is why these rows carry additional metadata and a narrower counter constraint. `CounterMask`, `AnyThread`, and `PEBS` alter how the kernel programs or samples the event.

## State And Persistence
The file persists static encoding and descriptive metadata. Runtime cache and offcore state is in hardware PMU counters and offcore MSRs during a perf session. PEBS-capable rows declare precise-event eligibility, but actual sampling buffers and records are allocated by perf and the kernel. Counter constraints are persistent metadata used to prevent invalid scheduling or to drive multiplexing decisions.

## Dependencies And Integration Points
The file integrates with perf's Jake Town model map, the x86 core PMU driver, and offcore-response MSR programming support. It is a dependency for metrics that reference memory hierarchy events and for user workflows that inspect local versus remote DRAM, LLC hit snoop outcomes, L2 request types, and pending miss pressure. The event names must match metric expressions in other JSON metric files if those metrics consume them.

## Risks And Edge Cases
Offcore response filters are the highest-risk area because a wrong `MSRValue` can still count a valid but different response class. Counter `2` restrictions on offcore aliases must be preserved. Some events use `CounterMask` to count cycles above an occupancy threshold rather than raw occurrences, so descriptions and metric formulas need to treat them differently. PEBS flags must align with hardware support or precise sampling may fail. Remote/local DRAM aliases depend on platform topology and may not behave intuitively on all systems.

## Test Signals
Validation includes `jq empty`, `jevents` parser success, duplicate-name checks, and inspection of generated offcore encodings. Runtime checks include `perf stat` on L1/L2/LLC workloads, PEBS sampling of retired memory-load events, offcore response counts changing under local and remote memory placement, and expected scheduling behavior when multiple counter-2-only offcore events are requested together.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/jaketown/cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/jaketown/counter.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/jaketown/counter.json

## Purpose
This JSON file declares Jake Town PMU counter inventory metadata for perf. Unlike event tables, it does not define event aliases; it tells perf how many fixed and generic counters exist for each core and uncore PMU unit. The listed units are `core`, `CBOX`, `PCU`, `UBOX`, `QPI`, `R3QPI`, `R2PCIe`, `HA`, `iMC`, and `IRP`.

## Important APIs, Types, And Functions
The schema contains `Unit`, `CountersNumFixed`, and `CountersNumGeneric`. There are 10 entries. The `core` unit has three fixed counters and four generic counters. Most uncore units have zero fixed counters and four generic counters, with `UBOX` and `IRP` providing two generic counters and `R3QPI` providing three. There are no `EventName`, `EventCode`, `UMask`, metric, or description fields because this file models capacity rather than events.

## Control Flow
There is no runtime control flow in the JSON. Perf's event metadata tooling reads this inventory alongside Jake Town event tables and uses it to understand PMU scheduling capacity, display metadata, or validate event placement. User-selected events from other files are constrained by both their per-event `Counter` fields and the unit-wide counter counts declared here.

## State And Persistence
The file persists static hardware inventory. It does not store current counter allocations, multiplexing state, or active perf sessions. At runtime, perf and the kernel allocate counters according to hardware availability, event constraints, pinned/exclusive requests, and multiplexing policy. This file simply records the baseline counter counts for Jake Town units.

## Dependencies And Integration Points
This file integrates with the Jake Town perf PMU metadata set. It complements `cache.json`, uncore unit event files, and metrics by declaring available counter resources. It depends on perf's parser recognizing the counter-inventory schema and on unit names matching the units used by event descriptors, such as `PCU`, `R2PCIe`, and `iMC`.

## Risks And Edge Cases
Incorrect counts can cause perf to overestimate or underestimate schedulable events. Unit-name mismatches are risky because they can disconnect inventory from event tables. The file is concise, but it represents multiple PMU blocks with different capacities, so copying a default count across all units would be wrong for `UBOX`, `IRP`, and `R3QPI`. Platform steppings or disabled units may still make runtime availability differ from this static metadata.

## Test Signals
Test signals include JSON syntax validation, parser acceptance of entries without `EventName`, and consistency checks that unit names align with Jake Town event files. Runtime validation can compare perf's event scheduling and multiplexing behavior against expected counter capacity, especially for UBOX, IRP, and R3QPI units with fewer than four generic counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/jaketown/counter.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/jaketown/floating-point.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/jaketown/floating-point.json

## Purpose
This JSON file defines Jake Town floating-point and SIMD assist PMU events for perf. Its 15 entries expose floating-point assists, x87 and SIMD input/output assists, SSE scalar and packed computation events, 256-bit SIMD floating-point operations, and AVX/SSE transition assists. It supports analysis of floating-point throughput, vectorization width, and costly assist or transition behavior.

## Important APIs, Types, And Functions
The file is a static array of core event descriptors. Important fields are `EventName`, `EventCode`, `UMask`, `Counter`, `CounterMask`, `SampleAfterValue`, and `BriefDescription`. All entries use counters `0,1,2,3`. Event families are `FP_ASSIST`, `FP_COMP_OPS_EXE`, `OTHER_ASSISTS`, and `SIMD_FP_256`. `FP_ASSIST.ANY` uses a counter mask, while other entries are direct event-code and unit-mask aliases.

## Control Flow
There is no in-file control flow. Perf parses the descriptors for Jake Town and programs the core PMU when users request these aliases. The table separates scalar, packed, x87, SSE, AVX transition, and 256-bit SIMD events so higher-level metrics can distinguish legacy floating point, SSE arithmetic, AVX-width work, and assist penalties.

## State And Persistence
Only static metadata and default sample periods are persisted. Runtime assist and operation counts are hardware counter values owned by perf sessions. `CounterMask` changes the semantics of the affected event from a simple count to a thresholded condition, depending on the hardware event definition. No floating-point architectural state is stored here.

## Dependencies And Integration Points
The file integrates with Jake Town perf event generation and with metrics that reference floating-point event names, including top-down or HPC-oriented metrics in `jkt-metrics.json`. It depends on the core PMU supporting the listed event codes and on perf preserving these aliases for user scripts and metric expressions.

## Risks And Edge Cases
Floating-point event names can be misleading if treated as exact FLOP counts; some count operations, uops, assists, or transitions rather than mathematical operations. AVX-to-SSE and SSE-to-AVX assists are workload- and ABI-sensitive. Incorrect unit masks would make scalar, packed, single, and double categories overlap incorrectly. Counter-mask semantics need parser support and clear interpretation in metrics.

## Test Signals
Validation includes JSON syntax checks, `jevents` generation, `perf list` visibility, and ability to open representative assist and computation events. Runtime tests should compare scalar SSE, packed SSE, and 256-bit SIMD aliases using controlled microbenchmarks, and should trigger AVX/SSE transition events with mixed instruction sequences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/jaketown/floating-point.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/jaketown/frontend.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/jaketown/frontend.json

## Purpose
This JSON file defines Jake Town frontend PMU events for perf. Its 33 entries cover branch resteers, DSB-to-MITE switches, decoded stream buffer fill cancellations, instruction-cache hits and misses, instruction decode queue sources and occupancy, microcode sequencer delivery, uops not delivered, and instructions written to the instruction queue. It supports frontend bottleneck analysis for instruction fetch, decode, uop cache, and delivery limits.

## Important APIs, Types, And Functions
The file contains declarative event descriptors. Important fields include `EventName`, `EventCode`, `UMask`, `Counter`, `CounterMask`, `EdgeDetect`, `Invert`, `SampleAfterValue`, `BriefDescription`, and `PublicDescription`. All entries use counters `0,1,2,3`. Event families include `BACLEARS`, `DSB2MITE_SWITCHES`, `DSB_FILL`, `ICACHE`, `IDQ`, `IDQ_UOPS_NOT_DELIVERED`, and `INSTS_WRITTEN_TO_IQ`. Several cycle-threshold events use counter masks, edge detection, or inversion to express specific frontend-delivery states.

## Control Flow
There is no executable control flow. Perf parses the JSON aliases and programs core PMU events with optional counter-mask, edge-detect, or invert attributes. The table intentionally distinguishes count events from cycle qualification events, for example DSB or MITE uop delivery versus cycles with any or four uops delivered. These aliases are building blocks for top-down frontend metrics.

## State And Persistence
The file persists hardware encoding metadata and default sampling values. Runtime frontend state, instruction queue occupancy, and uop delivery counts are not stored here; they are sampled from PMU counters. `CounterMask`, `EdgeDetect`, and `Invert` fields persist the conditions needed to count cycles matching frontend states such as zero delivered uops or microcode sequencer switches.

## Dependencies And Integration Points
The file integrates with perf's Jake Town PMU event table and with `jkt-metrics.json`, which references frontend concepts such as frontend bound, fetch latency, fetch bandwidth, DSB switches, and branch resteers. It depends on parser support for counter-mask, inversion, and edge-detect fields and on the core PMU driver mapping those attributes correctly.

## Risks And Edge Cases
Cycle-qualified delivery events are easy to misinterpret as raw uop counts. `Invert` and `CounterMask` mistakes can reverse a metric's meaning, especially for `IDQ_UOPS_NOT_DELIVERED` aliases. Frontend events are sensitive to SMT state and pipeline source, so metric formulas must include appropriate denominators. DSB/MITE terminology should stay aligned with vendor docs to avoid confusing decoded-uop-cache and legacy decode paths.

## Test Signals
Useful checks include JSON syntax validation, event-table generation, and `perf list` visibility. Runtime signals include increased instruction-cache misses under large code footprints, DSB/MITE distribution shifts under uop-cache-friendly versus unfriendly loops, branch resteer events under branch-mispredict microbenchmarks, and top-down frontend metrics resolving all referenced aliases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/jaketown/frontend.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/jaketown/jkt-metrics.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/jaketown/jkt-metrics.json

## Purpose
This JSON file defines Jake Town derived perf metrics. Its 72 metric descriptors compute package and core C-state residency, uncore frequency, SMI activity, top-down microarchitecture categories, memory and frontend bottlenecks, floating-point mix, pipeline information ratios, and summary signals. Unlike event files, this file combines raw events, constants, conditionals, and thresholds into named metrics for `perf stat -M` style workflows.

## Important APIs, Types, And Functions
The file is declarative metric metadata. Key fields are `MetricName`, `MetricExpr`, `MetricGroup`, `MetricThreshold`, `MetricConstraint`, `MetricgroupNoGroup`, `ScaleUnit`, `BriefDescription`, and `PublicDescription`. Metric groups include `Power`, `SoC`, `smi`, `TopdownL1` through `TopdownL5`, `Backend`, `Frontend`, `MemoryBound`, `FetchLat`, `FetchBW`, `Compute`, `Flops`, `HPC`, `Pipeline`, and summary categories. Many metrics use `tma_` names and reference other metrics, creating a dependency graph rather than independent event aliases.

## Control Flow
There is no imperative control flow, but metric evaluation has dependency flow. Perf parses `MetricExpr`, schedules the referenced events and prerequisite metrics, evaluates arithmetic and conditionals such as SMT-aware formulas, applies scaling units, and can compare results to `MetricThreshold`. Parent top-down metrics such as `tma_backend_bound`, `tma_bad_speculation`, `tma_frontend_bound`, and `tma_retiring` feed lower-level metrics including branch mispredicts, DSB switches, DTLB load cost, DRAM bound, FP vector mix, and port utilization.

## State And Persistence
The file persists formulas, grouping labels, constraints, and thresholds. It does not store measured results or previous evaluations. Runtime metric state is produced by perf from active counter values, duration, topology constants, and model helper variables such as `#SMT_on`, `#num_dies`, and top-down slot denominators. Constraints such as `NO_GROUP_EVENTS` and `NO_GROUP_EVENTS_SMT` affect scheduling policy rather than persistent state.

## Dependencies And Integration Points
The metrics depend on Jake Town event aliases from cache, frontend, floating-point, pipeline, branch, memory, and MSR/cstate sources. Expressions reference raw events such as `BR_MISP_RETIRED.ALL_BRANCHES`, `MACHINE_CLEARS.COUNT`, `FP_COMP_OPS_EXE.*`, `DTLB_LOAD_MISSES.*`, `MEM_LOAD_UOPS_RETIRED.*`, `DSB2MITE_SWITCHES.PENALTY_CYCLES`, MSR aliases, and synthetic top-down helper metrics. The file integrates with perf's metric parser, event scheduler, threshold display, and metric group selection.

## Risks And Edge Cases
Metric dependency and naming consistency are the main risks. A referenced event missing from the Jake Town set will make the metric unusable even though this JSON is syntactically valid. Formulas can divide by zero or produce misleading values when workloads do not retire relevant events; some use conditionals to mitigate that. SMT-specific formulas and constraints must match hardware behavior. Several FP metrics note possible overcounting, so users should not treat them as exact FLOP rates. Thresholds are heuristic guidance, not pass/fail correctness.

## Test Signals
Validation includes JSON syntax checks, perf metric parser acceptance, no unresolved event or metric references, and successful `perf list --metrics` output for Jake Town. Runtime tests should run representative `perf stat -M` groups, verify top-down L1 categories sum sensibly, confirm Power and SMI metrics resolve MSR dependencies, and exercise metrics with SMT on and off. Regression tests should include expression parsing for escaped cstate names, conditionals, `min()`, constants such as `#num_dies`, and metric constraints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/jaketown/jkt-metrics.json -->
