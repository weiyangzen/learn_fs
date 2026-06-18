<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwell/bdw-metrics.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwell/bdw-metrics.json

## Purpose
Broadwell PMU metric definition table for Linux `perf`. The file is a JSON array of 146 derived metrics used by the perf PMU-events generator to expose human-readable `perf stat -M ...` metrics for Broadwell x86 systems. It does not implement executable control flow; its behavior is expressed through perf metric schema fields and formulas.

The metrics cover power residency, SMI accounting, top-down microarchitecture analysis (`tma_*`), memory hierarchy behavior, floating-point throughput, frontend/backend bottlenecks, branch speculation, SMT/core-level normalization, OS/kernel utilization, and SoC/uncore bandwidth/frequency views. Many metrics are grouped under `TopdownL1` through `TopdownL6`, `TmaL*`, `Mem`, `Flops`, `Power`, `Summary`, `Pipeline`, `PortsUtil`, `FetchLat`, and related issue tags.

## Important APIs, Types, and Functions
The data contract is the perf PMU-events metric object schema:

- `MetricName`: exported symbolic metric name such as `tma_frontend_bound`, `tma_backend_bound`, `tma_info_thread_ipc`, `C7_Pkg_Residency`, or `UNCORE_FREQ`.
- `MetricExpr`: perf expression language formula. Expressions reference raw events from neighboring Broadwell event files, MSR/PMU aliases such as `msr@tsc@`, cstate aliases such as `cstate_pkg@c2-residency@`, uncore events such as `UNC_CLOCK.SOCKET`, constants like `#SMT_on` and `#num_cpus_online`, and helper metrics defined in this same file.
- `MetricGroup`: semicolon-separated grouping/indexing tags used by perf to list and select related metrics.
- `BriefDescription`: short text shown by perf metric listing/help.
- `ScaleUnit`: optional output unit, commonly `100%` for ratios or `1SMI#` for SMI count.

There are no functions or local types, but the metrics form a dependency graph. Base helper metrics such as `tma_info_thread_clks`, `tma_info_core_core_clks`, `tma_info_thread_slots`, `tma_info_system_time`, and `tma_info_inst_mix_instructions` feed higher-level ratios. Level-1 top-down categories are `tma_frontend_bound`, `tma_bad_speculation`, `tma_retiring`, and `tma_backend_bound`; later levels refine them into branch resteers, memory bound, core bound, frontend latency/bandwidth, ports utilization, FP vector/scalar use, and cache/TLB/store bottlenecks.

## Control Flow
Runtime control is owned by perf, not this file. During build or installation, perf's PMU-events tooling ingests this JSON with the other Broadwell tables and emits compiled metric maps. At collection time, perf resolves a requested metric group/name, parses `MetricExpr`, schedules the referenced events, substitutes runtime constants such as SMT state and CPU count, evaluates conditional expressions, and scales the result according to `ScaleUnit`.

The implicit control flow within the data is dependency ordering. For example, `tma_backend_bound` depends on the other L1 top-down metrics, `tma_core_bound` subtracts `tma_memory_bound` from backend bound, `tma_fetch_bandwidth` subtracts `tma_fetch_latency` from frontend bound, and detailed memory metrics reuse helper quantities like `tma_info_memory_load_miss_real_latency`. Conditional expressions handle SMT/core-wide differences, such as formulas switching between `CPU_CLK_UNHALTED.THREAD_ANY`, `CPU_CLK_UNHALTED.THREAD`, or divided core-wide counts.

## State and Persistence Behavior
The file is static architecture metadata. Persistent state is the checked-in JSON content and any generated perf tables derived from it. At runtime, metric values are ephemeral and depend on scheduled PMU readings, MSR readings, cstate counters, uncore counters, elapsed time, SMT topology, CPU online count, and multiplexing accuracy. No state is written back to this JSON.

Because metrics reference each other by name, renames or removals are persistent API changes: downstream metric formulas and user scripts using `perf stat -M` can break even though the JSON remains syntactically valid.

## Dependencies and Integration Points
This file integrates with the perf PMU-events subsystem under `tools/perf/pmu-events/arch/x86/broadwell`. It depends on event names defined across other Broadwell JSON files, including cache/memory events (`L1D_PEND_MISS.*`, `L2_RQSTS.*`, `MEM_LOAD_UOPS_RETIRED.*`, `OFFCORE_REQUESTS*`, `OFFCORE_RESPONSE.*`), frontend events (`IDQ*`, `ICACHE.*`, `DSB2MITE_SWITCHES.*`, `BACLEARS.*`), floating-point events (`FP_ARITH_INST_RETIRED.*`, `FP_ASSIST.*`, `OTHER_ASSISTS.*`), core pipeline/speculation events from other Broadwell tables, MSR/cstate aliases, uncore events, and perf expression variables.

The metrics also integrate with Intel Top-down Microarchitecture Analysis naming conventions. `MetricGroup` tags let `perf list` and `perf stat -M` expose hierarchical analysis groups rather than forcing users to know every individual event.

## Risks
Important risks are semantic rather than memory-safety related:

- Formula drift: a referenced event name must exist in the generated Broadwell event map. Missing or renamed events cause metric evaluation failures.
- Division by zero: several expressions divide by event totals such as retired instructions, load/store counts, or branch counts. Perf expression handling must tolerate zero-denominator workloads.
- Multiplexing accuracy: large metrics reference many events, so limited counters can require multiplexing. `tma_info_system_mux` exists as an accuracy signal, but derived metrics can still be misleading under heavy multiplexing.
- SMT normalization: formulas condition on `#SMT_on` and divide core-wide counts by two in places. Wrong topology detection or collection scope can skew ratios.
- Offcore programming constraints: formulas referencing `OFFCORE_RESPONSE.*` rely on special MSR programming described in `cache.json`; only limited offcore filters can be scheduled concurrently.
- Architectural specificity: these formulas are Broadwell-specific. Reusing them for another x86 generation can produce unsupported event selections or wrong top-down slot math.
- Typographical risk: expression strings are not type checked by a compiler in this source file; mistakes in event names, escaped perf syntax, or group tags are caught only by tooling/tests.

## Test Signals
Useful validation signals include `jq` syntax validation, perf PMU-events build success, generated metric map tests for Broadwell, and runtime smoke tests such as `perf list metric`, `perf stat -M tma_frontend_bound,tma_backend_bound,tma_retiring,tma_bad_speculation`, and `perf stat -M tma_info_thread_ipc,tma_info_system_mux`. Cross-file tests should ensure every event token referenced in `MetricExpr` resolves to an event or a known perf variable/helper metric, top-down L1 categories are schedulable together, power/cstate metrics work on systems exposing the required MSRs, and offcore-dependent metrics either collect correctly or fail with a clear unsupported-event diagnostic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwell/bdw-metrics.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwell/cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwell/cache.json

## Purpose
Broadwell cache, memory hierarchy, TLB, lock, and offcore event table for Linux `perf`. The file is a JSON array of 275 event definitions consumed by the perf PMU-events generator. It supplies the raw event names and encodings used directly by users and indirectly by metrics in `bdw-metrics.json`.

Coverage includes L1D replacements and pending misses, L2 line fills/evictions/transactions/requests, longest-latency cache references and misses, retired memory uop source levels, STLB misses, split loads/stores, locked loads, offcore request issue/outstanding cycles, offcore response filter combinations, superqueue fullness, and split locks.

## Important APIs, Types, and Functions
The schema is perf's event object contract:

- `EventName`: exported event alias such as `L1D.REPLACEMENT`, `L2_RQSTS.DEMAND_DATA_RD_MISS`, `MEM_LOAD_UOPS_RETIRED.L3_MISS`, `OFFCORE_REQUESTS_OUTSTANDING.DEMAND_DATA_RD`, or `OFFCORE_RESPONSE.DEMAND_DATA_RD.L3_HIT.SNOOP_HITM`.
- `EventCode`: raw event select value. Most events use a single hex value; `OFFCORE_RESPONSE.*` entries use `0xB7, 0xBB`, reflecting the paired offcore response event-select slots.
- `UMask`: unit mask for the subevent. Offcore response rows use `0x1` while their full filter meaning is encoded by the event alias and perf's offcore response handling.
- `Counter`: programmable counter constraints. Nearly all rows allow `0,1,2,3`; `L1D_PEND_MISS.PENDING`, `PENDING_CYCLES`, and `PENDING_CYCLES_ANY` constrain to counter `2`.
- `CounterMask`: optional cmask for cycle-qualified variants, including pending-cycle rows, offcore cycles-with rows, and threshold rows such as `OFFCORE_REQUESTS_OUTSTANDING.DEMAND_DATA_RD_GE_6`.
- `AnyThread`: used by `L1D_PEND_MISS.PENDING_CYCLES_ANY`.
- `SampleAfterValue`: default sampling period field for perf.
- `BriefDescription` and `PublicDescription`: user-facing descriptions.

There are no functions, but repeated event families act like data-driven APIs. `L2_RQSTS.*` distinguishes hits, misses, references, RFOs, code reads, demand data reads, and prefetches. `MEM_LOAD_UOPS_RETIRED.*` maps retired load data source levels. `OFFCORE_RESPONSE.*` forms a matrix across request types (`ALL_DATA_RD`, `DEMAND_DATA_RD`, `DEMAND_RFO`, `ALL_RFO`, prefetch code/data/RFO variants, `COREWB`, `OTHER`) and response/snoop categories (`ANY_RESPONSE`, `L3_HIT.*`, `SUPPLIER_NONE.*`).

## Control Flow
Perf controls runtime behavior. The PMU-events build step parses this JSON into event tables. At runtime, selecting an event name causes perf to program the listed event select, umask, cmask, any-thread bit, counter constraints, and offcore response filters where applicable.

The main data-driven flow is selection and expansion:

1. User or metric expression references an event alias.
2. Perf resolves the alias in the Broadwell PMU map.
3. Perf checks counter constraints, including the hard counter-2 requirement for some L1D pending miss events.
4. For offcore response aliases, perf must program one of the offcore response event-selects plus the corresponding offcore response MSR filter.
5. Counts are returned to direct users or to metrics in `bdw-metrics.json`.

## State and Persistence Behavior
The JSON is persistent static metadata. Runtime counter state exists only in CPU PMU registers, offcore response MSRs, perf file descriptors, and sample buffers. This file does not persist collected data.

The event aliases are a stable interface for Broadwell perf users and for in-tree metric expressions. Removing aliases, changing counter constraints, or changing event encodings alters that interface. Offcore rows are especially stateful at runtime because event selection consumes both a programmable counter and an offcore filter register; scheduling two incompatible offcore filters can force multiplexing or rejection.

## Dependencies and Integration Points
This file integrates with the rest of the Broadwell PMU-events directory and the perf PMU-events generator. Metrics in `bdw-metrics.json` consume many of its aliases, including `L1D_PEND_MISS.*`, `L2_LINES_IN.ALL`, `L2_RQSTS.*`, `LONGEST_LAT_CACHE.*`, `MEM_LOAD_UOPS_RETIRED.*`, `MEM_LOAD_UOPS_L3_HIT_RETIRED.*`, `MEM_UOPS_RETIRED.*`, `OFFCORE_REQUESTS*`, `OFFCORE_RESPONSE.DEMAND_RFO.L3_HIT.SNOOP_HITM`, and `SQ_MISC.SPLIT_LOCK`.

The event table also depends on Broadwell PMU hardware semantics: general programmable counters, cmask filtering, any-thread filtering, precise event behavior for retired memory uops, and offcore response MSR encoding. It is used by `perf list`, `perf stat`, `perf record`, metric evaluation, and tests that validate generated event maps.

## Risks
Primary risks are event correctness and scheduling constraints:

- Offcore response complexity: 203 of the 275 rows are `OFFCORE_RESPONSE.*` aliases. These require special offcore MSR programming and cannot be treated like simple event-code/umask pairs.
- Counter constraints: `L1D_PEND_MISS.*` rows constrained to counter `2` can conflict with other events and cause scheduling failures if ignored.
- Similar aliases with different semantics: `L2_TRANS.*` counts transactions accessing the L2 pipe including rejects, while `L2_RQSTS.*` counts non-rejected request outcomes; confusing them changes metric meaning.
- Retired load-source caveats: `MEM_LOAD_UOPS_RETIRED.*` descriptions note limitations for AVX-256 loads and unknown/uncacheable sources.
- Cmask threshold semantics: events with `CounterMask` count cycles meeting a condition, not occurrences. Metrics must distinguish duration/count variants.
- Duplicate event-select use: many rows share the same `EventCode` and differ only by umask or offcore filter, so alias resolution must preserve the full encoding.
- Broadwell specificity: encodings and request/response categories should not be generalized to other Intel generations without checking their PMU tables.

## Test Signals
Validation should include JSON parsing, PMU-events generation, `perf list` visibility for representative aliases, and runtime `perf stat -e` tests for each family: `L1D.REPLACEMENT`, `L2_RQSTS.REFERENCES`, `L2_RQSTS.MISS`, `MEM_LOAD_UOPS_RETIRED.L1_HIT`, `MEM_LOAD_UOPS_RETIRED.L3_MISS`, `OFFCORE_REQUESTS.DEMAND_DATA_RD`, `OFFCORE_REQUESTS_OUTSTANDING.CYCLES_WITH_DEMAND_DATA_RD`, and one or more `OFFCORE_RESPONSE.*` aliases. Scheduling tests should cover counter-2-only L1D pending events, cmask cycle events, and incompatible offcore filters. Metric tests from `bdw-metrics.json` are also indirect validation because many top-down memory metrics depend on this table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwell/cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwell/counter.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwell/counter.json

## Purpose
Broadwell PMU counter topology declaration for Linux `perf`. The file is a compact JSON array of four unit records describing how many generic and fixed counters are available for core and selected uncore-like Broadwell PMU units.

The records declare `core` with four generic and three fixed counters, `CBOX` with two generic and zero fixed counters, `ARB` with two generic and zero fixed counters, and `cbox_0` with zero generic and one fixed counter.

## Important APIs, Types, and Functions
The schema is a counter-unit object:

- `Unit`: PMU unit name, such as `core`, `CBOX`, `ARB`, or `cbox_0`.
- `CountersNumGeneric`: number of programmable generic counters for that unit.
- `CountersNumFixed`: number of fixed counters for that unit.

There are no functions or executable types. The file acts as metadata consumed by perf tooling when modeling event scheduling capacity for Broadwell PMU units.

## Control Flow
Perf tooling reads this file during PMU-events table generation or event-map loading. At runtime, scheduling logic can use the declared counter counts to understand how many events can be placed on each unit without multiplexing. The file does not decide scheduling itself; it supplies capacity data to the perf infrastructure.

The effective flow is: parse unit records, attach counter capacity to the architecture PMU map, then combine this capacity with per-event `Counter` constraints from event JSON files such as `cache.json`, `floating-point.json`, and `frontend.json`.

## State and Persistence Behavior
The only persistent state is the checked-in counter metadata. Runtime state is the allocation of perf events to hardware counters during a perf session. No collection data is persisted here, and the file is not mutated by perf.

Changing values in this file changes scheduling assumptions. For example, reducing `core` generic counter count would increase expected multiplexing, while incorrect uncore counts could make generated maps advertise unsupported schedules.

## Dependencies and Integration Points
This file integrates with the Broadwell PMU-events architecture directory and complements event definition files. Core event files typically constrain events to counters `0,1,2,3`, matching `core`'s four generic counters. The fixed counter count is relevant to standard fixed-function events such as cycles, instructions, and reference cycles used by metrics in `bdw-metrics.json`.

The `CBOX`, `ARB`, and `cbox_0` records integrate with uncore event tables and metrics that reference uncore/system events such as socket clocks and memory bandwidth. This file is part of the same generated PMU map used by `perf list` and `perf stat`.

## Risks
Risks are small but high impact:

- Incorrect counter counts can make perf over-schedule events, underuse available counters, or report misleading multiplexing pressure.
- Unit naming must match event tables and PMU discovery names. Case differences such as `CBOX` versus `cbox_0` are semantically meaningful in the JSON and tooling.
- Fixed-counter declarations must align with kernel PMU support; otherwise metrics that rely on fixed events can appear schedulable but fail at runtime.
- The file is too small to catch errors through internal redundancy, so validation must come from integration tests.

## Test Signals
Useful checks include JSON syntax validation, generated PMU map inspection, `perf list` on Broadwell systems, and scheduling smoke tests that collect four generic core events without multiplexing and a fifth with expected multiplexing. Fixed-counter availability can be checked with cycles/instructions/reference-cycle style events. Uncore counter declarations should be validated with representative CBOX and ARB events from the same Broadwell PMU-events tree.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwell/counter.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwell/floating-point.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwell/floating-point.json

## Purpose
Broadwell floating-point and SIMD event table for Linux `perf`. The file is a JSON array of 22 event definitions used to count retired FP arithmetic by precision/vector width, FP assists, SIMD move elimination, AVX/SSE transition assists, and SIMD physical register file dispatch cancellations.

These events are the raw inputs for FP/HPC metrics in `bdw-metrics.json`, including scalar/vector FP fractions, vector-width breakdowns, FLOP rate estimates, FP arithmetic utilization, and x87/assist-related top-down categories.

## Important APIs, Types, and Functions
The event schema mirrors the other Broadwell PMU event files:

- `EventName`: aliases such as `FP_ARITH_INST_RETIRED.SCALAR_DOUBLE`, `FP_ARITH_INST_RETIRED.256B_PACKED_SINGLE`, `FP_ASSIST.ANY`, `OTHER_ASSISTS.AVX_TO_SSE`, and `UOP_DISPATCHES_CANCELLED.SIMD_PRF`.
- `EventCode`: mainly `0xc7` for FP arithmetic retirement, `0xCA` for FP assists, `0x58` for move elimination, `0xC1` for other assists, and `0xA0` for dispatch cancellations.
- `UMask`: subevent mask selecting precision, width, assist type, transition direction, or PRF cancellation category.
- `Counter`: all rows allow core programmable counters `0,1,2,3`.
- `CounterMask`: only `FP_ASSIST.ANY` uses `1`, making it a cycle-qualified assist event rather than a raw per-assist subevent like the other `FP_ASSIST.*` rows.
- `BriefDescription`, `PublicDescription`, and `SampleAfterValue`: descriptive and sampling metadata.

There are no functions. Event families define the data API. `FP_ARITH_INST_RETIRED.*` includes scalar single/double, packed 128-bit/256-bit single/double, aggregate scalar/vector/single/double/packed aliases, and the combined `4_FLOPS` category. Descriptions specify how many FP operations each retired instruction represents and note that some DPP or fused multiply-add/subtract instructions count twice.

## Control Flow
At build/load time, perf ingests these rows as Broadwell event aliases. At runtime, direct user requests or metric expressions resolve the alias to the event code and umask, then program one of the core generic counters. Metric expressions in `bdw-metrics.json` combine these counts with retired slots, instructions, elapsed time, or core clocks to derive FP ratios and FLOP rates.

The important data-driven control is aggregation. For example, metrics treat `FP_ARITH_INST_RETIRED.SCALAR` and `FP_ARITH_INST_RETIRED.VECTOR` as broad categories, while width-specific metrics use `128B_PACKED_*` and `256B_PACKED_*`. System GFLOP formulas weight scalar, 128-bit packed double, 4-FLOP, and 256-bit packed single events differently.

## State and Persistence Behavior
The JSON is persistent static metadata. Runtime values live in PMU counters during a perf session. Floating-point interpretation depends on workload MXCSR state and instruction mix but is not persisted here.

The public descriptions include an operational caveat: DAZ and FTZ flags in MXCSR need to be set when using many FP arithmetic events. That is not enforced by the metadata, so runtime state outside perf can affect count interpretability.

## Dependencies and Integration Points
This file integrates with perf PMU-events and with `bdw-metrics.json` FP-related metrics such as `tma_fp_scalar`, `tma_fp_vector`, `tma_fp_vector_128b`, `tma_fp_vector_256b`, `tma_info_core_flopc`, `tma_info_core_fp_arith_utilization`, `tma_info_system_gflops`, and instruction-mix metrics like `tma_info_inst_mix_iparith_*`.

It also depends on Broadwell PMU semantics for FP arithmetic retirement, SIMD/x87 assist classification, SIMD move elimination, AVX/SSE transition penalties, and scheduler dispatch cancellation events.

## Risks
Key risks are semantic accuracy and documentation consistency:

- Arithmetic events count retired instructions or microarchitectural events, not always mathematical operations directly. Metrics must apply the correct vector-width multipliers.
- Descriptions note doubled counts for some DPP and fused operations; users can over- or under-estimate FLOPs if they treat all counts uniformly.
- Several public descriptions mention DAZ/FTZ MXCSR requirements. Results can be misleading if workloads run with different denormal handling.
- `FP_ASSIST.ANY` uses a cmask cycle encoding while specific assist rows count assist occurrences; mixing them without recognizing the unit difference is risky.
- Aggregate aliases such as `FP_ARITH_INST_RETIRED.SINGLE`, `DOUBLE`, `PACKED`, `SCALAR`, and `VECTOR` overlap with more specific aliases, so summing them naively double-counts.
- Broadwell event semantics may differ from later Intel generations, especially around AVX widths and fused operations.

## Test Signals
Validation should include JSON parsing, generated event map checks, `perf list` visibility, and runtime smoke tests for scalar, packed, assist, transition, and move-elimination aliases. Metric-level tests should verify that `perf stat -M tma_fp_scalar,tma_fp_vector,tma_info_system_gflops` resolves all referenced events. Microbenchmarks with scalar FP, 128-bit packed FP, 256-bit packed FP, and denormal/assist-heavy operations can validate that the expected event families move while unrelated families remain comparatively low.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwell/floating-point.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwell/frontend.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwell/frontend.json

## Purpose
Broadwell frontend PMU event table for Linux `perf`. The file is a JSON array of 28 events describing branch resteers, DSB-to-MITE switch penalties, instruction cache activity, IDQ delivery sources, microcode sequencer delivery, and top-down frontend under-delivery.

These events feed frontend-bound and fetch-latency/fetch-bandwidth metrics in `bdw-metrics.json`, especially `tma_frontend_bound`, `tma_fetch_latency`, `tma_fetch_bandwidth`, `tma_dsb`, `tma_mite`, `tma_dsb_switches`, `tma_ms_switches`, `tma_icache_misses`, `tma_branch_resteers`, and DSB coverage helper metrics.

## Important APIs, Types, and Functions
The event object schema contains:

- `EventName`: aliases such as `BACLEARS.ANY`, `DSB2MITE_SWITCHES.PENALTY_CYCLES`, `ICACHE.HIT`, `IDQ.DSB_UOPS`, `IDQ.MITE_UOPS`, `IDQ.MS_UOPS`, `IDQ_UOPS_NOT_DELIVERED.CORE`, and thresholded `IDQ_UOPS_NOT_DELIVERED.CYCLES_*` variants.
- `EventCode`: key codes include `0xe6` for BACLEARS, `0xAB` for DSB-to-MITE switches, `0x80` for instruction cache, `0x79` for IDQ source/delivery events, and `0x9C` for not-delivered frontend slots.
- `UMask`: subevent mask selecting the frontend source or condition.
- `Counter`: all rows allow counters `0,1,2,3`.
- `CounterMask`: used for cycle/threshold forms, including IDQ delivery cycles, all-DSB/all-MITE 4-uop or any-uop cycles, MS switches, and not-delivered thresholds.
- `BriefDescription`, `PublicDescription`, and `SampleAfterValue`: user-facing descriptions and sampling metadata.

There are no functions. The main event families are `IDQ.*` delivery-source aliases, `IDQ_UOPS_NOT_DELIVERED.*` top-down frontend availability aliases, and `ICACHE.*` instruction-cache aliases.

## Control Flow
Perf parses the JSON into Broadwell event maps, then programs selected aliases into generic core counters at runtime. Metrics combine the raw counts into frontend categories. For example, `tma_frontend_bound` divides `IDQ_UOPS_NOT_DELIVERED.CORE` by top-down slots, `tma_fetch_latency` uses the zero-uop-delivered threshold event, `tma_dsb` and `tma_mite` compare any-uop cycles against 4-uop cycles for DSB/MITE paths, and `tma_icache_misses` uses `ICACHE.IFDATA_STALL`.

The event data distinguishes count events from cycle-qualified events. `IDQ.DSB_UOPS` counts delivered uops, while `IDQ.DSB_CYCLES` and `IDQ.ALL_DSB_CYCLES_*` count cycles meeting delivery conditions. This distinction is the central control signal for correct metric formulas.

## State and Persistence Behavior
The JSON is static architecture metadata. Runtime state is limited to PMU counter configuration and collected counts. No data is persisted back to the source file.

Frontend event values are sensitive to workload instruction layout, branch predictor state, DSB/uop-cache residency, legacy decode path use, microcode sequencer activity, and backend stalls. `IDQ_UOPS_NOT_DELIVERED.*` descriptions explicitly exclude cases where the backend stalls the frontend, so interpretation depends on pipeline state during the sampled interval.

## Dependencies and Integration Points
This file integrates with the Broadwell PMU-events generator and with `bdw-metrics.json` frontend and branch metrics. It also integrates with other event files: branch-mispredict metrics combine frontend resteer signals with branch retired/mispredict and machine-clear events from other tables; top-down frontend metrics combine these events with slot and clock helper metrics.

At user level, the aliases are exposed through `perf list`, `perf stat -e`, `perf record -e`, and `perf stat -M` when metric expressions reference them.

## Risks
Important risks include:

- Cmask interpretation: many frontend rows are cycle-qualified threshold events. Treating them as raw uop counts produces incorrect ratios.
- Similar IDQ aliases differ subtly: `IDQ.MITE_UOPS`, `IDQ.MITE_ALL_UOPS`, `IDQ.MITE_CYCLES`, and `IDQ.ALL_MITE_CYCLES_*` are not interchangeable.
- DSB/MITE descriptions note bypass and merge behavior; counts can include uops that bypass the IDQ, which can surprise users expecting only queued uops.
- `IDQ_UOPS_NOT_DELIVERED.*` depends on backend-not-stalled conditions. It is a top-down input, not a standalone proof that the frontend alone caused slowdown.
- `BACLEARS.ANY` is a broad front-end resteer signal and should be interpreted with branch mispredict and machine clear events.
- Architectural specificity matters: DSB, MITE, IDQ, and top-down slot semantics are Broadwell-era definitions and should not be copied to unrelated CPU generations.

## Test Signals
Validation signals include JSON parse success, generated PMU-event map tests, `perf list` presence for `IDQ_UOPS_NOT_DELIVERED.CORE`, `IDQ.DSB_UOPS`, `IDQ.MITE_UOPS`, `ICACHE.IFDATA_STALL`, and `DSB2MITE_SWITCHES.PENALTY_CYCLES`, plus runtime `perf stat` checks on representative frontend aliases. Metric validation should run `perf stat -M tma_frontend_bound,tma_fetch_latency,tma_fetch_bandwidth,tma_dsb,tma_mite,tma_icache_misses` and confirm all referenced aliases resolve. Targeted instruction-cache and branch-stress microbenchmarks can provide stronger behavioral signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwell/frontend.json -->
