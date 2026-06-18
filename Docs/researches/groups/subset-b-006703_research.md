# subset-b-006703 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/nehalemep/pipeline.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/nehalemep/pipeline.json

## Purpose
This JSON file is the Nehalem EP pipeline PMU event table consumed by perf's `pmu-events` generator. It declares 109 core pipeline aliases for arithmetic execution, branch decode/execute/retire, clocks, instruction decode queue behavior, loop stream detector behavior, machine clears, renamer/resource stalls, SIMD uop retirement, and uop decode/issue/execute/retire accounting. The file is byte-identical to the Nehalem EX `pipeline.json`, so its architectural meaning is shared while its source path keeps it selectable for the `nehalemep` CPU-map entry.

## Important APIs, Types, And Fields
The data is an array of event objects, not executable code. The API surface is the perf PMU event schema: `EventName`, `EventCode`, `UMask`, `BriefDescription`, `Counter`, and `SampleAfterValue`, plus optional `PEBS`, `AnyThread`, `EdgeDetect`, `Invert`, and `CounterMask`. Fixed-counter aliases such as `INST_RETIRED.ANY`, `CPU_CLK_UNHALTED.THREAD`, and `CPU_CLK_UNHALTED.REF` use strings like `Fixed counter 1`, `Fixed counter 2`, and `Fixed counter 3` in `Counter` instead of `EventCode`/`UMask`. Programmable forms such as `CPU_CLK_UNHALTED.THREAD_P` and `CPU_CLK_UNHALTED.REF_P` use event `0x3C`.

## Control Flow
There is no local function control flow. Build-time flow is declarative: `tools/perf/pmu-events/jevents.py` reads the JSON, validates object fields, emits generated `pmu-events.c`, and `Makefile.perf` links the generated object into `libpmu-events.a`. Runtime perf list/record/stat paths then resolve an alias such as `UOPS_RETIRED.ANY` to the event encoding and constraints declared here.

## State And Persistence
The file persists hardware event metadata only. It does not mutate state, but it determines generated static tables shipped in the perf binary. Sampling defaults are mostly `SampleAfterValue: 2000000`. Precise events are marked with `PEBS`, including retired branches, retired instructions, retired SSE uops, and retired uops. Stall cycle aliases rely on `CounterMask`/`Invert`, for example total-cycle style events and no-uop-issued cycle counts.

## Dependencies And Integration Points
The table depends on x86 Nehalem EP PMU semantics and on the x86 `mapfile.csv` selecting the `nehalemep` directory for matching CPUs. It integrates with perf's alias lookup, generated event printing, and tests around generated `pmu-events.c`. Counter constraints matter: several events are available on `0,1,2,3`, while fixed counter aliases bypass generic counters. `AnyThread` appears on selected core-wide issue/execute cycle events, so schedulers and users must account for cross-thread counting semantics.

## Risks
The main risk is silent semantic drift: a wrong `UMask`, `CounterMask`, `Invert`, or fixed-counter string builds cleanly but produces incorrect measurements. Precise `PEBS` values must match kernel support expectations. Because this file duplicates the EX pipeline table, any intentional EP/EX divergence would be hidden unless both paths are reviewed. The spelling in descriptions is not functional, but event names and encodings are parser-sensitive.

## Test Signals
Useful signals are `jq empty`/schema validation, `make -C tools/perf JEVENTS_ARCH=x86` or equivalent generation of `pmu-events.c`, `perf test` cases for generated PMU events, and `perf list` on a Nehalem EP mapping to confirm aliases appear. Spot-check fixed aliases, PEBS aliases, and counter-mask/invert stall aliases because they exercise nontrivial schema fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/nehalemep/pipeline.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/nehalemep/virtual-memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/nehalemep/virtual-memory.json

## Purpose
This file defines 14 Nehalem EP virtual-memory PMU aliases for data and instruction TLB behavior. It covers first-level DTLB misses, second-level TLB hits, completed page walks, ITLB flushes, ITLB misses, large ITLB hits, and precise retired load/store/instruction events that missed translation structures. It is byte-identical to the Nehalem EX `virtual-memory.json`, preserving shared event semantics under the EP source path.

## Important APIs, Types, And Fields
The schema is the perf PMU event JSON array. Objects use `EventName`, `EventCode`, `UMask`, `Counter`, `BriefDescription`, `SampleAfterValue`, and optional `PEBS`. Representative families are `DTLB_LOAD_MISSES`, `DTLB_MISSES`, `ITLB_MISSES`, `ITLB_MISS_RETIRED`, `LARGE_ITLB`, `MEM_LOAD_RETIRED.DTLB_MISS`, and `MEM_STORE_RETIRED.DTLB_MISS`. Most aliases can use counters `0,1,2,3`, and precise retired translation misses use `PEBS: 1`.

## Control Flow
The file has no executable flow. During perf builds, `jevents.py` loads the JSON for the selected x86 model directory, converts the aliases into generated C tables, and the perf frontend later resolves user-facing names into raw event selectors. At runtime, the hardware PMU performs counting; the JSON only controls how perf programs the event code and unit mask.

## State And Persistence
The persisted state is the event catalog. There is no mutable state, persistence layer, or runtime cache in the file itself. Its contents become static generated data in `pmu-events.c`. `SampleAfterValue` uses `2000000`, which affects the default sampling period exposed for these aliases.

## Dependencies And Integration Points
The file depends on Nehalem EP PMU definitions and the perf `pmu-events` schema. It integrates with model selection through the x86 mapfile, with alias display through `perf list`, and with event parsing for `perf stat`/`perf record`. The precise retired DTLB/ITLB events integrate with PEBS-capable sampling paths, while non-precise walk/miss aliases use generic counters.

## Risks
Translation events are often used for memory-latency diagnosis, so event-code or `UMask` mistakes can mislead performance investigations. The small table reduces maintenance surface, but the EP/EX duplication means fixes must be kept synchronized unless a real model difference is discovered. The `MEM_STORE_RETIRED.DTLB_MISS` event uses event code `0xC` while load-retired DTLB miss uses `0xCB`; these asymmetric encodings are easy to accidentally normalize.

## Test Signals
Validate JSON syntax and generated `pmu-events.c`. Use `perf list` on a mapped Nehalem EP build to verify all 14 aliases are present. Functional smoke tests should include at least one generic walk event and one PEBS retired miss event so both plain and precise paths are covered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/nehalemep/virtual-memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/nehalemex/cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/nehalemex/cache.json

## Purpose
This is the large Nehalem EX cache and offcore-cache PMU table. It contains 319 aliases spanning L1D line replacement and MESI-state accesses, L1I hits/misses/stalls, L2 data requests, lines in/out, L2 request/transaction/write categories, longest-latency cache references, retired load/cache-hit PEBS events, retired memory latency threshold events, offcore response matrices, lock cycles, super-queue pressure, and store-block events.

## Important APIs, Types, And Fields
Objects follow the perf event schema with `EventName`, `EventCode`, `UMask`, `Counter`, `BriefDescription`, and `SampleAfterValue`. This file also uses `PEBS` for 23 precise retired memory events and `MSRIndex`/`MSRValue` for 218 threshold/offcore events. Offcore response aliases use event `0xB7`, `UMask: 0x1`, counter `2`, and `MSRIndex: 0x1A6`; the `MSRValue` encodes request class and response location. Memory latency threshold aliases use `MSRIndex: 0x3F6`, event `0xB`, `UMask: 0x10`, counter `3`, and threshold values from 0 through 32768.

## Control Flow
The JSON is declarative. `jevents.py` reads each object, emits generated PMU tables, and perf later programs counters using the encoded event selector. The special flow for this file is offcore and threshold programming: when a user selects an alias like `OFFCORE_RESPONSE.DEMAND_DATA_RD.REMOTE_CACHE_HITM`, perf must program the event plus the model-specific MSR filter, not just `EventCode`/`UMask`.

## State And Persistence
The file persists a static catalog of cache measurements. It has no mutable state, but its `MSRValue` fields persist model-specific filter bitmasks in generated data. Most events use `SampleAfterValue: 2000000`. PEBS retired load events such as `MEM_LOAD_RETIRED.L1D_HIT`, `L2_HIT`, `LLC_MISS`, and latency-threshold events influence precise sampling behavior.

## Dependencies And Integration Points
The file depends on Nehalem EX uncore/offcore filter semantics, generic x86 PMU counters, and perf support for `MSRIndex`/`MSRValue`. It integrates with `perf list` category display, event alias resolution, generated `pmu-events.c`, and kernel PMU programming for offcore response events. It is closely related to `memory.json`, which contains a narrower DRAM/LLC-miss offcore subset.

## Risks
The highest risk is incorrect offcore filter masks: many aliases share the same visible event selector, so only `MSRValue` differentiates local/remote cache, DRAM, IO/CSR/MMIO, HIT/HITM, demand, prefetch, RFO, and code/data forms. Counter constraints are also significant because offcore aliases are bound to counter 2 and latency thresholds to counter 3. A generated table may compile while measuring the wrong request class. Duplicated matrix entries also raise copy/paste drift risk.

## Test Signals
Run JSON validation, `jevents.py` generation, and generated PMU event tests. Inspect generated rows for at least one L1/L2 plain event, one PEBS retired load event, one latency-threshold event using MSR `0x3F6`, and one offcore response event using MSR `0x1A6`. On capable hardware or emulation, `perf stat -e` smoke tests should include an offcore alias to catch MSR programming issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/nehalemex/cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/nehalemex/counter.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/nehalemex/counter.json

## Purpose
This file is the Nehalem EX PMU counter inventory. It does not define event aliases; it declares the core PMU unit and the number of fixed and generic counters available to perf metadata consumers.

## Important APIs, Types, And Fields
The array contains a single object: `Unit: core`, `CountersNumFixed: 4`, and `CountersNumGeneric: 4`. Unlike the event tables, it has no `EventName`, `EventCode`, `UMask`, or descriptions. Its schema role is capacity metadata rather than alias metadata.

## Control Flow
There is no executable control flow. Build-time parsing treats this as an input to the same `pmu-events` data pipeline, allowing generated metadata to represent the PMU's counter resources for the `nehalemex` model.

## State And Persistence
The file persists static counter-count data. It does not store runtime counter state and does not change with workload execution. Generated perf tables may embed this metadata so user-facing tooling understands the available fixed and programmable counters.

## Dependencies And Integration Points
It depends on the perf JSON parser accepting counter metadata objects in architecture model directories. It integrates with `jevents.py`, generated `pmu-events.c`, and perf code that reports or reasons about PMU counter capabilities. It should remain consistent with fixed-counter aliases in the neighboring event files, such as fixed counter 1 for instructions retired and fixed counters 2/3 for unhalted/thread reference cycles.

## Risks
The file is tiny, but a wrong count has broad scheduling implications: perf may overstate or understate the number of simultaneously usable counters. The `CountersNumFixed: 4` value must be reconciled with any fixed aliases exposed elsewhere for this model. Because this object lacks `EventName`, tooling that assumes every JSON object is an event can fail or misclassify the file.

## Test Signals
Run `jq` validation and the perf `pmu-events` generator. Tests should include the generation path for model metadata, not only event aliases. A useful review check is to compare fixed-counter alias usage in `pipeline.json` against the declared fixed counter count here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/nehalemex/counter.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/nehalemex/floating-point.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/nehalemex/floating-point.json

## Purpose
This file defines 28 Nehalem EX floating-point, MMX, SSE, and SIMD integer PMU aliases. It covers x87 floating-point assists, computational FP operations, FP/MMX transitions, 128-bit SIMD integer operation classes, and 64-bit SIMD integer operation classes.

## Important APIs, Types, And Fields
The schema is an event-object array with `EventName`, `EventCode`, `UMask`, `Counter`, `BriefDescription`, `SampleAfterValue`, and optional `PEBS`. Families include `FP_ASSIST`, `FP_COMP_OPS_EXE`, `FP_MMX_TRANS`, `SIMD_INT_128`, and `SIMD_INT_64`. `FP_ASSIST.ALL`, `.INPUT`, and `.OUTPUT` are precise events with `PEBS: 1`; the rest are generic execution counters available on counters `0,1,2,3`.

## Control Flow
The file has no functions. Perf's build process reads the JSON, generates C event tables, and runtime perf alias lookup maps user names to event selectors. The CPU hardware performs the actual counting of FP and SIMD activity.

## State And Persistence
The file persists static event metadata and default sample periods. It does not maintain runtime state. Precise assist events are important because they can be used to sample problematic x87 operations more accurately than broad execution counters.

## Dependencies And Integration Points
It depends on Nehalem EX PMU encodings for FP/SIMD execution and on perf's PEBS handling for assist events. It integrates with the generated x86 event table, `perf list`, and command lines such as `perf stat -e FP_COMP_OPS_EXE.SSE_FP_PACKED`. The event families complement pipeline retired SSE-uop aliases, but this file focuses on execution and assist categories.

## Risks
The table mixes x87, MMX, SSE floating-point, and SIMD integer terminology; mislabeling an event can send users to the wrong optimization target. `FP_COMP_OPS_EXE` masks are easy to confuse because several aliases share the same event code with different unit masks. PEBS support on assist events must be preserved if the event is used for precise sampling.

## Test Signals
Validate JSON and generated `pmu-events.c`. Check that all five families appear in `perf list`. Generation tests should include at least one PEBS `FP_ASSIST` alias and one SIMD integer alias to cover both precise and generic forms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/nehalemex/floating-point.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/nehalemex/frontend.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/nehalemex/frontend.json

## Purpose
This small file defines three Nehalem EX frontend/decode aliases: `MACRO_INSTS.DECODED`, `MACRO_INSTS.FUSIONS_DECODED`, and `TWO_UOP_INSTS_DECODED`. They expose decoded instruction volume, macro-fusion activity, and two-uop decoded instruction counts.

## Important APIs, Types, And Fields
Each object uses the standard event fields `EventName`, `EventCode`, `UMask`, `Counter`, `BriefDescription`, and `SampleAfterValue`. All three aliases are usable on counters `0,1,2,3` and use the default sample value `2000000`. No `PEBS`, `MSRIndex`, edge, invert, or counter-mask fields are present.

## Control Flow
There is no executable control flow. `jevents.py` converts the three declarative aliases into generated C entries. At runtime, perf resolves the names and programs the PMU event selector, while the processor counts decode/frontend activity.

## State And Persistence
The file stores static alias metadata only. It does not persist workload state. Because the table is small and simple, the main persisted behavior is alias naming and event encoding.

## Dependencies And Integration Points
The file depends on Nehalem EX frontend PMU event encodings. It integrates with the x86 model event table, `perf list`, and `perf stat`/`perf record` alias parsing. These counters complement broader pipeline events in `pipeline.json`, especially decode and uop-delivery diagnostics.

## Risks
The risk profile is mostly schema and encoding correctness. With only three aliases, any wrong event code or mask has visible user impact. Because no special fields are present, parser regressions are unlikely to be isolated here; this file is better as a simple baseline event-table fixture.

## Test Signals
Run JSON validation and generated table tests. Use `perf list` or generated output inspection to confirm all three aliases are emitted with counters `0,1,2,3`. These entries are useful as plain-event smoke tests because they avoid PEBS and MSR side paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/nehalemex/frontend.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/nehalemex/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/nehalemex/memory.json

## Purpose
This file defines 67 Nehalem EX memory-oriented offcore response aliases. It focuses on LLC misses and DRAM locality: `ANY_DRAM`, `ANY_LLC_MISS`, `LOCAL_DRAM`, and `REMOTE_DRAM` variants across request classes such as data reads, instruction fetches, all requests, RFOs, core writebacks, demand data, demand ifetch, demand RFO, prefetch data, prefetch ifetch, and prefetch RFO.

## Important APIs, Types, And Fields
Each alias uses `EventCode: 0xB7`, `UMask: 0x1`, `Counter: 2`, `MSRIndex: 0x1A6`, and a request/response-specific `MSRValue`. The objects also include `EventName`, `BriefDescription`, and `SampleAfterValue`. Unlike `cache.json`, this file has no `PEBS`; it is entirely offcore MSR-filter metadata.

## Control Flow
The file is declarative. Build-time `jevents.py` emits generated rows that include both the visible PMU event selector and the model-specific offcore filter. Runtime perf must program the offcore response MSR as well as the counter event; otherwise aliases collapse to the same raw event and lose their memory-location meaning.

## State And Persistence
The static state is the offcore request/response matrix. The important persisted values are the `MSRValue` bitmasks, which distinguish local DRAM, remote DRAM, all DRAM, and LLC-miss categories. There is no mutable state in the JSON itself.

## Dependencies And Integration Points
This table depends on Nehalem EX offcore response MSR semantics and perf support for `MSRIndex`/`MSRValue`. It integrates with `cache.json`, which contains broader offcore cache/location aliases. It is relevant for NUMA and memory locality diagnosis because local-vs-remote DRAM distinctions are encoded directly in alias names and filters.

## Risks
The primary risk is offcore filter drift. Since all aliases share `EventCode`, `UMask`, and counter, incorrect `MSRValue` values are hard to detect by superficial generated-code checks. Missing locality variants could weaken performance diagnostics on multi-socket Nehalem EX systems. Counter 2 binding can also create scheduling conflicts with other counter-2-only events.

## Test Signals
Validate JSON syntax and generated `pmu-events.c`. Inspect generated entries for representative aliases from each response class: `ANY_LLC_MISS`, `LOCAL_DRAM`, and `REMOTE_DRAM`. Hardware smoke tests should use at least one local and one remote DRAM alias where the platform can expose different traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/nehalemex/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/nehalemex/other.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/nehalemex/other.json

## Purpose
This file collects 13 Nehalem EX aliases that do not fit cleanly into cache, memory, frontend, pipeline, or floating-point categories. It covers segment rename events, I/O transactions, load dispatch paths, partial address alias false dependencies, store-buffer drain stalls, snoop responses, and super-queue full stalls.

## Important APIs, Types, And Fields
Objects use the simple event schema: `EventName`, `EventCode`, `UMask`, `Counter`, `BriefDescription`, and `SampleAfterValue`. Families are `ES_REG_RENAMES`, `IO_TRANSACTIONS`, `LOAD_DISPATCH`, `PARTIAL_ADDRESS_ALIAS`, `SB_DRAIN`, `SEG_RENAME_STALLS`, `SNOOP_RESPONSE`, and `SQ_FULL_STALL_CYCLES`. No PEBS, offcore MSR, edge, invert, or counter-mask fields are used.

## Control Flow
The file has no local code flow. It enters perf through the same `jevents.py` build pipeline and becomes generated alias data. Runtime perf resolves these aliases to raw event selectors, and the hardware counts the corresponding microarchitectural condition.

## State And Persistence
The file persists static alias names and encodings only. It does not track runtime state. Its `SampleAfterValue` values are the default sampling periods used when these aliases are sampled.

## Dependencies And Integration Points
The table depends on Nehalem EX PMU definitions for miscellaneous core events. It integrates with perf alias lookup and with other category files by filling diagnostic gaps: for example, `SNOOP_RESPONSE.*` complements cache-coherency analysis, while `LOAD_DISPATCH.*`, `PARTIAL_ADDRESS_ALIAS`, and `SB_DRAIN.ANY` complement memory-ordering and pipeline-stall analysis.

## Risks
The category is heterogeneous, so reviewers may overlook semantic coupling with other files. `LOAD_DISPATCH` descriptions include stage-specific naming, making copy/paste or architecture-porting errors plausible. Snoop response aliases can be misinterpreted without cache coherency context, but the JSON itself cannot encode that nuance beyond descriptions.

## Test Signals
Use JSON validation and generated-table inspection. `perf list` should show all 13 aliases under the Nehalem EX model. A broad smoke test can select one load-dispatch alias and one snoop-response alias to cover different event families in the file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/nehalemex/other.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/nehalemex/pipeline.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/nehalemex/pipeline.json

## Purpose
This JSON file is the Nehalem EX pipeline PMU event table. It declares 109 aliases for arithmetic units, branch prediction and branch retirement, unhalted clocks, instruction length decoder stalls, instruction queue writes, retired instruction classes, loop stream detector activity, machine clears, resource and renamer stalls, SSE retired uops, and uop decode/execute/issue/retire behavior. It is byte-identical to the Nehalem EP pipeline table.

## Important APIs, Types, And Fields
The file uses the perf event-object schema: `EventName`, `EventCode`, `UMask`, `BriefDescription`, `Counter`, and `SampleAfterValue`, plus `PEBS`, `AnyThread`, `EdgeDetect`, `Invert`, and `CounterMask` for selected events. Fixed aliases identify fixed counters directly. Programmable and fixed forms coexist, for example `INST_RETIRED.ANY` and `INST_RETIRED.ANY_P`, plus fixed and programmable unhalted clock aliases.

## Control Flow
There are no functions or branches in the file. The effective control flow is perf's data ingestion: `jevents.py` parses this model-directory JSON, emits generated C tables, the build links them into perf, and runtime alias lookup uses the generated row to program the PMU. Counter-mask and invert fields alter how the kernel programs event selection for stall-cycle style aliases.

## State And Persistence
The file is static metadata. It persists event encodings and default sampling periods, not measured values. `PEBS` appears on 20 precise retirement-related aliases. `CounterMask`, `Invert`, and `EdgeDetect` appear on derived cycle or edge-count forms such as total cycles, LSD inactive cycles, BACLEAR counts, and core stall cycles.

## Dependencies And Integration Points
It depends on Nehalem EX x86 PMU semantics and the model-selection mapfile. It integrates with generated `pmu-events.c`, `perf list`, event parser aliases, and kernel PMU programming. It also interacts conceptually with `frontend.json` and `floating-point.json`, which break out narrower decode and FP/SIMD event groups.

## Risks
Pipeline events are heavily used for top-down and bottleneck analysis, so incorrect encodings can distort optimization work. The nuanced fields are the riskiest: `Invert`/`CounterMask` define cycle predicates, `AnyThread` changes counting scope, and `PEBS` changes sampling behavior. Because EP and EX copies are identical, synchronization is expected; accidental divergence should be reviewed carefully.

## Test Signals
Run syntax validation and perf PMU event generation. Inspect generated entries for fixed-counter aliases, `PEBS` retired aliases, `AnyThread` stall aliases, and `CounterMask`/`Invert` cycle aliases. `perf list` should expose all 109 names for the Nehalem EX mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/nehalemex/pipeline.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/nehalemex/virtual-memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/nehalemex/virtual-memory.json

## Purpose
This file defines 14 Nehalem EX virtual-memory PMU aliases for TLB misses, page walks, ITLB flushes, large ITLB hits, and precise retired translation misses. It is byte-identical to the Nehalem EP virtual-memory table.

## Important APIs, Types, And Fields
The objects use `EventName`, `EventCode`, `UMask`, `Counter`, `BriefDescription`, `SampleAfterValue`, and optional `PEBS`. The families are `DTLB_LOAD_MISSES`, `DTLB_MISSES`, `ITLB_FLUSH`, `ITLB_MISSES`, `ITLB_MISS_RETIRED`, `LARGE_ITLB`, `MEM_LOAD_RETIRED.DTLB_MISS`, and `MEM_STORE_RETIRED.DTLB_MISS`. Precise aliases are `ITLB_MISS_RETIRED`, `MEM_LOAD_RETIRED.DTLB_MISS`, and `MEM_STORE_RETIRED.DTLB_MISS`.

## Control Flow
The file is declarative. `jevents.py` loads it during perf builds for the Nehalem EX model, writes generated PMU-event C data, and runtime perf resolves event aliases to PMU encodings. The processor and kernel PMU layer perform counting and optional precise sampling.

## State And Persistence
Only static event metadata is persisted. The file has no runtime state or persistence behavior beyond generated tables. Default sample periods are `2000000`.

## Dependencies And Integration Points
It depends on Nehalem EX TLB event encodings and perf's x86 PMU alias schema. It integrates with the generated event table and complements `memory.json` and `cache.json`: those files describe data-source locality and cache behavior, while this file isolates address-translation pressure.

## Risks
The table is small but diagnostic-sensitive. Misencoding a page-walk or second-level TLB hit event can lead to incorrect conclusions about memory pressure. The precise retired aliases must preserve `PEBS`. The EP/EX duplication should be maintained unless architecture documentation justifies divergence.

## Test Signals
Use JSON validation, `jevents.py` generation, generated-table tests, and `perf list` inspection. Include tests that exercise one non-precise walk event and one PEBS retired DTLB/ITLB event.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/nehalemex/virtual-memory.json -->
