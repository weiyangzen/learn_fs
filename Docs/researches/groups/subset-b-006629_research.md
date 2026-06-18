<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellde/bdwde-metrics.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellde/bdwde-metrics.json

## Purpose
Broadwell-DE derived metric catalog for Linux perf PMU events. The file defines 145 formula-based metrics for power residency, SMI visibility, uncore frequency, top-down microarchitecture analysis, instruction mix, memory behavior, frontend behavior, floating-point throughput, system utilization, and pipeline efficiency. It turns the raw events from sibling Broadwell-DE JSON files into named `perf stat -M` metrics such as `tma_backend_bound`, `tma_memory_bound`, `tma_frontend_bound`, `tma_retiring`, `tma_info_thread_ipc`, `tma_info_system_dram_bw_use`, and C-state residency metrics.

## Important APIs, Types, and Functions
There are no executable functions. The stable interface is the perf PMU metric schema: `MetricName`, `MetricExpr`, `MetricGroup`, and `BriefDescription` appear on every entry. Optional fields are meaningful API surface too: `MetricThreshold` appears on 91 entries, `PublicDescription` and `ScaleUnit` on 78 entries, `MetricConstraint` on 16 entries, and `MetricgroupNoGroup` on 12 top-down rollup entries. Expressions reference event names from sibling files, fixed events like `cycles` and `instructions`, MSR pseudo-events such as `msr@tsc@`, cstate pseudo-events, perf duration variables, topology variables like `#num_dies`, and helper variables such as `#SMT_on`.

## Control Flow
At perf build time this JSON is parsed into generated PMU event tables. At runtime perf resolves a requested metric name or metric group, expands `MetricExpr`, schedules the referenced counters, evaluates conditional expressions, and presents scaled output. The top-down hierarchy is encoded as data dependencies: level 1 metrics derive from slots and speculation counters; level 2 and lower metrics reuse parent metrics such as `tma_backend_bound`, `tma_memory_bound`, `tma_fetch_latency`, and `tma_core_bound`.

## State and Persistence
The file is immutable source data. Runtime state is created by perf when expressions are expanded, counters are scheduled, multiplexed, and sampled. Persistence concerns are schema stability and expression validity: metric names, group names, formulas, constraints, and thresholds must remain compatible with perf's metric parser and with the event aliases provided by the Broadwell-DE event files.

## Dependencies and Integration
This file depends on sibling event catalogs for cache, memory, frontend, floating-point, pipeline, other, uncore, C-state, and MSR aliases. The formulas integrate with `metricgroups.json` through group names such as `TopdownL1`, `TopdownL2`, `Backend`, `Frontend`, `MemoryBound`, `Flops`, `Power`, `SoC`, and many `tma_*_group` groupings. The 16 constrained metrics include `NO_GROUP_EVENTS` or `NO_GROUP_EVENTS_SMT` restrictions for ratios that cannot safely share counter groups or SMT contexts.

## Risks
The main risks are stale formulas for Broadwell-DE hardware behavior, event alias drift against sibling JSON files, division by zero in formulas with sparse workloads, top-down percentages that do not sum as users expect under multiplexing, and constraints that are too weak or too strong for available counters. Metrics referencing MSRs, C-states, or topology variables may fail or report partial data when kernel support, permissions, or topology discovery is missing.

## Test Signals
Useful signals are successful `jq empty` validation, perf PMU table generation without parser warnings, `perf list` showing all 145 metric names and expected groups, `perf stat -M` runs for `TopdownL1`, `MemoryBound`, `Frontend`, `Flops`, `Power`, and `SoC`, and targeted checks that constrained metrics avoid invalid counter grouping. Formula smoke tests should include SMT enabled and disabled cases, workloads with low event counts, and systems where MSR or C-state events are unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellde/bdwde-metrics.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellde/cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellde/cache.json

## Purpose
Broadwell-DE core cache and offcore memory event catalog for perf. It defines 76 raw event aliases covering L1D replacement and pending misses, L2 requests/transitions/line fills, LLC reference and miss proxies, load hit levels, snoop outcomes, split locks, store queue fullness, offcore requests, and offcore response selection.

## Important APIs, Types, and Functions
The data entries use the perf PMU event schema: every event has `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, and `BriefDescription`. Optional fields model hardware restrictions and sampling behavior: `CounterMask` on 7 events, `AnyThread` on 1 event, `PEBS` plus `Data_LA` on 22 precise load-address events, and `Errata` on 20 entries. Important event families are `L1D`, `L1D_PEND_MISS`, `L2_RQSTS`, `L2_TRANS`, `LONGEST_LAT_CACHE`, `MEM_LOAD_UOPS_RETIRED`, `MEM_LOAD_UOPS_L3_HIT_RETIRED`, `MEM_LOAD_UOPS_L3_MISS_RETIRED`, `MEM_UOPS_RETIRED`, `OFFCORE_REQUESTS`, `OFFCORE_REQUESTS_OUTSTANDING`, `OFFCORE_RESPONSE`, and `SQ_MISC`.

## Control Flow
Perf parses this file into aliases that users can request directly or indirectly through metrics. For a direct event, perf programs the listed event select, umask, counter mask, PEBS flag, and offcore MSR configuration when present. For derived metrics in `bdwde-metrics.json`, these aliases become operands in formulas for L1/L2/L3 bound, DRAM bound, data sharing, contested accesses, split loads/stores, DTLB behavior, memory-level parallelism, and cache bandwidth.

## State and Persistence
The JSON has no runtime state. Persistent semantics live in event names and encodings. The `OFFCORE_RESPONSE` entry is stateful at programming time because perf must combine the event with an offcore response MSR value, while PEBS/Data_LA events create sampled records with data addresses when used in sampling mode.

## Dependencies and Integration
The file integrates with perf's x86 PMU JSON loader, the Broadwell-DE core PMU, PEBS support, and offcore response MSR programming. It is consumed heavily by the memory and top-down metrics file. Counter availability is constrained by `counter.json`, with most events accepting generic counters 0 through 3 and some pending-miss duration events limited to counter 2.

## Risks
Risks include incorrect offcore response programming, PEBS/Data_LA events being used on kernels or privilege settings that do not expose precise address records, errata-marked events being trusted too broadly, and alias overlap between hit/miss/reference events leading to double counting in derived formulas. Counter-specific events can fail to schedule when grouped with other counter-restricted events.

## Test Signals
Test with `jq empty`, `perf list` aliases for each major family, and `perf stat -e` smoke runs for L1D, L2, LLC, offcore, and split-lock events. Sampling tests should verify PEBS events produce data address records. Metric tests should confirm memory-bound formulas using `MEM_LOAD_UOPS_RETIRED.*`, `OFFCORE_REQUESTS_OUTSTANDING.*`, and `MEM_LOAD_UOPS_L3_*` expand without unresolved aliases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellde/cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellde/counter.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellde/counter.json

## Purpose
Broadwell-DE PMU counter inventory. It tells perf and related tooling how many fixed and generic counters exist for each core and uncore unit represented by this architecture directory.

## Important APIs, Types, and Functions
The schema has one object per PMU unit with `Unit`, `CountersNumFixed`, and `CountersNumGeneric`. The file declares `core` with 3 fixed and 4 generic counters, `CBOX` with 4 generic counters, `HA` with 4, `IRP` with 2, `PCU` with 4, `R2PCIe` with 4, `UBOX` with 2, and `iMC` with 4. There are no functions or executable code paths; the unit names are the interface.

## Control Flow
Perf tooling reads this metadata while building or loading event tables, then uses it to reason about event scheduling capacity and unit-specific counter constraints. Core event files reference counters explicitly, while uncore files reference units such as CBOX, HA, PCU, UBOX, R2PCIe, and iMC.

## State and Persistence
The file is static architecture metadata. Runtime state appears only when perf opens events and the kernel PMU driver allocates real counters. Persistence risk is that these counts become the assumed hardware contract for Broadwell-DE event scheduling.

## Dependencies and Integration
This file integrates all sibling Broadwell-DE event JSON files with perf's counter scheduler. It is especially important for groups and metrics that attempt to collect multiple events simultaneously, since the 4 generic core counters and smaller 2-counter IRP/UBOX units bound what can be measured without multiplexing.

## Risks
Incorrect counter counts cause misleading schedulability decisions, excessive multiplexing, or event-open failures. The file does not encode all event-specific counter restrictions, so it must be interpreted with each event's `Counter` field and metric constraints.

## Test Signals
Validation signals are `jq empty`, schema checks for all expected units, and perf event group tests that intentionally approach the core and uncore counter limits. Counter scheduling should be checked for both raw event groups and derived metric groups with constrained metrics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellde/counter.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellde/floating-point.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellde/floating-point.json

## Purpose
Broadwell-DE floating-point and SIMD event catalog for perf. It defines 22 events for retired scalar/vector floating-point arithmetic, 128-bit and 256-bit packed operations, FP assists, SIMD move elimination, AVX/SSE transition assists, and SIMD physical-register-file cancellation.

## Important APIs, Types, and Functions
Every entry provides `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, and `BriefDescription`. Optional fields include `PublicDescription` on 16 entries, `Errata` on 2, and one `CounterMask`. Event families are `FP_ARITH_INST_RETIRED` with 12 aliases, `FP_ASSIST` with 5, `MOVE_ELIMINATION` with 2, `OTHER_ASSISTS` with 2, and `UOP_DISPATCHES_CANCELLED` with 1.

## Control Flow
Perf converts these entries into raw event aliases. The metrics file consumes the arithmetic aliases to build `tma_fp_arith`, `tma_fp_scalar`, `tma_fp_vector`, `tma_fp_vector_128b`, `tma_fp_vector_256b`, instruction mix metrics, and GFLOPS estimates. Assist events contribute to heavy-operation and microcode-sequencer diagnosis.

## State and Persistence
The file is static. Runtime state is limited to counter values or PEBS-free sampling records collected by perf. The semantic persistence contract is that the retired arithmetic aliases continue to represent Broadwell-DE's scalar, packed, vector, and flop-count categories expected by top-down metrics.

## Dependencies and Integration
The file integrates with `bdwde-metrics.json` floating-point formulas and with pipeline events for assists, uop dispatch, and retirement. It depends on perf's core event parser and the Broadwell-DE PMU encodings.

## Risks
The biggest risks are formula misuse: retired FP instruction counts are not automatically equal to floating-point operations unless the metric weights match vector width and precision. Errata-marked events need conservative interpretation. AVX/SSE transition assists may be workload rare and can be hidden by multiplexing or sampling intervals.

## Test Signals
Use `jq empty`, `perf list | grep FP_ARITH_INST_RETIRED`, and controlled scalar SSE, AVX128, and AVX256 workloads to check the expected event families. Metric tests should validate `Flops`, `FpScalar`, and `FpVector` groups and compare rough GFLOPS output against known loop work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellde/floating-point.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellde/frontend.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellde/frontend.json

## Purpose
Broadwell-DE frontend event catalog. The 28 events describe branch address clears, decoded-stream-buffer to MITE switches, instruction cache hits/misses/stalls, instruction delivery queue activity, microcode sequencer delivery, and frontend under-delivery cycles.

## Important APIs, Types, and Functions
Each event uses the perf PMU event schema with `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, and `BriefDescription`. Optional fields include `CounterMask` on 15 entries, `EdgeDetect` on 2, `Invert` on 1, and `PublicDescription` on 23. Event families are `BACLEARS`, `DSB2MITE_SWITCHES`, `ICACHE`, `IDQ`, and `IDQ_UOPS_NOT_DELIVERED`.

## Control Flow
Perf uses these aliases directly for event counting and indirectly for top-down frontend metrics. The metrics file combines IDQ, DSB, MITE, ICACHE, BACLEARS, and DSB-to-MITE switch events into `tma_frontend_bound`, `tma_fetch_latency`, `tma_fetch_bandwidth`, `tma_dsb`, `tma_mite`, `tma_icache_misses`, `tma_lcp`, `tma_dsb_switches`, `tma_ms_switches`, and instruction fetch coverage metrics.

## State and Persistence
The file itself is static. Runtime state is counter-programming state, including edge detection, inversion, and counter masks for cycle-qualified aliases. Persistent meaning depends on the Broadwell-DE frontend pipeline model: DSB, MITE, IDQ, and microcode sequencer names are used as stable integration points by metric formulas.

## Dependencies and Integration
The catalog integrates with pipeline branch and machine-clear events to explain frontend latency after resteers. It also integrates with `metricgroups.json` groups such as `Frontend`, `FetchBW`, `FetchLat`, `DSB`, `DSBmiss`, `IcMiss`, and top-down frontend groups.

## Risks
Risks include misinterpreting cycles-with-condition events as event counts, grouping too many frontend aliases with limited counters, and under-delivery metrics being affected by SMT and backend backpressure. DSB and MITE attribution is model-specific and should not be generalized to other x86 generations.

## Test Signals
Run JSON validation, confirm aliases appear in `perf list`, and test with workloads that stress I-cache misses, large instruction footprints, branch resteers, and microcode-heavy instructions. Derived metrics should be checked through `perf stat -M Frontend,FetchBW,FetchLat`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellde/frontend.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellde/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellde/memory.json

## Purpose
Broadwell-DE memory-ordering, misalignment, load-latency, and transactional-memory event catalog. It defines 39 events covering HLE and RTM starts, commits, abort categories, transaction execution and memory abort reasons, machine clears from memory ordering, misaligned loads/stores, and `MEM_TRANS_RETIRED` load-latency thresholds.

## Important APIs, Types, and Functions
All events have `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, and `BriefDescription`. Optional fields include `PublicDescription` on 37 entries, `PEBS` on 10, `Data_LA` on 8 load-latency entries, `MSRIndex` and `MSRValue` on 8 latency-threshold events, and `Errata` on 8. Families are `HLE_RETIRED`, `RTM_RETIRED`, `TX_EXEC`, `TX_MEM`, `MEM_TRANS_RETIRED`, `MISALIGN_MEM_REF`, and `MACHINE_CLEARS`.

## Control Flow
Perf programs these aliases as raw events. The `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_*` aliases require latency-threshold MSR programming through the specified `MSRIndex`/`MSRValue`, then collect PEBS-capable load latency samples. Transactional-memory events are counted directly and can feed user analysis of TSX/HLE/RTM behavior. `MACHINE_CLEARS.MEMORY_ORDERING` is also used by top-down bad speculation and memory-ordering diagnosis.

## State and Persistence
The file is static, but some events create runtime PMU state beyond the event select register: latency events program an MSR threshold and can produce precise samples with data linear addresses. Transactional counters persist only during measurement and reflect workload use of HLE/RTM instructions.

## Dependencies and Integration
The memory file integrates with perf PEBS support, MSR programming support for load latency thresholds, pipeline machine-clear metrics, and cache/offcore files for broader memory-bound analysis. It complements but does not replace cache hierarchy events.

## Risks
Risks include latency-threshold events failing when MSR programming is unavailable, PEBS/Data_LA data being blocked by kernel permissions, TSX events being irrelevant or unavailable when TSX is disabled by microcode or kernel policy, and errata affecting transaction or latency counts. Misaligned and memory-ordering events are narrow signals that need context from cache and pipeline metrics.

## Test Signals
Validate JSON, list all `HLE_RETIRED`, `RTM_RETIRED`, `TX_*`, and `MEM_TRANS_RETIRED` aliases, and run `perf stat` on workloads with misaligned memory access, lock elision or RTM when available, and controlled load-latency patterns. PEBS tests should verify that latency-threshold events produce precise sample records with data addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellde/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellde/metricgroups.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellde/metricgroups.json

## Purpose
Metric group description map for Broadwell-DE perf metrics. It gives human-readable descriptions for 124 group keys used by `bdwde-metrics.json`, including top-down hierarchy groups, issue-oriented groups, category groups, and spreadsheet-derived group names.

## Important APIs, Types, and Functions
Unlike the event files, this file is a JSON object rather than an array. Each key is a metric group name and each value is its description. Important keys include `TopdownL1` through `TopdownL6`, `tma_L1_group` through `tma_L6_group`, category groups such as `Backend`, `Frontend`, `MemoryBound`, `Flops`, `Power`, `SoC`, and contributor groups such as `tma_backend_bound_group`, `tma_fetch_latency_group`, `tma_memory_bound_group`, `tma_ports_utilization_group`, and `tma_store_bound_group`.

## Control Flow
Perf loads this map as metadata for presentation and discovery. Metric definitions assign semicolon-separated `MetricGroup` values; this file lets perf display those groups with descriptions and helps users discover related metrics through group names. It does not schedule counters or evaluate expressions directly.

## State and Persistence
The file is static descriptive state. The persistence contract is name alignment: every group key that metrics reference should either be present here or intentionally omitted, and descriptions should remain accurate for the model-specific Broadwell-DE metric set.

## Dependencies and Integration
The file depends on `bdwde-metrics.json` for actual usage. It bridges top-down metric names to user-facing `perf list` and `perf stat -M <group>` discovery. It also preserves compatibility with group names from Intel's top-down microarchitecture analysis spreadsheet and perf's lowercase `tma_*` naming convention.

## Risks
Risks are mostly documentation and discoverability issues: stale group descriptions, unused group keys, missing keys for metrics, or inconsistent spelling such as `MachineClears` versus `Machine_Clears` can make metric discovery confusing. Because it is an object, array-oriented validation scripts can incorrectly reject it unless they handle this file's schema separately.

## Test Signals
Run `jq empty`, verify object shape with `jq type`, compare all `MetricGroup` tokens from `bdwde-metrics.json` against this map, and check `perf list` output for useful group descriptions. Group smoke tests should include `TopdownL1`, `TopdownL2`, `Frontend`, `Backend`, `MemoryBound`, `Flops`, and a few `tma_*_group` names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellde/metricgroups.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellde/other.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellde/other.json

## Purpose
Small Broadwell-DE catalog for miscellaneous privilege-level and lock-duration events that do not fit the main cache, memory, frontend, floating-point, or pipeline buckets. It defines 4 events: `CPL_CYCLES.RING0`, `CPL_CYCLES.RING0_TRANS`, `CPL_CYCLES.RING123`, and `LOCK_CYCLES.SPLIT_LOCK_UC_LOCK_DURATION`.

## Important APIs, Types, and Functions
All entries use standard perf PMU fields: `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, and `PublicDescription`. One event uses `CounterMask` plus `EdgeDetect` for ring-0 transition counting. There are no functions; the alias names are the exported interface.

## Control Flow
Perf programs these events directly when requested. Metrics may use privilege cycle information for OS/kernel utilization analysis, while split-lock uncacheable lock duration complements cache lock and split-lock signals from the cache file.

## State and Persistence
The file has no runtime state. Runtime behavior is simple counter collection with one transition-style event that depends on edge detection. Persistent semantics are privilege-level cycle attribution and split-lock duration visibility.

## Dependencies and Integration
The file integrates with system and OS-oriented metrics in `bdwde-metrics.json`, especially kernel utilization and lock-contention analysis. It depends on perf's support for event masks, counter masks, and edge detection.

## Risks
Privilege cycle interpretation depends on kernel/user filtering and workload context. Ring transition counts can be misunderstood as total kernel time, and split-lock duration is a narrow signal that should be correlated with `SQ_MISC.SPLIT_LOCK` and lock-cycle events from `cache.json`.

## Test Signals
Validate JSON, confirm the four aliases are listed by perf, run privilege-level cycle counts on user-only and syscall-heavy workloads, and run split-lock tests only in controlled environments where platform policy allows observation without disrupting the system.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellde/other.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellde/pipeline.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellde/pipeline.json

## Purpose
Broadwell-DE pipeline, branch, retirement, execution-port, resource-stall, and cycle-activity event catalog. It defines 137 events used to analyze branch behavior, bad speculation, uop issue/execute/retire flow, stalls, port pressure, machine clears, load blocking, loop stream detector behavior, and core clocking.

## Important APIs, Types, and Functions
Entries use the standard perf PMU event fields. All 137 have `EventName`, `Counter`, `SampleAfterValue`, and `BriefDescription`; 133 include `EventCode`, 132 include `UMask`, 94 include `PublicDescription`, 32 include `CounterMask`, 13 include `AnyThread`, 13 include `PEBS`, 6 include `Invert`, 4 include `Errata`, and 2 include `EdgeDetect`. Major event families include `BR_INST_EXEC`, `BR_INST_RETIRED`, `BR_MISP_EXEC`, `BR_MISP_RETIRED`, `CPU_CLK_UNHALTED`, `CPU_CLK_THREAD_UNHALTED`, `CYCLE_ACTIVITY`, `INST_RETIRED`, `INT_MISC`, `LD_BLOCKS`, `LSD`, `MACHINE_CLEARS`, `RESOURCE_STALLS`, `RS_EVENTS`, `UOPS_DISPATCHED_PORT`, `UOPS_EXECUTED`, `UOPS_EXECUTED_PORT`, `UOPS_ISSUED`, and `UOPS_RETIRED`.

## Control Flow
Perf expands aliases from this file into event programming requests. The derived metrics file consumes these events throughout the top-down hierarchy: branch and machine-clear events feed bad speculation and resteer metrics; uop issued/retired/executed events feed slot, retiring, and execution efficiency metrics; port events feed port utilization; cycle activity and resource stalls feed backend and memory/core-bound metrics.

## State and Persistence
The file is static PMU metadata. Runtime state includes counter allocation, any-thread counting for physical-core views, PEBS sampling for selected retired branch or instruction events, edge detection for transition events, and inversion/counter-mask qualifiers for cycle conditions. Persistent semantics must track Broadwell-DE pipeline naming and event encodings.

## Dependencies and Integration
This file is central to `bdwde-metrics.json` and integrates with frontend, cache, memory, floating-point, and other event files. Counter pressure is significant because many formulas combine events from this file with cache and frontend operands; `counter.json` and metric constraints determine whether metrics can be measured together or require multiplexing.

## Risks
Risks include grouped measurements exceeding the 4 generic core counters, SMT and any-thread aliases being mixed incorrectly, PEBS events being treated as ordinary precise-free counters, and cycle-qualified aliases being misread as raw occurrence counts. Port utilization metrics are sensitive to event family choice, and bad speculation metrics can be distorted by machine clears, recovery cycles, and multiplexing.

## Test Signals
Run JSON validation, check `perf list` for all major families, and use synthetic workloads for predictable branch mispredicts, port pressure, divider activity, memory stalls, and retirement throughput. Metric smoke tests should include `TopdownL1`, `BadSpec`, `PortsUtil`, `Pipeline`, `Branches`, `Retire`, and backend/core-bound groups, with special attention to SMT and counter multiplexing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellde/pipeline.json -->
