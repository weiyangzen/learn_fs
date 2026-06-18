# subset-b-006705 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/pantherlake/pipeline.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/pantherlake/pipeline.json

## Purpose

`pipeline.json` is the Panther Lake perf PMU event catalog for core pipeline, branch, retirement, topdown, execution, divider, stall, and uop-flow analysis. It contains 243 event rows: 155 for `cpu_core` and 88 for `cpu_atom`, reflecting Panther Lake's hybrid core/atom PMU split. The file is not executable code, but it is a direct input to perf's `pmu-events` generator and therefore becomes user-visible `perf list`, `perf stat`, and `perf record` event metadata.

## Important APIs, Types, and Data Fields

The file is a JSON array of event objects. The core schema fields are `EventName`, `EventCode`, `UMask`, `Counter`, `Unit`, `SampleAfterValue`, `BriefDescription`, and often `PublicDescription`. Qualifier fields include `CounterMask`, `EdgeDetect`, `Invert`, `MSRIndex`, `MSRValue`, and `Deprecated`. `Unit` is critical because the same logical event name can appear twice with different encodings for `cpu_core` and `cpu_atom`, such as `ARITH.DIV_ACTIVE`, branch-retired rows, and TLB-adjacent pipeline rows.

Major event families are `ARITH`, `ASSISTS`, `BE_STALLS`, `BR_INST_RETIRED`, `BR_MISP_RETIRED`, `CPU_CLK_UNHALTED`, `CYCLE_ACTIVITY`, `EXE_ACTIVITY`, `INST_RETIRED`, `INT_MISC`, `INT_UOPS_EXECUTED`, `INT_VEC_RETIRED`, `LD_BLOCKS`, `LSD`, `MACHINE_CLEARS`, `MEMORY_STALLS`, `RS`, `SERIALIZATION`, `TOPDOWN*`, `UOPS_DECODED`, `UOPS_DISPATCHED`, `UOPS_EXECUTED`, `UOPS_ISSUED`, and `UOPS_RETIRED`. Four events use MSR selectors: `INT_MISC.BPCLEAR_CYCLES`, `INT_MISC.UNKNOWN_BRANCH_CYCLES`, `UOPS_RETIRED.MS`, and `UOPS_RETIRED.MS_SWITCHES`. Twenty-three branch cost or older near-branch aliases are marked `Deprecated`.

## Control Flow and Data Flow

There is no local runtime control flow. Build-time flow is handled by `tools/perf/pmu-events/jevents.py`: each JSON row becomes a generated PMU table entry, `EventName` is lowercased for alias matching, `Unit` is converted to the target PMU name, event and umask fields become config encodings, and optional MSR/filter fields are preserved in the generated C string. Runtime flow starts when a user requests an alias; perf resolves it against the generated Panther Lake table, chooses the correct PMU instance for `cpu_core` or `cpu_atom`, and programs the counter and any MSR selector.

The analysis flow is layered. Branch families count retired and mispredicted branch types. `CPU_CLK_UNHALTED`, `TOPDOWN`, and `TOPDOWN_*` rows feed top-down pipeline slots and bound categories. Uop families observe decode, dispatch, issue, execution, retirement, and microcode-sequencer behavior. `ARITH` and divider events expose long-latency arithmetic pressure. `LD_BLOCKS`, `MEMORY_STALLS`, `RS`, and `CYCLE_ACTIVITY` describe backend and memory-related stalls.

## State and Persistence Behavior

The only persistent state is static metadata in the repository. Runtime counter state lives in hardware PMU counters for the selected measurement interval and is not stored here. `SampleAfterValue` supplies default sampling periods but does not impose persistence semantics. Deprecated rows still persist as aliases, so compatibility is maintained while downstream tools should avoid treating them as preferred metric inputs. `CounterMask`, `EdgeDetect`, `Invert`, `MSRIndex`, and `MSRValue` are semantic state in the generated table; losing them changes what hardware condition is counted.

## Dependencies and Integration Points

This catalog depends on Panther Lake PMU encodings and Linux perf's `jevents.py` generator. It integrates with `perf list` for discoverability, `perf stat` for aggregate measurement, `perf record` for sampling, top-down analysis in `builtin-stat.c` and `util/metricgroup.c`, and any generated Intel metric expressions that refer to these event names. The file sits beside Panther Lake cache, memory, virtual-memory, and uncore catalogs, and its `cpu_core`/`cpu_atom` split must align with kernel hybrid PMU naming.

## Risks and Edge Cases

Hybrid duplication is the main risk: the same `EventName` can require different `EventCode`, `UMask`, counters, and descriptions depending on `Unit`. Tests must not deduplicate by name alone. Deprecated branch aliases may remain visible but should not be used for new metrics without checking replacements. Topdown events have special interpretation as pipeline-slot categories rather than simple event counts. MSR-qualified events can conflict with other events using the same programmable MSRs. Counter restrictions differ between core and atom rows, so oversubscribed event groups may fail or multiplex differently. Similar branch names such as `COND_TAKEN`, `COND_TAKEN_BWD`, cost, and TPEBS variants are easy to confuse.

## Test Signals

Useful validation includes JSON parse success, `jevents.py` generation success, and `perf list` exposure under both Panther Lake core PMUs. Runtime smoke tests should check that branch-heavy workloads move `BR_INST_RETIRED` and `BR_MISP_RETIRED`, divide-heavy code moves `ARITH.*`, microcode-heavy or assisted operations move `ASSISTS`/`UOPS_RETIRED.MS`, and frontend/backend pressure changes topdown categories. Hybrid systems should verify core-only and atom-only workload placement produces counts on the expected `cpu_core` or `cpu_atom` aliases. Regression tests should preserve the 23 `Deprecated` markers and the four MSR-qualified rows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/pantherlake/pipeline.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/pantherlake/uncore-memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/pantherlake/uncore-memory.json

## Purpose

`uncore-memory.json` is the Panther Lake integrated memory-controller event catalog for perf. It contains three package-scoped `iMC` events: `UNC_M_CAS_COUNT_RD`, `UNC_M_CAS_COUNT_WR`, and `UNC_M_TOTAL_DATA`. These rows expose DRAM read CAS commands, write CAS commands, and total 32-byte data transfers per DDR channel.

## Important APIs, Types, and Data Fields

The file is a JSON event array using `EventName`, `EventCode`, `Counter`, `Unit`, `PerPkg`, and `BriefDescription`. All rows use `Unit: iMC`, `PerPkg: 1`, and programmable counters `0,1,2,3,4`. The read and write CAS events use event codes `0x22` and `0x23`; total data uses event code `0x3C` and documents that the counter increments per 32-byte data chunk.

## Control Flow and Data Flow

The file has no executable flow. At build time, perf's `jevents.py` reads the rows and maps `Unit: iMC` to an uncore PMU table. At runtime, perf resolves the alias, programs the package-level iMC counter on the relevant memory-controller instance, and reports aggregate counts for the measurement interval. Data flows from memory-controller transaction accounting into perf counts, usually consumed as bandwidth or read/write traffic ratios.

## State and Persistence Behavior

The static JSON metadata is persistent. Counter values are interval-local hardware state and are not persisted by this file. `PerPkg: 1` means counts are package-scoped rather than task-scoped; any workload on the package can contribute. The 32-byte transfer granularity on `UNC_M_TOTAL_DATA` is part of the event's semantic state and must be preserved when converting counts to bytes.

## Dependencies and Integration Points

This file depends on Panther Lake iMC PMU support in the kernel and perf. It integrates with `perf list`, `perf stat`, memory bandwidth tools, and any higher-level Intel metrics that estimate DRAM traffic. It complements Panther Lake core cache, memory, and virtual-memory events by measuring traffic after requests reach the memory controller.

## Risks and Edge Cases

The package scope can mislead process-level analysis because unrelated activity contributes to counts. Per-channel interpretation depends on how perf exposes iMC instances and how users aggregate them. CAS counts and total data counts are not interchangeable: CAS rows count commands, while total data counts 32-byte chunks. Counter scheduling can be constrained by the five iMC counters. Systems without exposed Panther Lake iMC PMUs may list no usable aliases even though the generated table exists.

## Test Signals

Validation should include JSON parse success, generated event-table build success, and `perf list` visibility for `UNC_M_CAS_COUNT_RD`, `UNC_M_CAS_COUNT_WR`, and `UNC_M_TOTAL_DATA` on matching hardware. Streaming read workloads should raise read CAS and total data; streaming stores should raise write CAS and total data; idle baselines should remain low apart from background traffic. Bandwidth checks should convert `UNC_M_TOTAL_DATA` using the documented 32-byte granularity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/pantherlake/uncore-memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/pantherlake/virtual-memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/pantherlake/virtual-memory.json

## Purpose

`virtual-memory.json` defines Panther Lake perf events for data and instruction translation behavior. It contains 34 event rows: 20 for `cpu_core` and 14 for `cpu_atom`. The catalog covers DTLB load misses, DTLB store misses, ITLB misses, second-level TLB hits, page-walk starts or completions, page-walk active cycles, page-walk pending occupancy, and a load-blocked-on-DTLB-miss signal.

## Important APIs, Types, and Data Fields

Entries use `EventName`, `EventCode`, `UMask`, `Counter`, `Unit`, `SampleAfterValue`, `BriefDescription`, optional `PublicDescription`, and optional `CounterMask`. Families are `DTLB_LOAD_MISSES`, `DTLB_STORE_MISSES`, `ITLB_MISSES`, and `LD_BLOCKS.DTLB_MISS`. The same logical event names appear with different encodings for `cpu_core` and `cpu_atom`; for example `DTLB_LOAD_MISSES.STLB_HIT` is present for both units. Core rows include page-size-specific completions for 4K, 2M/4M, and 1G where applicable, while atom rows include `MISS_CAUSED_WALK` and selected completion rows.

## Control Flow and Data Flow

Build-time flow is the standard perf PMU path: `jevents.py` parses the JSON, converts `Unit` to the PMU selector, and emits event-table metadata. Runtime flow starts when perf programs the requested alias on the relevant hybrid PMU. Translation hardware then increments counters when demand loads, stores, or instruction fetches miss first-level TLBs, hit the STLB, trigger page walks, or spend cycles with busy page miss handlers.

The event families form a diagnostic progression. `STLB_HIT` identifies first-level TLB misses that were resolved without a full walk. `WALK_COMPLETED*` counts completed page walks by access type and page size. `WALK_ACTIVE` and `WALK_PENDING` expose cycle/occupancy pressure rather than transaction counts. `LD_BLOCKS.DTLB_MISS` links translation misses to load blocking behavior.

## State and Persistence Behavior

The file persists static aliases and default sample periods only. Runtime TLB contents, page tables, and PMU counter values are external state. `CounterMask` on active-cycle rows is semantically important because it changes a raw event into a thresholded cycle condition. Hybrid `Unit` state is also important: atom rows and core rows cannot be merged by name without respecting their different encodings and available counters.

## Dependencies and Integration Points

This file depends on Panther Lake core and atom PMU support, perf's generated PMU tables, and kernel exposure of hybrid PMUs. It integrates with `perf stat`, `perf record`, virtual-memory tuning, huge-page validation, code-footprint analysis, and memory-latency investigation. It complements Panther Lake pipeline stall rows and cache/memory rows by separating address-translation cost from cache-hit and DRAM-latency cost.

## Risks and Edge Cases

The main risk is comparing unlike units: walk completions are event counts, while active and pending rows are cycle or occupancy style measurements. Page-size-specific rows must be interpreted in the context of actual mappings. Some event names are duplicated across `cpu_core` and `cpu_atom`; deduplication by `EventName` would lose the correct hardware encoding. Page walks can include faulting walks where descriptions say so, so counts are not always successful translations. Workload migration across hybrid cores can obscure per-unit attribution.

## Test Signals

Validation should parse the JSON, build generated tables, and expose aliases through `perf list` for Panther Lake hybrid PMUs. Random pointer-chasing should raise DTLB load walk counters. Store-heavy sparse workloads should raise store-side rows. Huge-page runs should shift 4K walk completions toward larger-page counters. Large code-footprint workloads should affect ITLB rows. A test should verify `WALK_ACTIVE` behaves like cycle pressure while `WALK_COMPLETED` behaves like transaction counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/pantherlake/virtual-memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/rocketlake/cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/rocketlake/cache.json

## Purpose

`cache.json` is Rocket Lake's perf PMU event catalog for cache hierarchy, retired memory operations, L1/L2 behavior, offcore response filtering, snoop outcomes, and software or hardware prefetch behavior. It contains 109 event rows and is the primary Rocket Lake source for cache-hit, cache-miss, L2 request, offcore response, and address-capable retired-load diagnostics.

## Important APIs, Types, and Data Fields

The JSON event objects use `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, and often `PublicDescription`. Optional fields include `CounterMask`, `EdgeDetect`, `MSRIndex`, `MSRValue`, and `Data_LA`. There is no explicit `Unit`, so perf treats these as core PMU events for the Rocket Lake model.

Major families are `L1D`, `L1D_PEND_MISS`, `L2_LINES_IN`, `L2_LINES_OUT`, `L2_RQSTS`, `L2_TRANS`, `LONGEST_LAT_CACHE`, `MEM_INST_RETIRED`, `MEM_LOAD_L3_HIT_RETIRED`, `MEM_LOAD_MISC_RETIRED`, `MEM_LOAD_RETIRED`, `OCR`, `OFFCORE_REQUESTS`, `OFFCORE_REQUESTS_OUTSTANDING`, `SQ_MISC`, and `SW_PREFETCH_ACCESS`. Forty-five `OCR.*` rows use offcore response MSRs `0x1a6,0x1a7` with detailed `MSRValue` filters. Twenty retired memory/load rows have `Data_LA: 1`, meaning perf appends address-support wording for precise address sampling when used appropriately.

## Control Flow and Data Flow

There is no local control flow. `jevents.py` parses each row, converts event and umask fields into generated C metadata, lowercases aliases for lookup, and preserves MSR and data-address fields. At runtime, normal L1/L2 rows program core counters directly. `OCR.*` rows additionally program offcore response filter MSRs to count selected request and response combinations, such as demand code reads, demand data reads, RFOs, prefetches, L3 hits, snoop hitm, snoop miss, and any-response cases.

The analysis flow spans the cache hierarchy. `L1D_PEND_MISS` shows fill-buffer pressure and pending cycles. `L2_RQSTS` and `L2_LINES_*` show L2 access, fill, and eviction behavior. `MEM_LOAD_RETIRED` and `MEM_INST_RETIRED` identify retired memory operations and where loads were satisfied. `OCR` rows provide offcore response classification after requests leave the core.

## State and Persistence Behavior

The file persists only static PMU metadata. Runtime cache state, line ownership, snoop results, and offcore response counts live in hardware during perf sessions. `MSRValue` filters are critical persistent semantics in the generated table; changing a single mask changes the request/response category. `Data_LA` does not store addresses, but marks events that can support data address reporting when precise sampling is configured.

## Dependencies and Integration Points

This catalog depends on Rocket Lake core PMU support, offcore response MSRs, and perf's PMU event generator. It integrates with `perf stat`, `perf record`, `perf mem`, cache tuning, NUMA/coherency investigations, and Intel metric expressions that reference L1/L2/L3 and offcore events. It complements `memory.json`, which covers L3-miss DRAM and transactional-memory behavior, and `frontend.json`, which covers instruction-fetch side pressure.

## Risks and Edge Cases

The largest risk is offcore filter correctness: all `OCR.*` rows share event `0x2a` style programming but differ by `MSRValue`; any generator or manual edit that drops MSR fields collapses distinct aliases into wrong counts. `Data_LA` events need precise sampling support to produce useful addresses. `CounterMask` and `EdgeDetect` distinguish cycles from periods for rows like `L1D_PEND_MISS.FB_FULL_PERIODS`. L2 events, retired load events, and offcore rows count different stages and should not be summed blindly. Offcore response MSRs are limited resources and can conflict when grouping many filtered events.

## Test Signals

Validation should include JSON parsing, generated table build success, and `perf list` visibility for L1D, L2, retired-memory, and OCR aliases. Pointer chasing should raise `L1D_PEND_MISS` and deeper miss rows. L2-sized and LLC-sized working sets should separate L2 hits from misses. Cross-core sharing tests should exercise snoop and HITM OCR rows. Precise load sampling tests should confirm `Data_LA` rows expose address-capable descriptions and work with `perf mem` or precise `perf record` modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/rocketlake/cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/rocketlake/counter.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/rocketlake/counter.json

## Purpose

`counter.json` is Rocket Lake PMU topology metadata. It does not define named hardware events. Instead, it declares how many fixed and generic counters are available for each PMU unit represented in this model: `core`, `ARB`, and `CLOCK`.

## Important APIs, Types, and Data Fields

The file is a JSON array of three objects using `Unit`, `CountersNumFixed`, and `CountersNumGeneric`. `core` declares 4 fixed counters and 8 generic counters. `ARB` declares 0 fixed and 2 generic counters. `CLOCK` declares 1 fixed and 0 generic counters. Unlike event catalogs, rows do not have `EventName`, `EventCode`, `UMask`, descriptions, or sampling periods.

## Control Flow and Data Flow

There is no executable control flow and no runtime counting definition in the file itself. Perf build tooling reads this as model metadata alongside event JSON files. Downstream scheduling and display logic can use the declared counter capacities to understand how many events can be programmed on a PMU before multiplexing or grouping constraints apply.

## State and Persistence Behavior

The persistent state is the declared counter capacity per unit. Runtime counter allocation is external to this file and depends on requested event groups, kernel scheduling, and active perf sessions. The mixed numeric representation is notable: most values are strings, while `CLOCK.CountersNumFixed` appears as a JSON number `1`; consumers must tolerate both.

## Dependencies and Integration Points

This file depends on the Rocket Lake PMU model and perf's PMU-events metadata parser. It integrates with the other Rocket Lake event files by describing capacity rather than event semantics. It is especially relevant when users group many `cache.json`, `frontend.json`, `memory.json`, or `floating-point.json` events and perf must schedule them on finite counters.

## Risks and Edge Cases

Treating this file as a normal event list would be wrong because there are no aliases to expose. Type inconsistency between string and numeric counter counts can break strict parsers. Counter capacities are model-level facts; if they are inaccurate, perf may produce misleading scheduling expectations. `ARB` and `CLOCK` units have specialized capacities and should not be conflated with core counters.

## Test Signals

Validation should parse the JSON and confirm exactly three rows with the expected units. Generator tests should verify the file does not create bogus `EventName` aliases. Counter scheduling smoke tests can request event groups larger than eight generic core events and observe multiplexing, while fixed-counter checks should confirm fixed core and clock resources are modeled separately.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/rocketlake/counter.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/rocketlake/floating-point.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/rocketlake/floating-point.json

## Purpose

`floating-point.json` defines Rocket Lake perf events for floating-point assists and retired SSE/AVX arithmetic instruction classes. It contains 13 event rows: one `ASSISTS.FP` row and twelve `FP_ARITH_INST_RETIRED.*` rows covering scalar, vector, packed single, packed double, and width-based FLOP categories from 128-bit through 512-bit.

## Important APIs, Types, and Data Fields

Rows use `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, and `PublicDescription`. `ASSISTS.FP` uses event `0xc1`, umask `0x2`, and counters `0-7`. All arithmetic rows use event `0xc7` with different umasks for scalar, scalar single, scalar double, vector, packed 128-bit, 256-bit, 512-bit, and combined `4_FLOPS`/`8_FLOPS` categories. Descriptions explicitly state how many operations each retired instruction represents and warn that DAZ and FTZ MXCSR flags need to be set for these events.

## Control Flow and Data Flow

Build-time flow is standard JSON-to-generated-table processing through `jevents.py`. Runtime flow is perf programming the core PMU for the chosen alias. The hardware increments counters as matching floating-point instructions retire or as floating-point microcode assists occur. Higher-level analysis often multiplies counts by lane widths to estimate operations or FLOP rates, using the descriptions to distinguish scalar, packed single, packed double, and vector rows.

## State and Persistence Behavior

The file stores static metadata and default sample periods only. Runtime SIMD width, instruction mix, MXCSR state, and assist causes are external state. The meaning of a count depends on instruction class: one count can represent different numbers of arithmetic operations depending on vector width and precision. `ASSISTS.FP` measures assist events rather than retired arithmetic throughput.

## Dependencies and Integration Points

This catalog depends on Rocket Lake core PMU support and perf event-table generation. It integrates with `perf stat`, HPC FLOP accounting, compiler vectorization analysis, numerical workload tuning, and Intel metrics that group floating-point throughput under FLOPS or top-down compute categories. It complements pipeline events for execution pressure and memory/cache events for distinguishing compute-bound from memory-bound code.

## Risks and Edge Cases

Counts are not automatically FLOPs; consumers must apply the documented operation multiplier and account for instructions that count twice, such as some DPP and fused multiply-add/subtract forms. MXCSR DAZ/FTZ requirements can affect validity. 512-bit categories may be irrelevant for workloads or systems where those instruction classes are unavailable or downclocked. `ASSISTS.FP` can indicate exceptional or denormal behavior but does not identify the exact instruction without sampling context.

## Test Signals

Validation should parse the JSON, build generated tables, and expose all `FP_ARITH_INST_RETIRED.*` aliases. Microbenchmarks using scalar, 128-bit, 256-bit, and 512-bit arithmetic should move the corresponding rows. Denormal or exception-heavy floating-point tests should raise `ASSISTS.FP`. FLOP-rate tests should verify that count-to-operation conversion uses the documented lane multipliers and special double-count cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/rocketlake/floating-point.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/rocketlake/frontend.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/rocketlake/frontend.json

## Purpose

`frontend.json` is Rocket Lake's perf catalog for instruction-fetch, decode, uop-cache, MITE, microcode sequencer, and frontend starvation analysis. It contains 39 event rows spanning branch resteers, length-changing-prefix decode stalls, DSB-to-MITE transitions, frontend-retired latency sampling, instruction-cache stalls, IDQ source cycles/uops, and not-delivered uop cycles.

## Important APIs, Types, and Data Fields

Rows use `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, `PublicDescription`, and optional `CounterMask`, `EdgeDetect`, `Invert`, `MSRIndex`, and `MSRValue`. Families are `BACLEARS`, `DECODE`, `DSB2MITE_SWITCHES`, `FRONTEND_RETIRED`, `ICACHE_16B`, `ICACHE_64B`, `ICACHE_DATA`, `ICACHE_TAG`, `IDQ`, and `IDQ_UOPS_NOT_DELIVERED`.

Seventeen `FRONTEND_RETIRED.*` rows use MSR `0x3F7` with different `MSRValue` selectors for DSB misses, ITLB misses, L1I/L2/STLB misses, and latency thresholds from 1 through 512 cycles. `DSB2MITE_SWITCHES.COUNT` uses both `CounterMask: 1` and `EdgeDetect: 1`, while not-delivered rows use counter masks and inverted logic to distinguish no-uop and frontend-ok cycles.

## Control Flow and Data Flow

At build time, `jevents.py` serializes these rows into generated Rocket Lake PMU tables, preserving MSR selectors and edge/counter-mask qualifiers. At runtime, perf programs core counters and, for `FRONTEND_RETIRED.*`, configures the frontend-retired selector MSR. Data flows from branch prediction and fetch/decode structures into counters: branch resteers, DSB/MITE transitions, instruction-cache tag/data stalls, IDQ delivery by source, and retired instructions that experienced frontend latency.

The diagnostic flow separates fetch latency from fetch bandwidth. ICACHE and ITLB-related rows identify supply misses. DSB/MITE and IDQ rows identify where uops were delivered from. `IDQ_UOPS_NOT_DELIVERED` rows quantify delivery shortfall to the backend. `FRONTEND_RETIRED.LATENCY_GE_*` rows attribute retired instructions to frontend starvation intervals.

## State and Persistence Behavior

Static metadata is persisted in the JSON. Runtime frontend queues, uop-cache state, branch-predictor state, and sampled latency intervals are external. MSR selectors are persistent semantics for the generated alias and must be preserved. Edge-detected count rows and cycle rows represent different state transitions; treating them as the same unit would corrupt analysis.

## Dependencies and Integration Points

This file depends on Rocket Lake frontend PMU encodings, perf's generator, and kernel support for frontend-retired MSR programming. It integrates with `perf stat`, `perf record`, top-down frontend-bound metrics, compiler/code-layout analysis, branch tuning, instruction-cache footprint studies, and `builtin-list.c` display of event descriptions. It complements `pipeline.json`-style topdown catalogs and `virtual-memory` ITLB rows on other models.

## Risks and Edge Cases

MSR-qualified `FRONTEND_RETIRED.*` rows are selector-sensitive; dropping `MSRValue` makes many aliases indistinguishable. Latency threshold rows overlap conceptually, so counts at higher thresholds are not independent categories unless the metric formula treats them correctly. `DSB2MITE_SWITCHES.COUNT` counts transition events while `.PENALTY_CYCLES` counts cycles. LCP decode stalls depend on instruction encoding and may be rare in modern compiler output. Frontend starvation can be hidden by backend stalls, as descriptions note for some latency rows.

## Test Signals

Validation should parse the JSON, build the generated tables, and expose all frontend aliases through `perf list`. Large code-footprint workloads should raise I-cache and ITLB-related rows. Code shaped to miss the uop cache should change DSB/MITE source ratios. Synthetic LCP-heavy instruction streams can validate `DECODE.LCP`. Branchy code should move `BACLEARS.ANY`. Frontend-starved workloads should increase `IDQ_UOPS_NOT_DELIVERED` and selected `FRONTEND_RETIRED.LATENCY_GE_*` rows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/rocketlake/frontend.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/rocketlake/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/rocketlake/memory.json

## Purpose

`memory.json` is Rocket Lake's perf PMU catalog for memory-latency stalls, L3-miss demand reads, offcore DRAM response filters, transactional-memory events, and machine clears caused by memory ordering. It contains 60 rows covering `CYCLE_ACTIVITY`, HLE/RTM transaction lifecycle and abort categories, `MEM_TRANS_RETIRED` load latency thresholds, DRAM/L3-miss `OCR` filters, `OFFCORE_REQUESTS`, `OFFCORE_REQUESTS_OUTSTANDING`, `TX_EXEC`, and `TX_MEM`.

## Important APIs, Types, and Data Fields

Rows use `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, and often `PublicDescription`. Optional fields include `CounterMask`, `MSRIndex`, `MSRValue`, and `Data_LA`. Thirty-two rows use MSR selectors. Eight `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_*` rows use MSR `0x3F6` with threshold values from `0x4` through `0x200` and mark `Data_LA: 1`. Twenty-four `OCR.*` rows use offcore response MSRs `0x1a6,0x1a7` for demand code/data/RFO, prefetch, other, and streaming write requests with DRAM, local DRAM, or L3-miss response masks.

## Control Flow and Data Flow

Build-time flow is JSON parsing and generated table creation through `jevents.py`. Runtime flow is perf programming core counters plus latency or offcore MSR filters for selected aliases. The data path splits into three analysis streams. `CYCLE_ACTIVITY` and `OFFCORE_REQUESTS*` quantify L3-miss demand-load cycles and outstanding requests. `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_*` samples or counts retired loads exceeding configured latency thresholds. Transactional rows count HLE/RTM starts, commits, abort causes, and TSX memory conflicts or capacity failures.

## State and Persistence Behavior

The file persists event definitions and selector constants only. Runtime memory latency, transaction state, abort causes, and offcore response state live in CPU hardware for the measurement interval. Threshold selectors in MSR `0x3F6` are part of each alias's meaning. `Data_LA` marks address-capable load-latency rows but does not persist sampled addresses. L3-miss cycles, outstanding-request cycles, retired-load latency events, and transaction abort counts are different measurement units.

## Dependencies and Integration Points

This catalog depends on Rocket Lake PMU support for latency threshold MSR programming, offcore response filters, and transactional-memory events. It integrates with `perf stat`, `perf record`, `perf mem`, memory-latency profiling, TSX/HLE diagnostics, offcore bandwidth and locality metrics, and top-down memory-bound analysis. It complements `cache.json`, where L1/L2/L3 hit and snoop outcomes are more detailed.

## Risks and Edge Cases

Threshold rows overlap: a load slower than 512 cycles also satisfies lower threshold concepts, depending on hardware event semantics, so metrics must avoid naive summation. DRAM and local-DRAM aliases use the same masks in this file for several request classes, so naming should be checked against current Intel guidance before building locality claims. Offcore response MSRs are scarce and can conflict when many `OCR` events are grouped. TSX/HLE events may be unavailable, disabled, or uninteresting on systems with TSX disabled by microcode or kernel policy. Address-capable latency rows require precise sampling setup to produce useful addresses.

## Test Signals

Validation should include JSON parsing, generated table build success, and `perf list` visibility for latency, offcore, and transaction aliases. Pointer-chasing and cache-miss microbenchmarks should move L3-miss cycle and load-latency threshold rows. Remote or high-latency memory scenarios should increase higher thresholds. TSX/HLE test programs should move start, commit, and abort counters when TSX is enabled. Group scheduling tests should check conflicts among MSR-filtered offcore rows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/rocketlake/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/rocketlake/metricgroups.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/rocketlake/metricgroups.json

## Purpose

`metricgroups.json` is Rocket Lake metric group description metadata for perf. It is not an event list. It maps 138 metric group names to human-readable descriptions, mostly derived from Intel top-down microarchitecture analysis grouping names and generated metric-group categories. Perf uses these descriptions to explain groups shown by metric listing and metric selection features.

## Important APIs, Types, and Data Fields

The file is a single JSON object, not an array. Keys are group names and values are descriptions. Examples include broad groups such as `Backend`, `Frontend`, `MemoryBound`, `Flops`, `Branches`, `Pipeline`, `TopdownL1` through `TopdownL6`, and generated category groups such as `tma_backend_bound_group`, `tma_fetch_latency_group`, `tma_memory_bound_group`, `tma_dtlb_load_group`, `tma_fp_arith_group`, and `tma_retiring_group`. There are also issue-link groups such as `tma_issueBW`, `tma_issueLat`, and `tma_issueTLB`. About 52 keys are topdown or `tma_*_group` style descriptions.

## Control Flow and Data Flow

`jevents.py` handles this file on a separate path from normal event JSON. When an item name ends with `metricgroups.json`, the generator loads it as a dictionary, adds each group name and description to the generated big C string table, stores offsets in `_metricgroups`, and emits a sorted `metricgroups` lookup table. The generated `describe_metricgroup(const char *group)` function performs binary search over that table and returns a description string for a group name.

At runtime, perf list and metric display code can use group names attached to metrics and call the generated description lookup to show what a group means. No hardware counter is programmed directly by this file.

## State and Persistence Behavior

The persistent state is the group-name-to-description mapping. There are no counters, event encodings, sample periods, or PMU units. Ordering in the source file is not semantically important because the generator sorts groups for binary search. The names are externally visible UI and metric-selection contracts; renaming a key can break user habits, tests, or generated metric references even if descriptions remain similar.

## Dependencies and Integration Points

This file depends on generated Intel metric names and perf's metricgroup infrastructure. It integrates with `jevents.py`, generated `pmu-events.c`, `util/metricgroup.c`, `builtin-list.c`, and Python list tooling that displays metrics by group. It complements Rocket Lake event files indirectly: event files provide raw aliases, metric definition files attach formulas to groups, and this file describes those groups for humans.

## Risks and Edge Cases

The schema differs from normal PMU event arrays; treating it as `.[].EventName` data will fail. Duplicate or misspelled group names can make descriptions unavailable for metrics that reference the intended group. Descriptions are mostly generic "Grouping from Top-down Microarchitecture Analysis Metrics spreadsheet" text, so they aid categorization but not detailed diagnosis. Binary-search lookup in generated code assumes the emitted table is sorted by group key. Because this is UI metadata, regressions may appear in `perf list metricgroups` rather than counter behavior.

## Test Signals

Validation should parse the file as a JSON object and confirm 138 key/value pairs. Generator tests should verify `jevents.py` routes it through the metricgroup path and does not try to parse event fields. Runtime tests should check `perf list metricgroups`, metric listing by groups such as `TopdownL1`, `MemoryBound`, and `tma_backend_bound_group`, and `describe_metricgroup` behavior for known and unknown group names. A schema test should reject conversion to event-array format.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/rocketlake/metricgroups.json -->
