# subset-b-006663 PMU event JSON research

Grouped research for Intel x86 PMU event and metric metadata under `sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86`. These files are declarative inputs to `tools/perf/pmu-events/jevents.py`, which converts topic JSON files into generated `pmu-events.c` tables matching `struct pmu_event` and `struct pmu_metric` in `pmu-events.h`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/goldmont/pipeline.json -->
## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/goldmont/pipeline.json

**Purpose:** Goldmont pipeline PMU topic with 40 core events for branch retirement and misprediction, unhalted/reference cycles, divider occupancy, retired instructions/uops, frontend delivery gaps, backend issue slot pressure, load blocking, and machine clears. It gives `perf list` and `perf stat -e` symbolic names such as `BR_INST_RETIRED.ALL_BRANCHES`, `UOPS_NOT_DELIVERED.ANY`, and `MACHINE_CLEARS.SMC`.

**Schema and important records:** Every item is a `pmu_event` source record using `EventName`, `EventCode`, `UMask`, `BriefDescription`, `PublicDescription`, `Counter`, `SampleAfterValue`, and optional `PEBS`. Fixed-counter events are encoded through `Counter` values like `Fixed counter 0/1/2` for `INST_RETIRED.ANY`, `CPU_CLK_UNHALTED.CORE`, and `CPU_CLK_UNHALTED.REF_TSC`; programmable variants use explicit event encodings and counter lists. PEBS-capable entries include retired branches, retired loads blocked, and retired uops.

**Control flow and integration:** `jevents.py` loads this topic while traversing the `goldmont` model directory, turns each JSON object into `JsonEvent`, derives the topic from `pipeline.json`, and emits compact C strings and `struct pmu_event` entries. Runtime lookup flows through `perf_pmu__find_events_table`, then `pmu_events_table__find_event` or iteration APIs used by `perf list`.

**State and persistence:** The file has no runtime mutation. Its persisted state is the event catalog compiled into the perf binary; sampling behavior is controlled later by perf and kernel PMU programming.

**Dependencies:** Depends on Intel Goldmont event encodings, perf's PMU JSON schema, and x86 mapfile CPU matching. Metrics in other files may refer to these names, especially `CPU_CLK_UNHALTED.*`, `INST_RETIRED.*`, branch, uop, and machine-clear events.

**Risks:** Incorrect `EventCode`, `UMask`, fixed-counter mapping, or PEBS annotation silently misprograms hardware counters or makes precise sampling unavailable/misleading. The distinction between fixed and programmable aliases must remain consistent because events like `INST_RETIRED.ANY` and `INST_RETIRED.ANY_P` have different collection constraints.

**Test signals:** Validate JSON syntax and schema with `jq`; build perf with jevents enabled; use `perf list` on a matching Goldmont CPU or generated-table tests to confirm event aliases. Spot-check branch/uop/cycle aliases with `perf stat -e` and verify fixed counter aliases are not emitted as programmable-only events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/goldmont/pipeline.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/goldmont/virtual-memory.json -->
## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/goldmont/virtual-memory.json

**Purpose:** Goldmont virtual-memory topic with seven PMU events for ITLB misses, retired memory uops that missed the DTLB, and page-walk cycle accounting. It exposes translation-related performance aliases used to distinguish instruction-side misses, data-side misses, and page-walk duration.

**Schema and important records:** Records use the event schema fields `EventName`, `EventCode`, `UMask`, descriptions, `Counter`, `SampleAfterValue`, and optional `PEBS`/`Data_LA`. `MEM_UOPS_RETIRED.DTLB_MISS_LOADS` and `MEM_UOPS_RETIRED.DTLB_MISS_STORES` are precise/data-address capable retirement events; `PAGE_WALKS.CYCLES`, `PAGE_WALKS.D_SIDE_CYCLES`, and `PAGE_WALKS.I_SIDE_CYCLES` count cycles with page walks in progress.

**Control flow and integration:** `jevents.py` tags these records with the `virtual-memory` topic and emits them into Goldmont's PMU event table. Runtime perf consumers can discover them with `perf list virtual-memory` and program them through the generated alias metadata.

**State and persistence:** The only persisted state is static event metadata compiled into perf. Counter accumulation occurs in hardware PMU counters during a perf session; the JSON itself has no persistence or control logic.

**Dependencies:** Depends on perf's `pmu_event` JSON conversion and Goldmont PMU encoding. It is conceptually linked to pipeline load-blocking events such as `LD_BLOCKS.UTLB_MISS` and to any metrics that divide TLB misses by retired instructions.

**Risks:** The file mixes speculative ITLB fill accounting with retired DTLB miss events, so descriptions must stay precise or users may compare non-equivalent counts. PEBS/data linear address flags are important for address attribution and should not be dropped during schema changes.

**Test signals:** `jq empty` confirms structural validity; perf jevents build confirms schema acceptance. On target hardware, `perf list | rg -i 'dtlb|itlb|page_walk'` and targeted `perf stat -e ITLB.MISS,PAGE_WALKS.CYCLES` can verify aliases resolve.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/goldmont/virtual-memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/goldmontplus/cache.json -->
## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/goldmontplus/cache.json

**Purpose:** Goldmont Plus cache and memory-hierarchy topic with 101 records. It covers L1 dirty replacements, instruction-cache fill stalls, L2 references/misses/rejects, load hit-source retirement events, memory uop mix, split/locked accesses, and a large set of `OFFCORE_RESPONSE.*` aliases for request/response combinations.

**Schema and important records:** Standard event records use `EventName`, `EventCode`, `UMask`, `Counter`, descriptions, `SampleAfterValue`, and optional `PEBS`/`Data_LA`. Offcore response records also use `MSRIndex` and `MSRValue`; `jevents.py` maps MSR index `0x1A6`/`0x1A7` to the `offcore_rsp=` event field. The base `OFFCORE_RESPONSE` entry documents the need for MSR programming, while derived records encode request classes such as demand data read, RFO, code read, prefetches, streaming stores, writebacks, and bus locks with response classes such as L2 hit, HITM other core, true L2 miss, and outstanding cycles.

**Control flow and integration:** During build, `jevents.py` emits these as Goldmont Plus `pmu_event` entries. At runtime, aliases that include `MSRValue` cause perf to program the offcore response MSR selector in addition to the core event code. The load-retired and memory-uop aliases also support precise sampling where PEBS/data-address metadata is present.

**State and persistence:** Static catalog only; hardware counter state is session-scoped. Offcore aliases persist selector values in generated event strings, so the JSON is the durable source of request/response programming semantics.

**Dependencies:** Depends on Intel Goldmont Plus offcore response encodings, perf's MSR mapping in `jevents.py`, and PMU counter availability from `counter.json`. Metrics and user workflows depend on stable names like `MEM_LOAD_UOPS_RETIRED.L1_HIT`, `LONGEST_LAT_CACHE.MISS`, and `OFFCORE_RESPONSE.DEMAND_DATA_RD.OUTSTANDING`.

**Risks:** Offcore response aliases are especially fragile: bad `MSRValue` values can produce valid-looking but semantically wrong counts. Duplicate descriptions for the two offcore MSRs must remain intentional. PEBS `Data_LA` handling is required for load-source attribution.

**Test signals:** `jq` schema checks; perf jevents generation; `perf list` should show cache topic aliases. Runtime smoke tests should include a simple load benchmark with `MEM_LOAD_UOPS_RETIRED.L1_HIT,L2_MISS` and one offcore alias to ensure MSR programming succeeds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/goldmontplus/cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/goldmontplus/counter.json -->
## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/goldmontplus/counter.json

**Purpose:** Goldmont Plus PMU counter-capacity descriptor. It declares the `core` PMU as having three fixed counters and four generic programmable counters.

**Schema and important records:** This file is not an event table. It is a one-object array with `Unit`, `CountersNumFixed`, and `CountersNumGeneric`. The record tells perf's PMU event generation and reporting layer what counter resources are available for the model.

**Control flow and integration:** `jevents.py` and associated PMU metadata processing include `counter.json` alongside topic files for the same CPU directory. Runtime metric scheduling and event grouping decisions can use the generated capacity metadata to understand fixed versus generic counter limits.

**State and persistence:** Persisted as static PMU metadata in generated perf tables. It does not store counts or runtime session state.

**Dependencies:** Must match the Goldmont Plus hardware PMU and the fixed-counter use in `pipeline.json` (`INST_RETIRED.ANY`, `CPU_CLK_UNHALTED.CORE`, `CPU_CLK_UNHALTED.REF_TSC`). It also constrains grouping for cache/offcore and virtual-memory events.

**Risks:** An incorrect generic-counter count can make perf overcommit groups or reject valid event sets. Incorrect fixed-counter count can make fixed aliases appear schedulable when hardware cannot support them.

**Test signals:** Validate JSON; build perf; run grouped `perf stat` workloads that mix fixed and programmable events. Metric scheduling failures or unexpected multiplexing are signals that this descriptor is stale.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/goldmontplus/counter.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/goldmontplus/floating-point.json -->
## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/goldmontplus/floating-point.json

**Purpose:** Goldmont Plus floating-point topic with three events: floating-point divide busy cycles, machine clears caused by FP assists, and retired FP divide uops. These aliases help diagnose long-latency FP division and assist-driven pipeline disruption.

**Schema and important records:** Records use the standard `pmu_event` fields. `CYCLES_DIV_BUSY.FPDIV` counts FP divider busy cycles, `MACHINE_CLEARS.FP_ASSIST` counts FP-assist machine clears, and `UOPS_RETIRED.FPDIV` is PEBS-capable retired FP divide uop accounting.

**Control flow and integration:** Build-time `jevents.py` places the records into the Goldmont Plus event table under the floating-point topic. At runtime they are listed and programmed by name through the generic PMU event-table lookup functions.

**State and persistence:** Static event metadata only. Runtime counts are accumulated in PMU counters during perf sessions and are not persisted by the JSON layer.

**Dependencies:** Depends on the Goldmont Plus PMU event encodings and counter resources in `counter.json`. Metrics or ad hoc analyses can combine these with cycle and instruction events from `pipeline.json`.

**Risks:** The small file is easy to overlook during model updates; stale FP assist/divide encodings would undermine floating-point bottleneck analysis. `MACHINE_CLEARS.FP_ASSIST` semantics must stay aligned with pipeline machine-clear aliases.

**Test signals:** `jq` validity; perf jevents build; `perf list floating` includes all three names. Runtime validation can use FP-divide-heavy microbenchmarks and compare `CYCLES_DIV_BUSY.FPDIV` with `UOPS_RETIRED.FPDIV`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/goldmontplus/floating-point.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/goldmontplus/frontend.json -->
## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/goldmontplus/frontend.json

**Purpose:** Goldmont Plus frontend topic with eight aliases for BACLEAR conditions, predecode restrictions, instruction-cache accesses/hits/misses, and micro-sequencer decoded entries. It exposes fetch/decode disruption and instruction-cache health.

**Schema and important records:** Uses standard event fields without PEBS-specific metadata. `BACLEARS.ALL`, `.COND`, and `.RETURN` classify branch-address-clear recovery; `DECODE_RESTRICTION.PREDECODE_WRONG` tracks decode restriction from predecode mistakes; `ICACHE.ACCESSES`, `.HIT`, and `.MISSES` count I-cache behavior; `MS_DECODED.MS_ENTRY` tracks micro-sequencer decoding.

**Control flow and integration:** `jevents.py` emits the file as a frontend topic for the Goldmont Plus model. Runtime consumers can select aliases directly or use them as components in frontend-bound analysis.

**State and persistence:** No mutable state. The JSON persists symbolic names, encodings, and descriptions in generated C tables.

**Dependencies:** Depends on Goldmont Plus frontend PMU encodings and integrates with pipeline-level `UOPS_NOT_DELIVERED.ANY`, fetch-stall events in `other.json`, and virtual-memory ITLB events.

**Risks:** Frontend events often have overlapping interpretations. Inaccurate descriptions can lead users to double-count or misattribute stalls between I-cache, ITLB, decode, and branch-recovery sources.

**Test signals:** JSON parse and jevents generation. On target hardware, compare `ICACHE.ACCESSES`, `ICACHE.HIT`, and `ICACHE.MISSES` for plausible relationships, and use `perf list frontend` to ensure topic grouping is correct.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/goldmontplus/frontend.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/goldmontplus/memory.json -->
## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/goldmontplus/memory.json

**Purpose:** Goldmont Plus memory topic with three aliases for memory-ordering machine clears and misaligned memory references that split pages. It targets correctness/replay costs rather than cache hit-source counting.

**Schema and important records:** Standard event fields plus PEBS where available. `MACHINE_CLEARS.MEMORY_ORDERING` records machine clears due to memory ordering conflicts. `MISALIGN_MEM_REF.LOAD_PAGE_SPLIT` and `.STORE_PAGE_SPLIT` count load/store references spanning page boundaries.

**Control flow and integration:** Build-time event conversion is standard `JsonEvent` processing. Runtime perf users can collect these aliases directly or combine them with load-blocking and machine-clear events from `pipeline.json`.

**State and persistence:** Static PMU metadata only. Hardware counters hold transient session state.

**Dependencies:** Depends on the same counter inventory as other Goldmont Plus core events. Semantic integration is strongest with `MACHINE_CLEARS.*`, `LD_BLOCKS.*`, and split cache-line events from `cache.json`.

**Risks:** Misalignment events are narrow and may be confused with cache-line split events; documentation must preserve page-split wording. Machine-clear categories can overlap in analysis, so event names and descriptions must remain distinct.

**Test signals:** `jq` validation and perf build. Runtime microbenchmarks with deliberately page-split accesses can check that load/store page-split aliases resolve and produce nonzero counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/goldmontplus/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/goldmontplus/other.json -->
## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/goldmontplus/other.json

**Purpose:** Goldmont Plus miscellaneous topic with five events for aggregate fetch stalls, ITLB-fill-related fetch stalls, and hardware interrupt delivery/masking behavior.

**Schema and important records:** Standard `pmu_event` fields. `FETCH_STALL.ALL` and `FETCH_STALL.ITLB_FILL_PENDING_CYCLES` count frontend fetch stall cycles. `HW_INTERRUPTS.RECEIVED`, `.MASKED`, and `.PENDING_AND_MASKED` account for interrupt activity that may perturb workload measurements.

**Control flow and integration:** `jevents.py` emits these into the Goldmont Plus event table under the `other` topic. Runtime perf event lookup treats them like the other core aliases.

**State and persistence:** Static metadata only; interrupt and stall counts live in hardware counters during a perf session.

**Dependencies:** Integrates with frontend and virtual-memory topics because fetch stalls can be caused by I-cache or ITLB behavior. Interrupt aliases depend on hardware PMU support for counting interrupt masking/receipt events.

**Risks:** The `other` topic is easy for users and tests to skip even though interrupts can explain noisy profiles. Fetch-stall aliases may be misinterpreted if compared directly with instruction-cache fill pending cycles from `cache.json`.

**Test signals:** JSON parse/build; `perf list other` or raw alias dump should include all five names. Runtime smoke tests can generate interrupt load and compare interrupt counters with expected activity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/goldmontplus/other.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/goldmontplus/pipeline.json -->
## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/goldmontplus/pipeline.json

**Purpose:** Goldmont Plus pipeline topic with 42 events. It is the Goldmont pipeline set plus additional machine-clear and precise-retirement coverage such as `INST_RETIRED.PREC_DIST` and `MACHINE_CLEARS.PAGE_FAULT`.

**Schema and important records:** Standard `pmu_event` fields with PEBS on precise retirement/load-blocking/uop records. Families include retired and mispredicted branches, unhalted/reference cycles, divider busy cycles, fixed and programmable retired instruction aliases, backend issue-slot pressure, load blocking (`4K_ALIAS`, `STORE_FORWARD`, `UTLB_MISS`), machine clears, and retired/issued uops.

**Control flow and integration:** `jevents.py` converts the JSON to C event-table rows, deriving topic from the filename. Runtime perf uses the generated table selected by x86 mapfile CPUID matching for Goldmont Plus.

**State and persistence:** Persistent static catalog. Runtime counts and sampling records are maintained by perf/kernel PMU paths, not by this file.

**Dependencies:** Depends on `counter.json` for fixed/generic capacity, and on related cache/frontend/memory/virtual-memory topics for full bottleneck analysis. Grandridge metrics use similar event families but with newer topdown names, so cross-model renames must be deliberate.

**Risks:** Goldmont and Goldmont Plus are similar enough that accidental copy-forward is plausible. The two extra records must stay model-appropriate. PEBS and fixed-counter distinctions are important for precise sampling and event grouping.

**Test signals:** JSON validation; perf jevents generation; `perf list pipeline` on matching CPU. Compare event inventory with Goldmont to verify intentional additions (`INST_RETIRED.PREC_DIST`, `MACHINE_CLEARS.PAGE_FAULT`) rather than accidental drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/goldmontplus/pipeline.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/goldmontplus/virtual-memory.json -->
## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/goldmontplus/virtual-memory.json

**Purpose:** Goldmont Plus virtual-memory topic with 18 events for detailed DTLB/ITLB walk completion by page size, walk-pending cycles, EPT walk pending, retired DTLB-miss memory uops, and STLB flushes.

**Schema and important records:** Standard event schema with optional `PEBS` and `Data_LA`. Event families include `DTLB_LOAD_MISSES.WALK_COMPLETED_4K/2M_4M/1GB`, matching store-side events, `ITLB_MISSES.WALK_COMPLETED_*`, `*.WALK_PENDING`, `EPT.WALK_PENDING`, `MEM_UOPS_RETIRED.DTLB_MISS*`, `ITLB.MISS`, and `TLB_FLUSHES.STLB_ANY`.

**Control flow and integration:** Build-time conversion is standard. Runtime users get aliases grouped under virtual-memory; precise data-address metadata supports locating retired memory uops that missed the DTLB.

**State and persistence:** Static metadata only. PMU counters store per-session counts; the JSON persists page-size-specific selector semantics.

**Dependencies:** Depends on Goldmont Plus translation PMU encodings. Integrates with frontend fetch-stall/ITLB events, pipeline `LD_BLOCKS.UTLB_MISS`, and memory page-split events.

**Risks:** Page-size suffixes are semantically important; swapping `4K`, `2M_4M`, and `1GB` masks changes in huge-page behavior. `WALK_PENDING` cycle events are not equivalent to completed-walk events, so metrics must use the right family.

**Test signals:** `jq` validation and jevents build. On target hardware, `perf list | rg 'DTLB_LOAD_MISSES|ITLB_MISSES|TLB_FLUSHES'`; huge-page and small-page microbenchmarks can exercise page-size-specific aliases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/goldmontplus/virtual-memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/grandridge/cache.json -->
## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/grandridge/cache.json

**Purpose:** Grand Ridge cache topic with 58 events for L1 dirty eviction, L2 line states and requests, LLC/longest-latency cache references, instruction-fetch and load memory-bound stalls, load hit levels through L3/WCB, memory scheduler blocking, load latency thresholds, split/locked accesses, STLB misses, store latency, offcore response (`OCR.*`) demand data/RFO snoop states, and topdown I-cache frontend bound.

**Schema and important records:** Uses standard event fields plus `MSRIndex`/`MSRValue` for `OCR.*` records and `Data_LA` on precise load-related records. `MEM_UOPS_RETIRED.LOAD_LATENCY_GT_*` spans thresholds from greater than 4 to greater than 2048 cycles. `MEM_BOUND_STALLS_LOAD.*` and `MEM_BOUND_STALLS_IFETCH.*` provide stall attribution by cache level.

**Control flow and integration:** `jevents.py` maps MSR-backed OCR selectors through the same offcore MSR conversion path and emits all records as Grand Ridge cache-topic `pmu_event` rows. `grr-metrics.json` references many of these names for load-store, memory-execution, and IO/memory bandwidth metrics.

**State and persistence:** Static event metadata. Offcore selector values and load-latency threshold encodings are persisted in generated event strings; actual counts are session-scoped.

**Dependencies:** Depends on Grand Ridge core PMU and OCR encodings, counter resources in `counter.json`, and uncore event availability for metrics that combine core cache aliases with CHA/IMC/IIO events.

**Risks:** OCR MSR selectors and load-latency threshold masks are high-risk fields because errors produce plausible but wrong measurements. Metrics in `grr-metrics.json` will fail or mislead if referenced event names are renamed.

**Test signals:** JSON/build validation; `perf list cache` for Grand Ridge table. Metric parser tests should cover `grr-metrics.json` expressions using `MEM_BOUND_STALLS_*`, `MEM_LOAD_UOPS_RETIRED.*`, and `OCR.*`; runtime offcore smoke tests should verify MSR selector programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/grandridge/cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/grandridge/counter.json -->
## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/grandridge/counter.json

**Purpose:** Grand Ridge PMU counter-capacity descriptor for core and uncore PMUs. It declares `core` as three fixed and eight generic counters, plus several uncore units with four generic counters and no fixed counters.

**Schema and important records:** Array of unit records using `Unit`, `CountersNumFixed`, and `CountersNumGeneric`. Units are `core`, `B2CMI`, `CHA`, `IMC`, `IIO`, `IRP`, `PCU`, and `CHACMS`. `PCU` has numeric `CountersNumGeneric` while most others encode counts as strings, so consumers must tolerate both JSON number and string forms.

**Control flow and integration:** Included in the model directory during jevents processing. Runtime event grouping and metric scheduling rely on these capacities when metrics use core events together with uncore aliases referenced by `grr-metrics.json`.

**State and persistence:** Static PMU resource metadata. It does not represent counter values or runtime state.

**Dependencies:** Must match Grand Ridge hardware PMU topology. The uncore unit list supports metrics for memory bandwidth, IO bandwidth, C-state residency, SMI, and uncore frequency.

**Risks:** Incorrect capacity causes perf to make poor grouping/multiplexing decisions. The mixed numeric/string representation for `CountersNumGeneric` is a compatibility risk for strict validators.

**Test signals:** JSON parse; jevents build; run `perf list` and metric scheduling tests for both core and uncore metrics. A schema lint should explicitly accept or normalize string/integer counter counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/grandridge/counter.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/grandridge/floating-point.json -->
## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/grandridge/floating-point.json

**Purpose:** Grand Ridge floating-point topic with 13 events for FP divide active cycles, retired FP FLOPs/instructions by precision and vector width, FP-assist machine clears, and retired FP divide uops.

**Schema and important records:** Standard event records with `CounterMask` on `ARITH.FPDIV_ACTIVE` and `Deprecated` on older compatibility aliases. Event families include `FP_FLOPS_RETIRED.ALL/DP/SP/FP32/FP64`, `FP_INST_RETIRED.128B_*`, `256B_DP`, scalar 32/64-bit aliases, `MACHINE_CLEARS.FP_ASSIST`, and `UOPS_RETIRED.FPDIV`.

**Control flow and integration:** `jevents.py` emits records under the floating-point topic. `grr-metrics.json` depends on these event names for `Flops` group metrics such as `tma_info_core_flopc`, `tma_info_system_gflops`, and FP instruction-mix ratios.

**State and persistence:** Static catalog metadata only. Deprecated markers persist into generated `pmu_event.deprecated` fields so perf can hide or annotate stale aliases as appropriate.

**Dependencies:** Depends on Grand Ridge FP PMU encodings, topdown metrics, and cycle/instruction events in `pipeline.json`.

**Risks:** Deprecated aliases must remain available only as intended; removing them can break metric expressions or user scripts. FLOP versus instruction counts differ, so descriptions and metric formulas must avoid mixing semantic units.

**Test signals:** JSON/build validation; metric parser coverage for Flops metrics; runtime FP scalar/vector microbenchmarks to check expected nonzero precision-specific aliases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/grandridge/floating-point.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/grandridge/frontend.json -->
## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/grandridge/frontend.json

**Purpose:** Grand Ridge frontend topic with five events for branch-address clears, frontend-retired ITLB misses, instruction-cache accesses/misses, and micro-sequencer busy cycles.

**Schema and important records:** Standard event records. `BACLEARS.ANY` feeds branch-mispredict diagnostics; `FRONTEND_RETIRED.ITLB_MISS` gives frontend retirement attribution; `ICACHE.ACCESSES` and `.MISSES` feed instruction-cache miss metrics; `MS_DECODED.MS_BUSY` exposes microcode sequencer pressure.

**Control flow and integration:** Converted by `jevents.py` into Grand Ridge event-table rows. `grr-metrics.json` references `ICACHE.MISSES`, `BACLEARS.ANY`, and frontend topdown events for Ifetch and TMA metrics.

**State and persistence:** Static alias metadata; runtime counter state is session-local.

**Dependencies:** Depends on Grand Ridge frontend PMU encodings and topdown pipeline events such as `TOPDOWN_FE_BOUND.*`. Integrated with virtual-memory events for ITLB analysis.

**Risks:** Grand Ridge names differ from Goldmont Plus (`BACLEARS.ANY` vs `BACLEARS.ALL`, `MS_DECODED.MS_BUSY` vs `MS_ENTRY`), so cross-model metric reuse must use model-specific names. Missing aliases will break metrics by name.

**Test signals:** `jq` and jevents build; metric parser tests for expressions using `ICACHE.MISSES` and `BACLEARS.ANY`; `perf list frontend` on Grand Ridge mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/grandridge/frontend.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/grandridge/grr-metrics.json -->
## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/grandridge/grr-metrics.json

**Purpose:** Grand Ridge metric table with 124 `pmu_metric` records. It defines user-facing formulas for topdown microarchitecture analysis, power/C-state residency, CPI/IPC/frequency/utilization, memory and IO bandwidth, SMI, load/store miss ratios, FLOPs, and detailed bottleneck breakdowns.

**Schema and important records:** Records use metric fields `MetricName`, `MetricExpr`, optional `MetricGroup`, `MetricThreshold`, `ScaleUnit`, `BriefDescription`, `PublicDescription`, and `MetricgroupNoGroup`. Groups include `TopdownL1`, `TopdownL2`, `TopdownL3`, `Flops`, `Ifetch`, `Load_Store_Miss`, `Mem_Exec`, `Power`, `Summary`, `load_store_bound`, and `smi`. Expressions reference core events (`CPU_CLK_UNHALTED.*`, `INST_RETIRED.ANY`, `TOPDOWN_*`, `MEM_*`, `BR_*`, `FP_*`), MSR pseudo-events (`msr@tsc@`, `msr@smi@`, `msr@aperf@`), cstate pseudo-events, and uncore events (`UNC_CHA_*`, `UNC_M_*`, `UNC_IIO_*`).

**Control flow and integration:** `jevents.py` emits these as `struct pmu_metric` rows, while `metric.py` and perf's metric parser validate and expand expressions. Runtime `perf stat -M <metric>` schedules the referenced event set, applies thresholds, scales units, and groups metrics according to `MetricGroup`.

**State and persistence:** Metric formulas and thresholds are static compiled metadata. Runtime values are derived from current counter readings, duration, source counts, and system constants such as `#SYSTEM_TSC_FREQ`.

**Dependencies:** Strongly depends on all Grand Ridge event-topic files plus uncore PMU event definitions outside this subset. `metricgroups.json` supplies descriptions for the group names used here.

**Risks:** This file is name-fragile: any event rename or missing uncore event breaks expression parsing or runtime collection. Division by zero, multiplexing, and threshold grouping can produce misleading output. Typographical metric names such as `adressaliasing` may be externally visible and should not be changed casually.

**Test signals:** Run perf metric parser tests and `tools/perf/pmu-events/metric_test.py` if available. `perf list metricgroups`, `perf list metrics`, and sample `perf stat -M TopdownL1,cpi,memory_bandwidth_total` on Grand Ridge are high-value integration checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/grandridge/grr-metrics.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/grandridge/memory.json -->
## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/grandridge/memory.json

**Purpose:** Grand Ridge memory topic with 11 events for load-head retirement attribution, memory-ordering machine clears, page-split misaligned memory references, and OCR demand data/RFO L3 misses.

**Schema and important records:** Standard event fields plus `MSRIndex`/`MSRValue` on `OCR.DEMAND_DATA_RD.L3_MISS` and `OCR.DEMAND_RFO.L3_MISS`. `LD_HEAD.*_AT_RET` classifies loads at retirement as L1-bound, L1-miss, page-walk, store-address, other, or any. `MACHINE_CLEARS.MEMORY_ORDERING` and `MISALIGN_MEM_REF.*_PAGE_SPLIT` mirror narrow memory-ordering and page-split diagnostics.

**Control flow and integration:** `jevents.py` emits static event rows and maps OCR MSR selectors to offcore response fields. `grr-metrics.json` uses `LD_HEAD.*` events for memory-execution bottleneck percentages and load-store-bound breakdowns.

**State and persistence:** Static alias and selector metadata; runtime PMU state is transient.

**Dependencies:** Depends on Grand Ridge OCR encodings and pipeline/cache event families. Metrics require these names to remain stable.

**Risks:** `LD_HEAD` attribution feeds derived percentages, so any wrong selector can skew topdown-style diagnostics. OCR L3 miss aliases require correct MSR programming.

**Test signals:** JSON/build validation; metric parser tests for `tma_info_mem_exec_bound_*` and `load_store_bound` metrics; runtime load-miss and page-split microbenchmarks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/grandridge/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/grandridge/metricgroups.json -->
## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/grandridge/metricgroups.json

**Purpose:** Grand Ridge metric-group description map with 21 group names used by `grr-metrics.json`. It gives human-readable descriptions for `perf list metricgroups` and metric grouping UI/output.

**Schema and important records:** Unlike event and metric arrays, this file is a JSON object mapping group name to description string. Groups include broad spreadsheet-derived groups (`Flops`, `Ifetch`, `Load_Store_Miss`, `Mem_Exec`, `Power`, `Summary`, `load_store_bound`), topdown levels (`TopdownL1`, `TopdownL2`, `TopdownL3`), internal TMA level groups (`tma_L1_group`, `tma_L2_group`, `tma_L3_group`), and contributor groups for backend, bad speculation, core bound, frontend bound, ifetch bandwidth/latency, machine clears, and resource bound.

**Control flow and integration:** `jevents.py` loads metric-group descriptions into `_metricgroups`; generated perf code exposes them through `describe_metricgroup`. Runtime `perf list metricgroups` and metric display paths use these descriptions when presenting groups from `grr-metrics.json`.

**State and persistence:** Static description metadata only. It has no counters, formulas, or mutable state.

**Dependencies:** Must stay synchronized with `MetricGroup` values in `grr-metrics.json`. Semicolon-delimited metric groups rely on each component name being present here for good descriptions.

**Risks:** This object-shaped schema differs from the array schema used by most PMU JSON files; generic tooling that assumes arrays will fail. Missing group descriptions do not necessarily break collection, but they degrade discoverability and may signal stale metric taxonomy.

**Test signals:** Validate as a JSON object, not an event array. Run `perf list metricgroups` or generated `describe_metricgroup` tests and compare every group referenced by `grr-metrics.json` against this map.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/grandridge/metricgroups.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/grandridge/other.json -->
## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/grandridge/other.json

**Purpose:** Grand Ridge miscellaneous topic with two events: last-branch-record insertions and OCR streaming write responses.

**Schema and important records:** Standard event fields plus `Deprecated` on `LBR_INSERTS.ANY`, and `MSRIndex`/`MSRValue` on `OCR.STREAMING_WR.ANY_RESPONSE`. The LBR event is compatibility-sensitive, while the OCR event tracks streaming write requests with any offcore response.

**Control flow and integration:** `jevents.py` emits both into Grand Ridge's `other` topic. The OCR record uses MSR selector conversion; the deprecated marker persists into generated metadata.

**State and persistence:** Static metadata only. Runtime LBR insertion and streaming write counts are held in PMU counters for the perf session.

**Dependencies:** Depends on Grand Ridge LBR/OCR event encodings and offcore MSR mapping. Related pipeline file has `MISC_RETIRED.LBR_INSERTS`, so users may see both old and newer naming.

**Risks:** Deprecated aliases can confuse users if preferred replacements are not clear. OCR streaming write selector errors are hard to catch because any-response counts may look plausible under memory traffic.

**Test signals:** JSON/build validation; `perf list other` should show deprecation handling. Runtime streaming/non-temporal store tests can exercise `OCR.STREAMING_WR.ANY_RESPONSE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/grandridge/other.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/grandridge/pipeline.json -->
## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/grandridge/pipeline.json

**Purpose:** Grand Ridge pipeline topic with 76 events. It covers arithmetic divide activity, retired and mispredicted branches, fixed and programmable cycle/instruction counters, load blocking, machine clears, miscellaneous retired events, serialization, topdown retiring/frontend/backend/bad-speculation categories, and retired/issued uops.

**Schema and important records:** Standard event records with `CounterMask` on selected threshold/active-cycle events and `Deprecated` on compatibility aliases (`BR_INST_RETIRED.IND_CALL`, `MACHINE_CLEARS.SLOW`, `TOPDOWN_FE_BOUND.ITLB`). Fixed-counter aliases include `INST_RETIRED.ANY`, `CPU_CLK_UNHALTED.THREAD`, and `CPU_CLK_UNHALTED.REF_TSC`; programmable variants add `_P` names. Topdown families include `TOPDOWN_RETIRING.ALL_P`, `TOPDOWN_FE_BOUND.*`, `TOPDOWN_BE_BOUND.*`, and `TOPDOWN_BAD_SPECULATION.*`.

**Control flow and integration:** `jevents.py` converts this topic to `pmu_event` rows selected by the Grand Ridge mapfile entry. `grr-metrics.json` is tightly coupled to this file: topdown metrics divide topdown slot events by `6 * CPU_CLK_UNHALTED.CORE`, and many info metrics reference branch, load-block, machine-clear, serialization, and uop aliases here.

**State and persistence:** Static PMU metadata only. Fixed/generic counter programming, multiplexing, and samples are runtime perf/kernel state.

**Dependencies:** Depends on the Grand Ridge core PMU and `counter.json` declaring eight generic counters. Also depends on naming compatibility with metric formulas and frontend/cache/memory topic events.

**Risks:** This is a central dependency for metrics; a single rename or deprecation mishandling can break topdown analysis. Fixed versus programmable aliases must stay correct. Topdown denominator width (`6 * CPU_CLK_UNHALTED.CORE`) in metrics assumes slot semantics matching these events.

**Test signals:** JSON/build validation; metric parser tests for all Topdown groups; `perf stat -M TopdownL1` on Grand Ridge; direct `perf stat -e TOPDOWN_FE_BOUND.ALL_P,TOPDOWN_BE_BOUND.ALL_P,TOPDOWN_RETIRING.ALL_P,TOPDOWN_BAD_SPECULATION.ALL_P` smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/grandridge/pipeline.json -->
