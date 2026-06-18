# subset-b-006741 perf PMU event JSON research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereep-dp/floating-point.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereep-dp/floating-point.json

Purpose: defines 28 Westmere-EP dual-processor core PMU aliases for floating-point, MMX, SSE, and SIMD integer execution. It is a static perf event topic file consumed by `tools/perf/pmu-events/jevents.py`, not executable logic.

Important APIs/types/functions: entries use perf's JSON event schema: `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, and `PEBS` where precise sampling is supported. The key groups are `FP_ASSIST.*`, `FP_COMP_OPS_EXE.*`, `FP_MMX_TRANS.*`, `SIMD_INT_128.*`, and `SIMD_INT_64.*`. `jevents.py` maps these records into generated `struct pmu_event` rows declared by `pmu-events.h`.

Control flow: during the perf build, the file is discovered under the `westmereep-dp` mapfile directory, parsed as a JSON array, normalized by `JsonEvent` into lowercase perf aliases, and emitted into generated `pmu-events.c`. At runtime, perf selects this table for CPUID `GenuineIntel-6-2C` and exposes names such as `fp_assist.all` and `fp_comp_ops_exe.x87`.

State and persistence: the file is persistent source data only. Runtime state lives in perf's generated tables and event selector setup. PEBS markings on `FP_ASSIST.*` indicate precise sampling capabilities but do not hold state.

Dependencies and integration points: depends on x86 mapfile binding, `jevents.py` field conversions, and the kernel PMU driver accepting event select and umask values. Integrates with `perf stat`, `perf record`, and symbolic event lookup.

Risks: incorrect event codes, umasks, counter availability, or PEBS tags silently mislead profiling. The table does not encode derived metrics, so users must know how to interpret overlapping SIMD categories. Counter fields list generic counters `0,1,2,3`, which must match Westmere-EP hardware constraints.

Test signals: `jq empty` validates syntax. Build-time `jevents.py` generation, perf PMU alias tests, and manual `perf list`/`perf stat -e fp_assist.all` on Westmere-EP hardware are the strongest validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereep-dp/floating-point.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereep-dp/frontend.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereep-dp/frontend.json

Purpose: provides the small Westmere-EP DP frontend-topic table with three decode-related aliases: decoded macro-instructions, decoded macro-fusions, and decoded two-uop instructions.

Important APIs/types/functions: each record uses `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, and `BriefDescription`. The events are `MACRO_INSTS.DECODED`, `MACRO_INSTS.FUSIONS_DECODED`, and `TWO_UOP_INSTS_DECODED`. They become `struct pmu_event` rows after `jevents.py` processing.

Control flow: `jevents.py` recursively loads topic JSON files for the `westmereep-dp` directory, assigns the topic from the filename, normalizes names to lowercase aliases, and writes generated event tables. Runtime perf table selection comes from `arch/x86/mapfile.csv`, where `GenuineIntel-6-2C` maps to `westmereep-dp`.

State and persistence: no mutable state. The persisted values are raw hardware select/umask tuples and default sampling periods. perf turns them into event encodings when a user requests the alias.

Dependencies and integration points: depends on the x86 PMU event schema and the frontend event definitions being valid for Westmere-EP DP. Integrates with frontend bottleneck analysis and can be combined with pipeline counters such as `uops_decoded.*`.

Risks: because the file is tiny, omissions are easy to miss: it covers decode counts but not instruction-cache or length-decoder stalls, which are in other topic files. Bad `SampleAfterValue` or event code values would affect sampling defaults for `perf record`.

Test signals: valid JSON parsing, generated `pmu-events.c` presence, `perf list frontend`/`perf list macro_insts`, and direct event scheduling on matching hardware. Cross-checking with `pipeline.json` helps detect name drift between decode and uop counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereep-dp/frontend.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereep-dp/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereep-dp/memory.json

Purpose: defines 69 DP memory-topic aliases, dominated by `OFFCORE_RESPONSE.*` combinations for request type versus DRAM/remote response classification, plus `MISALIGN_MEM_REF.STORE`.

Important APIs/types/functions: uses core event fields plus `MSRIndex` and `MSRValue` for offcore response programming. `jevents.py` maps `MSRIndex` `0x1a6,0x1a7` to the `offcore_rsp=` event attribute while `EventCode` `0xB7, 0xBB` identifies the offcore response events. Request families include `ANY_DATA`, `ANY_IFETCH`, `ANY_REQUEST`, `ANY_RFO`, `COREWB`, `DATA_IFETCH`, `DATA_IN`, `DEMAND_*`, `PF_*`, and `PREFETCH`.

Control flow: build-time generation converts each row into a perf alias with event select, umask, and offcore MSR filter bits. At runtime, selecting an alias causes perf to configure both the PMU event and the offcore response MSR filter.

State and persistence: the JSON is static. Runtime state consists of per-event PMU programming and offcore response MSR state held while perf events are active.

Dependencies and integration points: depends on `jevents.py` MSR handling, the x86 offcore PMU implementation, and mapfile selection for CPUID `GenuineIntel-6-2C`. Integrates with memory locality analysis, remote DRAM investigation, and cache-miss source attribution.

Risks: offcore response events are highly sensitive to correct MSR bitmasks. DP names use `ANY_DRAM_AND_REMOTE_FWD` and `OTHER_LOCAL_DRAM`; these differ from SP names such as `ANY_DRAM` and `LOCAL_DRAM`, so copying between models can break semantics. EventCode lists two selectors, but `JsonEvent` uses the first for event encoding unless the generator handles the pair as intended.

Test signals: `jq empty`, generated offcore aliases containing `offcore_rsp=`, `perf list offcore_response`, and hardware tests comparing mutually related filters such as demand data reads versus all data reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereep-dp/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereep-dp/other.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereep-dp/other.json

Purpose: collects 23 Westmere-EP DP events that do not fit cache, pipeline, frontend, FP, or virtual-memory topics. It covers segment rename behavior, I/O transactions, load-dispatch sources, store-buffer and super-queue stalls, snoop queues, and snoop responses.

Important APIs/types/functions: event rows use the standard perf PMU schema and, for occupancy-style aliases, `CounterMask`. Event families include `LOAD_DISPATCH.*`, `SNOOPQ_REQUESTS.*`, `SNOOPQ_REQUESTS_OUTSTANDING.*`, `SNOOP_RESPONSE.*`, `SB_DRAIN.ANY`, and `SQ_FULL_STALL_CYCLES`.

Control flow: the file is converted by `jevents.py` into topic-tagged `struct pmu_event` records. `CounterMask` values become event modifiers for counting cycles where queue conditions hold, such as non-empty snoop queues. Runtime perf resolves these symbolic aliases after matching the CPU to the `westmereep-dp` event table.

State and persistence: no persistent state beyond source data. Runtime state is limited to active perf event configuration and counter reads.

Dependencies and integration points: integrates with memory-ordering and coherency diagnosis. Snoop queue and response events are especially relevant when interpreting multi-socket traffic alongside `memory.json` offcore events.

Risks: "other" files tend to mix semantically unrelated events, so users may assume stronger relationships than exist. Counter-mask events can count cycles rather than occurrences; confusing them with request counts distorts analysis. Some aliases are restricted to counter `0`, reducing schedulability when grouped with other events.

Test signals: JSON syntax validation, build-time generation, `perf list snoop`, and workload checks that load/store stress increases `LOAD_DISPATCH` or `SB_DRAIN` counters. Cross-validation with offcore traffic counters is useful for snoop-related rows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereep-dp/other.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereep-dp/pipeline.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereep-dp/pipeline.json

Purpose: provides 111 DP pipeline, branch, retirement, stall, uop, arithmetic, and clock aliases. It is the central Westmere-EP DP table for execution pipeline and top-level performance analysis.

Important APIs/types/functions: records use normal event fields plus advanced modifiers including `CounterMask`, `EdgeDetect`, `Invert`, `AnyThread`, and `PEBS`. Major families include `ARITH.*`, `BR_INST_EXEC.*`, `BR_MISP_EXEC.*`, `BR_INST_RETIRED.*`, `CPU_CLK_UNHALTED.*`, `ILD_STALL.*`, `INST_RETIRED.*`, `RESOURCE_STALLS.*`, `UOPS_DECODED.*`, `UOPS_EXECUTED.*`, `UOPS_ISSUED.*`, and `UOPS_RETIRED.*`.

Control flow: `jevents.py` transforms event names and modifiers into generated C table rows. Fixed-counter aliases such as `INST_RETIRED.ANY`, `CPU_CLK_UNHALTED.THREAD`, and `CPU_CLK_UNHALTED.REF` rely on `JsonEvent.real_event` special handling instead of ordinary event-code fields. Runtime perf schedules these aliases subject to counter and modifier constraints.

State and persistence: only static JSON persists. Active event groups may program fixed counters, generic counters, PEBS precise events, edge detection, inversion, and any-thread counting depending on the selected alias.

Dependencies and integration points: depends on perf's generated PMU table APIs and Westmere event semantics. Integrates with branch analysis, IPC calculations, frontend/backend stall diagnosis, and uop port utilization.

Risks: many entries share raw selectors with different modifiers, so a dropped `CounterMask`, `Invert`, `EdgeDetect`, or `AnyThread` changes meaning completely. Several aliases are cycle-style derived encodings, not plain event counts. Fixed-counter aliases must remain compatible with perf's hardcoded mappings.

Test signals: generated table inspection, `perf list` for `uops_*` and `br_*`, event scheduling tests with and without grouping, and sanity checks such as retired instructions and cycles increasing with workload duration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereep-dp/pipeline.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereep-dp/virtual-memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereep-dp/virtual-memory.json

Purpose: defines 22 DP aliases for DTLB, ITLB, EPT walks, large-page ITLB hits, and precise retired load/store TLB misses.

Important APIs/types/functions: event families include `DTLB_LOAD_MISSES.*`, `DTLB_MISSES.*`, `ITLB_MISSES.*`, `EPT.WALK_CYCLES`, `ITLB_FLUSH`, `ITLB_MISS_RETIRED`, `LARGE_ITLB.HIT`, `MEM_LOAD_RETIRED.DTLB_MISS`, and `MEM_STORE_RETIRED.DTLB_MISS`. PEBS appears on retired TLB miss events.

Control flow: the build converts the JSON records into generated PMU aliases under the `virtual-memory` topic. At runtime, perf resolves aliases after CPUID selection and configures the relevant event select/umask pairs. Precise retired aliases can be used by `perf record` for sampled attribution.

State and persistence: static event source only. Runtime state is PMU counter and sampling state; the file does not persist measurements.

Dependencies and integration points: integrates with memory-management profiling, huge-page tuning, virtualization analysis through `EPT.WALK_CYCLES`, and cache/memory locality diagnosis. Depends on the `westmereep-dp` mapfile entry and perf's PEBS handling.

Risks: DP includes three aliases absent from the SP virtual-memory assignment: `DTLB_LOAD_MISSES.LARGE_WALK_COMPLETED`, `DTLB_MISSES.PDE_MISS`, and `ITLB_MISSES.LARGE_WALK_COMPLETED`. Treating DP and SP tables as interchangeable can hide large-page or page-directory behavior. Walk-cycle events count time rather than miss instances.

Test signals: JSON validation, generated aliases in `perf list tlb`, synthetic workloads with TLB pressure, huge-page tests for large-walk aliases, and virtualization workloads for EPT walk cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereep-dp/virtual-memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereep-sp/cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereep-sp/cache.json

Purpose: defines the large 325-entry Westmere-EP single-processor cache and memory-locality event table. It spans L1D/L1I, L2 requests and transactions, cache line movement, retired memory operations, offcore requests, offcore responses, and load-latency threshold sampling.

Important APIs/types/functions: standard event fields are extended with `MSRIndex`, `MSRValue`, `CounterMask`, and `PEBS`. Major families include `L1D*`, `L1I.*`, `L2_RQSTS.*`, `L2_DATA_RQSTS.*`, `L2_LINES_*`, `L2_TRANSACTIONS.*`, `L2_WRITE.*`, `LONGEST_LAT_CACHE.*`, `MEM_INST_RETIRED.*`, `MEM_LOAD_RETIRED.*`, `MEM_UNCORE_RETIRED.*`, `OFFCORE_REQUESTS*`, and 203 `OFFCORE_RESPONSE.*` aliases.

Control flow: build-time `jevents.py` reads every row and emits generated PMU table entries. Offcore response rows use `MSRIndex` `0x1a6,0x1a7`; load latency threshold rows use `MSRIndex` `0x3F6`, which `JsonEvent` maps to `ldlat=`. Runtime perf programs normal event selectors plus MSR filters where required.

State and persistence: static source data only. Runtime state is active PMU counter configuration and MSR filter programming. PEBS retired-memory rows can carry sampled instruction attribution.

Dependencies and integration points: tied to CPUID `GenuineIntel-6-25` via `arch/x86/mapfile.csv`. Integrates with `perf list`, `perf stat`, `perf record`, memory hierarchy tuning, and locality analysis.

Risks: this file has the broadest blast radius in the assignment. Offcore and latency events depend on exact MSR bitmasks and thresholds; a typo can produce plausible but wrong numbers. Several aliases are constrained to counters `0` or `3`, which affects event grouping. The SP table has much richer locality names than the DP memory file, so model-specific semantics must be preserved.

Test signals: `jq empty`, successful `jevents.py` generation, `perf list cache`, inspection for `offcore_rsp=` and `ldlat=`, and hardware sanity workloads for L1/L2 misses, remote/local source attribution, and latency thresholds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereep-sp/cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereep-sp/counter.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereep-sp/counter.json

Purpose: declares the Westmere-EP SP core counter topology: one `core` unit with four fixed counters and four generic programmable counters.

Important APIs/types/functions: this file uses the counter-description schema rather than event rows: `Unit`, `CountersNumFixed`, and `CountersNumGeneric`. It does not define `EventName`, `EventCode`, or `UMask`.

Control flow: when perf's PMU event tooling consumes architecture data, this descriptor documents counter capacity for the model directory. Runtime event scheduling still occurs in perf and the kernel PMU driver; this file provides model metadata rather than aliases.

State and persistence: static metadata only. It does not create runtime counters; it records the expected hardware counter counts that scheduling and documentation can rely on.

Dependencies and integration points: tied to the `westmereep-sp` event directory selected for CPUID `GenuineIntel-6-25`. It contextualizes other SP topic files: many aliases list generic counters `0,1,2,3`, and fixed-counter aliases in `pipeline.json` assume fixed counter availability.

Risks: if the declared counts do not match hardware or perf scheduler assumptions, event group feasibility and diagnostic output can be misleading. Because this is a one-row file, schema drift is easy to overlook in broad JSON validators focused on `EventName`.

Test signals: JSON syntax validation, generation tooling accepting a non-event JSON record, and runtime checks that fixed-counter aliases and four-way generic event groups schedule as expected on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereep-sp/counter.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereep-sp/floating-point.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereep-sp/floating-point.json

Purpose: defines 28 Westmere-EP SP floating-point and SIMD aliases. The content matches the DP floating-point topic in shape and event families, but is bound to the SP model directory.

Important APIs/types/functions: standard event records cover `FP_ASSIST.*`, `FP_COMP_OPS_EXE.*`, `FP_MMX_TRANS.*`, `SIMD_INT_128.*`, and `SIMD_INT_64.*`. Fields include `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, and `PEBS` for precise assist events.

Control flow: `jevents.py` parses the file during perf build, derives the topic from `floating-point.json`, lowercases aliases, and emits generated `struct pmu_event` rows. Runtime table selection comes from `GenuineIntel-6-25,v4,westmereep-sp,core` in `mapfile.csv`.

State and persistence: no mutable state. perf configures generic counters and PEBS sampling only when aliases are requested.

Dependencies and integration points: integrates with floating-point assist diagnosis, SIMD utilization analysis, and legacy MMX/SSE transition detection. It shares the generated PMU event table API in `pmu-events.h`.

Risks: the table counts uops and assists, not high-level FLOPs metrics. Users must distinguish scalar, packed, single, double, SSE integer, and MMX rows. Incorrect PEBS labeling on assist events affects sampled attribution.

Test signals: valid JSON, successful perf event table generation, `perf list fp_` output on a build containing these tables, and hardware runs using floating-point/SIMD microbenchmarks to check expected counter movement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereep-sp/floating-point.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereep-sp/frontend.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereep-sp/frontend.json

Purpose: supplies three Westmere-EP SP frontend decode aliases for macro-instruction decode volume, macro-fusion decode count, and two-uop decoded instructions.

Important APIs/types/functions: records are `MACRO_INSTS.DECODED`, `MACRO_INSTS.FUSIONS_DECODED`, and `TWO_UOP_INSTS_DECODED`, each with `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, and `BriefDescription`. `jevents.py` converts them to `struct pmu_event` entries.

Control flow: the build traverses the SP model directory, reads the frontend topic JSON, and writes generated C event tables. At runtime, perf selects the SP table for CPUID `GenuineIntel-6-25` and exposes lowercase aliases to command-line event parsing.

State and persistence: static source data only. Active counter state is held by perf/kernel PMU while recording or counting.

Dependencies and integration points: complements `pipeline.json` decode and uop stall rows and `cache.json` instruction fetch rows. It is useful for frontend throughput and macro-fusion analysis.

Risks: narrow scope may be mistaken for complete frontend coverage. Instruction-cache misses, length decoder stalls, instruction queue writes, and uop decode stalls live in other topic files. Any schema change in perf event JSON handling would affect this small file the same as larger event tables.

Test signals: `jq empty`, generated alias inspection, `perf list macro_insts`, and workloads that vary branch/fusion behavior or instruction mix.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereep-sp/frontend.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereep-sp/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereep-sp/memory.json

Purpose: defines 67 SP offcore-response memory aliases focused on request type versus DRAM locality. Unlike the SP cache file, this topic is a narrower memory classification set.

Important APIs/types/functions: all rows are `OFFCORE_RESPONSE.*` entries with `EventCode` `0xB7, 0xBB`, `UMask` `0x1`, generic counters, and `MSRIndex`/`MSRValue` offcore filters. Request families include `ANY_DATA`, `ANY_IFETCH`, `ANY_REQUEST`, `ANY_RFO`, `COREWB`, `DATA_IFETCH`, `DATA_IN`, `DEMAND_*`, `PF_*`, and `PREFETCH`. Response suffixes include `ANY_DRAM`, `LOCAL_DRAM`, `REMOTE_DRAM`, and for most families `ANY_LLC_MISS`.

Control flow: `jevents.py` maps the MSR index to `offcore_rsp=` while generating C table entries. Runtime perf configures the offcore response event and the associated MSR value for each selected alias.

State and persistence: source data is static. Runtime state is temporary PMU and offcore MSR programming.

Dependencies and integration points: integrates with memory locality analysis and overlaps semantically with many `OFFCORE_RESPONSE.*` rows in `cache.json`. It is selected via the `westmereep-sp` mapfile directory.

Risks: this SP memory table differs from DP: it lacks `MISALIGN_MEM_REF.STORE`, uses `LOCAL_DRAM` instead of `OTHER_LOCAL_DRAM`, and uses `ANY_DRAM` instead of `ANY_DRAM_AND_REMOTE_FWD`. Duplicate-looking aliases across `cache.json` and `memory.json` can confuse users if both topics expose similar names.

Test signals: valid JSON, generated offcore aliases, `perf list offcore_response`, and hardware memory placement tests that distinguish local and remote DRAM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereep-sp/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereep-sp/other.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereep-sp/other.json

Purpose: groups 23 miscellaneous SP events for load dispatch, store-buffer stalls, segment rename activity, I/O transactions, snoop queue requests/outstanding cycles, snoop responses, and super-queue full stalls.

Important APIs/types/functions: the schema is standard PMU event JSON with `CounterMask` on not-empty cycle aliases. Families include `LOAD_BLOCK.OVERLAP_STORE`, `LOAD_DISPATCH.*`, `SNOOPQ_REQUESTS.*`, `SNOOPQ_REQUESTS_OUTSTANDING.*`, `SNOOP_RESPONSE.*`, `SB_DRAIN.ANY`, and `SQ_FULL_STALL_CYCLES`.

Control flow: records are parsed by `jevents.py`, topic-tagged from `other.json`, emitted into generated C, and exposed at runtime through perf's event alias lookup for the `westmereep-sp` table.

State and persistence: static descriptor data only. Runtime state is active PMU event configuration.

Dependencies and integration points: complements SP cache and memory topics for coherence and load/store behavior. Snoop-related entries are useful when interpreting multi-core sharing even on the single-processor Westmere-EP model family.

Risks: miscellaneous grouping makes discoverability and semantic consistency weaker than topic-specific files. Counter-mask rows such as `*_NOT_EMPTY` represent cycles meeting a condition, while similarly named rows without that suffix count outstanding requests. Some rows use only counter `0`, causing grouping constraints.

Test signals: `jq empty`, generated aliases in `perf list`, stress tests for store forwarding/partial address aliasing, and coherence-heavy workloads for snoop response events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereep-sp/other.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereep-sp/pipeline.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereep-sp/pipeline.json

Purpose: defines 111 SP execution pipeline aliases covering arithmetic, branches, branch mispredicts, fixed/programmed cycles, instruction retirement, decoder stalls, machine clears, RAT/resource stalls, SSE uop retirement, and uop issue/execute/retire behavior.

Important APIs/types/functions: uses the same rich schema surface as DP pipeline: `CounterMask`, `EdgeDetect`, `Invert`, `AnyThread`, and `PEBS` in addition to event code fields. Important groups include `BR_INST_EXEC.*`, `BR_MISP_EXEC.*`, `BR_*_RETIRED.*`, `CPU_CLK_UNHALTED.*`, `INST_RETIRED.*`, `RESOURCE_STALLS.*`, `UOPS_EXECUTED.*`, `UOPS_ISSUED.*`, and `UOPS_RETIRED.*`.

Control flow: build-time parsing emits generated C aliases. `JsonEvent.real_event` supplies special encodings for fixed counter names such as retired instructions and unhalted cycles. Runtime perf schedules selected aliases on fixed or generic counters according to their encoded constraints.

State and persistence: static JSON only; runtime state lives in active perf events. PEBS rows support precise sampling for retirement-related aliases.

Dependencies and integration points: tied to CPUID `GenuineIntel-6-25` through `mapfile.csv`, and to `counter.json` through fixed/generic counter capacity. Integrates with top-down-style manual analysis on older Westmere hardware.

Risks: modifier-sensitive rows are easy to corrupt. Inversion plus counter masks represent cycles lacking activity for several aliases, so display names must be interpreted carefully. Port-utilization rows have `AnyThread` variants and generic-counter constraints that affect grouped measurements.

Test signals: JSON parsing, generated fixed-counter aliases, `perf list uops`/`perf list br_`, branchy microbenchmarks for branch rows, and IPC sanity checks using retired instructions and cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereep-sp/pipeline.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereep-sp/virtual-memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereep-sp/virtual-memory.json

Purpose: defines 19 SP virtual-memory aliases for DTLB and ITLB misses, page walks, EPT walk cycles, ITLB flushes, large ITLB hits, and precise retired load/store DTLB misses.

Important APIs/types/functions: event families include `DTLB_LOAD_MISSES.*`, `DTLB_MISSES.*`, `ITLB_MISSES.*`, `EPT.WALK_CYCLES`, `ITLB_FLUSH`, `ITLB_MISS_RETIRED`, `LARGE_ITLB.HIT`, `MEM_LOAD_RETIRED.DTLB_MISS`, and `MEM_STORE_RETIRED.DTLB_MISS`. Retired TLB miss rows carry `PEBS`.

Control flow: `jevents.py` loads this topic, normalizes aliases, and generates C PMU rows. At runtime, perf chooses the SP table by CPUID and programs the corresponding event select/umask values.

State and persistence: static source file only. Runtime state is active counter or sampling configuration.

Dependencies and integration points: integrates with memory translation profiling, huge-page analysis, and virtualization investigations through EPT walk cycles. It complements `cache.json` retired memory rows and `memory.json` offcore locality events.

Risks: this SP file is slightly narrower than the DP counterpart, omitting `DTLB_LOAD_MISSES.LARGE_WALK_COMPLETED`, `DTLB_MISSES.PDE_MISS`, and `ITLB_MISSES.LARGE_WALK_COMPLETED`. Page-walk cycle aliases measure time spent walking, not just miss counts. PEBS support must match kernel PMU behavior.

Test signals: `jq empty`, generated `perf list tlb` aliases, TLB-thrashing workloads, huge-page comparisons, and VM workloads that exercise EPT walks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereep-sp/virtual-memory.json -->
