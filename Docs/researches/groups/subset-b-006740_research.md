# subset-b-006740 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/tigerlake/tgl-metrics.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/tigerlake/tgl-metrics.json

## Purpose

`tgl-metrics.json` is the Tiger Lake perf metric catalog. It contains 243 metric records that turn raw core, uncore, MSR, cstate, and derived topdown events into user-facing `perf stat -M` metrics. The file covers package/core C-state residency, uncore frequency, SMI accounting, Top-Down Microarchitecture Analysis levels 1 through 6, bottleneck-view rollups, branch and fetch analysis, memory/cache/TLB pressure, port utilization, instruction mix, floating-point mix, system utilization, DRAM bandwidth, power-license utilization, SMT utilization, and TSX transaction behavior.

## Important APIs, Types, and Data Fields

The file is a JSON array of perf metric objects rather than executable code. Records use the metric schema fields `MetricName`, `MetricExpr`, `MetricGroup`, `BriefDescription`, and optional `PublicDescription`, `MetricThreshold`, `MetricConstraint`, `DefaultMetricgroupName`, `MetricgroupNoGroup`, and `ScaleUnit`. `MetricExpr` is the primary API surface: expressions reference raw events such as `UOPS_DISPATCHED.PORT_*`, `BR_MISP_RETIRED.ALL_BRANCHES`, `MEM_LOAD_RETIRED.*`, `OFFCORE_REQUESTS_OUTSTANDING.*`, pseudo-events such as `msr@tsc@`, `msr@aperf@`, `msr@smi@`, cstate aliases, duration constants, and other metrics such as `tma_backend_bound`.

Important metric families include the top-level categories `tma_backend_bound`, `tma_bad_speculation`, `tma_frontend_bound`, and `tma_retiring`; bottleneck-view formulas such as `tma_bottleneck_data_cache_memory_bandwidth`, `tma_bottleneck_data_cache_memory_latency`, `tma_bottleneck_memory_data_tlbs`, `tma_bottleneck_mispredictions`, and `tma_bottleneck_compute_bound_est`; system/info metrics under `tma_info_*`; memory hierarchy metrics such as `tma_l1_bound`, `tma_l2_bound`, `tma_l3_bound`, `tma_dram_bound`, `tma_mem_bandwidth`, and `tma_mem_latency`; and summary/power metrics such as `C*_Pkg_Residency`, `C*_Core_Residency`, `UNCORE_FREQ`, `smi_cycles`, and `smi_num`. There are 24 metrics with `MetricConstraint`, 22 with `MetricThreshold`, 19 with `PublicDescription`, and 7 with `ScaleUnit`.

## Control Flow and Data Flow

There is no local control flow in the JSON. The data flow starts when perf's PMU event build pipeline parses this file and emits generated metric descriptors. At runtime, perf's metric parser expands each `MetricExpr`, schedules the referenced events, applies arithmetic and conditional expressions, normalizes with constants such as `tma_info_thread_slots` or `duration_time`, evaluates thresholds, and groups metrics according to `MetricGroup`.

The formulas form a dependency graph. Base information metrics compute clock, slot, instruction, cache, memory, and system denominators; level-1 and deeper `tma_*` metrics reuse those bases; bottleneck-view metrics combine multiple topdown branches into higher-level cost estimates. This means a user request for one high-level metric can require many raw events and intermediate metrics.

## State and Persistence Behavior

The only persistent state is static metric metadata in the source tree and the generated perf event-table output produced from it. Runtime measurements are interval-local and are not written back to this file. Several metrics depend on package-wide or system-wide state, such as C-state residency, SMI counters, DRAM bandwidth, and uncore frequency, while most TMA metrics depend on per-thread or per-core counting. `MetricThreshold` values persist as advisory expressions that perf can use to flag likely bottlenecks.

## Dependencies and Integration Points

The file depends on Tiger Lake core PMU event definitions, uncore memory/event catalogs, cstate and MSR pseudo-event support, topdown hardware events, and the perf metric expression evaluator. It integrates with `perf list metrics`, `perf list metricgroups`, `perf stat -M`, generated `pmu-events.c`, metric tests, and topdown performance-analysis workflows. It also depends indirectly on sibling Tiger Lake event files for raw event names referenced by formulas, including cache, memory, frontend, pipeline, virtual-memory, uncore-memory, and uncore-interconnect topics.

## Risks and Edge Cases

The main risk is expression fragility. Any rename or removal of a referenced event or intermediate metric can break metric parsing or produce unavailable metrics. Large formulas can divide by zero or by near-zero denominators when a workload does not exercise the relevant hardware path; some expressions use `max(...)` or conditionals, but not every ratio is guarded. Package-wide and system-wide metrics can be misleading when interpreted as task-local. Multiplexing can distort formulas that combine many events if the PMU cannot schedule them together. `MetricConstraint: NO_GROUP_EVENTS` is important because losing it can force invalid grouped scheduling. Thresholds are heuristics, not correctness rules.

## Test Signals

Useful checks include JSON parsing with `jq`, generated perf PMU table builds, `tools/perf/pmu-events/metric_test.py` or equivalent metric-expression tests, and `perf list metrics` on a Tiger Lake-capable build. Runtime smoke tests should include `perf stat -M TopdownL1`, memory bandwidth/latency metrics under a streaming workload, branch-misprediction metrics under a branch-heavy workload, and power/SMI metrics on an idle versus busy system. Regression tests should specifically catch missing raw-event aliases, unguarded expression failures, and accidental group/threshold changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/tigerlake/tgl-metrics.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/tigerlake/uncore-interconnect.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/tigerlake/uncore-interconnect.json

## Purpose

`uncore-interconnect.json` defines 11 Tiger Lake package-level ARB uncore PMU events for coherent interconnect/request-tracker behavior. It exposes request allocation counts and occupancy for coherent and non-coherent traffic, with aliases for data-read tracker requests and occupancies. The catalog helps perf users inspect traffic leaving cores toward the fabric and memory subsystem.

## Important APIs, Types, and Data Fields

The file is a JSON array of event objects using `EventName`, `EventCode`, `UMask`, `Counter`, `Unit`, `PerPkg`, `BriefDescription`, plus optional `Experimental` and `Deprecated`. All rows use `Unit: ARB` and `PerPkg: 1`. Counter availability is split between event-counting requests on counters `0,1` and occupancy-style events on counter `0`.

Important events are `UNC_ARB_COH_TRK_REQUESTS.ALL`, `UNC_ARB_TRK_REQUESTS.ALL`, `UNC_ARB_TRK_REQUESTS.RD`, `UNC_ARB_TRK_OCCUPANCY.ALL`, `UNC_ARB_TRK_OCCUPANCY.RD`, `UNC_ARB_REQ_TRK_REQUEST.DRD`, `UNC_ARB_REQ_TRK_OCCUPANCY.DRD`, `UNC_ARB_DAT_OCCUPANCY.ALL`, and `UNC_ARB_DAT_OCCUPANCY.RD`. Two rows are deprecated aliases: `UNC_ARB_DAT_REQUESTS.RD` points users toward `UNC_ARB_REQ_TRK_REQUEST.DRD`, and `UNC_ARB_IFA_OCCUPANCY.ALL` points toward `UNC_ARB_DAT_OCCUPANCY.ALL`.

## Control Flow and Data Flow

The file has no executable control flow. Perf's PMU event generator ingests the rows, emits uncore ARB aliases, and at runtime programs package-level uncore counters with the encoded `EventCode`/`UMask`/counter constraints. Request events count allocations; occupancy events count valid tracker entries over cycles. The event families form a small analysis flow from all outgoing tracker traffic to coherent data-read-only traffic.

## State and Persistence Behavior

Static event metadata is persistent in the repository and generated perf tables. Runtime counter values are package-scoped and interval-local. The occupancy rows represent integrated hardware state, not discrete transactions, so they need a cycle denominator or comparable workload interval to be interpreted as pressure. Deprecated rows remain persistent aliases for compatibility but should not be treated as preferred API names.

## Dependencies and Integration Points

This file depends on Tiger Lake ARB uncore PMU support in perf and the kernel. It integrates with `perf list`, `perf stat`, uncore fabric analysis, memory traffic diagnosis, and sibling uncore-memory counters that observe traffic after it reaches the memory controller. It also provides raw events that can be referenced by higher-level metrics or user scripts.

## Risks and Edge Cases

Package-level ARB counts aggregate all activity on the package, not just the profiled process. Several rows are marked `Experimental`, so availability or exact semantics may vary by kernel, firmware, or stepping. Deprecated aliases can confuse users if both old and new names appear. Occupancy and request-count rows use different units and should not be summed directly. Counter restrictions matter because all occupancy rows require counter `0`, creating scheduling conflicts with each other.

## Test Signals

Validation should include JSON parse success, perf table generation, and `perf list` exposure of ARB aliases with deprecation metadata preserved. Runtime tests can compare idle, single-thread memory, and multi-thread memory workloads: request counters should rise with fabric traffic, while occupancy counters should increase under pressure. Tests should verify that deprecated aliases still parse but documentation and preferred metric formulas use the non-deprecated names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/tigerlake/uncore-interconnect.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/tigerlake/uncore-memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/tigerlake/uncore-memory.json

## Purpose

`uncore-memory.json` defines 6 Tiger Lake integrated memory-controller free-running PMU events. It exposes read CAS counts, write CAS counts, and total request counts for two memory-controller free-running units, allowing perf to estimate DRAM read/write traffic and aggregate memory-controller request pressure.

## Important APIs, Types, and Data Fields

The file is a JSON event array using `EventName`, `EventCode`, `UMask`, `Counter`, `Unit`, `PerPkg`, and `BriefDescription`. All entries use `EventCode: 0xff` and `PerPkg: 1`. The first controller uses `Unit: imc_free_running_0` with counters `0`, `1`, and `2`; the second uses `Unit: imc_free_running_1` with counters `3`, `4`, and `5`.

The six aliases are `UNC_MC0_TOTAL_REQCOUNT_FREERUN`, `UNC_MC0_RDCAS_COUNT_FREERUN`, `UNC_MC0_WRCAS_COUNT_FREERUN`, `UNC_MC1_TOTAL_REQCOUNT_FREERUN`, `UNC_MC1_RDCAS_COUNT_FREERUN`, and `UNC_MC1_WRCAS_COUNT_FREERUN`. Read and write CAS entries describe 64-byte DRAM transfers. Total request entries count 64-byte read and write requests entering the memory controller, with a note that same-cache-line full and partial writes can be combined into one 64-byte DRAM transfer.

## Control Flow and Data Flow

There is no executable flow. Perf parses the metadata into IMC free-running aliases, then maps selected aliases to the appropriate free-running counter. Data flows from memory-controller hardware counters to perf counts. Analysis usually sums the controller 0 and controller 1 read/write events, then multiplies CAS counts by 64 bytes and divides by measurement time to derive bandwidth.

## State and Persistence Behavior

The source file stores static counter metadata only. Runtime free-running counters may be continuously advancing hardware counters, and perf reads deltas over the measurement interval. Counts are package-scoped and memory-controller-scoped, not process-local. The file does not persist bandwidth calculations or sampled data.

## Dependencies and Integration Points

The catalog depends on Tiger Lake IMC free-running PMU support and perf's uncore event-table generation. It integrates with memory bandwidth metrics in `tgl-metrics.json`, `perf stat` memory studies, and uncore interconnect events that measure request pressure before memory-controller service. The event naming and `Unit` values must match kernel PMU names for the free-running IMC devices.

## Risks and Edge Cases

The fixed counter mapping is the critical risk: each alias is tied to a specific free-running counter number, and a bad counter assignment would silently report the wrong channel/controller statistic. Package-level aggregation can include unrelated system traffic. CAS-to-bandwidth conversion assumes 64-byte transfers, while total request count has write-combining semantics that differ from CAS counts. Systems without matching free-running IMC PMUs may expose none of these aliases.

## Test Signals

Checks should include JSON parsing, generated perf tables, and `perf list` visibility for `imc_free_running_0` and `imc_free_running_1` aliases. Runtime smoke tests should show read CAS counters moving under read-heavy streams, write CAS counters moving under write-heavy streams, and low deltas at idle. A bandwidth sanity test should compare summed CAS-derived GB/s against another trusted memory bandwidth source within expected platform variance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/tigerlake/uncore-memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/tigerlake/uncore-other.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/tigerlake/uncore-other.json

## Purpose

`uncore-other.json` defines the Tiger Lake uncore fixed-clock event `UNC_CLOCK.SOCKET`. It gives perf a package-level UCLK cycle counter that can be used as a denominator for uncore rates, residency-style calculations, and sanity checks for uncore PMU activity.

## Important APIs, Types, and Data Fields

The file is a one-entry JSON event array. The record uses `EventName: UNC_CLOCK.SOCKET`, `EventCode: 0xff`, `Counter: FIXED`, `Unit: CLOCK`, `PerPkg: 1`, and a `BriefDescription` stating that this 48-bit fixed counter counts UCLK cycles. Unlike programmable event files, it does not have a `UMask`, sample period, or multiple event variants.

## Control Flow and Data Flow

There is no executable flow. Perf's generator creates a fixed uncore clock alias for the Tiger Lake `CLOCK` PMU, and runtime perf reads the fixed counter over an interval. Other uncore analyses can use the value to normalize ARB occupancy events, memory-controller rates, or uncore frequency-related measurements.

## State and Persistence Behavior

Only the static alias metadata is persistent in the repository and generated tables. Runtime counter state lives in the hardware fixed counter and perf's measurement interval. Because the counter is fixed-width and hardware-owned, long intervals require normal perf counter wrap handling.

## Dependencies and Integration Points

The event depends on Tiger Lake uncore CLOCK PMU support. It integrates with `perf stat`, package-level uncore diagnostics, and formulas that need UCLK cycles as a denominator. It complements `uncore-interconnect.json` occupancy events and memory free-running counters by providing a time/cycle reference.

## Risks and Edge Cases

The event is package-scoped, not task-scoped. Misinterpreting UCLK cycles as core cycles can produce wrong rates, especially when core and uncore frequencies differ. The 48-bit width makes wrap behavior a consideration for long-running measurements if the kernel/tooling does not handle deltas correctly. Since it is fixed-counter metadata, consumers must not treat `Counter: FIXED` like programmable counter lists.

## Test Signals

Validation should include JSON parse success, generated alias exposure in `perf list`, and a runtime test that `UNC_CLOCK.SOCKET` advances during idle and busy intervals. Rate checks should compare deltas over known wall-clock intervals to plausible UCLK frequency ranges and confirm the alias can be collected alongside programmable uncore events without counter-scheduling conflicts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/tigerlake/uncore-other.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/tigerlake/virtual-memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/tigerlake/virtual-memory.json

## Purpose

`virtual-memory.json` defines 22 Tiger Lake core PMU events for translation behavior. It covers load, store, and instruction TLB misses; second-level TLB hits; page-walk active and pending cycles; completed page walks by page size; and TLB flush attempts. These definitions let perf distinguish translation cache hits from expensive page walks and flush activity.

## Important APIs, Types, and Data Fields

The file is a JSON array of event objects using `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, `PublicDescription`, and optional `CounterMask`. All events can use counters `0,1,2,3`. `DTLB_LOAD_MISSES` has 7 rows, `DTLB_STORE_MISSES` has 7 rows, `ITLB_MISSES` has 6 rows, and `TLB_FLUSH` has 2 rows.

Load and store families include `STLB_HIT`, `WALK_ACTIVE`, `WALK_COMPLETED`, `WALK_COMPLETED_1G`, `WALK_COMPLETED_2M_4M`, `WALK_COMPLETED_4K`, and `WALK_PENDING`. ITLB has `STLB_HIT`, `WALK_ACTIVE`, `WALK_COMPLETED`, `WALK_COMPLETED_2M_4M`, `WALK_COMPLETED_4K`, and `WALK_PENDING`. `WALK_ACTIVE` entries use `CounterMask: 1` to count cycles when at least one page miss handler is busy. `TLB_FLUSH.DTLB_THREAD` and `TLB_FLUSH.STLB_ANY` count flush attempts.

## Control Flow and Data Flow

There is no local control flow. Perf ingests the rows, emits event aliases, and programs the selected core PMU event select and umask values at runtime. The analysis flow is from first-level TLB misses that hit STLB, to misses that initiate page walks, to active/pending page-walk pressure, and finally to flush activity that can explain translation-cache churn.

## State and Persistence Behavior

The file persists static PMU metadata and default sample periods only. It does not store page tables, TLB contents, fault information, or samples. Runtime counts are per-core/per-thread scheduling dependent. Page-walk completion descriptions explicitly note that a walk can end with or without a page fault, so these counters are translation events rather than fault-only events.

## Dependencies and Integration Points

The catalog depends on Tiger Lake core PMU support and the perf PMU event generator. It integrates with `perf stat`, `perf record`, TLB miss analysis, huge-page validation, code-footprint investigations, memory-latency analysis, and topdown metrics such as `tma_dtlb_load`, `tma_dtlb_store`, and `tma_itlb_misses` in `tgl-metrics.json`. It also complements cache and uncore-memory files by explaining address-translation cost before cache or DRAM service.

## Risks and Edge Cases

`WALK_ACTIVE` and `WALK_PENDING` share the same event/umask in each family but have different semantics because `WALK_ACTIVE` uses `CounterMask: 1`; losing that field changes cycle counting into occupancy-like counting. Completed-walk counts and active/pending cycle counts must not be interpreted as the same unit. Page-size-specific counters only indicate mapping size for completed walks, not total memory footprint. ITLB lacks a 1G-specific row here, so load/store and code-fetch summaries are not perfectly symmetric. Flush attempts can be caused by OS and virtualization behavior outside the measured workload.

## Test Signals

Validation should include JSON parsing, generated perf tables, and `perf list` exposure for DTLB, ITLB, and TLB flush aliases. Runtime tests should use random-access data workloads to raise DTLB load/store walk counters, large-page workloads to shift completions from 4K to 2M/1G rows where applicable, code-footprint workloads to exercise ITLB rows, and mapping/unmapping or context-switch-heavy workloads to move flush counters. Regression tests should confirm `CounterMask` survives generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/tigerlake/virtual-memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereep-dp/cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereep-dp/cache.json

## Purpose

`cache.json` is the Westmere EP DP cache and offcore-response PMU catalog for perf. It contains 286 core PMU event records covering L1D and L1I behavior, L2 requests/transactions/line movement/write locks, LLC reference/miss proxies, retired memory instruction latency thresholds, retired load/store outcomes, offcore requests, outstanding offcore requests, store queue conditions, split locks, and a large matrix of offcore response filters. It is the main source for cache hierarchy and memory-response attribution on this architecture.

## Important APIs, Types, and Data Fields

The file is a JSON array of event objects using `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, and optional `MSRIndex`, `MSRValue`, and `PEBS`. Counter availability is mostly `0,1,2,3`, with some events restricted to `0`, `0,1`, or `3`. There are 185 records with offcore `MSRIndex` programming, 15 PEBS-capable records, and 185 records with `SampleAfterValue`.

Major event families include `CACHE_LOCK_CYCLES`, `L1D`, `L1D_PREFETCH`, `L1D_WB_L2`, `L1I`, `L2_DATA_RQSTS`, `L2_LINES_IN`, `L2_LINES_OUT`, `L2_RQSTS`, `L2_TRANSACTIONS`, `L2_WRITE`, `LONGEST_LAT_CACHE`, `MEM_INST_RETIRED`, `MEM_LOAD_RETIRED`, `OFFCORE_REQUESTS`, `OFFCORE_REQUESTS_OUTSTANDING`, `OFFCORE_REQUESTS_SQ_FULL`, `OFFCORE_RESPONSE`, `SQ_MISC`, and `STORE_BLOCKS`. The largest family is `OFFCORE_RESPONSE` with 170 records spanning request types such as demand data, demand ifetch, demand RFO, prefetch data/ifetch/RFO, core writeback, and response locations such as local cache, local DRAM plus remote cache hit, remote cache HITM, IO/CSR/MMIO, and other-core hit states.

## Control Flow and Data Flow

There is no executable control flow. Perf's generator turns each row into an alias. For normal cache events, runtime perf programs the core event select, umask, and counter constraint. For offcore-response rows, perf must also program the offcore response MSR specified by `MSRIndex` with the filter in `MSRValue`; this filter is the actual selector for request type and response source. PEBS-capable retired memory rows can feed precise sampling, while ordinary rows feed counts.

The data flow supports layered analysis: L1/L2 rows show near-core behavior; `LONGEST_LAT_CACHE` and `MEM_LOAD_RETIRED` rows indicate LLC and retired-load outcomes; `OFFCORE_REQUESTS*` rows measure requests and outstanding demand; and `OFFCORE_RESPONSE.*` rows attribute misses or offcore traffic to cache, local DRAM, remote cache, HITM, or IO-like sources.

## State and Persistence Behavior

The file persists static event encodings and MSR filter values. Runtime counter state is interval-local. Offcore-response measurement has temporary hardware state in offcore response MSRs during a perf session; the JSON's `MSRIndex`/`MSRValue` pairs are therefore part of the event's semantic identity. PEBS rows can produce sampled records if the kernel and CPU support precise events, but samples are not persisted here.

## Dependencies and Integration Points

This catalog depends on Westmere EP DP core PMU support, PEBS support for precise retired-memory rows, and kernel/perf support for programming offcore response MSRs. It integrates with `perf list`, `perf stat`, `perf record`, cache-miss analysis, memory-latency and source attribution, NUMA/local-versus-remote investigations, false-sharing/HITM studies, prefetch efficiency analysis, split-lock/lock-cycle diagnosis, and event scheduling logic constrained by the `counter.json` topology.

## Risks and Edge Cases

The highest risk is losing or corrupting `MSRIndex` and `MSRValue` on offcore-response rows; the alias may still exist but count a different request/response class. Many offcore rows are combinations of similar request and response masks, so copy/paste or generator ordering errors are hard to spot by name alone. PEBS-capable rows may degrade or fail on unsupported kernels. Counter restrictions can force multiplexing or reject groups, especially with events limited to counter `3` or `0,1`. Offcore and package/NUMA interpretations are architecture-specific; Westmere EP DP semantics should not be assumed to match newer Intel LLC/offcore definitions exactly.

## Test Signals

Validation should include JSON parse success, perf event-table generation, and `perf list` exposure of normal, PEBS, and offcore aliases. Runtime tests should compare cache-resident, streaming, and random-access workloads to separate L1/L2/LLC behavior; use local versus remote NUMA memory where available to exercise offcore response location filters; use cross-core sharing workloads to move HITM-related rows; and run precise sampling smoke tests for `MEM_INST_RETIRED.*` and `MEM_LOAD_RETIRED.*`. Generator tests should assert that `MSRIndex` and `MSRValue` are preserved exactly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereep-dp/cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereep-dp/counter.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereep-dp/counter.json

## Purpose

`counter.json` records Westmere EP DP PMU counter topology for perf. It declares the number of fixed and generic programmable counters available on the `core` PMU, which constrains event scheduling and grouping for the rest of the architecture's event catalogs.

## Important APIs, Types, and Data Fields

The file is a one-object JSON array with `Unit: core`, `CountersNumFixed: 4`, and `CountersNumGeneric: 4`. It is capability metadata, not a normal event list: it intentionally has no `EventName`, `EventCode`, `UMask`, descriptions, or sample periods.

## Control Flow and Data Flow

There is no control flow. Perf's PMU event tooling reads the topology metadata and uses it when generating or validating architecture-specific PMU tables. At runtime, the scheduler uses the available fixed and generic counter counts to decide whether requested events can be grouped directly or must be multiplexed/rejected.

## State and Persistence Behavior

The file persists static topology metadata only. It does not track active events, counter values, overflow state, or perf session results. The counts are architecture-level constraints that should remain stable for this PMU model.

## Dependencies and Integration Points

The metadata depends on Westmere EP DP core PMU architecture and integrates with sibling event files such as `cache.json`. It is relevant to all perf flows that schedule multiple core events, especially groups containing cache events with explicit `Counter` restrictions or fixed-counter events from other topic files.

## Risks and Edge Cases

Tools must treat this as a counter-topology file, not as an event catalog. If a parser requires `EventName`, it will reject this valid metadata. If the fixed or generic counter counts are wrong, perf may overpromise event grouping, underuse available counters, or multiplex unnecessarily. Numeric values are stored as strings, so consumers need to parse them carefully.

## Test Signals

Validation should include JSON parse success, schema compatibility for topology-only files, and perf scheduling tests that confirm four generic core events can be counted without multiplexing when counter-specific constraints permit. Regression tests should ensure event-list generation does not display this object as a normal PMU event and that sibling cache events respect the declared generic counter count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereep-dp/counter.json -->
