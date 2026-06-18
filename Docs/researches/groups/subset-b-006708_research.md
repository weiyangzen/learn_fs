# subset-b-006708 research

Grouped research for Sapphire Rapids perf PMU event definition files under `sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sapphirerapids/`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sapphirerapids/cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sapphirerapids/cache.json

## Purpose
`cache.json` is a declarative Sapphire Rapids core PMU event catalog for cache, memory-source, offcore, snoop, prefetch, and selected store-queue behavior. It contains 132 event objects consumed by perf's PMU event tooling, not executable code. The file lets users name events such as `L2_RQSTS.DEMAND_DATA_RD_MISS`, `MEM_LOAD_RETIRED.L3_MISS`, `OCR.READS_TO_CORE.REMOTE`, and `OFFCORE_REQUESTS_OUTSTANDING.DEMAND_DATA_RD` instead of spelling raw event select, umask, MSR filter, counter, and sampling attributes.

## Important APIs, types, and schema fields
The effective API is the JSON event schema used by `tools/perf/pmu-events/jevents.py` and exposed through `perf list` / event parsing. Common fields are `EventName`, `EventCode`, `UMask`, `Counter`, `BriefDescription`, `PublicDescription`, and `SampleAfterValue`. This file also uses `CounterMask`, `EdgeDetect`, `Deprecated`, `MSRIndex`, `MSRValue`, and `Data_LA`. `MSRIndex`/`MSRValue` are central for `OCR.*` offcore response filters using `0x1a6,0x1a7`; `Data_LA` marks data linear-address capable load/store events; `Deprecated` preserves aliases while steering users to replacement names.

## Control flow and integration
At build time perf's PMU event generator parses this JSON with the rest of the Sapphire Rapids model directory and emits compiled C tables. At runtime `perf list` prints the names/descriptions, and `perf stat`/`perf record` resolve names into raw encodings plus optional offcore MSR programming. There is no in-file execution order; dependencies are by schema and by event-family naming. Offcore response events are a two-part programming contract: `EventCode` `0x2A,0x2B` and `UMask` `0x1` select OCR counting while `MSRValue` chooses demand code/data/RFO, hardware prefetch, streaming write, local/remote DRAM, PMM, cache, snoop, and SNC response filters.

## State and persistence behavior
The file is static source data checked into the perf tree. It persists hardware encodings, descriptions, aliases, and sampling defaults. Runtime counter state lives in CPU PMU registers and offcore MSRs, not in this JSON. Any edit changes generated perf event tables and can affect user-visible event names, raw event encodings, PEBS/address-sampling affordances, and default sampling periods.

## Dependencies
This file depends on the Sapphire Rapids core PMU programming model, perf's JSON event schema, and `counter.json` for available core generic/fixed counter capacity. It integrates with sibling event groups (`memory.json`, `pipeline.json`, `frontend.json`, `floating-point.json`, `other.json`) and model mapping files that cause Sapphire Rapids CPUs to select this directory. Many event families are tied to Intel-specific facilities: offcore response MSRs, PEBS data source/load address sampling, SNC topology, and PMM naming.

## Notable event coverage
Major families are `OCR` (43 entries), `L2_RQSTS` (17), `OFFCORE_REQUESTS_OUTSTANDING` (8), `MEM_INST_RETIRED` (8), `MEM_LOAD_RETIRED` (8), `CORE_SNOOP_RESPONSE` (7), `L1D_PEND_MISS` (6), `SW_PREFETCH_ACCESS` (5), and smaller L1/L2/LLC and store-queue groups. There are aliases such as `L2_REQUEST.ALL` for `L2_RQSTS.REFERENCES` and `L2_REQUEST.MISS` for `L2_RQSTS.MISS`. `L1D_PEND_MISS.L2_STALL` and `OFFCORE_REQUESTS_OUTSTANDING.ALL_DATA_RD` are deprecated compatibility names.

## Risks and edge cases
Offcore events are high risk because incorrect `MSRValue` filters silently produce plausible but wrong locality, snoop, PMM, or SNC counts. Aliases and deprecations must remain consistent so scripts using older names continue to work while users can discover replacement names. Counter constraints matter: most events use core counters `0,1,2,3`, while load-retired PEBS style events also carry `Data_LA`; invalid counter masks or address-sampling tags can break `perf record` use cases. Descriptions contain hardware-specific semantics such as "true miss", "SNC", and "single snoop response counts on all hyperthreads"; these are part of the user contract and should not be simplified casually.

## Test signals
Useful validation is `jq empty cache.json`, `tools/perf/pmu-events/jevents.py` generation, `perf test` coverage for PMU event parsing, and `perf list` on a build that includes the Sapphire Rapids map. Spot checks should verify representative raw encodings for `L2_RQSTS.*`, deprecated replacement names, `Data_LA` events, and OCR MSR filters. Hardware validation on Sapphire Rapids should compare `perf stat -e` counts against known cache/memory microbenchmarks for local DRAM, remote DRAM, L2 hits/misses, and snoop-heavy sharing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sapphirerapids/cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sapphirerapids/counter.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sapphirerapids/counter.json

## Purpose
`counter.json` declares the number of programmable and fixed counters available for each Sapphire Rapids PMU unit known to perf. It is a compact capacity table with 16 objects. The core entry declares 4 fixed counters and 8 generic counters, while uncore units such as `PCU`, `IIO`, `iMC`, `M2M`, `UPI`, `CHA`, `CXLDP`, `MCHBM`, and others declare their generic counter counts.

## Important APIs, types, and schema fields
Each object has `Unit`, `CountersNumFixed`, and `CountersNumGeneric`. The schema is consumed as PMU metadata rather than an event list. `Unit` names must match perf's PMU naming/model vocabulary, and the numeric fields are stored as strings consistent with other pmu-events JSON files.

## Control flow and integration
The build-time event generator reads this file alongside the model's event JSON. Runtime perf code can use the generated metadata to reason about how many events can be scheduled on a PMU class before multiplexing or constraint failures. The file does not define encodings; it constrains capacity for events defined in this directory and other Sapphire Rapids uncore JSON files.

## State and persistence behavior
This is static hardware topology metadata. It persists the expected counter inventory for Sapphire Rapids PMUs: `core` has 8 generic and 4 fixed counters; most listed uncore boxes have 4 generic counters; `IRP` and `UBOX` have 2; `CXLCM` has 8. Runtime counter allocation and multiplexing state belongs to perf and the kernel PMU drivers.

## Dependencies
The table depends on kernel/perf PMU unit names and Sapphire Rapids uncore hardware definitions. It integrates with all Sapphire Rapids event files because their `Counter` fields must be meaningful relative to these counts. It also informs user-facing event scheduling expectations for CXL, HBM, mesh, memory controller, PCIe, power-control, and core PMUs.

## Risks and edge cases
Wrong counter counts cause scheduler confusion: perf may accept impossible groups, over-multiplex, reject valid groups, or display misleading PMU capacity. Unit-name drift is also risky; a typo creates orphan metadata that generated tables may not associate with the intended PMU. Because values are strings, tests should catch nonnumeric text and accidental integer/string shape changes.

## Test signals
Validate JSON syntax and that each row has exactly the three expected keys. Compare unit names against Sapphire Rapids uncore event files and generated PMU tables. On hardware, `perf list` plus grouped `perf stat` experiments can reveal whether counter counts match actual scheduling constraints, especially for `core`, `CHA`, `iMC`, `CXLCM`, and `UBOX`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sapphirerapids/counter.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sapphirerapids/floating-point.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sapphirerapids/floating-point.json

## Purpose
`floating-point.json` defines 28 Sapphire Rapids core PMU events for floating-point assists, divide activity, FP dispatch ports, retired SSE/AVX/AVX-512 arithmetic instructions, and half-precision arithmetic. It supports `perf stat` and `perf record` analysis of scalar/vector FP intensity and FP pipeline behavior.

## Important APIs, types, and schema fields
This file uses the standard event object fields `EventName`, `EventCode`, `UMask`, `Counter`, `CounterMask`, `BriefDescription`, `PublicDescription`, and `SampleAfterValue`. `Counter` is consistently `0,1,2,3,4,5,6,7`, matching the 8 generic core counters in `counter.json`. `CounterMask` is used by `ARITH.FPDIV_ACTIVE` to count cycles where the divide unit is active.

## Control flow and integration
Perf's PMU event generator compiles these JSON entries into the Sapphire Rapids event table. At runtime, event names such as `FP_ARITH_INST_RETIRED.512B_PACKED_SINGLE` resolve to event select `0xc7` plus the appropriate umask. The `FP_ARITH_DISPATCHED.PORT_*` and `V*` pairs are aliases over identical encodings, so event lookup must preserve both names while programming the same hardware selector.

## State and persistence behavior
The file stores static FP event metadata and descriptions. Hardware counts are maintained in core PMU counters. The descriptions include semantic multipliers: packed single/double events describe how many operations each event represents and warn that some FMA/DPP instructions count twice. Several retired FP events require DAZ and FTZ flags in MXCSR for reliable use; that runtime precondition is documented here rather than enforced by perf.

## Dependencies
The entries depend on Sapphire Rapids FP PMU semantics, vector ISA support, and perf's core event parser. The file integrates with top-down and HPC metrics through event names like `FP_ARITH_INST_RETIRED.*`, and with `metricgroups.json` groups such as `Flops`, `FpScalar`, `FpVector`, `HPC`, `tma_fp_arith_group`, and `tma_fp_vector_group`.

## Risks and edge cases
The biggest correctness risk is interpreting counts as FLOPs without applying width and instruction semantics. The retired arithmetic events count instructions or operations depending on the description, and FMA/DPP can double count computational work. Alias pairs (`PORT_0`/`V0`, `PORT_1`/`V1`, `PORT_5`/`V2`) must stay synchronized. Half-precision entries in `FP_ARITH_INST_RETIRED2.*` have minimal public descriptions, so downstream documentation or metrics should avoid inventing semantics not present in the source.

## Test signals
Validate JSON syntax and generated tables. `perf list fp` on a Sapphire Rapids-enabled build should show all 28 names. Microbenchmarks with scalar double/single, 128/256/512-bit vector loops, half-precision operations, and divides can sanity-check selector/umask behavior. Metric tests should confirm aliases resolve to identical raw encodings and that FP events can schedule on generic core counters 0-7.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sapphirerapids/floating-point.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sapphirerapids/frontend.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sapphirerapids/frontend.json

## Purpose
`frontend.json` defines 43 Sapphire Rapids core PMU events for instruction fetch/decode behavior: branch clears, length-changing prefix stalls, microcode sequencer busy time, DSB-to-MITE switches, frontend-retired latency and miss classification, instruction-cache stalls, IDQ delivery, and frontend bubble aliases.

## Important APIs, types, and schema fields
The file uses `EventName`, `EventCode`, `UMask`, `Counter`, `BriefDescription`, `PublicDescription`, and `SampleAfterValue`, plus modifier fields `CounterMask`, `EdgeDetect`, `Invert`, `MSRIndex`, and `MSRValue`. `FRONTEND_RETIRED.*` events use event `0xc6`, umask `0x1`, counters `0-7`, and MSR `0x3F7` with different values to select DSB misses, ITLB/L1I/L2/STLB misses, unknown branches, microcode-sequencer flows, and latency thresholds.

## Control flow and integration
During perf build, these entries become generated event tables. At runtime they feed `perf list`, event parsing, and top-down frontend analysis. Some families are direct counters (`IDQ.*`, `ICACHE_*`, `DECODE.*`), while `FRONTEND_RETIRED.*` relies on extra MSR programming to select a frontend retirement classification. Alias families `IDQ_BUBBLES.*` and `IDQ_UOPS_NOT_DELIVERED.*` map to the same encodings and must remain aligned.

## State and persistence behavior
The JSON persists stable event names, encodings, and threshold definitions. Runtime state is in PMU counters and frontend classification MSRs. Latency threshold events encode policy in `MSRValue`, for example `LATENCY_GE_1` through `LATENCY_GE_512`; edits change how users classify fetch starvation length.

## Dependencies
Dependencies include Sapphire Rapids frontend PMU facilities, perf's MSR-extra event support, and metric expressions/groups that consume frontend events. Integration points include `builtin-list.c` for listing, metric parsing tests, top-down frontend-bound metrics, and sibling pipeline events such as branch mispredicts, machine clears, and topdown slots.

## Risks and edge cases
MSR-coded frontend events are easy to break by changing only the name or description while leaving an inconsistent `MSRValue`. `CounterMask`, `Invert`, and `EdgeDetect` change cycle versus period/count semantics for events such as `ICACHE_DATA.STALL_PERIODS`, `IDQ.MS_SWITCHES`, and frontend bubble cycle variants. Alias drift between `IDQ_BUBBLES` and `IDQ_UOPS_NOT_DELIVERED` would confuse existing scripts. Descriptions distinguish frontend starvation not interrupted by backend stalls, so wording matters for top-down interpretation.

## Test signals
Run JSON validation and the perf PMU event generator. `perf list frontend` should expose all families, including aliases. On hardware, instruction-cache miss loops, branch-heavy code, large-code-footprint workloads, and microcode-heavy instruction streams can validate event directionality. Unit-level tests should assert `FRONTEND_RETIRED.*` rows keep `MSRIndex` `0x3F7` and expected threshold `MSRValue` patterns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sapphirerapids/frontend.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sapphirerapids/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sapphirerapids/memory.json

## Purpose
`memory.json` defines 55 Sapphire Rapids core PMU events for memory stalls, load latency sampling, DRAM/local/remote/SNC/PMM offcore responses, L3-miss demand reads, RTM retirement, and TSX memory abort causes. It complements `cache.json`: `cache.json` covers cache hits/snoops/cache-source responses, while this file emphasizes memory-service paths and latency.

## Important APIs, types, and schema fields
Event objects use `EventName`, `EventCode`, `UMask`, `Counter`, `BriefDescription`, `PublicDescription`, and `SampleAfterValue`, with `CounterMask`, `MSRIndex`, `MSRValue`, and `Data_LA` where needed. `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_*` events use event `0xcd`, umask `0x1`, counters `1-7`, MSR `0x3F6`, threshold-specific `MSRValue`, and `Data_LA=1`. OCR memory-response events use `EventCode` `0x2A,0x2B`, `UMask` `0x1`, and offcore MSRs `0x1a6,0x1a7`.

## Control flow and integration
Build-time generation turns the JSON into perf's Sapphire Rapids PMU table. Runtime event parsing programs normal core event selectors and, for OCR or load-latency threshold events, the associated MSR filter/threshold. `perf record` can use `Data_LA` events for address-aware sampling. Top-down memory-bound metrics and memory bandwidth/latency groups can consume events such as `MEMORY_ACTIVITY.STALLS_L3_MISS`, `OCR.READS_TO_CORE.LOCAL_DRAM`, and `OFFCORE_REQUESTS_OUTSTANDING.L3_MISS_DEMAND_DATA_RD`.

## State and persistence behavior
The file persists hardware event encodings and memory locality semantics. It does not persist measurements. Runtime state includes PEBS/load-latency sampling configuration, offcore response MSR values, transactional memory status, and counter values. The threshold ladder for load latency (`GT_4` through `GT_1024`) is encoded as data and should be treated as an ordered set.

## Dependencies
Dependencies include Sapphire Rapids offcore response semantics, PEBS load latency facility, RTM/TSX PMU events, perf's extra-MSR event handling, and the core counter inventory from `counter.json`. This file integrates with `cache.json` OCR naming conventions and with metric groups such as `MemoryBound`, `MemoryBW`, `MemoryLat`, `MemOffcore`, `tma_memory_bound_group`, `tma_mem_latency_group`, and `tma_dram_bound_group`.

## Risks and edge cases
OCR filter mistakes can swap local/remote, DRAM/PMM, or SNC-close/distant meanings with no syntax failure. Load-latency events are constrained to counters `1-7`, not counter `0`, and have address-sampling implications via `Data_LA`; violating that shape can break PEBS workflows. RTM/TSX event availability depends on platform/kernel support and CPU configuration. Some names use historical technologies such as PMM, so downstream metrics should handle platforms where the hardware path is absent or counts remain zero.

## Test signals
Run `jq empty`, generated-table builds, and perf PMU parse tests. Hardware validation should include pointer-chasing latency tests, local versus remote NUMA memory access, SNC configurations when available, RTM/TSX microbenchmarks, and `perf record` checks for load-latency address sampling. Static checks should assert all `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_*` thresholds use `MSRIndex` `0x3F6`, `Data_LA=1`, and counters `1-7`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sapphirerapids/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sapphirerapids/metricgroups.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sapphirerapids/metricgroups.json

## Purpose
`metricgroups.json` maps Sapphire Rapids metric group names to short descriptions. Unlike the event JSON files, it is a JSON object rather than an array of event records. It provides grouping labels used by perf's metric listing and UI paths so users can discover metrics by categories such as `Frontend`, `Backend`, `MemoryBound`, `Flops`, `TopdownL1`, and detailed `tma_*_group` categories.

## Important APIs, types, and schema fields
The API is a string-to-string object: keys are metric group identifiers, values are descriptions. There are 143 group entries. Most legacy-style groups share the description "Grouping from Top-down Microarchitecture Analysis Metrics spreadsheet"; top-down level groups use descriptions such as "Metrics for top-down breakdown at level 1"; category-specific groups use "Metrics contributing to ... category"; issue groups use "Metrics related by the issue $...".

## Control flow and integration
The perf PMU event generator ingests this object together with metrics files for the same CPU model. Runtime `perf list metricgroups` and metric browsing code can display group names and descriptions. `builtin-list.c` contains logic for metric group printing, filtering, and JSON output; this file supplies the group-name vocabulary and display text. There is no control flow within the file; its keys are lookup labels referenced by metric definitions elsewhere.

## State and persistence behavior
This is static metadata. It persists grouping taxonomy, not metric formulas or measurements. Changing a key can orphan metrics that reference the old group name or alter `perf list` filtering behavior. Changing descriptions affects user-facing help and discoverability but not counter programming.

## Dependencies
The file depends on consistency with Sapphire Rapids metric definition files and perf metric parsing/listing code. It integrates with top-down metrics, issue-oriented TMA groups (`tma_issue*`), and broad group labels used by user workflows (`HPC`, `Server`, `Power`, `SoC`, `Pipeline`, `Mem`, `Offcore`, `Branches`, `CacheHits`, `CacheMisses`).

## Risks and edge cases
Because this file has a different JSON shape, tools that assume every pmu-events JSON file is an array of objects will fail. Group-name drift is the main functional risk: metric expressions can still parse, but list filtering and grouping become incomplete or misleading. Duplicate-looking taxonomy exists intentionally, for example `TopdownL1` and `tma_L1_group`, `MemoryBW` and `Memory_BW`, `MachineClears` and `Machine_Clears`; cleanup that normalizes names may break compatibility.

## Test signals
Validate with `jq type` expecting `object`, not `array`. Cross-check that metric files referencing groups use keys present here. `perf list metricgroups`, `perf list --json metricgroups`, and metric parser tests should show these labels without crashes. Static tests should preserve intentionally similar names and verify no group value is empty.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sapphirerapids/metricgroups.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sapphirerapids/other.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sapphirerapids/other.json

## Purpose
`other.json` defines six Sapphire Rapids core PMU events that do not fit cleanly into the cache, frontend, memory, floating-point, or pipeline category files. The coverage is page-fault assists, hardware interrupts, a streaming-write OCR catch-all, and cycles where the allocation queue is full.

## Important APIs, types, and schema fields
Rows use `EventName`, `EventCode`, `UMask`, `Counter`, `BriefDescription`, `PublicDescription`, and `SampleAfterValue`. `XQ.FULL_CYCLES` uses `CounterMask=1` to count cycles. `OCR.STREAMING_WR.ANY_RESPONSE` uses the offcore response pattern with `EventCode` `0x2A,0x2B`, `UMask` `0x1`, `MSRIndex` `0x1a6,0x1a7`, and `MSRValue` `0x10800`.

## Control flow and integration
Build-time generation includes these events in the same Sapphire Rapids PMU table as the larger category files. Runtime users see names such as `ASSISTS.PAGE_FAULT`, `HW_INTERRUPTS.RECEIVED`, and `XQ.FULL_CYCLES` through `perf list`; event parsing then programs core counters or OCR MSRs as appropriate. The file acts as an overflow category while still following the same schema contract.

## State and persistence behavior
The file persists a small set of hardware encodings and descriptions. Runtime interrupt, assist, queue, and streaming-write counts are held in PMU counters and offcore MSR state. There is no local state or generated artifact in this source file beyond perf's normal build output.

## Dependencies
Dependencies include Sapphire Rapids core PMU event selectors for assists and interrupts, the offcore response MSRs for streaming writes, and perf's event generator. It integrates with broader metric groups such as `OS`, `Pipeline`, `MemOffcore`, and `tma_assists_group` when metrics reference these event names.

## Risks and edge cases
Small category files are easy to overlook during schema migrations. `OCR.STREAMING_WR.ANY_RESPONSE` must stay consistent with streaming-write events in `cache.json` and `memory.json`. Interrupt and page-fault assist counts are workload and OS sensitive, so tests should avoid asserting exact values outside controlled microbenchmarks. `XQ.FULL_CYCLES` depends on `CounterMask` semantics; dropping that field changes count meaning from cycles to raw occurrences.

## Test signals
Use `jq empty`, generated PMU table builds, and `perf list` filtering for `ASSISTS`, `HW_INTERRUPTS`, `OCR.STREAMING_WR`, and `XQ`. Runtime smoke tests can use interrupt-heavy workloads, page-fault inducing memory access, and streaming-store loops to check that counts are nonzero in expected scenarios. Static checks should verify the streaming-write OCR row retains `MSRIndex` and `MSRValue`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sapphirerapids/other.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sapphirerapids/pipeline.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sapphirerapids/pipeline.json

## Purpose
`pipeline.json` defines 124 Sapphire Rapids core PMU events for general pipeline analysis: arithmetic divider activity, assists, branch retirement and misprediction, unhalted clocks, cycle activity, execution port utilization, instruction/uop retirement, machine clears, vector integer instructions, load blocks, LSD, resource stalls, reservation station empty states, top-down slots, dispatched/executed/issued/retired uops, and AMX busy time.

## Important APIs, types, and schema fields
Rows use standard perf event fields plus modifier fields `CounterMask`, `EdgeDetect`, `Invert`, `Deprecated`, `MSRIndex`, and `MSRValue`. Fixed-counter events are present: `CPU_CLK_UNHALTED.THREAD` uses fixed counter 1, `CPU_CLK_UNHALTED.REF_TSC` fixed counter 2, and `TOPDOWN.SLOTS` fixed counter 3. General-counter variants such as `CPU_CLK_UNHALTED.THREAD_P`, `REF_TSC_P`, and `TOPDOWN.SLOTS_P` are also defined. Several cycle events use counter masks and inversion to distinguish busy, idle, or stall cycles.

## Control flow and integration
Perf's generator compiles the event records; runtime event lookup maps names to raw event select/umask/fixed counter encodings. These events are foundational for `perf stat`, top-down analysis, IPC/uop metrics, branch diagnostics, and execution-port studies. `UOPS_RETIRED.MS` and `INT_MISC.UNKNOWN_BRANCH_CYCLES` use MSR `0x3F7` filters, while topdown and CPU clock fixed counters depend on architectural PMU support.

## State and persistence behavior
The file persists the core pipeline event vocabulary and raw encodings. Measurement state is in core PMU counters, fixed counters, and extra MSRs at runtime. Deprecated rows preserve compatibility: `ARITH.DIVIDER_ACTIVE`, `ARITH.FP_DIVIDER_ACTIVE`, `ARITH.INT_DIVIDER_ACTIVE`, `RS_EMPTY.COUNT`, `RS_EMPTY.CYCLES`, `UOPS_EXECUTED.STALL_CYCLES`, and `UOPS_RETIRED.STALL_CYCLES` point to replacement names.

## Dependencies
Dependencies include the Sapphire Rapids PMU programming model, architectural fixed counters, perf's top-down metric code, metric group taxonomy, and sibling files for memory/frontend/floating-point details. `counter.json` supplies the core counter capacity that makes fixed versus generic event scheduling meaningful. This file integrates with broad metric groups such as `Pipeline`, `Branches`, `Retire`, `PortsUtil`, `TopdownL1`, `Backend`, `BadSpec`, and many `tma_*` categories.

## Risks and edge cases
Pipeline events are heavily reused by metrics, so renaming or changing encodings has broad blast radius. Fixed-counter rows have different shape from generic events and can be broken by validators that require `EventCode`. Deprecated aliases must stay present until intentionally removed because scripts may depend on them. Counter masks and inversion fields materially change cycle semantics for stall/empty/threshold events. Top-down slot events must remain consistent with perf's metric formulas, or high-level TMA percentages become wrong while raw counts still look valid.

## Test signals
Static validation should parse JSON, generate PMU tables, check deprecated replacement text, verify fixed-counter rows, and ensure alias/replacement encodings remain coherent. Runtime validation should include `perf stat` smoke tests for cycles, instructions, topdown slots, branch events, uop dispatch ports, divider loops, AMX workloads where available, and branch-mispredict microbenchmarks. Perf metric tests should cover top-down formulas that consume `TOPDOWN.*`, `UOPS_*`, `CPU_CLK_UNHALTED.*`, branch, and machine-clear events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sapphirerapids/pipeline.json -->
