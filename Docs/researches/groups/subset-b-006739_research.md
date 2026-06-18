# Research: subset-b-006739

This grouped report covers x86 PMU event definition JSON files under `sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/`. These files are declarative inputs for the Linux `perf` PMU event pipeline; they do not contain executable functions, but their field schema is an API consumed by perf's event table generator and runtime event lookup.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/snowridgex/uncore-memory.json -->
## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/snowridgex/uncore-memory.json

### Purpose
`uncore-memory.json` defines Snow Ridge uncore integrated-memory-controller events for `perf list`, `perf stat`, and metric evaluation. The file has 63 event objects focused on iMC DRAM traffic, queue pressure, power-down/self-refresh residency, command scheduling, refreshes, parity errors, read/write pending queues, and memory controller clocks. It also provides two derived aliases, `LLC_MISSES.MEM_READ` and `LLC_MISSES.MEM_WRITE`, scaled as 64-byte requests from CAS read/write counts.

### Important APIs, Types, and Fields
The public interface is the perf PMU event JSON schema. Every entry is a JSON object with fields such as `EventName`, `BriefDescription`, `PublicDescription`, `EventCode`, `UMask`, `Counter`, `Unit`, and `PerPkg`. `Unit` is consistently `iMC`, so the events bind to Snow Ridge memory controller PMUs rather than core PMUs. `Counter` is usually `0,1,2,3`; `UNC_M_CLOCKTICKS_FREERUN` uses fixed/free-running counter metadata. `ScaleUnit` appears on the LLC miss aliases to indicate 64-byte transfer accounting. Forty entries carry `Experimental`, marking them more fragile for user-facing workflows. Two entries also define `MetricName` and `MetricExpr`: `power_channel_ppd` and `power_self_refresh`, each computed as event cycles divided by `UNC_M_CLOCKTICKS` times 100.

### Control Flow and Data Flow
The file has no in-file branches or functions. Build-time flow is: perf's PMU event tooling parses the JSON array, validates known keys, generates architecture-specific event tables, and later exposes each `EventName` as a named event when the current CPU model maps to Snow Ridge. Runtime flow is user driven: a command such as `perf stat -e UNC_M_CAS_COUNT.RD` resolves the name, programs the iMC PMU with `EventCode` and `UMask`, selects one of the listed counters, and aggregates per-package/per-controller counts according to perf's uncore PMU discovery. Metric expressions depend on the presence and correct naming of their referenced base events.

### State and Persistence Behavior
The source file is static repository data. Runtime counter state lives in hardware PMU counters and perf's measurement process, not in the JSON. `PerPkg: 1` tells perf that events are package-scoped; this affects aggregation and can surprise callers expecting per-core behavior. Queue occupancy events such as `UNC_M_RDB_OCCUPANCY`, `UNC_M_RPQ_OCCUPANCY_PCH0/PCH1`, and `UNC_M_WPQ_OCCUPANCY_PCH0/PCH1` count occupancy over cycles, so consumers must divide by corresponding insert or active-cycle events for average residency-style interpretations.

### Dependencies and Integration Points
The file depends on perf's JSON schema support for uncore events, Snow Ridge CPU model mapping, and kernel PMU names for `iMC`. It integrates with sibling Snow Ridge event files and shared perf scripts that generate C tables from JSON. Metric expressions depend on `UNC_M_CLOCKTICKS` and the exact base event names in this file. Downstream tools such as `perf list`, `perf stat --metric-only`, and any generated event aliases rely on the event names remaining stable.

### Risks and Edge Cases
The largest risk is semantic drift between Intel event definitions and the JSON encodings, especially because most entries are marked experimental. Alias names beginning with `LLC_MISSES` may be misread as core LLC events even though they derive from memory-controller CAS counts. `ScaleUnit: 64Bytes` is meaningful only if downstream code uses it consistently for bandwidth or byte conversions. PCH0/PCH1 queue events must not be aggregated blindly with other channels without understanding package topology. The two metric expressions divide by clock ticks, so zero or unavailable `UNC_M_CLOCKTICKS` readings would produce invalid metrics.

### Test Signals
Strong checks are `jq empty` for syntax, perf PMU event-table generation, and `perf list` on a Snow Ridge system showing representative events such as `UNC_M_CAS_COUNT.RD`, `UNC_M_POWER_SELF_REFRESH`, and `LLC_MISSES.MEM_READ`. Runtime smoke tests should use `perf stat -e UNC_M_CLOCKTICKS,UNC_M_CAS_COUNT.RD,UNC_M_CAS_COUNT.WR` on supported hardware and confirm nonzero counts under memory load. Metric tests should verify that `power_channel_ppd` and `power_self_refresh` resolve their base events and render percentages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/snowridgex/uncore-memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/snowridgex/uncore-power.json -->
## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/snowridgex/uncore-power.json

### Purpose
`uncore-power.json` defines Snow Ridge package power-control-unit events. Its 26 records describe PCU clock ticks, core/package C-state residency, frequency transitions, thermal and power clipping, FIVR phase shedding, PROCHOT assertions, demotions, and power-state occupancy. These events let perf users correlate performance with package-level power management decisions.

### Important APIs, Types, and Fields
The schema uses perf event fields including `EventName`, `BriefDescription`, `EventCode`, `UMask`, `Counter`, `Unit`, `PerPkg`, and optional `PublicDescription` and `Experimental`. `Unit` is consistently `PCU`, binding these definitions to the uncore power control unit PMU. `UNC_P_CLOCKTICKS` has no explicit `EventCode`, implying special handling or a counter-native PCU clock event. Almost every other event is marked `Experimental`, so users and maintainers should treat exact encodings as hardware-stepping-sensitive.

### Control Flow and Data Flow
The file is parsed by perf's PMU event build tooling into Snow Ridge event tables. At runtime, perf resolves a requested name such as `UNC_P_FREQ_MAX_POWER_CYCLES` or `UNC_P_PKG_RESIDENCY_C6_CYCLES`, maps it to the PCU PMU, and programs one of counters `0,1,2,3` using the encoded event selector and unit mask. There is no procedural control flow in the JSON; all behavior is driven by event lookup and hardware counter sampling.

### State and Persistence Behavior
No persistent state is stored in the file. The measured state is package-level PCU counter state over the perf measurement interval. `PerPkg: 1` means results are package scoped. Residency and throttling cycle events represent time spent in power states, while transition events represent count-like behavior; consumers must not mix them without normalizing by `UNC_P_CLOCKTICKS` or elapsed time.

### Dependencies and Integration Points
The definitions depend on Snow Ridge PCU PMU support in the kernel and perf's uncore event table generation. They integrate with `perf list` and `perf stat` for package-level power diagnostics and with any higher-level metric formulas that may reference PCU events. The file should remain consistent with adjacent Snow Ridge uncore files so model matching exposes a coherent set of PCU, iMC, and core events.

### Risks and Edge Cases
Because 25 of 26 events are experimental, encodings may be less stable than architectural events. Several names are terse and mirror internal hardware concepts, such as `UNC_P_TOTAL_TRANSITION_CYCLES` and `UNC_P_MEMORY_PHASE_SHEDDING_CYCLES`; incorrect user interpretation is likely without Intel documentation. The lack of `PublicDescription` on some records reduces discoverability in `perf list --details`. Power and thermal limit events can be zero on idle or unconstrained systems, which is expected and should not be treated as event failure.

### Test Signals
Syntax validation with `jq empty` and perf PMU table generation are baseline tests. On Snow Ridge hardware, `perf list` should show `UNC_P_CLOCKTICKS`, `UNC_P_FREQ_MAX_POWER_CYCLES`, `UNC_P_PROCHOT_INTERNAL_CYCLES`, and package residency events. Runtime checks should compare PCU clock ticks with residency/throttling events over idle and loaded intervals and confirm package-scoped aggregation rather than per-core duplication.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/snowridgex/uncore-power.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/snowridgex/virtual-memory.json -->
## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/snowridgex/virtual-memory.json

### Purpose
`virtual-memory.json` defines 31 Snow Ridge core PMU events for TLB and page-walk behavior. It covers load/store DTLB misses, STLB hits, page-walk completions by page size, page-walk pending cycles, EPT walk cache hits/misses, ITLB fills and misses, and retired memory uops that missed DTLB structures. The file is aimed at diagnosing virtual-memory translation overhead and virtualization translation costs.

### Important APIs, Types, and Fields
Entries use core PMU fields such as `EventName`, `EventCode`, `UMask`, `Counter`, `BriefDescription`, `PublicDescription`, and `SampleAfterValue`. All events use programmable counters `0,1,2,3`. Four events include `PEBS`, enabling precise sampling semantics for selected retired DTLB miss events. Three events include `Data_LA`, identifying events that can provide data linear address information. `SampleAfterValue` differs by event family and controls perf's default sampling period for profile-style use.

### Control Flow and Data Flow
Perf's build-time parser turns the JSON entries into named Snow Ridge core events. Runtime flow is name resolution to event selector and unit mask, followed by programming core PMU counters. Events such as `DTLB_LOAD_MISSES.WALK_COMPLETED_4K` and `DTLB_STORE_MISSES.WALK_PENDING` distinguish count-style and cycle/occupancy-style measurements; `EPT.*` records capture extended page-table walk cache behavior when virtualization is active.

### State and Persistence Behavior
The file stores no mutable state. Hardware counters track translation events during the measurement interval. PEBS-capable records can persist sample payloads in perf data files when profiling; that persistence is owned by perf output, not by this JSON. Events with page-size-specific masks should be interpreted as subsets of broader `WALK_COMPLETED` counters, subject to hardware semantics and possible overlap in faulting paths.

### Dependencies and Integration Points
The definitions depend on Snow Ridge core PMU support, perf's JSON event tooling, and PEBS/Data_LA handling in perf and the kernel. They integrate with memory and cache analysis workflows because TLB misses often explain L1/L2/L3 or offcore latency. Virtualization-related `EPT.*` names integrate with hypervisor and guest workload profiling.

### Risks and Edge Cases
Page-walk events include page walks that fault in several descriptions, so raw counts are not equivalent to successful translations. `WALK_PENDING` events count cycles or outstanding walk occupancy, not completed walks, and require denominator care. EPT events may be unavailable or flat zero on non-virtualized workloads. PEBS/Data_LA fields raise compatibility risk if kernel support for precise address sampling differs across systems.

### Test Signals
Tests should include JSON syntax validation and perf table generation. On supported Snow Ridge systems, `perf list` should expose DTLB, ITLB, and EPT names from this file. Runtime smoke tests can compare `DTLB_LOAD_MISSES.WALK_COMPLETED`, page-size-specific variants, and `DTLB_LOAD_MISSES.STLB_HIT` while running workloads with 4K and huge pages. PEBS tests should verify that precise sampling works for `MEM_UOPS_RETIRED.DTLB_MISS*` where supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/snowridgex/virtual-memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/tigerlake/cache.json -->
## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/tigerlake/cache.json

### Purpose
`cache.json` defines 68 Tiger Lake core PMU events for cache hierarchy, memory instruction retirement, offcore request flow, snoop outcomes, software prefetches, super queue pressure, and locked or split memory accesses. It provides the main event vocabulary for analyzing L1D/L2/L3 behavior and core-originated memory traffic on Tiger Lake.

### Important APIs, Types, and Fields
The event schema includes `EventName`, `EventCode`, `UMask`, `Counter`, `BriefDescription`, `PublicDescription`, and `SampleAfterValue`. Some records add `CounterMask`, `EdgeDetect`, `Data_LA`, `MSRIndex`, and `MSRValue`. There are 20 `Data_LA` events, mostly retired memory load/store and load-source events, enabling address-aware sampling. Three OCR events use `MSRIndex`/`MSRValue` to program offcore response filters. `L1D_PEND_MISS.FB_FULL_PERIODS` uses `CounterMask: 1` plus `EdgeDetect: 1`, so it counts periods rather than cycles.

### Control Flow and Data Flow
Perf ingests the JSON into Tiger Lake event tables. Runtime flow resolves event names such as `L2_RQSTS.DEMAND_DATA_RD_MISS`, `MEM_LOAD_RETIRED.L3_MISS`, or `OFFCORE_REQUESTS_OUTSTANDING.DEMAND_DATA_RD_GE_6`, then programs generic core counters or offcore filter MSRs as required. The file distinguishes request counts, hit/miss counts, outstanding occupancy, cycles with outstanding requests, and retired-load data source classification.

### State and Persistence Behavior
The JSON is static. Runtime state is in core PMU counters, offcore response MSRs, and optional perf samples with data linear addresses. Events with occupancy or cycles semantics must be normalized differently from simple request counts. Fixed hardware resources such as offcore response filter MSRs can constrain multiplexing when users request several OCR-filtered events together.

### Dependencies and Integration Points
The file depends on Tiger Lake model matching, perf's JSON generator, kernel PMU support for offcore response programming, and Data_LA sampling support. It integrates with `memory.json` latency events, `frontend.json` instruction-cache events, `pipeline.json` stall/topdown events, and metric groups that classify cache hits, cache misses, memory bandwidth, memory latency, snoop, and prefetch behavior.

### Risks and Edge Cases
Several event families have similar names but different semantics: `L2_RQSTS.*` counts L2 accesses, `MEM_LOAD_RETIRED.*` classifies retired load sources, and `OFFCORE_REQUESTS_OUTSTANDING.*` counts occupancy or cycles. Misusing them as interchangeable cache miss rates can produce incorrect analysis. OCR events require MSR filters and can conflict with other offcore events. Address sampling through `Data_LA` is hardware/kernel dependent. `LONGEST_LAT_CACHE.MISS` includes speculative and prefetch behavior, so it is not identical to retired load L3 misses.

### Test Signals
Use `jq empty`, PMU table generation, and `perf list` on Tiger Lake to confirm representative names. Runtime checks should exercise memory streaming and pointer-chasing workloads, comparing `MEM_LOAD_RETIRED.L1_HIT/L2_HIT/L3_MISS`, `L2_RQSTS.*`, and `OFFCORE_REQUESTS_OUTSTANDING.*`. OCR tests should verify that events with `MSRIndex`/`MSRValue` can be scheduled and that perf reports conflicts or multiplexing clearly when resources are exhausted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/tigerlake/cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/tigerlake/counter.json -->
## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/tigerlake/counter.json

### Purpose
`counter.json` is a Tiger Lake counter inventory file rather than an event list. It declares how many fixed and generic counters are available for each PMU unit known to the Tiger Lake perf event tables.

### Important APIs, Types, and Fields
The file is a JSON array of three objects. Each object has `Unit`, `CountersNumFixed`, and `CountersNumGeneric`. The entries declare `core` with 4 fixed and 8 generic counters, `ARB` with 0 fixed and 2 generic counters, and `CLOCK` with 1 fixed and 0 generic counters. Values are mostly strings, with one numeric fixed-counter value for `CLOCK`; consumers must tolerate both numeric and string representations if the broader perf schema permits them.

### Control Flow and Data Flow
During perf PMU event generation, this metadata informs counter availability for Tiger Lake units. It does not map event names to selectors. Runtime scheduling uses this inventory indirectly when perf determines whether a requested set of events can fit on hardware counters or must be multiplexed.

### State and Persistence Behavior
The file is static metadata and stores no runtime state. Its values affect scheduling assumptions but do not persist measurement data. Incorrect counts can create persistent user-visible behavior in generated perf tables, such as unexpected multiplexing or impossible scheduling constraints.

### Dependencies and Integration Points
The file depends on perf's architecture PMU metadata loader and must agree with Tiger Lake hardware and kernel PMU exposure. It integrates with all Tiger Lake event JSON files because event definitions reference `Counter` sets that assume the declared counter resources.

### Risks and Edge Cases
The mixed string/integer representation is a schema consistency risk for strict parsers. If a future tool assumes every file in this directory is an event list with `EventName`, it will fail on this metadata file. Counter counts must stay aligned with the model; overstating counters can cause generated tables to advertise combinations perf cannot schedule, while understating them can cause unnecessary multiplexing.

### Test Signals
Validate JSON syntax and run the perf PMU event generation path. A targeted schema test should confirm that counter metadata files are parsed separately from event arrays. On Tiger Lake, `perf stat` with more than eight programmable core events can confirm multiplexing behavior, while fixed events such as instructions and cycles should continue to schedule through fixed counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/tigerlake/counter.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/tigerlake/floating-point.json -->
## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/tigerlake/floating-point.json

### Purpose
`floating-point.json` defines 13 Tiger Lake core PMU events for floating-point assists and retired floating-point arithmetic instruction classes. It distinguishes scalar single/double, packed 128-bit, packed 256-bit, packed 512-bit, and aggregate scalar/vector/FLOP-width categories.

### Important APIs, Types, and Fields
Entries use `EventName`, `EventCode`, `UMask`, `Counter`, `BriefDescription`, `PublicDescription`, and `SampleAfterValue`. All events can use generic counters `0,1,2,3,4,5,6,7`. The core event family is `FP_ARITH_INST_RETIRED.*`, with aggregation aliases such as `FP_ARITH_INST_RETIRED.SCALAR`, `VECTOR`, `4_FLOPS`, and `8_FLOPS`. `ASSISTS.FP` captures floating-point hardware assists and is a different diagnostic signal from retired arithmetic counts.

### Control Flow and Data Flow
Perf parses the file into Tiger Lake event tables. At runtime, named events program core PMU selectors and unit masks, then count retired FP instruction categories or assist occurrences. Aggregate masks allow users to request broad scalar/vector groups without combining many separate events manually.

### State and Persistence Behavior
The file is static. Hardware counters accumulate events during measurement. Retired instruction class events count instructions or categories, not necessarily mathematical operations unless the specific aggregate mask is documented as FLOP-oriented; users computing FLOP rates must apply the correct width semantics and denominator.

### Dependencies and Integration Points
The file depends on Tiger Lake core PMU support and perf's JSON event loader. It integrates with metric groups such as `Flops`, `FpScalar`, `FpVector`, and `Compute`, and with pipeline events such as divider activity or vector-width mismatch when diagnosing FP-heavy workloads.

### Risks and Edge Cases
Tiger Lake exposes 512-bit FP event categories even though actual instruction availability and frequency behavior may vary by SKU and instruction set support. Aggregate names can be misinterpreted as exact FLOP counts without accounting for vector width and instruction type. Assist counts may be rare but important; zero counts are normal for well-behaved FP code.

### Test Signals
Validate syntax and generated tables, then check `perf list` for `FP_ARITH_INST_RETIRED.*`. Runtime tests should run scalar and vector FP kernels and compare scalar, 128-bit, 256-bit, and aggregate vector counters. A denormal or exception-heavy FP workload can be used to see whether `ASSISTS.FP` increments on supported systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/tigerlake/floating-point.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/tigerlake/frontend.json -->
## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/tigerlake/frontend.json

### Purpose
`frontend.json` defines 39 Tiger Lake events for instruction fetch, decode, uop-cache delivery, microcode sequencer delivery, frontend latency, and frontend bandwidth limitations. It supports analysis of DSB-to-MITE switches, instruction cache misses and stalls, ITLB/STLB frontend misses, IDQ delivery source, and cycles where the frontend delivered too few uops.

### Important APIs, Types, and Fields
The event records use standard core PMU fields plus `CounterMask`, `EdgeDetect`, `Invert`, `MSRIndex`, and `MSRValue`. Seventeen `FRONTEND_RETIRED.*` events use MSR programming to configure frontend-retired latency or miss filters. `DSB2MITE_SWITCHES.COUNT` and `IDQ.MS_SWITCHES` use edge detection to count transitions rather than level cycles. `IDQ_UOPS_NOT_DELIVERED.CYCLES_FE_WAS_OK` uses `Invert: 1`, changing the comparison semantics for the counter mask.

### Control Flow and Data Flow
The file is converted into Tiger Lake event tables by perf tooling. Runtime event resolution programs the core PMU and, for frontend-retired events, auxiliary MSR filter values. Data flows from hardware frontend structures into counters representing delivered uops, stall cycles, or retired instructions that experienced a particular frontend problem. The latency threshold family `FRONTEND_RETIRED.LATENCY_GE_*` provides several cutoffs from 1 through 512 cycles.

### State and Persistence Behavior
No file-local state exists. Hardware counters collect over the measurement interval. MSR-filtered frontend events may be constrained by shared filter resources and can interact with scheduling/multiplexing. Threshold counters can overlap by design; for example, an instruction meeting a 128-cycle threshold also meets lower thresholds depending on hardware semantics, so users should not sum them as disjoint buckets.

### Dependencies and Integration Points
The file depends on Tiger Lake frontend PMU encodings and perf support for MSR-based event filters. It integrates with topdown metrics for frontend bound analysis, with `cache.json` instruction cache and memory hierarchy events, and with `pipeline.json` IDQ/uop delivery and machine-clear events.

### Risks and Edge Cases
MSR-filtered events can fail to schedule with other filter-heavy events or produce confusing multiplexing. Edge-detected switch events differ from cycle-count events with similar names. Threshold latency events are easy to overcount if treated as mutually exclusive. Some descriptions refer to aliases, such as `DECODE.LCP` mirroring `ILD_STALL.LCP`, so duplicate use can double-count the same underlying signal.

### Test Signals
Baseline tests are JSON validation, PMU event generation, and `perf list` visibility. Runtime checks should compare `IDQ.DSB_UOPS`, `IDQ.MITE_UOPS`, and `IDQ.MS_UOPS` under code-cache-friendly and decode-heavy workloads. Branchy or large-code-footprint workloads should raise selected `FRONTEND_RETIRED.*` miss or latency counters. Scheduling tests should request multiple MSR-filtered frontend events and verify perf handles constraints predictably.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/tigerlake/frontend.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/tigerlake/memory.json -->
## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/tigerlake/memory.json

### Purpose
`memory.json` defines 23 Tiger Lake events for memory latency, L3-miss stalls, memory-ordering machine clears, TSX/RTM transactional behavior, and transaction abort causes. It complements `cache.json` by focusing on latency thresholds and transactional memory failure modes rather than broad cache hierarchy request counts.

### Important APIs, Types, and Fields
The file uses `EventName`, `EventCode`, `UMask`, `Counter`, `BriefDescription`, `SampleAfterValue`, and optional `PublicDescription`. It includes `CounterMask` for `CYCLE_ACTIVITY.STALLS_L3_MISS`, `Data_LA` for eight `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_*` events, and `MSRIndex`/`MSRValue` for those same load-latency threshold events. Transactional events include `RTM_RETIRED.*`, `TX_EXEC.*`, and `TX_MEM.*` families.

### Control Flow and Data Flow
Perf turns these definitions into named Tiger Lake events. Runtime flow resolves threshold names such as `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_128`, programs the core PMU and latency threshold MSR, and optionally records data linear addresses for sampled loads. TSX events count transaction starts, commits, aborts, and abort categories.

### State and Persistence Behavior
The JSON stores only definitions. Hardware PMU state tracks counts during a measurement. Load-latency events with `Data_LA` can lead to address samples in perf output. TSX counters reflect architectural transaction behavior, and on systems where TSX is disabled or unavailable, they may be unsupported or always zero.

### Dependencies and Integration Points
The file depends on Tiger Lake PMU support for precise memory latency thresholds and TSX event encodings. It integrates with `cache.json` load-source events, `pipeline.json` stall and machine-clear counters, and topdown memory latency groups in `metricgroups.json`.

### Risks and Edge Cases
Latency threshold events are not disjoint buckets; a load above 512 cycles also satisfies lower thresholds. MSR threshold programming can conflict with other events that use the same filter mechanism. TSX availability varies by microcode, BIOS policy, and kernel mitigations, so TSX events can be present in tables but not meaningful on a given machine. `MACHINE_CLEARS.MEMORY_ORDERING` is a pipeline recovery signal, not a direct memory bandwidth metric.

### Test Signals
Validate JSON and generated event tables. On Tiger Lake hardware, `perf list` should expose load-latency threshold events and TSX families. Runtime tests should use pointer-chasing or cache-miss workloads to observe monotonic threshold behavior across `LOAD_LATENCY_GT_*`. Transactional tests require a TSX-enabled system and should compare `RTM_RETIRED.START`, `COMMIT`, and abort categories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/tigerlake/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/tigerlake/metricgroups.json -->
## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/tigerlake/metricgroups.json

### Purpose
`metricgroups.json` defines the named metric-group taxonomy for Tiger Lake. Unlike event files, it is a JSON object with 138 key/value pairs mapping group names to descriptions. The groups classify metrics for topdown analysis, frontend/backend breakdowns, cache and memory analysis, branch behavior, floating point, power, SMT, server/client concerns, and issue-oriented TMA categories.

### Important APIs, Types, and Fields
The API is an object map rather than an array of event records. Keys are metric group identifiers such as `Backend`, `Frontend`, `CacheMisses`, `MemoryBW`, `TopdownL1`, `tma_backend_bound_group`, and `tma_issueTLB`. Values are human-readable descriptions, commonly "Grouping from Top-down Microarchitecture Analysis Metrics spreadsheet" or "Metrics contributing to ..." a TMA category. The schema has no `EventName`, `EventCode`, or `UMask`.

### Control Flow and Data Flow
Build-time perf tooling reads the object and attaches descriptions to metric groups used by Tiger Lake metric definitions elsewhere. Runtime users encounter these strings through `perf list --metricgroups`, `perf stat -M`, or metric browsing. The data flow is from group key to display/filter taxonomy; it does not program hardware counters directly.

### State and Persistence Behavior
The file is static taxonomy metadata. It holds no runtime state and does not persist measurements. Changes affect user-facing grouping and discoverability of metrics, not raw event encodings.

### Dependencies and Integration Points
The file depends on perf's metric group parser accepting object maps. It must stay in sync with Tiger Lake metric definitions that reference these group names. It integrates with all Tiger Lake event files indirectly by organizing derived metrics over frontend, backend, memory, branch, cache, FP, and topdown event formulas.

### Risks and Edge Cases
Tools that assume every JSON file in the architecture directory is an array of event records will fail on this object-shaped file. Renaming a group breaks references from metric definitions and user workflows using `perf stat -M` group filters. The coexistence of legacy-style names (`TopdownL1`) and lower-case TMA group names (`tma_L1_group`) requires preserving exact spelling. Duplicate or near-duplicate categories can confuse users but may be intentional for compatibility.

### Test Signals
Run `jq type` and verify it is `object`, then run perf's PMU/metric generation. `perf list --metricgroups` on a build with Tiger Lake metrics should show representative groups including `Frontend`, `Backend`, `MemoryBound`, `TopdownL1`, and `tma_backend_bound_group`. A reference-integrity check should ensure every group named by metric definitions exists in this map.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/tigerlake/metricgroups.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/tigerlake/other.json -->
## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/tigerlake/other.json

### Purpose
`other.json` holds four Tiger Lake events that do not fit cleanly into the neighboring cache, memory, frontend, FP, or pipeline files. They cover core power turbo-license levels and a streaming write offcore-response event.

### Important APIs, Types, and Fields
The file uses the same event schema as other Tiger Lake event arrays: `EventName`, `EventCode`, `UMask`, `Counter`, `BriefDescription`, `PublicDescription`, and `SampleAfterValue`. `CORE_POWER.LVL0_TURBO_LICENSE`, `CORE_POWER.LVL1_TURBO_LICENSE`, and `CORE_POWER.LVL2_TURBO_LICENSE` use event code `0x28` with different unit masks. `OCR.STREAMING_WR.ANY_RESPONSE` uses `MSRIndex`/`MSRValue`, so it depends on offcore response filter programming.

### Control Flow and Data Flow
Perf parses these entries into the Tiger Lake event table. Runtime users can request turbo-license cycle events to understand power/frequency license residency, or the OCR streaming write event to count matching offcore responses. The OCR record follows the same MSR-filtered data path as offcore events in `cache.json`.

### State and Persistence Behavior
The file stores static definitions only. Runtime state is hardware counter state over the measurement interval. Turbo license events represent cycles in license levels, while the OCR event represents filtered response counts; they should not be aggregated without clear normalization.

### Dependencies and Integration Points
The file depends on Tiger Lake core PMU support and, for OCR, kernel/perf support for programming offcore response MSRs. It integrates with power-oriented metric groups and with offcore/cache analysis when streaming writes matter.

### Risks and Edge Cases
The file's catch-all name can hide important event ownership; maintainers may accidentally duplicate events in more specific files. OCR resource conflicts are possible when combined with other offcore-filtered events. Turbo-license counters can be workload-, SKU-, and firmware-dependent, so zero or skewed residency may be normal.

### Test Signals
Validate JSON syntax and generated event tables. `perf list` should expose the three `CORE_POWER.*TURBO_LICENSE` events and `OCR.STREAMING_WR.ANY_RESPONSE`. Runtime tests can compare turbo-license cycles under scalar, AVX, and idle workloads, and separately verify the OCR event schedules with other offcore events or reports constraints cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/tigerlake/other.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/tigerlake/pipeline.json -->
## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/tigerlake/pipeline.json

### Purpose
`pipeline.json` defines 96 Tiger Lake core PMU events for execution pipeline behavior. It covers arithmetic divider use, assists, retired branch and mispredict classes, unhalted cycles, cycle activity stalls, execution port utilization, instruction decode/retirement, recovery cycles, load/store blocking, LSD activity, machine clears, resource stalls, reservation-station empty cycles, topdown slots, uops decoded/dispatched/executed/issued/retired, and fixed-counter architectural events.

### Important APIs, Types, and Fields
The event array uses `EventName`, `EventCode`, `UMask`, `Counter`, `BriefDescription`, `PublicDescription`, and `SampleAfterValue`. Several records add `CounterMask`, `EdgeDetect`, and `Invert`. Fixed-counter events include `INST_RETIRED.ANY`, `INST_RETIRED.PREC_DIST`, `CPU_CLK_UNHALTED.THREAD`, and `CPU_CLK_UNHALTED.REF_TSC`; programmable counterparts include `INST_RETIRED.ANY_P` and `CPU_CLK_UNHALTED.THREAD_P`. Topdown events include `TOPDOWN.SLOTS`, `TOPDOWN.SLOTS_P`, and `TOPDOWN.BACKEND_BOUND_SLOTS`. Port utilization events encode dispatch to port groups such as `PORT_0`, `PORT_2_3`, and `PORT_7_8`.

### Control Flow and Data Flow
Perf builds these records into Tiger Lake core event tables. Runtime event resolution programs fixed or generic counters depending on the `Counter` field. Data flows from core pipeline structures to counters that represent retired instruction classes, cycles meeting a stall condition, edge-detected clears, uop movement between pipeline stages, and topdown slot accounting.

### State and Persistence Behavior
The JSON is immutable metadata. Runtime state lives in PMU counters and optional perf data. Fixed-counter events preserve generic counters for other events; using programmable aliases can change scheduling pressure. Inverted counter-mask events such as `UOPS_EXECUTED.STALL_CYCLES`, `UOPS_ISSUED.STALL_CYCLES`, and `UOPS_RETIRED.STALL_CYCLES` count cycles where the condition is not met, so users must interpret them carefully.

### Dependencies and Integration Points
The file depends on Tiger Lake core PMU encodings and perf support for fixed counters, topdown slots, counter masks, edge detection, and inverted comparisons. It integrates heavily with Tiger Lake metric groups for `Pipeline`, `Retire`, `BadSpec`, `Backend`, `PortsUtil`, `Branches`, `MachineClears`, `LSD`, and topdown TMA categories. It also pairs with `frontend.json` and `memory.json` to explain whether pipeline stalls are frontend-, backend-, memory-, branch-, or recovery-driven.

### Risks and Edge Cases
Counter-mask and invert semantics are easy to misread as simple event counts. Fixed and programmable aliases for instructions and cycles can double-count if used together without intent. Some branch and recovery events count retired outcomes while others count cycles or edge transitions, so derived rates need compatible denominators. Topdown slot events are foundational for metric formulas; incorrect encodings would cascade into many derived metrics. Events with broad names such as `ASSISTS.ANY` or `RESOURCE_STALLS.SCOREBOARD` require hardware documentation for precise interpretation.

### Test Signals
Run JSON syntax validation and perf event-table generation. On Tiger Lake, `perf list` should show fixed-counter, topdown, branch, port, and uop events from this file. Runtime tests should compare `INST_RETIRED.ANY` versus `INST_RETIRED.ANY_P`, fixed and programmable cycle events, and topdown slot metrics. Branch-heavy, divide-heavy, memory-stall, and port-pressure microbenchmarks can validate that representative families move in expected directions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/tigerlake/pipeline.json -->
