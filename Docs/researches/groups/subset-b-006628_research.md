# Research Group: subset-b-006628

This grouped report covers Broadwell PMU event catalog JSON files under `sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwell/`. The files are declarative perf event and metric-group data rather than executable code; the relevant "APIs" are the JSON schema fields consumed by perf's PMU event generator and downstream perf list/stat tooling.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwell/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwell/memory.json

## Purpose

`memory.json` defines 240 Broadwell core PMU events for memory-related profiling. It covers hardware lock elision and restricted transactional memory retire/abort accounting, memory-ordering machine clears, PEBS sampled load-latency thresholds, misaligned loads/stores, offcore response filters, and TSX memory abort causes. Its largest family is `OFFCORE_RESPONSE`, with 201 combinations of request type, cache outcome, local DRAM outcome, and snoop response.

## Important APIs, Types, and Data Fields

The file is a JSON array of event objects consumed by perf's `pmu-events` generator. Important fields are `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, and `PublicDescription`. Memory-specific rows also use `MSRIndex` and `MSRValue` for offcore response and load-latency filter programming, `PEBS` and `Data_LA` for precise load-latency sampling, and `Errata` for Broadwell errata annotations such as `BDM100, BDM35`.

Important event families include `HLE_RETIRED.*`, `RTM_RETIRED.*`, `TX_EXEC.*`, `TX_MEM.*`, `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_*`, `MISALIGN_MEM_REF.*`, `MACHINE_CLEARS.MEMORY_ORDERING`, and `OFFCORE_RESPONSE.*`. The offcore rows use event codes `0xB7, 0xBB` and MSRs `0x1a6,0x1a7`; this lets perf program either offcore response register while exposing one logical event name.

## Control Flow and Data Flow

There is no runtime control flow in the file. At build time, perf's PMU event tooling reads the JSON catalog and emits static event tables into generated `pmu-events.c`. At runtime, perf resolves a requested event name, maps it to event-select fields and any auxiliary MSR programming, then asks the kernel PMU driver to configure the hardware counters. For load-latency rows, the data path includes PEBS sampling and an MSR latency threshold. For offcore rows, the `MSRValue` encodes request/source/snoop filters and the hardware counts matching offcore responses.

## State and Persistence Behavior

The file persists static hardware metadata in the source tree. It does not store runtime state, user state, or counter values. The only persistent effects are generated build artifacts derived from the JSON table and installed perf event metadata. Sampling defaults in `SampleAfterValue` influence perf's default period if the event is sampled.

## Dependencies and Integration Points

This catalog depends on the Broadwell PMU architectural event definitions, model-specific offcore response encodings, TSX/HLE semantics, PEBS support, and Broadwell errata. It integrates with `tools/perf/pmu-events` JSON parsing, generated `pmu-events.c`, `perf list`, `perf stat`, `perf record`, perf's metric parser, and the kernel PMU implementation that accepts event select, umask, counter constraints, PEBS, and extra MSR programming.

## Risks and Edge Cases

The highest-risk rows are the offcore and PEBS load-latency entries because a wrong `MSRValue`, `MSRIndex`, or counter constraint silently measures a different traffic class. `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_*` is constrained to counter `3`, uses PEBS level `2`, and depends on load latency MSR programming; relaxing those constraints would create invalid or misleading profiles. Offcore events have dense, repetitive names, so copy/paste mistakes can swap request classes such as demand reads, RFOs, prefetches, code reads, and writebacks. TSX/HLE events are useful only where TSX is available and enabled; on affected systems, firmware or microcode policy may disable TSX even on a Broadwell-family CPU.

## Test Signals

Useful validation signals are successful JSON parsing, successful `pmu-events` generation, event visibility in `perf list` on a Broadwell matching model, and basic `perf stat -e` acceptance for representative rows from each family. For offcore rows, compare generated encodings against Intel tables and smoke-test both `0xB7` and `0xBB` programming paths. For PEBS load-latency rows, `perf record` should accept the event and produce precise samples with data address/latency support where the kernel and hardware expose it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwell/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwell/metricgroups.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwell/metricgroups.json

## Purpose

`metricgroups.json` maps Broadwell metric-group names to user-facing descriptions. It is an object, not an event array, and supplies grouping metadata for `perf list metricgroups`, metric browsing, and top-down microarchitecture analysis organization. Most entries state that the group comes from the Top-down Microarchitecture Analysis Metrics spreadsheet, while top-down levels and generated `tma_*` categories have specific descriptions.

## Important APIs, Types, and Data Fields

The file's public contract is a JSON object where each key is a metric group name and each value is a short description. Important groups include high-level categories such as `Backend`, `Frontend`, `BadSpec`, `MemoryBound`, `Pipeline`, `Retire`, `Summary`, `TopdownL1` through `TopdownL6`, legacy aliases such as `tma_L1_group` through `tma_L6_group`, and many issue/category groups such as `tma_memory_bound_group`, `tma_fetch_latency_group`, `tma_dtlb_load_group`, `tma_issueTLB`, and `tma_ports_utilization_group`.

## Control Flow and Data Flow

There is no control flow inside the file. The perf PMU event generation path loads the object and turns it into metric-group description tables. Runtime consumers use those descriptions when listing or presenting metric groups, and metrics from other JSON files or generated Intel metric code reference these group names through `MetricGroup` fields.

## State and Persistence Behavior

The file persists group labels and descriptions only. It does not own the membership list for each group and does not store runtime metric values. Generated perf artifacts persist a compiled representation of these descriptions.

## Dependencies and Integration Points

The entries depend on the broader Broadwell metric catalog using matching group names. They integrate with `tools/perf/pmu-events/metric.py` helpers that generate group descriptions, `perf list --raw-dump metricgroups`, perf's Python listing helper, and `tools/perf/util/metricgroup.c` for metric group lookup and display.

## Risks and Edge Cases

Because this file is keyed by free-form strings, typos create orphan descriptions or leave referenced metric groups undescribed. Duplicate conceptual groups exist in legacy and generated forms, such as `TopdownL1` and `tma_L1_group`; removing aliases may regress scripts that depend on older names. Description text is not validated against metric membership, so stale descriptions can survive after metrics move groups.

## Test Signals

Validation should include JSON object parsing, generated `pmu-events.c` build success, and `perf list --raw-dump metricgroups` showing representative high-level and `tma_*` group names. A useful consistency check is comparing group names referenced by Broadwell metrics against keys in this file and flagging unreferenced or missing descriptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwell/metricgroups.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwell/other.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwell/other.json

## Purpose

`other.json` defines four Broadwell core PMU events that do not fit the neighboring memory, pipeline, virtual-memory, or uncore categories. The events expose privilege-level cycle accounting and split-lock/uncacheable-lock stall duration.

## Important APIs, Types, and Data Fields

The file is a JSON array of event objects using the standard perf PMU event schema. It contains `CPL_CYCLES.RING0`, `CPL_CYCLES.RING0_TRANS`, `CPL_CYCLES.RING123`, and `LOCK_CYCLES.SPLIT_LOCK_UC_LOCK_DURATION`. The cycle events use event code `0x5C` with umasks `0x1` and `0x2`; the transition event uses `CounterMask: 1` and `EdgeDetect: 1`; the lock-duration event uses event code `0x63` and umask `0x1`.

## Control Flow and Data Flow

The data flow matches other perf event catalogs: JSON is parsed during perf's PMU table generation, users select event names through perf, and the generated encoding is passed through the kernel PMU driver to Broadwell counters. The ring-transition event uses edge-detect semantics so hardware increments on transitions instead of counting every eligible cycle.

## State and Persistence Behavior

This file is static metadata. It does not store runtime privilege transitions or lock events. `SampleAfterValue` provides default sampling periods for generated perf metadata.

## Dependencies and Integration Points

The file depends on Broadwell core PMU semantics for current privilege level cycles and lock-cycle detection. It integrates with perf list/stat/record through generated PMU event tables and with operating-system profiling workflows that distinguish kernel cycles, user cycles, ring transitions, and expensive split-lock or uncacheable locked operations.

## Risks and Edge Cases

Ring-level accounting can be misinterpreted in virtualized or unusual privilege environments where rings 1 and 2 are uncommon or remapped. `CPL_CYCLES.RING0_TRANS` is not a cycle count; it counts transitions, so comparing it directly to `RING0` or `RING123` is a units bug. The split-lock event describes a severe performance hazard, but support and behavior can vary with platform lock-detection policy.

## Test Signals

Smoke tests should verify the four event names appear in `perf list` and can be accepted by `perf stat` on Broadwell. A targeted kernel-heavy workload should move `CPL_CYCLES.RING0`; user-only loops should mostly move `CPL_CYCLES.RING123`; split-lock tests, where safe and permitted, should trigger `LOCK_CYCLES.SPLIT_LOCK_UC_LOCK_DURATION`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwell/other.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwell/pipeline.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwell/pipeline.json

## Purpose

`pipeline.json` defines 137 Broadwell core PMU events for execution pipeline analysis. It covers branch execution and retirement, branch mispredicts, core and reference cycles, cycle activity and stalls, instruction retirement, allocation/issue/retirement uops, port utilization, resource stalls, machine clears, move elimination, load blocking, loop stream detector activity, and floating-point divide activity.

## Important APIs, Types, and Data Fields

The file is a JSON event array. Common fields include `EventName`, `EventCode`, `UMask`, `Counter`, `CounterMask`, `Invert`, `AnyThread`, `PEBS`, `SampleAfterValue`, `BriefDescription`, and `PublicDescription`. Event families include `BR_INST_EXEC`, `BR_INST_RETIRED`, `BR_MISP_EXEC`, `BR_MISP_RETIRED`, `CPU_CLK_THREAD_UNHALTED`, `CPU_CLK_UNHALTED`, `CYCLE_ACTIVITY`, `INST_RETIRED`, `UOPS_EXECUTED`, `UOPS_EXECUTED_PORT`, `UOPS_DISPATCHED_PORT`, `UOPS_ISSUED`, `UOPS_RETIRED`, `RESOURCE_STALLS`, `RS_EVENTS`, `MACHINE_CLEARS`, `LD_BLOCKS`, `LSD`, `MOVE_ELIMINATION`, `INT_MISC`, and `ARITH`.

Several rows expose fixed counters, such as `CPU_CLK_UNHALTED.THREAD`, `CPU_CLK_UNHALTED.REF_TSC`, and retired-instruction variants. Many top-down style rows use `CounterMask` to count cycles meeting a threshold, for example `UOPS_EXECUTED.CORE_CYCLES_GE_*` and `CYCLE_ACTIVITY.STALLS_*`.

## Control Flow and Data Flow

The file has no executable branches. Perf's event generator transforms these rows into lookup data. Runtime control is driven by user selection of events: branch rows configure branch event-select/umask pairs, cycle rows may select fixed or programmable counters, and uop/stall rows use counter masks and sometimes inversion to measure cycle occupancy. Results feed top-down analysis, low-level pipeline bottleneck diagnosis, and direct `perf stat` ratios.

## State and Persistence Behavior

The file persists hardware encodings and sampling defaults. It stores no live pipeline state. Generated tables preserve enough metadata for perf to select fixed counters, programmable counters, PEBS-capable events, any-thread variants, and event constraints.

## Dependencies and Integration Points

The catalog depends on Broadwell core PMU behavior, Hyper-Threading semantics for `AnyThread` events, fixed-counter availability, and PEBS support for precise retired branch/instruction events. It integrates with perf's generated PMU tables, top-down metric groups, `perf stat` ratio calculations, `perf record` sampling, and tests that parse all metric groups or expand PMU event names.

## Risks and Edge Cases

Counter constraints are a key risk: some events are tied to fixed counters or a subset of programmable counters, and some `CYCLE_ACTIVITY` events specifically require counter `2`. Incorrect `CounterMask` or `Invert` values change the event's unit from occurrence count to cycle threshold logic. `AnyThread` rows count activity from either logical thread on a physical core and are not interchangeable with per-thread rows. Branch execution events and retired branch events answer different questions; mixing them in metrics can produce misleading rates.

## Test Signals

Test signals include JSON parse success, generated table build success, `perf list` visibility for representative branch, cycle, uop, and stall rows, and `perf stat` acceptance of fixed-counter and programmable-counter rows. Sanity workloads should show retired instructions and unhalted cycles increasing on CPU-bound loops, branch mispredict events increasing on unpredictable branches, and port/uop counters moving during arithmetic-heavy loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwell/pipeline.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwell/uncore-cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwell/uncore-cache.json

## Purpose

`uncore-cache.json` defines 16 Broadwell uncore cache PMU events for last-level cache/CBOX behavior. It covers L3 lookup outcomes by request type and MESI state, cross-core snoop responses, and the fixed uncore clock counter.

## Important APIs, Types, and Data Fields

The file is a JSON array using uncore-specific schema fields in addition to the normal event fields. Important fields are `EventName`, `EventCode`, `UMask`, `Counter`, `Unit`, `PerPkg`, `BriefDescription`, and `PublicDescription`. The main families are `UNC_CBO_CACHE_LOOKUP.*`, `UNC_CBO_XSNP_RESPONSE.*`, and `UNC_CLOCK.SOCKET`. Most rows use `Unit: CBOX`, `Counter: 0,1`, and `PerPkg: 1`; the clock row uses `Counter: FIXED`, `EventCode: 0xff`, and `Unit: cbox_0`.

## Control Flow and Data Flow

There is no code-level control flow. Perf's generated event table exposes these as uncore PMU events rather than per-core events. At runtime, perf maps `Unit` to the relevant uncore PMU instance, configures package-level CBOX counters, and reports counts per package. Cache lookup rows count LLC lookup results; snoop response rows count cross-core snoop outcomes such as hit, hit-modified, and miss.

## State and Persistence Behavior

The file persists static uncore event metadata. It stores no cache state or package counter values. `PerPkg: 1` signals package-level aggregation semantics, which affects how perf presents and aggregates results on multi-socket or multi-package systems.

## Dependencies and Integration Points

The file depends on Broadwell uncore CBOX PMU support and kernel exposure of matching uncore PMU names. It integrates with perf's uncore PMU lookup, `perf stat` package-level measurement, LLC behavior analysis, cross-core data-sharing diagnosis, and memory hierarchy metrics that need LLC hits/misses or HITM snoop evidence.

## Risks and Edge Cases

Uncore unit naming is platform-sensitive. If the kernel exposes CBOX instances with names that do not match generated expectations, events may list but fail to schedule. `PerPkg` aggregation can surprise users expecting per-core attribution. MESI-state filters are dense bitmasks, so umask mistakes can confuse invalid, shared/exclusive, modified, and all-state lookup counts. The fixed `UNC_CLOCK.SOCKET` row uses `cbox_0`, which is a special unit form compared with the other `CBOX` rows.

## Test Signals

Validation should include `perf list` visibility under uncore/CBOX PMUs, `perf stat` acceptance for representative `UNC_CBO_CACHE_LOOKUP.*` and `UNC_CBO_XSNP_RESPONSE.*` rows, and nonzero `UNC_CLOCK.SOCKET` counts during an interval. Cache-stressing workloads should increase lookup counts; cross-core sharing workloads should affect snoop response counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwell/uncore-cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwell/uncore-interconnect.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwell/uncore-interconnect.json

## Purpose

`uncore-interconnect.json` defines seven Broadwell uncore ARB events for coherence tracker and interconnect request tracking. It measures allocated tracker entries, tracker occupancy, cycles with outstanding requests waiting for memory-controller data return, direct data-read occupancy, and write/request allocations.

## Important APIs, Types, and Data Fields

The file is a JSON event array with uncore fields. All rows use `Unit: ARB` and `PerPkg: 1`. The families are `UNC_ARB_COH_TRK_REQUESTS.ALL`, `UNC_ARB_TRK_OCCUPANCY.*`, and `UNC_ARB_TRK_REQUESTS.*`. Occupancy rows use event code `0x80`, request allocation rows use `0x81`, and coherence tracker requests use `0x84`. Some occupancy rows are constrained to counter `0`; request rows typically use counters `0,1`. `UNC_ARB_TRK_OCCUPANCY.CYCLES_WITH_ANY_REQUEST` uses `CounterMask: 1` to count cycles with at least one qualifying outstanding request.

## Control Flow and Data Flow

There is no executable control flow. Perf's generator emits uncore ARB event metadata; runtime perf commands resolve the event name to an ARB PMU instance and program package-level uncore counters. Occupancy events count cycle-weighted tracker residency, while request events count allocations, so downstream analysis must treat them as different units.

## State and Persistence Behavior

The file stores static metadata only. It does not persist interconnect queues or request state. Package-level aggregation is declared through `PerPkg: 1`.

## Dependencies and Integration Points

The file depends on Broadwell uncore ARB PMU support in the kernel and the platform exposing ARB units. It integrates with uncore perf stat workflows, memory-controller latency investigation, coherence pressure analysis, and package-level traffic profiling that complements CBOX and offcore core events.

## Risks and Edge Cases

The main risk is unit confusion: occupancy rows count cycle residency, while request rows count allocations. Counter constraints are narrower than many core events, especially for occupancy rows limited to counter `0`. Platform/kernel uncore support may vary across Broadwell client/server derivatives. The descriptions mention coherent and non-coherent traffic from IA cores, graphics, LLC, and memory controller interactions, so attribution to one requester requires additional events or workload control.

## Test Signals

Smoke-test `perf list` and `perf stat` for ARB events on a Broadwell system with uncore PMUs. Memory-intensive workloads should move occupancy and request counters. A consistency check should ensure occupancy rows keep their counter restrictions and request rows keep `PerPkg` package semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwell/uncore-interconnect.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwell/virtual-memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwell/virtual-memory.json

## Purpose

`virtual-memory.json` defines 38 Broadwell core PMU events for TLB misses, page walks, TLB flushes, and extended page table walk cycles. It separates load, store, and instruction TLB behavior and provides page-size-specific walk completion counters.

## Important APIs, Types, and Data Fields

The file is a JSON event array using standard perf PMU event fields. Important families are `DTLB_LOAD_MISSES.*`, `DTLB_STORE_MISSES.*`, `ITLB_MISSES.*`, `PAGE_WALKER_LOADS.*`, `TLB_FLUSH.*`, `ITLB.ITLB_FLUSH`, and `EPT.WALK_CYCLES`. Common fields include `EventName`, `EventCode`, `UMask`, `Counter`, `CounterMask`, `SampleAfterValue`, `BriefDescription`, and `PublicDescription`. The DTLB and ITLB miss families include `MISS_CAUSES_A_WALK`, `STLB_HIT`, `STLB_HIT_4K`, `STLB_HIT_2M`, `WALK_COMPLETED`, `WALK_COMPLETED_4K`, `WALK_COMPLETED_2M_4M`, `WALK_COMPLETED_1G`, and `WALK_DURATION`.

## Control Flow and Data Flow

There is no executable control flow. Build-time perf tooling turns the JSON rows into generated event tables. At runtime, perf programs Broadwell PMU counters for selected TLB/page-walk events. Miss-causes-walk rows count miss occurrences, walk-duration rows count cycles spent walking, page-walker-load rows identify which cache/memory level supplied page-table data, and flush rows count invalidation activity.

## State and Persistence Behavior

The file is static metadata and stores no page tables, mappings, TLB state, or counter samples. `SampleAfterValue` sets default sampling periods for generated metadata.

## Dependencies and Integration Points

This file depends on Broadwell PMU definitions for DTLB, ITLB, second-level TLB, page walker, EPT, and flush events. It integrates with perf list/stat/record, virtual memory performance analysis, huge-page tuning, virtualization profiling through EPT walk cycles, and top-down memory/TLB metric groups.

## Risks and Edge Cases

Page-size suffixes must be interpreted carefully: 2M/4M and 1G walk-completion events do not represent the same workload class as 4K events. Walk counts and walk-duration cycles are different units and should not be added directly. EPT walk cycles are virtualization-specific and may be zero or unsupported outside nested/guest contexts. Some rows have only brief descriptions, so downstream UI may expose sparse documentation. TLB flush counters can be affected by OS scheduling and shootdown behavior outside the profiled process.

## Test Signals

Validation should include JSON parse/build success, event visibility in `perf list`, and representative `perf stat` runs for DTLB, ITLB, page-walker, flush, and EPT rows. Workloads with random memory access should increase DTLB misses and page walks; large-page workloads should shift page-size-specific counters; virtualization workloads are the right signal for `EPT.WALK_CYCLES`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwell/virtual-memory.json -->
