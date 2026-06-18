<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/graniterapids/frontend.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/graniterapids/frontend.json

## Purpose
Granite Rapids x86 perf PMU event table for front-end pipeline observation. The file is data, not executable code: perf's PMU event tooling parses the 46 JSON objects to expose named hardware events such as branch resteers, decode stalls, DSB/MITE/MS delivery, instruction-cache stalls, and precise front-end retirement latency events.

## APIs, Types, and Functions
The effective API is the perf `pmu-events` JSON schema. Each object maps an `EventName` to encodings and metadata consumed by the perf event alias generator: `EventCode`, `UMask`, optional `Counter`, `CounterMask`, `EdgeDetect`, `Invert`, `MSRIndex`, `MSRValue`, `SampleAfterValue`, `BriefDescription`, `PublicDescription`, and for some precise retired events `RetirementLatencyMin/Mean/Max`. There are no C functions or local types in the file, but downstream generated C tables treat these fields as declarative event descriptors.

The event families are:
- `BACLEARS.ANY`, `DECODE.LCP`, `DECODE.MS_BUSY`, and `DSB2MITE_SWITCHES.PENALTY_CYCLES` for branch-discovery, length-changing-prefix, microcode, and DSB-to-MITE penalties.
- `FRONTEND_RETIRED.*` precise-distribution events for DSB miss, iTLB/STLB/L1I/L2 misses, unknown branches, MS flows, software prefetch lateness, ANT and mispredicted ANT branches, and latency thresholds from 1 to 512 cycles. These use `EventCode` `0xc6`, `UMask` `0x3`, and PEBS/PDist-related MSR programming through `MSRIndex` `0x3F7`.
- `ICACHE_DATA.*` and `ICACHE_TAG.*` stalls for fetch misses and instruction TLB/tag-side stalls.
- `IDQ.*`, `IDQ_BUBBLES.*`, and `IDQ_UOPS_NOT_DELIVERED.*` events for DSB, MITE, microcode sequencer uop delivery, front-end bubbles, and no-uop-delivery cycles.

## Control Flow, State, and Persistence
At build or runtime table-generation time, perf reads this JSON array, validates field names, and folds each entry into architecture-specific PMU alias tables for `arch/x86/graniterapids`. At perf execution time, a user-facing event alias such as `frontend_retired.l1i_miss` resolves to the encoded event select, umask, counter constraints, and optional MSR filter values from the entry. The file itself keeps no mutable state; persistence is the version-controlled JSON plus generated perf tables when the kernel/perf source is built.

The control relationship is mostly dependency-oriented: metrics in `gnr-metrics.json` refer directly to many names in this file, including `FRONTEND_RETIRED.L1I_MISS`, `FRONTEND_RETIRED.L2_MISS`, `FRONTEND_RETIRED.ITLB_MISS`, `FRONTEND_RETIRED.STLB_MISS`, `FRONTEND_RETIRED.ANY_DSB_MISS`, `FRONTEND_RETIRED.MS_FLOWS`, `FRONTEND_RETIRED.UNKNOWN_BRANCH`, `ICACHE_DATA.STALLS`, `ICACHE_DATA.STALL_PERIODS`, `ICACHE_TAG.STALLS`, `DECODE.LCP`, `DSB2MITE_SWITCHES.PENALTY_CYCLES`, `IDQ.DSB_UOPS`, `IDQ.MITE_UOPS`, and `IDQ.MS_UOPS`.

## Dependencies and Integration
This table integrates with perf's PMU event parser, generated event alias tables, `perf list`, `perf stat`, `perf record`, and the Granite Rapids metric formulas. It depends on the kernel perf PMU JSON schema and on Intel Granite Rapids architectural event definitions. It is paired with sibling event files for branch, cache, floating point, memory, uncore, and topdown sources, because metrics in `gnr-metrics.json` combine this front-end data with core, offcore, branch, and uncore events.

Counter constraints are part of the integration contract. General events often allow counters `0,1,2,3`; several `FRONTEND_RETIRED.*` aliases allow `0..7` but declare PDist counter availability in descriptions. MSR-backed selectors require perf to program `MSRIndex`/`MSRValue` consistently, and ratio formulas that use the `:R` retirement-latency companion depend on the event being recognized as a retired latency-capable source.

## Risks
Risks are primarily data-contract risks. A wrong `EventCode`, `UMask`, `MSRValue`, or counter mask silently produces misleading measurements. Precise events using `MSRIndex` `0x3F7` are especially sensitive because multiple aliases share the same architectural event but differ by MSR selector. Several metrics divide by these events or multiply by `:R`, so missing PEBS/retirement-latency support can break top-down formulas or produce zeros. The file also contains human-facing descriptions; typo-level issues are less operationally severe but can confuse `perf list` output.

## Test Signals
Useful validation signals are `jq` parse success, perf PMU event-table generation without schema warnings, `perf list` showing the expected Granite Rapids front-end aliases, and `perf stat -e` acceptance for representative aliases from each family. Metric-level signals include successful evaluation of `tma_icache_misses`, `tma_itlb_misses`, `tma_dsb_switches`, `tma_lcp`, DSB/MITE/MS delivery percentages, and front-end information metrics such as DSB miss, unknown branch, and icache miss latency ratios. Hardware validation should include workloads with known instruction-cache pressure, branch misprediction/resteer behavior, microcode-heavy instructions, and DSB-vs-MITE shifts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/graniterapids/frontend.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/graniterapids/gnr-metrics.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/graniterapids/gnr-metrics.json

## Purpose
Granite Rapids derived metric catalog for perf. The file defines 325 metrics that turn raw PMU events, topdown slots, model variables, uncore counters, MSR counters, and helper constants into user-facing ratios, bandwidths, latency estimates, top-down hierarchy nodes, instruction-mix views, and bottleneck estimates.

## APIs, Types, and Functions
The effective API is perf's metric JSON schema. Each entry is a metric object keyed by `MetricName`, with formula text in `MetricExpr`, optional `MetricGroup`, `BriefDescription`, `PublicDescription`, `ScaleUnit`, `MetricThreshold`, `MetricConstraint`, `DefaultMetricgroupName`, and `MetricgroupNoGroup`. There are no local functions, but `MetricExpr` uses perf's expression language: arithmetic, `min`, `max`, conditional expressions, event modifiers such as `:R`, raw event terms like `cpu@...@`, uncore PMU terms, runtime variables such as `duration_time`, topology constants such as `#num_packages`, `#num_cpus_online`, `#SMT_on`, `#SYSTEM_TSC_FREQ`, and source helpers such as `source_count(...)`.

The catalog includes:
- Basic system and CPU metrics: `cpi`, CPU utilization, operating frequency, c-state residency, SMI counts/cycles, uncore frequency, UPI bandwidth, IIO and IO bandwidth.
- Cache, memory, NUMA, and offcore metrics: L1/L2/LLC misses per instruction, memory bandwidth read/write/total, local/remote memory bandwidth, LLC miss latency estimates, CXL memory bandwidth conditional on `#has_pmem`, NUMA locality ratios, and reads-to-core bandwidth.
- Front-end delivery metrics: DSB/MITE/MS uop percentages and TMA front-end nodes such as fetch bandwidth, fetch latency, icache misses, iTLB misses, DSB switches, LCP, unknown branches, and associated informational ratios.
- Full TMA hierarchy: level 1 topdown metrics (`tma_frontend_bound`, `tma_bad_speculation`, `tma_backend_bound`, `tma_retiring`), level 2/3/4/5/6 breakdowns, issue-oriented groups, and synthesized bottleneck metrics such as memory bandwidth, memory latency, synchronization, compute-bound estimate, mispredictions, irregular overhead, branching overhead, useful work, and other bottlenecks.
- Instruction mix and pipeline metrics: branches, calls, loads/stores, arithmetic, scalar/vector floating point, integer vector, x87, fused/non-fused branches, NOPs, assists, page faults, serializing operations, pause, C0 wait, and port utilization.

## Control Flow, State, and Persistence
Perf consumes this file as declarative metric data. During table generation or runtime loading, each `MetricExpr` is parsed into an expression tree and associated with the named metric and semicolon-separated metric groups. When a user runs `perf stat -M <metric>` or selects a metric group, perf resolves all referenced metrics and raw events, schedules the required counters subject to constraints, reads counter values, and evaluates the expression. Metrics can depend on other metrics, so the control flow is a dependency graph rather than a linear procedure; for example `tma_bottleneck_data_cache_memory_latency` depends on `tma_memory_bound`, `tma_dram_bound`, `tma_l1_bound`, `tma_l2_bound`, `tma_l3_bound`, `tma_store_bound`, `tma_mem_latency`, and many lower-level latency components.

There is no mutable state stored in the JSON. Persistence is the checked-in formula catalog and any generated perf tables. Runtime state lives in perf's stat/metric engine: scheduled event groups, counts, time-enabled/time-running normalization, topology variables, and expression evaluation intermediates.

## Dependencies and Integration
This file is the central integration point for the Granite Rapids PMU model. It depends on event names declared across sibling JSON files, including `frontend.json` for front-end and precise retired latency events, `memory.json` for `MEMORY_ACTIVITY`, `CYCLE_ACTIVITY`, `MEM_TRANS_RETIRED`, `OCR`, `OFFCORE_REQUESTS`, RTM, and transactional-memory events, and many other core/uncore files for branch, cache, TLB, FP, integer-vector, topdown, CHA, memory-controller, IIO, CXL, UPI, and power events. It also depends on `metricgroups.json`; every group tag in `MetricGroup` should resolve to a group description so `perf list --metricgroups` and grouped metric selection remain coherent.

Important expression-language integration points include escaped event syntax (`cpu@...@`, `uncore_cha_0@...@`), raw event attributes (`event=`, `umask=`, `cmask=`, `edge=`, `offcore_rsp=`, `thresh=`), kernel/user filters (`:k`, `:u`), PEBS latency aliases with `:R`, conditional terms based on `#has_pmem` and `#SMT_on`, and `source_count()` normalization for multi-source uncore PMUs.

## Risks
The main risk is formula fragility. Many expressions divide by raw events or derived metrics that may be zero for short runs, idle systems, or workloads lacking a class of instructions. Several formulas use `max()` or small constants to limit this, but not all divisions are guarded. Event-name drift between this file and sibling event tables will cause metric parse or runtime resolution failures. Escaping mistakes in raw event syntax can make formulas unparsable. Uncore metrics depend on topology and source counts; wrong `#num_packages`, `#num_dies`, `source_count()`, or PMU availability changes units and magnitudes. Metrics gated on `#has_pmem` should be checked on systems without CXL/PMem so they evaluate to zero rather than failing. TMA formulas are also sensitive to multiplexing and counter scheduling constraints because they combine many raw counters into a hierarchy where percentages are expected to sum sensibly.

Another integration risk is semantic mismatch between group labels and formulas. Metric groups are used by humans and tooling to select related metrics; a missing or stale group name can hide a metric from expected bundles even when its formula works.

## Test Signals
Test signals include `jq` parse success, perf metric-table generation without expression or group warnings, `perf list --metrics` showing all 325 names, and `perf list --metricgroups` resolving all group tags. Runtime smoke tests should cover `perf stat -M tma_L1_group`, selected TMA level groups, `-M Summary`, `-M MemoryBW`, `-M Frontend`, `-M SoC`, `-M Power`, and individual metrics with raw-event escaping such as SMI, uncore, CXL-gated, DSB, and PEBS `:R` formulas. Numerical signals include TMA L1 components staying within plausible percentage ranges, bandwidth metrics scaling with `duration_time`, latency formulas producing finite values on nonzero traffic, and no unexpected NaN/inf output under idle, single-threaded, SMT, memory-bound, branch-heavy, and vector/HPC workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/graniterapids/gnr-metrics.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/graniterapids/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/graniterapids/memory.json

## Purpose
Granite Rapids x86 perf PMU event table for memory, offcore, load latency, transactional memory, and memory-ordering observation. The 50 JSON objects provide raw aliases used directly by users and indirectly by Granite Rapids metrics to reason about cache-miss stalls, demand data/code/RFO offcore responses, memory locality, store sampling, and RTM/transaction abort causes.

## APIs, Types, and Functions
The file uses the same perf PMU event JSON schema as other architecture event tables. Fields include `EventName`, `EventCode`, `UMask`, `Counter`, optional `CounterMask`, `MSRIndex`, `MSRValue`, `Data_LA`, `SampleAfterValue`, `BriefDescription`, and `PublicDescription`. It defines data, not functions or local types.

The event families are:
- `CYCLE_ACTIVITY.*` and `MEMORY_ACTIVITY.*` counters for cycles or execution stalls while L1D, L2, or L3 miss demand loads are outstanding.
- `MACHINE_CLEARS.MEMORY_ORDERING` for machine clears triggered by memory-ordering conflicts.
- `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_*` thresholds from 4 through 2048 cycles and `MEM_TRANS_RETIRED.STORE_SAMPLE`, using `Data_LA` and MSR threshold programming through `MSRIndex` `0x3F6`.
- `OCR.*` offcore response aliases for demand code reads, demand data reads, RFOs, reads-to-core, and write estimates. Many use combined `EventCode` values `0x2A,0x2B`, paired offcore MSRs `0x1a6,0x1a7`, and different `MSRValue` response masks for DRAM, L3 miss, local/remote DRAM, local socket, remote memory, and local cluster/cache variants.
- `OFFCORE_REQUESTS.*` and `OFFCORE_REQUESTS_OUTSTANDING.*` demand-data L3 miss request and occupancy events.
- `RTM_RETIRED.*` and `TX_MEM.*` events for restricted transactional memory start/commit/abort and capacity/conflict abort reasons.

## Control Flow, State, and Persistence
Perf parses the JSON array into event aliases for Granite Rapids. At runtime an alias maps to an event select, umask, counter constraints, counter mask, optional latency-address sampling flag, and optional MSR selector. Offcore response events require programming the offcore response MSR mask named by `MSRIndex`/`MSRValue`. Load latency threshold aliases require programming the latency threshold MSR value. The JSON itself has no mutable state; persistence is source control plus generated perf alias tables.

This file feeds many formulas in `gnr-metrics.json`. Examples include `tma_dram_bound`, `tma_mem_latency`, `tma_l1_bound`, `tma_l2_bound`, `tma_l3_bound`, `tma_cxl_mem_bound`, `tma_false_sharing`, `tma_info_memory_latency_load_l3_miss_latency`, `tma_info_memory_mix_offcore_read_l3m_pki`, `tma_info_memory_soc_r2c_dram_bw`, and NUMA/locality bandwidth formulas. The memory activity stall counters also sit under the top-down backend/memory hierarchy.

## Dependencies and Integration
The file depends on perf's PMU event schema, Intel Granite Rapids event encodings, PEBS/load-latency support for `Data_LA` events, and offcore response MSR programming support. Integration points are `perf list`, `perf stat`, `perf record` sampling for load/store latency, the metric engine, and raw offcore response handling. It must stay consistent with formula references in `gnr-metrics.json` and with sibling cache/TLB/uncore event files that provide companion events in the same memory metrics.

Counter restrictions matter. Some cycle/stall events are limited to counters `0,1,2,3`; load-latency threshold events allow counters `1..7`; store sampling specifies counter `0`; and OCR events allow `0..3` while programming offcore MSRs. Perf scheduling must respect these constraints when a metric group combines many memory aliases.

## Risks
Offcore and latency events have high risk because multiple aliases share the same base event but differ only by MSR response mask or threshold. A single wrong `MSRValue` changes the semantic category while still producing counts. `Data_LA` events are sampling-oriented and may not behave like ordinary counting events on all perf paths. Counter conflicts are likely in large metric groups because memory metrics combine core, offcore, PEBS, and uncore counters. Several public descriptions include topology caveats such as Sub-NUMA Cluster behavior; formulas and human interpretation need to account for SNC/local-cluster modes. Transactional-memory events may be low or unsupported depending on platform configuration and workload, so metrics should tolerate zeros.

## Test Signals
Validation starts with JSON parsing and perf event-table generation. Runtime smoke tests should confirm `perf list` exposes the aliases and `perf stat -e` accepts representative events from each family: `MEMORY_ACTIVITY.STALLS_L1D_MISS`, `MEMORY_ACTIVITY.STALLS_L3_MISS`, `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_128`, `OCR.DEMAND_DATA_RD.L3_MISS`, `OCR.READS_TO_CORE.REMOTE_MEMORY`, `OFFCORE_REQUESTS_OUTSTANDING.L3_MISS_DEMAND_DATA_RD`, and `RTM_RETIRED.ABORTED`. Metric-level tests should run memory-bound, cache-resident, remote-NUMA, and transactional-memory workloads where available, checking that memory-bound TMA nodes and bandwidth/latency formulas move in expected directions and do not emit parse errors, NaNs, or impossible negative values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/graniterapids/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/graniterapids/metricgroups.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/graniterapids/metricgroups.json

## Purpose
Granite Rapids metric-group description map for perf. The file defines 143 group-name keys used by `gnr-metrics.json` and maps each to a human-readable description for grouped metric discovery, selection, and display.

## APIs, Types, and Functions
The effective API is a JSON object whose keys are metric group names and whose values are descriptions. It has no local functions or concrete C types. Keys include broad domains such as `Backend`, `Bad`, `Branches`, `Compute`, `Frontend`, `HPC`, `Mem`, `MemoryBW`, `MemoryLat`, `MemoryTLB`, `Offcore`, `Pipeline`, `Power`, `Server`, `SoC`, `Summary`, and `TopdownL1` through `TopdownL6`; bottleneck-view groups such as `BvBC`, `BvBO`, `BvCB`, `BvFB`, `BvIO`, `BvMB`, `BvML`, `BvMP`, `BvMS`, `BvMT`, `BvOB`, and `BvUW`; TMA rollup groups such as `tma_L1_group` through `tma_L6_group`; category contributor groups such as `tma_memory_bound_group`, `tma_fetch_latency_group`, and `tma_ports_utilization_group`; and issue tags such as `tma_issueBW`, `tma_issueLat`, `tma_issueTLB`, `tma_issueFB`, and `tma_issueSyncxn`.

## Control Flow, State, and Persistence
Perf loads this map alongside metric definitions. When metrics declare semicolon-separated `MetricGroup` values, the group names are resolved against this file to provide descriptions and to support user selection of whole groups. There is no runtime mutation in the JSON; state lives in perf's in-memory metric-group registry after parsing.

The control relationship is one level removed from counters: selecting a group causes perf to select all metrics in `gnr-metrics.json` tagged with that group, which in turn expands into the metric dependency graph and raw event schedule. The group map therefore affects discoverability and command-line ergonomics, not the raw hardware encodings.

## Dependencies and Integration
This file depends on the group tags used in `gnr-metrics.json`. The observed metric catalog heavily uses `TopdownL4`, `tma_L4_group`, `Mem`, `TopdownL3`, `tma_L3_group`, `Offcore`, `MemoryTLB`, `MemoryBW`, `Fed`, `Server`, `TopdownL5`, and pipeline/front-end/back-end tags, so stale or missing descriptions for those names would degrade `perf list --metricgroups` output. The naming convention also integrates with Intel's Top-down Microarchitecture Analysis spreadsheet terminology, which is referenced by most broad group descriptions.

## Risks
The primary risk is drift: if a metric adds a new `MetricGroup` tag that is absent here, grouped discovery becomes inconsistent. Conversely, unused keys are harmless but can mislead users if they appear as supported groups with no metrics. Case and punctuation matter (`MachineClears` and `Machine_Clears`, `MemoryBW` and `Memory_BW`, `MemoryLat` and `Memory_Lat` are distinct), so accidental normalization by tools would break lookups. Generic descriptions for many groups are adequate for machine readability but not very explanatory for users trying to choose between similar bottleneck-view or issue groups.

## Test Signals
Useful tests are JSON parse success, checking every semicolon-separated `MetricGroup` tag in `gnr-metrics.json` has a key here, checking every key here is either used or intentionally retained for compatibility, and verifying `perf list --metricgroups` shows descriptions for top-down levels, issue groups, memory groups, front-end groups, and SoC/power groups. Runtime selection tests should include `perf stat -M TopdownL1`, `-M tma_L3_group`, `-M MemoryBW`, `-M Frontend`, `-M Offcore`, `-M Power`, and at least one `tma_issue*` group to ensure group names expand into metrics rather than only displaying descriptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/graniterapids/metricgroups.json -->
