# subset-b-006716 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sapphirerapids/uncore-memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sapphirerapids/uncore-memory.json

## Purpose

This 403-entry JSON catalog defines Sapphire Rapids package-level uncore memory PMU events for Linux `perf`. It covers three uncore units: 161 `iMC` events for standard integrated memory controllers, 67 `MCHBM` events for HBM memory-channel controller behavior, and 175 `M2HBM` events for mesh-to-HBM and directory/fabric behavior. The file lets users and metrics request named aliases for DRAM/HBM CAS traffic, activate/precharge behavior, queue occupancy, power-state memory events, directory hit/miss/update states, direct-to-core/direct-to-UPI paths, prefetch CAM activity, tracker pressure, and read/write pending queues instead of hand-programming event select and mask fields.

## Important APIs, Types, and Data

The schema is the perf PMU event-object schema: `EventName`, `EventCode`, `UMask`, `Counter`, `Unit`, `PerPkg`, `BriefDescription`, optional `PublicDescription`, and several less common fields such as `FCMask`, `PortMask`, and `Experimental`. Every event is package scoped through `PerPkg: 1` and is constrained to counters `0,1,2,3`. Major `iMC` and `MCHBM` families include `UNC_M*_ACT_COUNT`, `UNC_M*_CAS_COUNT`, `UNC_M*_CAS_ISSUED_REQ_LEN`, `UNC_M*_PRE_COUNT`, `UNC_M*_RDB_*`, `UNC_M*_RPQ_*`, and `UNC_M*_WPQ_*`. `iMC` also adds PMM queue, power, refresh, scrub/buffer, and tag-check families. `M2HBM` adds directory hit/miss/update, `DIRECT2CORE`, `DIRECT2UPI`, distress, ingress/egress queue, prefetch CAM, tracker, and write-tracker families.

## Control Flow

There is no executable control flow in this file. Perf's pmu-events build/runtime path reads the array, maps each record to the Sapphire Rapids model, and exposes aliases under the corresponding uncore PMU unit. When a user requests an alias, perf selects the `Unit`, programs `EventCode`, `UMask`, filter masks, and one of the allowed counters, then aggregates at package scope. Metrics and operators interpret related aliases together, for example read/write CAS counts for bandwidth, activate/precharge counts for row locality, and queue occupancy/inserts for memory-controller pressure.

## State and Persistence Behavior

The persistent state is the checked-in alias-to-encoding contract and the distinction between `iMC`, `MCHBM`, and `M2HBM` counting domains. Runtime counter state lives only in uncore PMU hardware during a perf session and is shared by all work on the package. The package-scoped nature means counts are not attributable to a single task without careful workload isolation. HBM, PMM, and directory/fabric events also persist platform assumptions: unavailable units or disabled HBM modes may expose no counters or zero counts even though the JSON parses.

## Dependencies and Integration Points

This file integrates with `tools/perf/pmu-events` JSON parsing, generated perf event tables, `perf list`, `perf stat`, Sapphire Rapids uncore PMU kernel drivers, and higher-level memory bandwidth/locality metrics. It complements core-side cache/TLB event files by measuring controller and fabric traffic after requests leave cores. Downstream usage depends on Intel's uncore PMU programming model, kernel support for the named uncore units, and SKU/firmware exposure of HBM, PMM, and memory power telemetry.

## Risks

The largest risk is semantic drift in event encodings: a valid `EventCode`/`UMask` pair can still count the wrong HBM channel, request type, or directory state. Some aliases intentionally overlap as aggregate and per-channel variants, so metric formulas can double-count if they sum both. Blank `UMask` fields on some `M2HBM` write and non-inclusive variants need parser support and manual validation against hardware docs. HBM and PMM events are platform dependent, and package-level uncore counts are noisy on shared systems. Queue occupancy events often need normalization by clockticks; treating them as simple transaction counts can mislead analysis.

## Test Signals

Useful checks include JSON parsing with perf's pmu-events tooling, `perf list` coverage for `iMC`, `MCHBM`, and `M2HBM` aliases on Sapphire Rapids, and event encoding comparisons against Intel reference tables. Runtime smoke tests should use memory streaming read/write workloads, HBM-local workloads where available, and multi-socket traffic to exercise directory/direct-to-UPI events. Metric tests should verify CAS-to-byte conversion, aggregate versus per-channel consistency, package aggregation, and graceful absence when a platform lacks HBM or PMM support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sapphirerapids/uncore-memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sapphirerapids/uncore-power.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sapphirerapids/uncore-power.json

## Purpose

This 25-entry table defines Sapphire Rapids uncore power-control-unit events for perf. All records use the `PCU` unit and expose package-level telemetry for PCU clockticks, core/package C-state residency and transitions, frequency transitions and clipping, phase shedding, thermal and power throttling, PROCHOT conditions, voltage-regulator heat, and core C-state occupancy. It is the named-event catalog for diagnosing power-management effects on package performance.

## Important APIs, Types, and Data

Entries use `EventName`, `EventCode`, `Counter`, `Unit`, `PerPkg`, `BriefDescription`, optional `PublicDescription`, and frequent `Experimental: 1` markers. Most events can use counters `0,1,2,3`; `UNC_P_PMAX_THROTTLED_CYCLES` is restricted to counter `0`. Key families include `UNC_P_FREQ_*`, `UNC_P_PKG_RESIDENCY_*`, `UNC_P_POWER_STATE_OCCUPANCY_*`, `UNC_P_FIVR_PS_*`, `UNC_P_PROCHOT_*`, `UNC_P_TOTAL_TRANSITION_CYCLES`, and `UNC_P_MEMORY_PHASE_SHEDDING_CYCLES`.

## Control Flow

Perf reads the JSON as static PMU metadata and exposes the aliases when the Sapphire Rapids PCU PMU is present. A `perf stat` or metric request programs the PCU event select onto an allowed package-level counter. Analysts typically compare these cycle counters to `UNC_P_CLOCKTICKS` or wall time to compute residency or throttling ratios. Occupancy events can be used directly for averages or with thresholding modes when supported by the PMU.

## State and Persistence Behavior

The persistent state is the alias set and encoding metadata. Runtime values are package-wide PCU counter values for the active perf session. Residency events explicitly exclude transition time, while transition events count time spent changing frequency or C-states. Most entries are marked experimental, so their behavior is less stable than architectural core events and may vary across steppings, firmware policy, and kernel driver support.

## Dependencies and Integration Points

This file integrates with the perf uncore PCU driver, generated pmu-events tables, power and thermal diagnosis workflows, and top-level performance investigations that correlate memory/core stalls with package frequency policy. It complements core pipeline and uncore memory counters by explaining whether observed throughput changes coincide with frequency caps, thermal limits, package C-state behavior, memory phase shedding, or VR/PROCHOT events.

## Risks

Experimental events can be renamed, unavailable, or have unclear semantics on some systems. Package-level PCU counters cannot attribute throttling to one workload on a shared host. Some cycle events require normalization against PCU clockticks rather than CPU core cycles. Firmware power policy, BIOS settings, and platform sensors can change whether thermal, VR, and external PROCHOT events appear. Counter restrictions, especially the single-counter PMAX event, can cause scheduling failures if metrics overbook PCU counters.

## Test Signals

Validation should include schema parsing, `perf list` exposure of `UNC_P_*` aliases, and simple `perf stat` runs for clockticks and package residency. Stress tests can use AVX, thermal, and power-limited workloads to check frequency clipping and throttling aliases. Idle/active transitions should affect C-state residency and occupancy events. Tests should also confirm experimental events fail gracefully when unavailable and that counter scheduling respects the `Counter` field.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sapphirerapids/uncore-power.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sapphirerapids/virtual-memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sapphirerapids/virtual-memory.json

## Purpose

This 20-entry JSON file defines Sapphire Rapids core virtual-memory PMU aliases for TLB misses and page walks. It covers demand-load DTLB misses, demand-store DTLB misses, and instruction-side ITLB misses, including STLB hits, active or pending page walks, completed walks, and completed walks by page size. The catalog supports perf analysis of translation overhead and page-size effects.

## Important APIs, Types, and Data

Records use `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, optional `PublicDescription`, and `CounterMask` for active page-walk cycle events. `DTLB_LOAD_MISSES` uses event `0x12`, `DTLB_STORE_MISSES` uses `0x13`, and `ITLB_MISSES` uses `0x11`. Load and store groups include 4K, 2M/4M, and 1G completed-walk variants; instruction fetch lacks a 1G-specific variant here. `WALK_ACTIVE` adds `CounterMask: 1` to count cycles with at least one page miss handler active, while `WALK_PENDING` counts outstanding walks per cycle.

## Control Flow

Perf ingests the static table and exposes aliases for the Sapphire Rapids core PMU. Runtime use programs the specified event and mask on generic counters `0,1,2,3`. Users compare STLB hits, walk-completed counts, and walk-active cycles to determine whether translation misses are frequent, whether large pages are effective, and whether page walking is consuming significant execution time.

## State and Persistence Behavior

The file persists the event encoding and sampling defaults; runtime counter values are per perf event and usually per CPU/thread depending on how perf is invoked. `SampleAfterValue` values provide default sampling periods but do not imply persistent state. Page-walk events may include walks that end with or without faults, so fault attribution requires additional kernel or exception signals. Counter-mask cycle events have different semantics from completed-walk event counts.

## Dependencies and Integration Points

This file integrates with perf core PMU support, `perf stat`, `perf record`, virtual-memory tuning, huge-page investigations, and topdown metrics that include frontend or backend stalls from page walks. It complements Sierra/Sapphire cache and memory events by explaining whether cache misses are accompanied by address-translation bottlenecks.

## Risks

A common risk is mixing event counts and cycle-style occupancy counts in ratios without normalization. Page-size variants are not symmetrical across load/store/instruction groups, so formulas must not assume every group has a 1G instruction event. STLB hits are cheaper than page walks but still indicate first-level TLB pressure. Shared-system noise and kernel activity can affect per-CPU counts. Hardware errata or kernel PMU constraints may affect precise attribution for sampled translation events.

## Test Signals

Validation should include JSON parsing, perf alias listing, and smoke workloads that deliberately thrash data and instruction TLBs. Huge-page and 4K-page variants should shift the relevant `WALK_COMPLETED_*` counts. Sampling tests should verify default periods are accepted. Metric tests should separately validate count-based ratios and cycle-based page-walk residency calculations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sapphirerapids/virtual-memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sierraforest/cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sierraforest/cache.json

## Purpose

This 63-entry Sierra Forest cache and memory-hierarchy event table describes core PMU aliases for L1D dirty evictions, L2 line movement and requests, LLC references/misses, memory-bound stalls, retired load/cache-level classifications, memory scheduler blocks, retired memory uops, PEBS load-latency thresholds, offcore response filters, and a topdown frontend-cache signal. It is source metadata for perf, not executable code.

## Important APIs, Types, and Data

The schema includes `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, optional `PublicDescription`, `Data_LA`, `MSRIndex`, and `MSRValue`. All core events use generic counters `0,1,2,3,4,5,6,7` except PEBS load-latency threshold aliases, which are restricted to counters `0,1` and program `MSRIndex 0x3F6` with threshold `MSRValue` values from `0x4` through `0x800`. `Data_LA: 1` marks memory uop sampling aliases that can capture data linear address. Offcore `OCR.*` entries program MSRs `0x1a6,0x1a7`.

## Control Flow

Perf resolves a requested alias to its event select, mask, optional MSR filter, and allowed counter set. Normal cache and stall events program generic counters. Offcore-response events require programming the offcore response MSRs before the counter starts. Load-latency aliases rely on PEBS-style sampling and the latency threshold MSR. Higher-level metrics combine these events to separate L2, LLC, local/remote DRAM, scheduler, store-buffer, and frontend-cache pressure.

## State and Persistence Behavior

The persistent state is the checked-in alias table and its hardware filter encodings. Runtime counter state is held in core PMU counters and optional filter MSRs for the duration of a perf session. `SampleAfterValue` persists default sampling periods. `Data_LA` and threshold MSR metadata are part of the observable contract: removing or changing them would alter sampling behavior even if `EventName` stayed stable.

## Dependencies and Integration Points

This file integrates with perf pmu-events generation, `perf list`, `perf stat`, `perf record`, PEBS/data-address sampling support, offcore response MSR programming, and Sierra Forest topdown metric expressions. It complements `memory.json` by providing broader cache residency and scheduler events, and complements `pipeline.json` by providing stall-cause events used for backend and frontend breakdowns.

## Risks

Offcore `MSRValue` filters are high risk because syntactically valid numbers can encode the wrong response type. PEBS load-latency events require both correct counter restrictions and kernel support for the latency threshold MSR. Some LLC descriptions note that systems without an L3 cache reinterpret LLC hits/misses as zero or L2 misses, so metrics must account for SKU topology. `Data_LA` events can be incorrectly exposed as precise sampling candidates if kernel support is missing. Aggregate and subevent aliases can be double-counted if summed blindly.

## Test Signals

Useful tests include schema parsing, alias listing, generated config/MSR comparisons, and `perf stat` runs for L2, LLC, memory-bound stall, and memory-uop families. PEBS tests should verify latency thresholds program `0x3F6` and only schedule on counters `0,1`. Offcore tests should verify MSR filters for local/remote DRAM and snoop responses. Workloads with L1/L2-resident data, LLC misses, store-buffer pressure, and remote memory access should move the expected counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sierraforest/cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sierraforest/counter.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sierraforest/counter.json

## Purpose

This 15-entry file declares the number of fixed and generic counters available for Sierra Forest core and uncore PMU units. It gives perf the resource model needed to schedule events on `core`, `B2CMI`, `CHA`, `IMC`, `CXLCM`, `CXLDP`, `B2HOT`, `IIO`, `IRP`, `UPI`, `B2UPI`, `B2CXL`, `PCU`, `CHACMS`, and `MDF` units.

## Important APIs, Types, and Data

Each object contains `Unit`, `CountersNumFixed`, and `CountersNumGeneric`. The `core` unit declares 3 fixed counters and 8 generic counters. Every listed uncore unit declares 0 fixed counters. Most uncore units have 4 generic counters, while `CXLCM` declares 8. Values are inconsistently typed as strings and JSON numbers, so consumers must tolerate both.

## Control Flow

Perf's pmu-events tooling reads this table as PMU capability metadata. Event scheduling uses the counter counts to decide whether a requested event group can fit without multiplexing and how many generic slots are available per PMU unit. This file does not name events; it constrains the events declared in adjacent Sierra Forest files and uncore catalogs.

## State and Persistence Behavior

The persistent state is the counter-capacity contract for the model. Runtime state is perf's scheduling decision and PMU counter allocation during a measurement session. Because the file describes hardware resources, changing a count changes whether event groups are accepted, rejected, or multiplexed.

## Dependencies and Integration Points

This file integrates with perf event scheduling, generated PMU tables, uncore PMU discovery, and metric groups that may request several events at once. It is especially relevant for large topdown or uncore metric sets, where exceeding the declared counter count can force multiplexing. It also documents the presence of CXL- and UPI-related uncore units used by adjacent event catalogs.

## Risks

The main risk is incorrect scheduling from a wrong counter count. Overstating counters can make perf attempt impossible event groups; understating them can unnecessarily multiplex or reject valid groups. Mixed numeric/string typing can break strict validators. Hardware SKUs may not expose every uncore unit even though the model table lists it, so runtime code still needs PMU discovery and graceful fallback.

## Test Signals

Validation should include JSON parsing that accepts mixed value types, generated table inspection, and `perf stat` group scheduling tests around 4-event, 8-event, and fixed-counter boundaries. Runtime tests should compare listed units against `/sys/bus/event_source/devices` on Sierra Forest systems and verify absent uncore units do not break perf list or metrics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sierraforest/counter.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sierraforest/floating-point.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sierraforest/floating-point.json

## Purpose

This 13-entry Sierra Forest table defines core PMU aliases for floating-point activity. It covers floating-point divider active cycles, retired floating-point operations by precision, retired floating-point instructions by vector width/precision, floating-point assists, and retired FP divide uops.

## Important APIs, Types, and Data

Records use `EventName`, `EventCode`, `UMask`, `Counter`, `CounterMask`, `SampleAfterValue`, `BriefDescription`, optional `PublicDescription`, and `Deprecated`. `ARITH.FPDIV_ACTIVE` uses `CounterMask: 1` to count cycles with an active FP divider. `FP_FLOPS_RETIRED.*` uses event `0xc8`; `FP_FLOPS_RETIRED.DP` and `.SP` are deprecated aliases for `.FP64` and `.FP32`. `FP_INST_RETIRED.*` uses event `0xc7` for scalar and packed instruction classes. `MACHINE_CLEARS.FP_ASSIST` and `UOPS_RETIRED.FPDIV` capture assist and divider-uop signals.

## Control Flow

Perf maps each alias to a generic counter event on counters `0-7`. Users and metrics combine operation counts, instruction-width counts, divider occupancy, and assist counts to characterize FP throughput and slow paths. Deprecated aliases should still resolve for compatibility but should not be preferred by generated documentation or new metric formulas.

## State and Persistence Behavior

The persistent state is alias naming, encodings, default sampling periods, and deprecation markers. Runtime state is per-session core PMU counts. Cycle-style divider activity differs from retired operation counts, so calculations need consistent denominators. Assist counts are not a direct count of FP instructions or uops; they indicate slow assisted operations.

## Dependencies and Integration Points

This file integrates with perf list/stat/record, Sierra Forest metric groups such as `Flops`, and topdown analyses that correlate FP activity with backend pressure. It depends on core PMU support for the listed event encodings and on perf preserving deprecated aliases for compatibility.

## Risks

The main semantic risks are using deprecated `DP`/`SP` aliases in new formulas, treating weighted FLOP counts and retired instruction counts as interchangeable, and interpreting FP assists as normal operation volume. Workloads using vector widths not represented here may require companion events or derived formulas. Sampling periods differ significantly, so mixed sampled profiles can have uneven resolution.

## Test Signals

Tests should parse the JSON, expose aliases in `perf list`, and verify deprecated markers remain attached. Runtime smoke tests can use scalar single/double, packed 128-bit and 256-bit FP loops, FP divide loops, and denormal/assist-prone operations. Metric validation should compare expected FLOP ratios and ensure new formulas prefer `FP32`/`FP64` over deprecated `SP`/`DP`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sierraforest/floating-point.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sierraforest/frontend.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sierraforest/frontend.json

## Purpose

This 13-entry Sierra Forest frontend event table defines aliases for branch-address clears, frontend-retired stall attribution, instruction-cache accesses/misses, and micro-sequencer busy cycles. It supports topdown frontend-bound analysis and instruction-fetch troubleshooting.

## Important APIs, Types, and Data

Entries use `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, and optional `PublicDescription`. The `FRONTEND_RETIRED.*` family uses event `0xc6` to tag retired instructions following frontend-bound behavior, with categories for branch detect, branch resteer, CISC/micro-sequencer flows, decode, instruction cache, ITLB miss, predecode, and other. `BACLEARS.ANY` uses event `0xe6`, `ICACHE.*` uses event `0x80`, and `MS_DECODED.MS_BUSY` uses event `0xe7`.

## Control Flow

Perf exposes these aliases as core PMU events on generic counters `0-7`. Runtime analysis usually starts with aggregate frontend-bound or topdown events, then uses these aliases to separate branch redirection, decode, instruction-cache, ITLB, micro-sequencer, and residual frontend costs. The table itself has no code flow; the control path is perf alias resolution and counter programming.

## State and Persistence Behavior

The file persists event encodings and sample defaults. Runtime counts are per perf session and per selected CPU/thread scope. `FRONTEND_RETIRED` events are attribution/tagging signals tied to retired instructions after frontend bubbles, not direct raw counts of each root-cause occurrence. `BACLEARS` and `ICACHE` events count different domains and should be normalized before comparison.

## Dependencies and Integration Points

This table integrates with Sierra Forest topdown metric groups, `pipeline.json` topdown slots, `virtual-memory`-style ITLB signals from other architectures, and perf frontend profiling workflows. It depends on core PMU support for frontend-retired tagging and instruction-cache events.

## Risks

Frontend attribution events can be misread as exact causal counts rather than sampled/tagged retirement signals. Branch detect/resteer, predecode, and other categories may overlap conceptually with topdown slot events in `pipeline.json`, so formulas need documented semantics. Instruction-cache miss behavior is workload and code-layout sensitive, and sampling can perturb tiny loops. Metrics should avoid assuming one frontend category fully partitions all stalls unless Intel's model says so.

## Test Signals

Validation should include JSON parsing, alias listing, and smoke tests with branch-heavy code, large instruction footprints, ITLB pressure, decode-heavy instruction streams, and microcoded instruction loops. Topdown tests should verify frontend-bound formulas resolve both this file's `FRONTEND_RETIRED.*` aliases and `pipeline.json` slot aliases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sierraforest/frontend.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sierraforest/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sierraforest/memory.json

## Purpose

This 13-entry Sierra Forest memory event table focuses on load-head stalls, memory-ordering clears, misaligned page splits, and offcore demand-read/RFO outcomes. It is narrower than `cache.json` and provides memory execution and NUMA/DRAM response signals for perf.

## Important APIs, Types, and Data

Records use `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, optional `PublicDescription`, and offcore `MSRIndex`/`MSRValue`. `LD_HEAD.*` uses event `0x05` for oldest-load stall cycles at retirement, split into any, L1-bound, L1 miss, page walk, store-address, and other causes. `MACHINE_CLEARS.MEMORY_ORDERING` uses event `0xc3`, `MISALIGN_MEM_REF.*_PAGE_SPLIT` uses `0x13`, and `OCR.*` events use `EventCode 0xB7`, `UMask 0x1`, and MSRs `0x1a6,0x1a7` for L3 miss, local DRAM, remote DRAM, and RFO L3-miss filters.

## Control Flow

Perf programs regular core counters for load-head, machine-clear, and misalignment aliases. For `OCR.*`, perf also programs offcore response MSRs with the listed filter value before enabling the event. Users combine this file with cache and pipeline events to determine whether backend stalls come from load-buffer head blocking, page walks, store-address conflicts, misaligned accesses, ordering nukes, or remote/local DRAM responses.

## State and Persistence Behavior

The persistent state is the alias-to-encoding table and offcore filter values. Runtime state includes counter values and temporary offcore MSR programming for the perf session. Load-head events count cycles with the oldest load stalled at retirement and are not simple retired-load counts. Offcore response filters are shared hardware state managed by perf, so concurrent offcore users must be scheduled carefully.

## Dependencies and Integration Points

This file integrates with perf's core PMU and offcore response handling, `cache.json` load/cache events, `pipeline.json` backend topdown events, and NUMA/local-versus-remote memory analysis. It depends on kernel support for programming the offcore response MSRs and on accurate Sierra Forest response encodings.

## Risks

Offcore filters are the highest-risk data because a wrong `MSRValue` silently changes the memory-response class. Load-head stall categories can overlap conceptually with broader topdown backend-bound categories, so metric formulas need careful normalization. Misaligned page-split events are rare in normal workloads and may need targeted tests. Remote DRAM counts require a multi-socket or otherwise remote-memory setup; on single-socket systems they may be zero by design.

## Test Signals

Tests should parse the JSON, expose aliases, and compare generated offcore MSR programming to reference encodings. Runtime smoke tests should include pointer-chasing, page-walk-heavy loads, store-address conflict patterns, page-split load/store cases, and local versus remote NUMA memory placement. Metrics should verify `LD_HEAD` cycle counts are normalized against cycles or slots, not retired loads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sierraforest/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sierraforest/metricgroups.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sierraforest/metricgroups.json

## Purpose

This JSON object maps Sierra Forest metric group names to human-readable group descriptions. It is not an event array. The groups organize perf metric expressions into topdown levels, FLOP, instruction-fetch, memory-execution, power, summary, load/store-bound, and category-specific topdown buckets.

## Important APIs, Types, and Data

The file is a single object whose keys are group names and whose values are descriptions. It contains 21 groups: `Flops`, `Ifetch`, `Load_Store_Miss`, `Mem_Exec`, `Power`, `Summary`, `TopdownL1`, `TopdownL2`, `TopdownL3`, `load_store_bound`, `tma_L1_group`, `tma_L2_group`, `tma_L3_group`, `tma_backend_bound_group`, `tma_bad_speculation_group`, `tma_core_bound_group`, `tma_frontend_bound_group`, `tma_ifetch_bandwidth_group`, `tma_ifetch_latency_group`, `tma_machine_clears_group`, and `tma_resource_bound_group`.

## Control Flow

Perf's metric handling reads these mappings to label and display metric groups. The file does not program hardware counters directly. Its effect appears when metric JSON files assign metrics to these group names and perf presents group descriptions through list or metric-selection interfaces.

## State and Persistence Behavior

The persistent state is the stable set of group labels and descriptions for Sierra Forest. Runtime state is only perf's in-memory grouping of available metrics. Renaming a key changes the grouping API for users and scripts even though no event encoding changes. Descriptions document the intended analysis category and should stay aligned with actual metric formulas in adjacent files.

## Dependencies and Integration Points

This file integrates with Sierra Forest metric expression files, `perf list --metrics`-style output, topdown metric UI grouping, and documentation generated from pmu-events. It depends on exact string matching between metric `MetricGroup` references and these keys. The legacy-looking `TopdownL*` names coexist with newer `tma_*` group names, so both naming styles may be referenced by metrics.

## Risks

Because the schema differs from normal event arrays, generic event validators can incorrectly fail it. Stale group names can orphan metrics or hide them from expected category listings. Similar groups such as `TopdownL1` and `tma_L1_group` can confuse scripts that assume one canonical topdown naming scheme. Description-only changes can still affect generated help and user-facing documentation.

## Test Signals

Validation should include JSON object parsing, key uniqueness, and cross-checks that every Sierra Forest metric group reference resolves to a key here or to a globally accepted group. Perf list tests should show grouped metrics under the expected names. Schema tests should treat this as a metric-group map, not as an event-object array.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sierraforest/metricgroups.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sierraforest/other.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sierraforest/other.json

## Purpose

This two-entry Sierra Forest table holds miscellaneous core events that do not fit the cache, memory, frontend, floating-point, or pipeline buckets. It includes a deprecated last-branch-record insert alias and an offcore response event for streaming writes.

## Important APIs, Types, and Data

Entries use standard event fields: `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, and optional `Deprecated`, `PublicDescription`, `MSRIndex`, and `MSRValue`. `LBR_INSERTS.ANY` uses event `0xe4`, mask `0x1`, is marked deprecated, and aliases `MISC_RETIRED.LBR_INSERTS`. `OCR.STREAMING_WR.ANY_RESPONSE` uses event `0xB7`, mask `0x1`, offcore MSRs `0x1a6,0x1a7`, and filter value `0x10800`.

## Control Flow

Perf resolves these aliases like other core events. The LBR alias counts only when LBRs are enabled/configured, and should generally be reached through its non-deprecated replacement. The streaming-write OCR event requires offcore MSR programming before the counter can count responses.

## State and Persistence Behavior

The file persists compatibility and miscellaneous aliases. Runtime state includes normal core counter state, LBR facility configuration for `LBR_INSERTS.ANY`, and temporary offcore MSR filter state for streaming writes. The deprecated marker is persistent user-facing metadata and should steer new metric formulas away from the old name.

## Dependencies and Integration Points

This file integrates with perf's LBR support, offcore response support, generated pmu-events tables, and any metrics or workflows that track streaming store traffic. It also ties to `pipeline.json`, where `MISC_RETIRED.LBR_INSERTS` is the preferred alias for the same LBR behavior.

## Risks

Using the deprecated LBR alias in new metrics can preserve stale naming. LBR counting depends on LBR enablement, so zero counts may indicate configuration rather than absence of branches. The streaming-write offcore filter has the same risk as other OCR events: an incorrect `MSRValue` silently changes the response class. Offcore MSR resources can conflict with other OCR events in the same group.

## Test Signals

Tests should confirm the deprecated alias appears with metadata and that `MISC_RETIRED.LBR_INSERTS` remains available. Runtime tests should enable LBRs and verify insert counts move on branch-heavy workloads. Streaming-write tests should use non-temporal store workloads and verify offcore MSR programming for `0x10800`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sierraforest/other.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sierraforest/pipeline.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sierraforest/pipeline.json

## Purpose

This 76-entry Sierra Forest pipeline table defines core PMU aliases for branch retirement and misprediction, clocks and instructions, load blocking, machine clears, miscellaneous retired operations, serialization, topdown slot categories, issued and retired uops, and arithmetic divider activity. It is the central event catalog for pipeline and topdown performance analysis on Sierra Forest.

## Important APIs, Types, and Data

Records use `EventName`, `EventCode`, `UMask`, `Counter`, `CounterMask`, `SampleAfterValue`, `BriefDescription`, optional `PublicDescription`, `Deprecated`, and `Errata`. Families include `BR_INST_RETIRED`, `BR_MISP_RETIRED`, `CPU_CLK_UNHALTED`, `INST_RETIRED`, `LD_BLOCKS`, `MACHINE_CLEARS`, `MISC_RETIRED*`, `SERIALIZATION`, `TOPDOWN_BAD_SPECULATION`, `TOPDOWN_BE_BOUND`, `TOPDOWN_FE_BOUND`, `TOPDOWN_RETIRING`, `UOPS_ISSUED`, and `UOPS_RETIRED`. Fixed-counter aliases use `Fixed counter 0/1/2`; programmable variants use counters `0-7`. Deprecated aliases include older indirect-call/ITLB/machine-clear names, and several topdown aliases intentionally mirror `_P` variants.

## Control Flow

Perf maps requested aliases to fixed or generic counters. Topdown events count issue or retirement slots for high-level categories, while branch and machine-clear events count retired instructions or clears. Pipeline investigation usually starts with clocks, instructions, and level-1 topdown categories, then drills into branch mispredict, frontend, backend, serialization, uop, and machine-clear subevents. The file itself is static data; perf's alias resolution and counter scheduling provide runtime behavior.

## State and Persistence Behavior

The persistent state is the model-specific alias, encoding, counter, deprecation, errata, and sampling metadata. Runtime state is PMU counter state during a perf session. Fixed counters are limited resources with special semantics, while programmable aliases consume generic counters. Topdown slot events require compatible normalization and should not be mixed directly with raw instruction counts without the intended formulas.

## Dependencies and Integration Points

This file integrates with perf's core PMU support, Sierra Forest metric expressions, `metricgroups.json` topdown group labels, frontend/cache/memory event files for drilldown, LBR-related miscellaneous events, and generated documentation. It depends on the kernel exposing Sierra Forest fixed and generic counters and honoring deprecation/errata metadata in user-facing listings.

## Risks

Topdown event semantics are easy to misuse: slot counts, cycle counts, retired instruction counts, and branch counts have different denominators. Alias pairs such as `CPU_CLK_UNHALTED.CORE`/`.THREAD` and `TOPDOWN_*`/`*_P` must remain consistent without creating duplicate metric contributions. Deprecated aliases should remain for compatibility but not become preferred names. Errata-bearing events require caution in metric formulas and tests. Fixed-counter events can create scheduling conflicts if grouped with assumptions that all aliases use generic counters.

## Test Signals

Validation should include schema parsing, fixed versus generic counter handling, alias listing, deprecation/errata metadata checks, and generated encoding comparisons. Runtime smoke tests should cover branch-heavy code, misprediction patterns, divide-heavy code, serializing instructions, self-modifying-code or page-fault machine clears where feasible, and topdown level-1 breakdowns. Metric tests should verify topdown formulas sum and normalize as expected and that deprecated aliases do not appear in new preferred metric expressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sierraforest/pipeline.json -->
