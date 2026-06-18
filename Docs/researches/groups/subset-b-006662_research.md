# subset-b-006662 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/emeraldrapids/uncore-memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/emeraldrapids/uncore-memory.json

## Purpose

`uncore-memory.json` is the Emerald Rapids uncore memory PMU catalog for perf. It contains 403 package-level memory events split across `iMC`, `MCHBM`, and `M2HBM` units, covering integrated memory-controller traffic, HBM controller traffic, directory/coherency behavior, queues, tracker occupancy, prefetch CAM behavior, power-management memory states, ECC, refresh, precharge, and PMM-side queues. The file is data, not executable code, but it is a central input to perf's generated event tables.

## Important APIs, Types, and Data Fields

The file is a JSON array of event objects. Common fields are `EventName`, `EventCode`, `UMask`, `Counter`, `Unit`, `PerPkg`, `BriefDescription`, `PublicDescription`, and optional qualifiers such as `Experimental`, `FCMask`, and `PortMask`. `Unit` is the PMU selector: 161 events use `iMC`, 67 use `MCHBM`, and 175 use `M2HBM`. Most events are programmable on counters `0,1,2,3`.

Major event families include `UNC_M_CAS_COUNT.*`, `UNC_M_ACT_COUNT.*`, `UNC_M_PRE_COUNT.*`, `UNC_M_DRAM_REFRESH.*`, `UNC_M_POWER_*`, `UNC_M_RDB_*`, `UNC_M_RPQ_*`, `UNC_M_WPQ_*`, `UNC_M_SB_*`, `UNC_M_PMM_*`, `UNC_MCHBM_CAS_COUNT.*`, `UNC_MCHBM_ACT_COUNT.*`, `UNC_MCHBM_PRE_COUNT.*`, `UNC_M2HBM_IMC_READS.*`, `UNC_M2HBM_IMC_WRITES.*`, `UNC_M2HBM_DIRECTORY_*`, `UNC_M2HBM_DIRECT2CORE_*`, `UNC_M2HBM_DIRECT2UPI_*`, `UNC_M2HBM_PREFCAM_*`, `UNC_M2HBM_TRACKER_*`, and `UNC_M2HBM_WR_TRACKER_*`.

## Control Flow and Data Flow

There is no local control flow. Perf PMU tooling parses this JSON, generates architecture-specific event aliases, and maps selected aliases to uncore PMU event encodings at runtime. The data flow is from static JSON rows into perf list/stat metadata, then into programmed uncore counters on the selected package. `PerPkg` marks these as package-scoped measurements rather than thread-local core events.

The families form analysis flows: CAS and request counters estimate read/write bandwidth; ACT/PRE/page-policy counters describe DRAM/HBM row behavior; RPQ/WPQ/RDB/SB queues expose pressure and occupancy; directory and direct-to-core/direct-to-UPI events expose HBM coherency routing; PMM and power rows describe persistent-memory and memory power-management side effects.

## State and Persistence Behavior

The only persistent state is the static event metadata in the repository. Runtime counter values are produced by perf sessions and are not stored here. Occupancy and cycle events represent time-integrated hardware states, while insert/count events represent transactions. Experimental rows persist as event aliases but should be treated as less stable contracts. `PerPkg` and `Unit` are important persistence semantics because they determine aggregation boundaries and PMU instance selection.

## Dependencies and Integration Points

This file depends on Emerald Rapids uncore PMU support in the Linux perf tooling and kernel PMU drivers. It integrates with `perf list`, `perf stat`, memory bandwidth diagnostics, HBM/DRAM balancing analysis, coherency routing investigations, PMM queue analysis, and platform power/thermal studies. It complements `uncore-power.json` by exposing memory-side power states and complements core cache/TLB events by measuring controller and fabric behavior after requests leave the core.

## Risks and Edge Cases

The largest risk is semantic misaggregation: package-level uncore counts include all cores and processes on a package, not just the profiled task. Counters in different units cannot be freely summed without understanding topology. Occupancy/cycle events and transaction events use different units and should not be mixed as raw counts. HBM and DRAM names are similar but refer to different PMU units. Many `M2HBM` rows are marked `Experimental`, so downstream tests should tolerate platform or kernel support gaps. Events using `FCMask` or `PortMask` depend on perf preserving the mask fields exactly. Bandwidth conversions from CAS/read/write events need the correct transaction width and channel interpretation.

## Test Signals

Useful validation starts with JSON parse success and generated perf event-table build success. Runtime smoke tests should verify `perf list` exposes `iMC`, `MCHBM`, and `M2HBM` aliases on matching Emerald Rapids systems. Streaming read/write workloads should move CAS, read, and write counters; random-access workloads should affect activation/precharge and queue-pressure rows; HBM-capable workloads should move `MCHBM`/`M2HBM` counters; power-management scenarios should affect `UNC_M_POWER_*`; and idle baselines should keep transaction counters low while clocktick counters advance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/emeraldrapids/uncore-memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/emeraldrapids/uncore-power.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/emeraldrapids/uncore-power.json

## Purpose

`uncore-power.json` defines 25 Emerald Rapids PCU uncore power events for package clocking, C-state residency, core occupancy by power state, frequency clipping, thermal and power throttling, phase shedding, PROCHOT, voltage-regulator hot cycles, and frequency/C-state transitions. It gives perf package-level visibility into the platform control unit rather than core-local execution.

## Important APIs, Types, and Data Fields

The JSON entries use `EventName`, `EventCode`, `Counter`, `Unit`, `PerPkg`, `BriefDescription`, optional `PublicDescription`, and frequent `Experimental` flags. All rows use `Unit: PCU` and `PerPkg: 1`. Most rows allow counters `0,1,2,3`; `UNC_P_PMAX_THROTTLED_CYCLES` is restricted to counter `0`.

Important families are `UNC_P_CLOCKTICKS`, `UNC_P_PKG_RESIDENCY_*`, `UNC_P_POWER_STATE_OCCUPANCY_CORES_*`, `UNC_P_FREQ_*`, `UNC_P_FIVR_PS_*`, `UNC_P_MEMORY_PHASE_SHEDDING_CYCLES`, `UNC_P_PROCHOT_*`, `UNC_P_VR_HOT_CYCLES`, and transition/demotion events.

## Control Flow and Data Flow

There is no executable flow in the file. Perf ingests the rows as PCU PMU aliases, then programs package-level PCU counters for selected events. Users typically compare clockticks to residency, occupancy, and throttling-cycle events to identify whether performance is limited by idle residency, power limits, thermal limits, AVX frequency clipping, voltage-regulator limits, or transition overhead.

## State and Persistence Behavior

The file persists event encodings and package-scope metadata only. Runtime residency and throttling counters persist only for the measurement interval. Several rows describe cycles in a state, while occupancy rows count number of cores in a C-state over time; those values need normalization by elapsed PCU clock cycles to become percentages or averages.

## Dependencies and Integration Points

This catalog depends on Emerald Rapids PCU uncore PMU support in perf and the kernel. It integrates with power tuning, thermal diagnostics, AVX workload analysis, idle-state validation, memory phase-shedding investigations, and package-level performance analysis. It pairs naturally with core frequency metrics, RAPL/power telemetry, and `uncore-memory.json` memory power-state rows.

## Risks and Edge Cases

Most entries are marked `Experimental`, so availability and semantics may vary across steppings, firmware, or kernel support. Package-level PCU counters include all cores and system activity on the package. Cycle counts do not directly equal percentages without an appropriate denominator. Occupancy counters may require thresholding or normalization to derive average core counts. Counter restriction on `UNC_P_PMAX_THROTTLED_CYCLES` can create scheduling conflicts with other PCU events.

## Test Signals

Validation should include JSON parsing, generated perf table success, and `perf list` exposure of PCU aliases. Idle and busy workloads should change package residency and core C0 occupancy. AVX-heavy workloads should be checked against AVX frequency clipping rows. Thermal or power-limited stress tests should move thermal, power, PROCHOT, and VR-hot counters when the platform allows safe observation. Counter scheduling tests should verify the counter-0-only row is handled correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/emeraldrapids/uncore-power.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/emeraldrapids/virtual-memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/emeraldrapids/virtual-memory.json

## Purpose

`virtual-memory.json` defines 20 Emerald Rapids core PMU events for data and instruction TLB misses, second-level TLB hits, page-walk completions by page size, page-walk active cycles, and outstanding page-walk pressure. It supports perf analysis of translation overhead for loads, stores, and instruction fetches.

## Important APIs, Types, and Data Fields

The file is a JSON event array using `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, `PublicDescription`, and optional `CounterMask`. Event families are `DTLB_LOAD_MISSES.*`, `DTLB_STORE_MISSES.*`, and `ITLB_MISSES.*`. Load and store families include `STLB_HIT`, `WALK_ACTIVE`, `WALK_COMPLETED`, `WALK_COMPLETED_1G`, `WALK_COMPLETED_2M_4M`, `WALK_COMPLETED_4K`, and `WALK_PENDING`. ITLB has the same shape except no 1G-specific completion row. `WALK_ACTIVE` rows use `CounterMask: 1`.

## Control Flow and Data Flow

Perf parses the metadata into event aliases and programs core counters when users request those aliases. At runtime, STLB-hit rows count first-level TLB misses resolved by the second-level TLB, walk-completed rows count misses that trigger completed page walks, walk-active rows count cycles with at least one busy page miss handler, and walk-pending rows count outstanding walks per cycle. Data flows from CPU translation hardware into perf samples or counts.

## State and Persistence Behavior

The file stores only static event definitions and default sampling periods. It does not store TLB contents, page tables, address mappings, or samples. Counters are per-core PMU events, so measured state is interval-local and workload/scheduling dependent.

## Dependencies and Integration Points

The definitions depend on Emerald Rapids core PMU event encodings and perf's x86 PMU event-table generator. They integrate with `perf stat`, `perf record`, page-size tuning, huge-page validation, TLB miss analysis, instruction-cache/front-end investigations, and memory-latency studies. The rows complement cache and uncore-memory catalogs by explaining translation cost before memory requests reach cache or memory-controller analysis.

## Risks and Edge Cases

`WALK_ACTIVE` and `WALK_PENDING` share the same event/umask shape but differ by counter-mask semantics, so generated metadata must preserve `CounterMask`. Walk-completed counts and walk-active cycles are different units. Page-size-specific rows should not be interpreted as interchangeable; 4K, 2M/4M, and 1G rows signal different mappings. Page walks can complete with or without a fault according to the descriptions. ITLB and DTLB events are separate and need workload-specific interpretation.

## Test Signals

Validation should include JSON parsing, perf event generation, and `perf list` visibility for all three families. Random-access memory workloads should increase DTLB load/store walk counters. Huge-page workloads should shift counts from 4K toward large-page rows. Code-footprint or branch-heavy instruction-fetch workloads should exercise ITLB events. Tests should check that `WALK_ACTIVE` produces cycle-like behavior while `WALK_COMPLETED` produces event counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/emeraldrapids/virtual-memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/goldmont/cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/goldmont/cache.json

## Purpose

`cache.json` defines 103 Goldmont core PMU events for cache behavior, retired memory uops, L1/L2 hits and misses, dirty evictions, fetch stalls caused by I-cache fill, L2 queue rejection, and a large offcore-response matrix. It is the main Goldmont perf catalog for cache hierarchy and offcore memory-response analysis.

## Important APIs, Types, and Data Fields

Entries use `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, `PublicDescription`, and optional `PEBS`, `Data_LA`, `MSRIndex`, and `MSRValue`. Families include `LONGEST_LAT_CACHE.*`, `MEM_LOAD_UOPS_RETIRED.*`, `MEM_UOPS_RETIRED.*`, `OFFCORE_RESPONSE.*`, `DL1.DIRTY_EVICTION`, `FETCH_STALL.ICACHE_FILL_PENDING_CYCLES`, `CORE_REJECT_L2Q.ALL`, and `L2_REJECT_XQ.ALL`.

The 83 `OFFCORE_RESPONSE.*` rows are notable because they use `MSR_OFFCORE_RESP` programming through `MSRIndex` values such as `0x1a6,0x1a7` and detailed `MSRValue` filters. Retired load/uop rows are precise-capable (`PEBS: 2`) and mark load-address support with `Data_LA: 1`.

## Control Flow and Data Flow

The file has no executable control flow. Perf tooling translates the JSON rows into Goldmont event aliases. For normal cache and retired-uop rows, perf programs core event select/umask counters. For offcore-response rows, perf also writes the offcore response MSR filter to select request types and response categories such as L2 hit, L2 miss, HITM from another core, snoop miss, outstanding demand data reads, RFOs, code reads, prefetches, streaming stores, and bus locks.

## State and Persistence Behavior

Static event definitions are persistent in the source tree; runtime counter values and PEBS samples are session-local. Offcore rows have hidden state in the programmed MSR filter during the perf session. Precise retired-memory rows can produce sampled data-address records when the kernel and CPU support PEBS with data linear address.

## Dependencies and Integration Points

The catalog depends on Goldmont core PMU support, PEBS support for precise rows, and kernel support for programming offcore-response MSRs. It integrates with perf cache analysis, memory-load latency and source analysis, false-sharing/HITM studies, non-temporal and streaming-store analysis, prefetch efficiency studies, front-end fetch-stall diagnosis, and lock/split-lock investigations.

## Risks and Edge Cases

Offcore-response rows are sensitive to correct `MSRIndex`/`MSRValue` handling; losing those fields changes the event meaning completely. Some rows can use both offcore MSRs, while `COREWB` and `OUTSTANDING` rows list only `0x1a6`; scheduling may be constrained. PEBS rows require hardware/kernel support and may fail or degrade to counting only on unsupported setups. `LONGEST_LAT_CACHE` counts L2-oriented requests on Goldmont and should not be assumed to match larger-core LLC semantics. `FETCH_STALL.ICACHE_FILL_PENDING_CYCLES` belongs in this cache file but measures front-end stall cycles.

## Test Signals

Validation should include JSON parsing, perf table generation, and `perf list` checks for normal, PEBS, and offcore aliases. Cache-resident versus streaming workloads should separate L1/L2 hit and miss counts. Cross-core sharing tests should move HITM offcore rows. Non-temporal store workloads should exercise streaming-store rows. PEBS smoke tests should confirm precise sampling and data-address capture for `MEM_LOAD_UOPS_RETIRED.*` where supported. Offcore tests should verify MSR filters are programmed and restored correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/goldmont/cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/goldmont/counter.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/goldmont/counter.json

## Purpose

`counter.json` records Goldmont PMU counter topology. It declares that the `core` PMU has 3 fixed counters and 4 generic programmable counters.

## Important APIs, Types, and Data Fields

The file is a one-object JSON array with `Unit: core`, `CountersNumFixed: 3`, and `CountersNumGeneric: 4`. Unlike event catalogs, it has no `EventName`, `EventCode`, `UMask`, or descriptions.

## Control Flow and Data Flow

There is no control flow. Perf metadata generation reads this file as capability data for the Goldmont core PMU. The values inform scheduling, grouping, multiplexing decisions, and validation of event counter availability.

## State and Persistence Behavior

The file persists static PMU topology only. It does not track active counters, current values, or runtime scheduling state. Runtime perf sessions use the values as constraints but store measurements elsewhere.

## Dependencies and Integration Points

This metadata depends on the Goldmont PMU architecture and integrates with the rest of the Goldmont event files in this directory. It is relevant to perf event scheduling and to tests that assert how many events can be measured concurrently without multiplexing.

## Risks and Edge Cases

The absence of event rows is intentional; tools must not require `EventName` for counter-topology files. If the fixed/generic counts are wrong, perf may overpromise grouping or unnecessarily multiplex events. Consumers should parse the numeric strings as counts and associate them with `Unit: core`.

## Test Signals

Validation should include JSON parsing, schema compatibility for counter files, and perf scheduling tests that can place up to four generic core events plus fixed-counter events according to Goldmont capabilities. Regression tests should ensure event-list generators do not try to display this object as a normal PMU event.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/goldmont/counter.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/goldmont/floating-point.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/goldmont/floating-point.json

## Purpose

`floating-point.json` defines 3 Goldmont core PMU events for floating-point divide pressure and floating-point assists. It lets perf distinguish cycles where the FP divide unit is busy, retired FP divide uops, and pipeline clears caused by FP assists such as denormal handling.

## Important APIs, Types, and Data Fields

The entries use `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, `PublicDescription`, and optional `PEBS`. Events are `CYCLES_DIV_BUSY.FPDIV`, `UOPS_RETIRED.FPDIV`, and `MACHINE_CLEARS.FP_ASSIST`. `UOPS_RETIRED.FPDIV` is precise-capable with `PEBS: 2`; all rows can use counters `0,1,2,3`.

## Control Flow and Data Flow

Perf parses these rows into event aliases and programs Goldmont core counters. Runtime data distinguishes divider occupancy cycles from retired divide instructions and exceptional assist behavior. The assist row counts machine clears caused by FP operations that need microcode or pipeline replay to produce architecturally correct results.

## State and Persistence Behavior

The file stores only static metadata and default sampling periods. Runtime counts and PEBS records are session-local. The precise retired-uop row may persist richer sample records through perf output files, but not through this JSON.

## Dependencies and Integration Points

These events depend on Goldmont core PMU and PEBS support. They integrate with floating-point performance tuning, denormal/assist diagnosis, top-down pipeline-clear analysis, and perf record/stat workflows. They complement generic uop and machine-clear catalogs by focusing on FP-specific causes.

## Risks and Edge Cases

Divider-busy cycles and retired divide uops answer different questions; high busy cycles may indicate long-latency divides even if retired divide count is modest. FP assists are data-dependent and can be rare unless inputs trigger denormals or other assisted cases. PEBS availability for `UOPS_RETIRED.FPDIV` depends on kernel and hardware support.

## Test Signals

Validation should include JSON parsing and perf alias visibility. Microbenchmarks with repeated floating-point divides should increase divide busy cycles and retired divide uops. Denormal-heavy or assist-triggering workloads should move `MACHINE_CLEARS.FP_ASSIST`. PEBS tests should verify precise sampling for retired FP divides where supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/goldmont/floating-point.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/goldmont/frontend.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/goldmont/frontend.json

## Purpose

`frontend.json` defines 8 Goldmont front-end PMU events for branch-address clears, predecode length prediction problems, instruction-cache line access/hit/miss accounting, and microcode sequencer entries. It supports diagnosis of instruction delivery and front-end speculation issues.

## Important APIs, Types, and Data Fields

Rows use `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, and `PublicDescription`. Event groups are `BACLEARS.ALL`, `BACLEARS.COND`, `BACLEARS.RETURN`, `DECODE_RESTRICTION.PREDECODE_WRONG`, `ICACHE.ACCESSES`, `ICACHE.HIT`, `ICACHE.MISSES`, and `MS_DECODED.MS_ENTRY`.

The `ICACHE.*` descriptions explicitly warn that Goldmont counts instruction-cache line references differently from Intel processors based on Silvermont microarchitecture. `MS_DECODED.MS_ENTRY` counts starts of microcode sequencer flows rather than every uop read from MSROM.

## Control Flow and Data Flow

There is no executable flow. Perf loads the aliases and programs core PMU counters. Runtime data flows from branch prediction, predecode, I-cache, and microcode-sequencer hardware into perf counts. The branch-address clear rows split total BACLEARs into conditional and return subcategories.

## State and Persistence Behavior

The file persists static event metadata and default sample periods only. Runtime counts are per-core and session-local. Speculative front-end activity can be counted before later machine clears or branch recovery, especially for microcode sequencer starts.

## Dependencies and Integration Points

These definitions depend on Goldmont front-end PMU encodings and integrate with perf front-end analysis, branch prediction studies, instruction-cache locality tuning, and microcoded-instruction diagnosis. They complement `cache.json`, which has `FETCH_STALL.ICACHE_FILL_PENDING_CYCLES`, and `other.json`, which has broader fetch-stall and ITLB-related stall counters.

## Risks and Edge Cases

The I-cache accounting model is Goldmont-specific and should not be compared blindly to Silvermont or larger-core Intel CPUs. `MS_DECODED.MS_ENTRY` is not a retired-uop count and may include speculative flows. BACLEAR subevents may overlap conceptually with broader branch-misprediction metrics outside this file, so ratios need careful denominators.

## Test Signals

Validation should include JSON parsing, perf list exposure, and front-end workload tests. Large instruction-footprint workloads should increase I-cache misses. Branch-heavy tests should affect BACLEAR rows. Workloads with microcoded instructions or fault/assist paths should affect `MS_DECODED.MS_ENTRY`. Tests should compare `ICACHE.ACCESSES`, `ICACHE.HIT`, and `ICACHE.MISSES` for plausible relationships without assuming exact additive behavior across architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/goldmont/frontend.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/goldmont/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/goldmont/memory.json

## Purpose

`memory.json` defines 3 Goldmont core PMU events for memory-ordering machine clears and page-split retired memory operations. It focuses on correctness and alignment pathologies rather than general cache hit/miss behavior.

## Important APIs, Types, and Data Fields

Rows use `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, `PublicDescription`, and optional `PEBS`. Events are `MACHINE_CLEARS.MEMORY_ORDERING`, `MISALIGN_MEM_REF.LOAD_PAGE_SPLIT`, and `MISALIGN_MEM_REF.STORE_PAGE_SPLIT`. The load and store page-split events are precise-capable (`PEBS: 2`).

## Control Flow and Data Flow

Perf converts the rows into Goldmont event aliases and programs core PMU counters. Runtime data distinguishes machine clears caused by uncertain memory ordering from retired load/store uops that span a page boundary. The page-split rows can support precise sampling to locate offending instructions.

## State and Persistence Behavior

The JSON stores only static definitions and sampling defaults. Runtime machine-clear counts and page-split samples are not persisted here. PEBS records, when collected, are written by perf to its output stream.

## Dependencies and Integration Points

The file depends on Goldmont core PMU and PEBS support. It integrates with memory-ordering diagnostics, alignment tuning, page-layout analysis, and perf sampling workflows. It complements `cache.json` retired memory-uop rows and `virtual-memory` style TLB/page-walk analysis by identifying split accesses that cross page boundaries.

## Risks and Edge Cases

Page splits are not the same as cache-line splits; this file specifically tracks page-boundary splits. The machine-clear event can be affected by multicore snoop behavior and may not point to a single local instruction without corroborating samples. PEBS support is required for precise attribution of page-split load/store rows.

## Test Signals

Validation should include JSON parsing and perf alias visibility. Microbenchmarks with deliberately page-crossing loads and stores should increase the split rows. Multicore memory-sharing tests can exercise memory-ordering clears. PEBS tests should verify precise attribution for split load/store instructions where supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/goldmont/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/goldmont/other.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/goldmont/other.json

## Purpose

`other.json` defines 5 Goldmont core PMU events that do not fit cleanly into the cache, front-end, floating-point, or memory files. It covers broad fetch stalls, ITLB-related fetch stalls, and hardware interrupt delivery or masking.

## Important APIs, Types, and Data Fields

Rows use `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, and `PublicDescription`. Events are `FETCH_STALL.ALL`, `FETCH_STALL.ITLB_FILL_PENDING_CYCLES`, `HW_INTERRUPTS.MASKED`, `HW_INTERRUPTS.PENDING_AND_MASKED`, and `HW_INTERRUPTS.RECEIVED`. `FETCH_STALL.ALL` has no `UMask`; the more specific ITLB stall and interrupt rows use `UMask` values.

## Control Flow and Data Flow

Perf ingests the aliases and programs Goldmont core counters. Runtime data identifies cycles where fetch cannot provide bytes while the decoder queue can accept them, cycles where ITLB fill is the fetch-stall reason, cycles where interrupts are masked, cycles where pending interrupts remain masked, and counts of received hardware interrupts.

## State and Persistence Behavior

The file persists static PMU metadata only. Runtime interrupt and fetch-stall counts are per-core and interval-local. Interrupt counters are especially sensitive to OS scheduling, interrupt affinity, and kernel configuration.

## Dependencies and Integration Points

These definitions depend on Goldmont core PMU support and integrate with perf front-end stall analysis, ITLB/fetch diagnosis, interrupt-latency investigations, and OS/kernel performance studies. They complement `frontend.json` I-cache and branch-clear rows and `cache.json` I-cache-fill stall rows.

## Risks and Edge Cases

`FETCH_STALL.ITLB_FILL_PENDING_CYCLES` is explicitly not the same as page-walk cycles to retrieve an instruction translation, so it should not be substituted for ITLB page-walk events. `FETCH_STALL.ALL` includes multiple causes and needs more specific events for attribution. Hardware interrupt events are system-noise-sensitive and may reflect unrelated devices or kernel activity. `HW_INTERRUPTS.RECEIVED` uses a much smaller default sample period than the cycle events.

## Test Signals

Validation should include JSON parsing and perf list exposure. Instruction-footprint and ITLB-pressure workloads should increase fetch-stall rows. Interrupt-heavy workloads, controlled interrupt affinity, or timer tests should affect interrupt received/masked rows. Cross-checking `FETCH_STALL.ALL` against `FETCH_STALL.ITLB_FILL_PENDING_CYCLES` and cache/front-end stall events provides a useful consistency signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/goldmont/other.json -->
