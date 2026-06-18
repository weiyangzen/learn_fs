# subset-b-006652 Research

Grouped research for `subset-b-006652`. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/cascadelakex/uncore-memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/cascadelakex/uncore-memory.json

Purpose: Defines the Cascade Lake X integrated memory-controller PMU event table for Linux perf. The file is a 509-entry JSON array under the `cascadelakex` model directory, selected by `tools/perf/pmu-events/arch/x86/mapfile.csv` for `GenuineIntel-6-55-[56789ABCDEF]`. It lets perf users name memory-controller events such as `UNC_M_CAS_COUNT.RD`, `UNC_M_PMM_READ_LATENCY`, and `LLC_MISSES.MEM_READ` instead of programming raw uncore event selectors.

Important APIs/types/functions: There are no executable functions in this file; its API is the perf PMU event JSON schema consumed by `tools/perf/pmu-events/jevents.py`. The records use `EventName`, `EventCode`, `UMask`, `Counter`, `Unit`, `PerPkg`, `BriefDescription`, `PublicDescription`, `ScaleUnit`, `MetricName`, `MetricExpr`, and `Experimental`. All entries target `Unit: iMC` and almost all use programmable counters `0,1,2,3`; `UNC_M_CLOCKTICKS_F` is the fixed 48-bit counter. The table includes DRAM CAS/read/write aliases, page activate/precharge, read/write queue inserts/occupancy/full cycles, major-mode state, Intel Optane PMM command/read/write queues, memory power states, throttling, scrub/tag-check activity, and rank/bank-specific CAS events.

Control flow: At perf build time, `jevents.py` traverses `arch/x86/cascadelakex/*.json`, parses each object, lowercases `EventName` into the generated alias name, maps `Unit: iMC` to the uncore PMU name, carries `ScaleUnit` into unit metadata, parses `MetricExpr` with the metric parser, and generates C tables compiled into perf. At runtime perf matches the Cascade Lake X CPUID mapfile row, exposes these aliases in `perf list`, and programs the underlying iMC PMU event selectors when a user records or stats one of the names. In this file, derived aliases such as `LLC_MISSES.MEM_READ` and `LLC_MISSES.MEM_WRITE` reuse CAS count encodings with `ScaleUnit: 64Bytes`, while metrics such as `UNC_M_PMM_READ_LATENCY` and `power_self_refresh` depend on other event names in the same generated table.

State and persistence behavior: The JSON is static build input. It creates no runtime state by itself, but the generated perf tables persist inside the perf binary and describe per-package uncore counters. Several events encode occupancy or residency style state in the hardware, for example queue occupancy, cycles full/not-empty, major-mode cycles, self-refresh, CKE, channel PPD, and PCU throttling. `PerPkg: 1` signals package-level aggregation rather than per-thread counting.

Dependencies: Depends on the perf PMU event schema, `jevents.py`, `metric.py` for metric expression parsing, `builtin-list.c` for displaying `ScaleUnit`/metric fields, the x86 mapfile entry for Cascade Lake X, and the kernel/hardware uncore iMC PMU exposing the expected event codes. Metric rows depend by name on `UNC_M_CLOCKTICKS`, `UNC_M_PMM_RPQ_OCCUPANCY.ALL`, `UNC_M_PMM_RPQ_INSERTS`, and `UNC_M_PMM_WPQ_INSERTS`.

Integration points: Integrates with `perf list`, `perf stat`, generated `pmu-events.c`, generated aliases for uncore iMC PMUs, and higher-level metric groups from `clx-metrics.json`/`metricgroups.json` when those metrics reference these event names. The uncore-memory topic sits beside Cascade Lake X core and uncore topic files, and its per-package iMC events are intended for socket/channel-level memory bandwidth, latency, power, and PMM analysis rather than per-process attribution.

Risks: The table is large and repetitive, especially the 8 ranks x 21 read-bank events and 8 ranks x 21 write-bank events, so copy/paste drift in `EventCode`, `UMask`, or descriptions is the main maintenance risk. `Experimental: 1` is widespread across rank/bank, PMM, power, and scrub-buffer events, so users may treat unstable encodings as authoritative. Metric expressions can divide by zero or disappear if a dependent event is renamed. The `LLC_MISSES.*` names are convenient but are backed by memory-controller CAS traffic, so they can be mistaken for core LLC miss events. `ScaleUnit: 6.103515625E-5MiB/sec` on PMM bandwidth implies a sampling/time convention that must remain consistent with perf's scaling rules.

Test signals: Validate the file with JSON parsing; run perf's `jevents.py` generation for x86; verify `perf list` shows representative aliases from CAS, PMM, power, queue, rank, and scrub families; check generated metrics parse for `UNC_M_PMM_BANDWIDTH.TOTAL`, `UNC_M_PMM_READ_LATENCY`, `power_channel_ppd`, and `power_self_refresh`; compare key encodings against Intel uncore documentation; and smoke-test `perf stat` on Cascade Lake X hardware for `unc_m_cas_count.rd`, `LLC_MISSES.MEM_READ`, fixed `UNC_M_CLOCKTICKS_F`, and one rank/bank event.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/cascadelakex/uncore-memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/cascadelakex/uncore-power.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/cascadelakex/uncore-power.json

Purpose: Defines 25 Cascade Lake X package-control-unit power and residency PMU aliases for perf. The events expose PCU fixed-clock time, frequency-limit causes, package C-state residency, power-state occupancy, phase shedding, PROCHOT, VR hot, and transition-cycle accounting.

Important APIs/types/functions: The schema is the perf PMU event JSON object consumed by `jevents.py`. Every record uses `Unit: PCU`, `PerPkg: 1`, and counters `0,1,2,3`; most are marked `Experimental: 1`. `EventName` families include `UNC_P_CLOCKTICKS`, `UNC_P_FREQ_MAX_LIMIT_THERMAL_CYCLES`, `UNC_P_FREQ_MAX_POWER_CYCLES`, `UNC_P_FREQ_MIN_IO_P_CYCLES`, `UNC_P_FREQ_TRANS_CYCLES`, `UNC_P_PKG_RESIDENCY_C0/C2E/C3/C6_CYCLES`, `UNC_P_POWER_STATE_OCCUPANCY.CORES_C0/C3/C6`, `UNC_P_PROCHOT_*`, and `UNC_P_VR_HOT_CYCLES`.

Control flow: During perf generation, each JSON object becomes a PCU alias in the Cascade Lake X generated table. At runtime, perf selects this table through the x86 mapfile, resolves the alias to the PCU PMU, and programs the listed `EventCode`/`UMask` values. The PCU clock event has no explicit `EventCode` and is described as a fixed 1 GHz pclk cycle source, which users can combine with residency or limit cycles to compute percentages.

State and persistence behavior: This file is static metadata. Hardware state represented by the events is package-wide and persistent across cores while the counters are enabled: package C-state residency excludes transition time, transition events count frequency or core/package state changes, and occupancy events report the number of cores in selected C-states. No data is stored by the JSON at runtime beyond generated perf tables.

Dependencies: Depends on perf's uncore event schema, the generated x86 Cascade Lake X event map, and kernel exposure of the PCU uncore PMU. The descriptions assume Cascade Lake X PCU semantics, including 1 GHz pclk, package residency states C0/C2E/C3/C6, FIVR phase-shedding states, and PROCHOT/VR hot throttling sources.

Integration points: Integrates with `perf list` and `perf stat` for package-level power diagnosis. It complements `uncore-memory.json`: PCU throttling and memory phase-shedding events help explain memory-controller latency or bandwidth drops observed through iMC counters. Occupancy and transition events can be paired with core workload counters to separate idle policy from workload bottlenecks.

Risks: Nearly every event is experimental, so names or encodings may lag vendor documentation. Several rows have terse descriptions only, making user interpretation depend on external PCU documentation. Package-wide events can be misread as per-process metrics. Events without `UMask` rely on perf generating a valid event string from only the event code and PMU unit; `UNC_P_CLOCKTICKS` additionally relies on special uncore handling for clockticks.

Test signals: JSON parse and x86 `jevents.py` generation should succeed. `perf list` should expose PCU aliases under Cascade Lake X. On hardware, `UNC_P_CLOCKTICKS` should scale close to elapsed wall time at 1 GHz while enabled; residency and transition events should respond to idle-state and frequency-policy changes; thermal/power/PROCHOT events should stay near zero on an unconstrained system and increase under controlled throttling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/cascadelakex/uncore-power.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/cascadelakex/virtual-memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/cascadelakex/virtual-memory.json

Purpose: Defines 28 Cascade Lake X core PMU aliases for virtual-memory translation behavior. It covers DTLB load and store misses, ITLB misses, EPT walks, instruction TLB flushes, DTLB thread flush attempts, and STLB flush attempts.

Important APIs/types/functions: The file uses the core perf event schema with `EventName`, `EventCode`, `UMask`, `Counter`, `CounterMask`, `SampleAfterValue`, `BriefDescription`, and `PublicDescription`. All programmable entries use counters `0,1,2,3`. Event families are `DTLB_LOAD_MISSES`, `DTLB_STORE_MISSES`, `ITLB_MISSES`, `EPT`, `ITLB`, and `TLB_FLUSH`. `WALK_ACTIVE` events use `CounterMask: 1` with `UMask: 0x10`; `WALK_PENDING` uses the same umask without the counter mask to count PMH-busy cycles per page-miss handler.

Control flow: `jevents.py` parses the virtual-memory topic into generated Cascade Lake X core aliases. At runtime, perf maps alias names such as `dtlb_load_misses.walk_completed_4k` or `itlb_misses.walk_pending` to raw core PMU event encodings. The load, store, and instruction families share a pattern: cause-a-walk, STLB hit, active cycles, completed walks for all page sizes, and completed walks split by 4K, 2M/4M, and 1G pages.

State and persistence behavior: The JSON is immutable build metadata. The observed hardware state is per-core translation activity while counters run. Completed walk events include page walks that end with or without faults; EPT walk pending counts nested translation work; TLB flush events count attempts rather than necessarily completed invalidations. `SampleAfterValue` provides perf's default sampling period, with high periods for common events and lower values for rarer flush/walk events.

Dependencies: Depends on the core Cascade Lake X mapfile selection, perf event generation, and the CPU core PMU supporting event codes `0x08`, `0x49`, `0x4f`, `0x85`, `0xAE`, and `0xBD`. The descriptions assume Skylake-derived page-miss-handler semantics and explicitly note that EPT page-walk duration is excluded from the DTLB/ITLB walk-active and walk-pending events on Skylake-family cores.

Integration points: Integrates with `perf stat`/`perf record` for page-walk and TLB-pressure profiling. It can be paired with memory, cache, and pipeline events to diagnose translation overhead versus cache misses, and with virtualization workloads through `EPT.WALK_PENDING`. It is source-tree-aligned with the Cascade Lake X topic files generated into the same CPU model table.

Risks: `MISS_CAUSES_A_WALK` does not require walk completion, while `WALK_COMPLETED` does; mixing them in ratios can produce misleading fault or cancellation interpretations. `WALK_ACTIVE` and `WALK_PENDING` share the same umask but different counting semantics, so losing `CounterMask` would change the meaning. The public descriptions mention Skylake behavior even though the file is Cascade Lake X, which is probably intentional lineage but may confuse users. Flush attempt events may overcount relative to effective TLB invalidations.

Test signals: Parse the JSON, run `jevents.py`, and verify `perf list` shows all load/store/ITLB walk aliases plus `EPT.WALK_PENDING`, `ITLB.ITLB_FLUSH`, and `TLB_FLUSH.*`. Hardware tests should compare page-walk events under 4K pages versus huge pages, check store and load walks separately, and confirm `WALK_ACTIVE`/`WALK_PENDING` increase under TLB-stressing workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/cascadelakex/virtual-memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/clearwaterforest/cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/clearwaterforest/cache.json

Purpose: Defines the Clearwater Forest core cache-topic PMU aliases for perf. The 17 entries cover LLC references/misses, retired load/store memory uops, PEBS load-latency threshold events, store-latency aliasing, and offcore response demand data/RFO events with any response.

Important APIs/types/functions: This is perf PMU event JSON consumed by `jevents.py` for the `clearwaterforest` model selected by `GenuineIntel-6-DD`. Common fields are `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, and `PublicDescription`. PEBS load-latency events also use `MSRIndex: 0x3F6` and threshold-specific `MSRValue` values from `0x4` through `0x800`. Offcore response events use `EventCode: 0xB7`, `UMask: 0x1`, `MSRIndex: 0x1a6,0x1a7`, and response selector `MSRValue` values `0x10001` and `0x10002`.

Control flow: Build-time generation converts these JSON rows into Clearwater Forest aliases. At runtime, perf resolves `LONGEST_LAT_CACHE.MISS` and `.REFERENCE` to core PMU event `0x2e`, resolves `MEM_UOPS_RETIRED.*` to event `0xd0`, and writes the extra MSRs for latency threshold or offcore-response filters when required. The latency threshold aliases all share event `0xd0/umask 0x5` but differ by `MSRValue`, so the event name is the user-facing selector for the threshold.

State and persistence behavior: The file is static. Runtime state lives in programmable core counters and in extra MSR filters while perf owns the event. PEBS load-latency rows only count when PEBS is enabled and are limited to counters `0,1`, while general cache and memory-uop events allow counters `0,1,2,3,4,5,6,7`. Offcore response events are per-core requests filtered through shared offcore MSR state.

Dependencies: Depends on perf's core event parser, extra-MSR support in `jevents.py` through `MSRIndex`/`MSRValue`, Clearwater Forest core PMU support for eight programmable counters, PEBS support for tagged load latency, and offcore response MSRs `0x1a6/0x1a7`. The descriptions mention available PDIST counters, so downstream tools may rely on those constraints when selecting precise distribution counters.

Integration points: Integrates with cache and memory analysis through `perf list`, `perf stat`, and PEBS sampling. The `OCR.*.ANY_RESPONSE` aliases are broad companions to the stricter `clearwaterforest/memory.json` L3-miss OCR aliases. `MEM_UOPS_RETIRED.LOAD_LATENCY_GT_*` events are useful for latency histograms when paired with PEBS and the `counter.json` information about fixed/generic counter counts.

Risks: The threshold events require PEBS and write `MEC_CR_PEBS_LD_LAT_THRESHOLD`; using them without PEBS produces misleading or zero counts. Multiple threshold events programmed together may contend for the same threshold MSR, so perf scheduling must serialize or reject incompatible combinations. Offcore events rely on two MSRs and a large response mask, making encoding mistakes hard to notice from `EventCode`/`UMask` alone. `LONGEST_LAT_CACHE` descriptions define LLC as L3 when present and L2 otherwise, which matters for Clearwater Forest configurations without the expected cache hierarchy.

Test signals: Validate JSON and `jevents.py` generation. `perf list` should show all 17 aliases. On Clearwater Forest hardware, run cache-hit/miss microbenchmarks for `LONGEST_LAT_CACHE`, load/store loops for `MEM_UOPS_RETIRED.ALL_*`, PEBS sampling for several latency thresholds, and offcore-response checks where `OCR.DEMAND_DATA_RD.ANY_RESPONSE` exceeds or equals the L3-miss subset from `memory.json`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/clearwaterforest/cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/clearwaterforest/counter.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/clearwaterforest/counter.json

Purpose: Declares Clearwater Forest core PMU counter capacity metadata for perf. The single JSON object states that the core PMU has `CountersNumFixed: 3` and `CountersNumGeneric: 39` for `Unit: core`.

Important APIs/types/functions: This file uses a metadata-only variant of the perf PMU events JSON schema. It has no `EventName`; instead, `jevents.py` treats the object as PMU unit metadata. `Unit` identifies the affected PMU namespace, while `CountersNumFixed` and `CountersNumGeneric` describe fixed and generic counter counts available for scheduling and display logic.

Control flow: During build generation, the metadata is folded into the Clearwater Forest generated PMU table rather than becoming a user-facing event alias. At runtime, perf can use the generated counter-count metadata alongside normal event aliases from `cache.json`, `pipeline.json`, and other topic files when reasoning about available fixed and generic counters.

State and persistence behavior: The file contains static hardware capability metadata. It creates no counters, events, or persisted runtime measurements. The values persist in the generated perf binary until the PMU event tables are regenerated.

Dependencies: Depends on `jevents.py` accepting JSON records without `EventName` and on perf's generated PMU-events structures preserving counter metadata. It must stay consistent with Clearwater Forest hardware and with fixed-counter event rows in `pipeline.json`, where counters 36, 37, and 38 are used for topdown slots and fixed counters 0 through 2 are used for instructions/core/reference cycles.

Integration points: Integrates with the Clearwater Forest model directory and x86 mapfile row. It is the capacity companion to the event-topic files, especially `pipeline.json` where both fixed counters and high-number topdown counters are named explicitly.

Risks: Incorrect counter counts can cause perf to over-schedule events, reject valid groups, or display misleading hardware capabilities. Because the file has no `EventName`, validation scripts that assume every JSON object is an event can fail or report a false problem. The 39 generic-counter value is unusual enough that regressions should be checked against vendor PMU documentation and kernel PMU exposure.

Test signals: JSON parsing should report one object with no `EventName`. `jevents.py` generation should not emit an alias but should preserve counter metadata. On hardware or a generated-table inspection, perf should recognize 3 fixed counters and 39 generic counters for Clearwater Forest core PMU capacity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/clearwaterforest/counter.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/clearwaterforest/frontend.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/clearwaterforest/frontend.json

Purpose: Defines two Clearwater Forest instruction-cache frontend PMU aliases: `ICACHE.ACCESSES` and `ICACHE.MISSES`. These support perf analysis of instruction stream cache-line entry and instruction-cache miss behavior.

Important APIs/types/functions: Both records use `EventCode: 0x80`, counters `0,1,2,3,4,5,6,7`, and `SampleAfterValue: 1000003`. `ICACHE.ACCESSES` uses `UMask: 0x3`; `ICACHE.MISSES` uses `UMask: 0x2`. There are no metrics, MSR filters, or public descriptions beyond the brief descriptions.

Control flow: `jevents.py` generates two Clearwater Forest frontend aliases from the JSON. At runtime, perf maps the aliases to core PMU event `0x80` with the selected umask, allowing users to count instruction-cache line accesses and missing cache-line entries. The same event code with different masks lets users compute miss ratios if the hardware definitions are compatible.

State and persistence behavior: Static build metadata only. Runtime state is per-core frontend PMU counting while the event is enabled. `SampleAfterValue` sets the default sampling period for record-style use but does not affect stat-mode counts.

Dependencies: Depends on the Clearwater Forest core PMU implementing event `0x80` as described, perf JSON generation, and the x86 model map. It also depends on users understanding that the access definition includes sequential line walks and jump redirections into new cache lines.

Integration points: Integrates with `pipeline.json` frontend-bound topdown events and branch events. I-cache misses can help explain `TOPDOWN_FE_BOUND.ALL` or branch-resteer-heavy workloads, while `ICACHE.ACCESSES` gives the denominator for miss-rate style analysis.

Risks: The miss description ends with a dangling hyphen and lacks a `PublicDescription`, so generated help text is thin. Accesses and misses share one event code; a wrong umask would invert or collapse the ratio. Instruction-cache behavior can be sensitive to SMT, code layout, and predecode/fetch details that are not captured in this metadata.

Test signals: JSON parse, `jevents.py` generation, and `perf list` should show both `icache.accesses` and `icache.misses`. Hardware smoke tests should compare tight loops that fit in the I-cache against large code-footprint or branch-heavy workloads and check that misses rise while accesses remain plausible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/clearwaterforest/frontend.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/clearwaterforest/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/clearwaterforest/memory.json

Purpose: Defines two Clearwater Forest memory-topic offcore response aliases for demand data reads and demand RFOs that miss in L3. These are narrower memory-subsystem companions to the cache-topic `OCR.*.ANY_RESPONSE` aliases.

Important APIs/types/functions: Both records use `EventCode: 0xB7`, `UMask: 0x1`, counters `0,1,2,3,4,5,6,7`, `SampleAfterValue: 100003`, `MSRIndex: 0x1a6,0x1a7`, and offcore `MSRValue` filters. `OCR.DEMAND_DATA_RD.L3_MISS` uses `MSRValue: 0x33FBFC00001`; `OCR.DEMAND_RFO.L3_MISS` uses `MSRValue: 0x33FBFC00002`.

Control flow: At build time, `jevents.py` records these rows as Clearwater Forest aliases with extra MSR programming. At runtime, perf programs the core event selector plus the offcore response MSR mask, so only demand data read or RFO transactions not supplied by L3 are counted. The two events differ only in the low request-type bits of the MSR value.

State and persistence behavior: The JSON is static. Runtime state includes the selected offcore response MSR filter while perf owns the event and the per-core counter values. These are request/response filters, not durable memory state; counts depend on enabled intervals and scheduling.

Dependencies: Depends on perf support for `MSRIndex`/`MSRValue`, Clearwater Forest offcore response MSR semantics, and the core PMU event `0xB7`. It also depends on cache hierarchy semantics where "not supplied by L3" is the desired boundary for memory-level analysis.

Integration points: Integrates with `cache.json` through the matching `OCR.DEMAND_DATA_RD.ANY_RESPONSE` and `OCR.DEMAND_RFO.ANY_RESPONSE` events; the L3-miss variants should be subsets of those broader response counts. They also pair with `pipeline.json` backend-bound events and `virtual-memory.json` page-walk events to distinguish memory misses from translation or execution stalls.

Risks: Offcore response masks are dense and easy to mistype; both rows share the raw event selector and differ mainly by large `MSRValue` constants. Extra MSR filters may conflict if multiple OCR events are scheduled together. The events count demand requests and software prefetches for exclusive ownership for RFO, so they should not be interpreted as pure retired-store misses.

Test signals: JSON generation should preserve both `MSRIndex` and large `MSRValue` constants. `perf list` should show the two L3-miss OCR aliases. Hardware checks should compare streaming read and write/RFO workloads, and verify L3-miss counts are less than or equal to corresponding any-response aliases from `cache.json`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/clearwaterforest/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/clearwaterforest/pipeline.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/clearwaterforest/pipeline.json

Purpose: Defines 15 Clearwater Forest pipeline and topdown PMU aliases for perf. The file covers retired branches, mispredicted retired branches, core and reference cycles, instructions retired, and topdown slot categories for bad speculation, backend bound, frontend bound, and retiring.

Important APIs/types/functions: The schema fields are `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, and `PublicDescription`. Fixed-counter aliases include `INST_RETIRED.ANY` on fixed counter 0, `CPU_CLK_UNHALTED.CORE`/`THREAD` on fixed counter 1, and `CPU_CLK_UNHALTED.REF_TSC` on fixed counter 2. Programmable aliases include `BR_INST_RETIRED.ALL_BRANCHES` (`0xc4`), `BR_MISP_RETIRED.ALL_BRANCHES` (`0xc5`), `CPU_CLK_UNHALTED.*_P` (`0x3c`), `INST_RETIRED.ANY_P` (`0xc0`), and `TOPDOWN_BE_BOUND.ALL(_P)` (`0xa4/0x2`). Topdown fixed slots use counters 36, 37, and 38 for bad speculation, frontend bound, and retiring.

Control flow: `jevents.py` generates the Clearwater Forest pipeline aliases and preserves fixed-counter names as aliases without ordinary event codes where applicable. At runtime, perf resolves the `_P` forms to programmable counters and the non-`_P` fixed forms to fixed or topdown counters. Alias descriptions document equivalences such as `CPU_CLK_UNHALTED.CORE_P` being an alias of `THREAD_P` and `TOPDOWN_BE_BOUND.ALL` being an alias of `ALL_P`.

State and persistence behavior: The file is static metadata. Hardware state is per-core counting of retired branches/instructions, unhalted cycles, and topdown slot categories. Fixed counters have dedicated hardware resources, while programmable versions compete for the general counter pool declared in `counter.json`.

Dependencies: Depends on Clearwater Forest PMU support for fixed counters, topdown counters, and programmable event encodings. The topdown rows must stay consistent with `counter.json` because counters 36 through 38 are outside the classic fixed-counter 0 through 2 range. Perf's generated alias layer must preserve rows without `EventCode` for fixed counters.

Integration points: Integrates with every other Clearwater Forest topic as the high-level performance context. Cache, memory, virtual-memory, and frontend events can explain whether backend, frontend, speculation, or retiring topdown slots dominate. Branch retired and mispredict retired events provide branch-mispredict rates and help interpret bad-speculation slots.

Risks: Alias duplication can confuse users: core/thread cycle aliases and topdown backend-bound aliases map to equivalent hardware events. Fixed topdown counter numbering is unusual and must match kernel PMU exposure. Rows without `EventCode` rely on perf's fixed-counter handling; generic validators may flag them incorrectly. Branch descriptions include a typo in "resteered" but the semantics are clear.

Test signals: JSON parsing and `jevents.py` generation must keep both fixed and programmable aliases. `perf list` should show fixed cycle/instruction/topdown names and programmable `_P` variants. On hardware, sanity checks should confirm IPC from instructions/cycles, branch miss ratio from branch rows, and topdown categories responding to frontend-bound, backend-bound, and branch-mispredict workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/clearwaterforest/pipeline.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/clearwaterforest/virtual-memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/clearwaterforest/virtual-memory.json

Purpose: Defines three Clearwater Forest virtual-memory PMU aliases for completed page walks from load DTLB misses, store DTLB misses, and instruction TLB misses. It is a compact translation-pressure topic compared with the broader Cascade Lake X virtual-memory table.

Important APIs/types/functions: Each record uses counters `0,1,2,3,4,5,6,7`, `SampleAfterValue: 1000003`, and `UMask: 0xe`. `DTLB_LOAD_MISSES.WALK_COMPLETED` uses `EventCode: 0x08`; `DTLB_STORE_MISSES.WALK_COMPLETED` uses `EventCode: 0x49`; `ITLB_MISSES.WALK_COMPLETED` uses `EventCode: 0x85`. Public descriptions state that walks include all page sizes and page walks that fault.

Control flow: The build generator creates three core aliases in the Clearwater Forest table. At runtime, perf maps each alias to the corresponding core PMU event and counts completed page walks caused by data loads, data stores, or instruction fetches after misses in all TLB levels.

State and persistence behavior: Static build metadata only. Runtime counts are per-core and interval-based. The events count completed walks, including faulting walks, and do not distinguish 4K, 2M/4M, or 1G page sizes in this model file.

Dependencies: Depends on perf event generation and Clearwater Forest core PMU support for the standard DTLB/ITLB walk-completed encodings. It also depends on the x86 mapfile selecting the `clearwaterforest` model directory for family/model `GenuineIntel-6-DD`.

Integration points: Integrates with `pipeline.json` backend/frontend topdown events and `cache.json`/`memory.json` memory-latency events. These aliases identify translation overhead at a coarse level; if counts rise with backend bound or frontend bound slots, the workload may benefit from huge pages, locality changes, or reduced code/data footprint.

Risks: The file has only aggregate completed-walk events, so it cannot distinguish page size, STLB hits, walk pending cycles, or EPT overhead. Counts include faulting walks, so page-fault-heavy workloads can inflate translation metrics. Because all three rows share `UMask: 0xe`, a wrong event code is the main way load/store/instruction categories could be swapped.

Test signals: Validate JSON and generated aliases. `perf list` should expose all three walk-completed events. Hardware tests should compare TLB-friendly workloads with random page walks, huge-page versus 4K-page configurations, and instruction-footprint tests that selectively raise `ITLB_MISSES.WALK_COMPLETED`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/clearwaterforest/virtual-memory.json -->
