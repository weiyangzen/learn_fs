# subset-b-006673 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswellx/uncore-io.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswellx/uncore-io.json

## Purpose

`haswellx/uncore-io.json` defines 59 Intel Haswell Xeon R2PCIe uncore PMU event aliases for perf. The file is static source data used by the perf PMU event generator, not executable code. Its entries describe R2PCIe clock, IIO credit, ring utilization, ring bounce, receive/transmit queue, and S-box credit pressure events that allow `perf list` and event lookup to expose hardware encodings for Haswell-EP/Haswell-EX style server I/O uncore monitoring.

## Important APIs, types, and schema

The effective API is the perf PMU JSON schema consumed by `tools/perf/pmu-events/jevents.py`. Each object uses `EventName`, `EventCode`, optional `UMask`, `BriefDescription`, optional `PublicDescription`, `Counter`, `Unit`, and `PerPkg`. All records have `Unit: R2PCIe`, which `jevents.py` maps through `unit_to_pmu()` to the Linux PMU name `uncore_r2pcie`. `PerPkg: 1` marks package-scoped uncore events. `Counter` constrains which unit counters can program each event: 24 records allow `0,1,2,3`, 26 allow only `0,1`, and 9 allow only counter `0`.

The major event families are `UNC_R2_CLOCKTICKS`; IIO credit availability and acquisition events such as `UNC_R2_IIO_CREDIT.*`, `UNC_R2_IIO_CREDITS_ACQUIRED.*`, and `UNC_R2_IIO_CREDITS_USED.*`; ring activity families `UNC_R2_RING_AD_USED.*`, `UNC_R2_RING_AK_USED.*`, `UNC_R2_RING_BL_USED.*`, and `UNC_R2_RING_IV_USED.*`; queue occupancy and insert events for RxR and TxR; `UNC_R2_TxR_NACK_CW.*`; and S-box credit families `UNC_R2_SBO0_CREDITS_ACQUIRED.*`, `UNC_R2_SBO0_CREDIT_OCCUPANCY.*`, and `UNC_R2_STALL_NO_SBO_CREDIT.*`.

## Control flow and integration

There is no runtime control flow inside the JSON. Build and lookup flow is: `arch/x86/mapfile.csv` maps CPUID pattern `GenuineIntel-6-3F` to the `haswellx` model directory; the perf build invokes `jevents.py`; `JsonEvent` lowercases `EventName`, converts `Unit` into a PMU selector, combines `EventCode` and `UMask` into an event string, and emits generated PMU tables in `pmu-events.c`; perf runtime code uses those tables for `perf list`, alias lookup, and event programming. The R2PCIe `Unit` is the key integration point because a wrong or missing unit would route these aliases to the wrong PMU.

## State and persistence behavior

The file has no mutable process state. The persistent state is the source-controlled mapping from public alias names to event select values, unit masks, counter constraints, and package scope. Renaming an alias changes the user-visible perf interface. Changing `EventCode`, `UMask`, `Counter`, or `Unit` changes the hardware register programming or scheduling constraints.

## Dependencies

The file depends on Intel Haswell uncore R2PCIe event definitions, the perf PMU JSON schema, the x86 model map, `jevents.py` unit conversion, and kernel exposure of matching `uncore_r2pcie` PMU devices. Its descriptions also depend on Intel terminology for IIO, QPI, BL/AD/AK/IV rings, S-box credits, and message classes such as DRS, NCB, and NCS.

## Risks

The main risk is silent mismeasurement: event aliases will still parse if a mask or code is wrong, but perf would program the wrong counter. Counter restrictions are also important because some R2PCIe events are limited to two counters or a single counter; relaxing them can make perf accept impossible schedules. Some `PublicDescription` text combines generic family descriptions with suffix-specific notes, so bulk editing can accidentally attach the wrong message class or polarity. Because all records are `PerPkg`, using these aliases as if they were per-core events can mislead higher-level analysis.

## Test signals

Useful checks are `python3 -m json.tool` or `jq empty` for syntax, perf's PMU event generation tests, `perf list` on Haswell Xeon hardware showing `uncore_r2pcie` aliases, and controlled workloads that exercise PCIe/IIO traffic while comparing ring used, credit used, and credit acquired relationships. Hardware validation should confirm package-level aggregation and counter scheduling limits for events restricted to `0,1` or `0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswellx/uncore-io.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswellx/uncore-memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswellx/uncore-memory.json

## Purpose

`haswellx/uncore-memory.json` defines 325 Intel Haswell Xeon integrated memory controller (`iMC`) uncore PMU event aliases for perf. It covers DRAM command counts, major controller modes, priority and preemption behavior, power and CKE state cycles, rank-level CAS events, write/read mode transitions, refresh and ECC events, and two scaled aliases for memory read/write volume. It is the largest file in this work item and provides the primary HaswellX memory-channel event catalog.

## Important APIs, types, and schema

Entries use the perf JSON event schema with `EventName`, `EventCode` on most records, optional `UMask`, `BriefDescription`, optional `PublicDescription`, `Counter`, `PerPkg`, `Unit`, and occasional `ScaleUnit`. All records use `Unit: iMC`; `jevents.py` maps that by default to `uncore_imc`. All records are package scoped and allow counters `0,1,2,3`.

Important families include `LLC_MISSES.MEM_READ` and `LLC_MISSES.MEM_WRITE`, which are derived from `UNC_M_CAS_COUNT` masks and carry `ScaleUnit: 64Bytes`; `UNC_M_ACT_COUNT.*`, `UNC_M_PRE_COUNT.*`, `UNC_M_CAS_COUNT.*`, and `UNC_M_DRAM_REFRESH.*` for DRAM command accounting; `UNC_M_MAJOR_MODES.*`, `UNC_M_PREEMPTION.*`, `UNC_M_WMM_TO_RMM.*`, and `UNC_M_RD_CAS_PRIO.*` for controller scheduling modes; `UNC_M_POWER_CKE_CYCLES.*`, `UNC_M_POWER_THROTTLE_CYCLES.*`, and `UNC_M_POWER_CHANNEL_DLLOFF` for channel power behavior; `UNC_M_ECC_CORRECTABLE_ERRORS`; and large rank matrices such as `UNC_M_RD_CAS_RANK{0,1,4,5,6,7}.*` and `UNC_M_WR_CAS_RANK{0,1,4,5,6,7}.*`.

## Control flow and integration

The file is parsed during perf's PMU table generation after `arch/x86/mapfile.csv` selects the `haswellx` model for CPUID `GenuineIntel-6-3F`. `jevents.py` turns each JSON object into a generated table entry, preserving the alias name, event code, umask, description, scale unit, unit/PMU routing, and package flag. Runtime perf lookup then exposes these aliases under the generated HaswellX event table and routes them to the memory-controller PMU rather than the core PMU.

There is no internal control flow, but there are structural patterns that matter. The rank-level families repeat the same mask vocabulary across rank-specific event codes from `0xB0` through `0xBF`; the aggregate `UNC_M_CAS_COUNT` aliases use a shared event code `0x4` with different masks; and the memory bandwidth aliases depend on the same read/write CAS encodings plus `ScaleUnit`.

## State and persistence behavior

The file is immutable source data. Its durable contract is the hardware encoding of every memory-controller alias. The `ScaleUnit: 64Bytes` fields persist semantic unit conversion for bandwidth-like aliases; removing them would not necessarily break event parsing, but it would change how perf describes and scales those events. The rank naming and masks are also persistent external identifiers used in scripts and dashboards that call `perf stat -e`.

## Dependencies

Dependencies include Intel HaswellX iMC uncore event definitions, perf's JSON schema, `jevents.py`, the x86 mapfile, generated `pmu-events.c`, and availability of `uncore_imc` PMUs in the running kernel. The file also depends on architectural assumptions about channel/rank topology, read-major/write-major modes, underfills, page policy, CKE states, and DRAM command granularity.

## Risks

The repeated rank matrices are error-prone: a copied mask or event code for the wrong rank would silently attribute traffic to the wrong rank. `LLC_MISSES.MEM_READ` and `.MEM_WRITE` are named like cache events but are derived from iMC CAS counts; consumers may overinterpret them as LLC-only misses instead of memory-controller read/write commands. Some records intentionally lack `EventCode` or `UMask` for clock tick style events, so validators must distinguish missing optional fields from accidental omissions. Package scope and channel PMU routing are critical for interpreting counts on multi-socket systems.

## Test signals

Syntax validation with `python3 -m json.tool` is the first gate. Build-time test signals are successful `jevents.py` generation and perf PMU event tests. Runtime checks include `perf list` exposing `uncore_imc` HaswellX aliases, `perf stat` on memory bandwidth workloads showing read/write CAS changes, ECC counters remaining zero on healthy systems, and consistency checks where `UNC_M_CAS_COUNT.RD` roughly aligns with rank read CAS sums for populated ranks and known channel topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswellx/uncore-memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswellx/uncore-power.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswellx/uncore-power.json

## Purpose

`haswellx/uncore-power.json` defines 62 HaswellX PCU uncore PMU aliases for package and core power-management observation. It exposes PCU clock ticks, per-core C-state transition and demotion counts, package C-state residencies, core C-state occupancy filters, PROCHOT thermal throttle cycles, ring frequency transition events, and VR hot cycles. The events are used by perf to report server package power-state behavior via the PCU PMU.

## Important APIs, types, and schema

The file uses JSON event objects with `EventName`, optional `EventCode`, `BriefDescription`, `PublicDescription`, `Counter`, `PerPkg`, and `Unit`. Three occupancy aliases also use `Filter` values such as `occ_sel=1`, `occ_sel=2`, and `occ_sel=3`. All entries use `Unit: PCU`, which maps to `uncore_pcu`, and all allow counters `0,1,2,3`.

Event families include `UNC_P_CLOCKTICKS`; per-core transition events `UNC_P_CORE0_TRANSITION_CYCLES` through `UNC_P_CORE17_TRANSITION_CYCLES`; per-core demotion events `UNC_P_DEMOTIONS_CORE0` through `UNC_P_DEMOTIONS_CORE17`; package residency aliases `UNC_P_PKG_RESIDENCY_C0_CYCLES`, `C1E`, `C2E`, `C3`, `C6`, and `C7`; occupancy aliases `UNC_P_POWER_STATE_OCCUPANCY.CORES_C0`, `.CORES_C3`, and `.CORES_C6`; `UNC_P_PROCHOT_EXTERNAL_CYCLES` and `UNC_P_PROCHOT_INTERNAL_CYCLES`; `UNC_P_TOTAL_TRANSITION_CYCLES`; `UNC_P_UFS_TRANSITIONS_NO_CHANGE` and `UNC_P_UFS_TRANSITIONS_RING_GV`; and `UNC_P_VR_HOT_CYCLES`.

## Control flow and integration

There is no executable flow in the JSON. Perf build flow selects the `haswellx` directory via the x86 mapfile, parses the file with `jevents.py`, converts `Unit: PCU` to `uncore_pcu`, preserves `Filter` strings, and emits generated PMU event table rows. At runtime, perf uses those rows to program PCU counters and, for occupancy events, include the filter terms needed by the uncore PMU driver.

## State and persistence behavior

The persistent state is the alias-to-PCU-encoding mapping. The per-core entries encode a fixed 18-core naming range and event-code sequence, so edits must preserve the association between core number and code. Residency events count cycles in package states and explicitly exclude transition time; transition events count cycles spent entering or leaving C-states. This distinction is a semantic contract for downstream power analysis.

## Dependencies

Dependencies are Intel HaswellX PCU PMU definitions, perf's JSON schema, the uncore PCU kernel PMU, `jevents.py` field handling for `Filter`, and the model mapping for HaswellX. The descriptions depend on Intel C-state, PROCHOT, UFS/ring global voltage/frequency, and SVID VR terminology.

## Risks

The per-core event list is vulnerable to off-by-one or lexicographic-order mistakes because event names are not numerically sorted in every sequence. Occupancy events share event code `0x80` and differ by `Filter`; dropping or changing a filter would make multiple aliases count the same condition. C-state residency and transition-cycle events sound similar but measure different phases, so documentation drift can lead to wrong power conclusions. These are package-level uncore events, not task-attributable per-thread counters.

## Test signals

Validation includes JSON syntax checks, successful `jevents.py` generation, and `perf list` visibility under `uncore_pcu`. Runtime signals include nonzero PCU clock ticks at the fixed PCU clock rate, residency changes under idle versus load, PROCHOT counters staying zero unless thermal throttling is induced or observed, and occupancy filters producing different distributions for C0/C3/C6 states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswellx/uncore-power.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswellx/virtual-memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswellx/virtual-memory.json

## Purpose

`haswellx/virtual-memory.json` defines 49 HaswellX core PMU aliases for TLB misses, page walks, page-walker load sources, EPT walk cycles, ITLB flushes, and TLB flush classes. Unlike the uncore files in this work item, these entries omit `Unit` and therefore target the default core PMU. They let perf expose virtual-memory translation behavior for demand loads, stores, instruction fetches, and page-walk memory hierarchy outcomes.

## Important APIs, types, and schema

Entries use `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, and usually `PublicDescription`. Four records carry `Errata` notes. `Unit` is absent, so `jevents.py` maps these records to `default_core`. Every event allows counters `0,1,2,3`, and every record has a sampling period hint through `SampleAfterValue`.

Important families are `DTLB_LOAD_MISSES.*` and `DTLB_STORE_MISSES.*` for first-level and second-level DTLB outcomes, STLB hits, completed page walks by page size, and walk duration; `ITLB_MISSES.*` for instruction TLB miss and walk outcomes; `PAGE_WALKER_LOADS.*` for DTLB and ITLB page-walk accesses that hit L1, L2, L3, or memory; `EPT.WALK_CYCLES` for extended page-table walk cycle cost; `ITLB.ITLB_FLUSH`; and `TLB_FLUSH.DTLB_THREAD` plus `TLB_FLUSH.STLB_ANY`.

## Control flow and integration

The JSON is parsed into generated perf event tables for the HaswellX CPU model. `jevents.py` lowercases `EventName`, treats the missing `Unit` as `default_core`, preserves `SampleAfterValue`, and appends errata text to event descriptions when `Errata` exists. At runtime, perf core PMU alias lookup uses the generated rows to program the event select and umask on general-purpose core counters.

## State and persistence behavior

This file has no mutable state. Its persistent behavior is the mapping from TLB/page-walk alias names to core PMU encodings and default sample periods. `SampleAfterValue` is part of the profiling contract: changing it affects sampling frequency and overhead even when the raw event encoding is unchanged. Errata annotations are also persistent user-facing risk metadata.

## Dependencies

Dependencies include Intel HaswellX core PMU documentation, perf's PMU JSON schema, generated `pmu-events.c`, core PMU counter availability, and `jevents.py` support for `Errata` and `SampleAfterValue`. The file depends semantically on x86 paging concepts, STLB behavior, page sizes, page-miss handler cycles, EPT virtualization walks, and TLB shootdown/flush behavior.

## Risks

TLB events are easy to misaggregate because masks such as `WALK_COMPLETED` combine page sizes while sibling aliases isolate 4K, 2M/4M, and 1G walks. `PAGE_WALKER_LOADS` errata on L3 and memory outcomes must be preserved so users understand specification caveats. `EPT.WALK_CYCLES` is virtualization-specific and can be misread on non-virtualized workloads. High-frequency sampling of page-walk duration or STLB events can perturb workloads if `SampleAfterValue` is reduced too far.

## Test signals

Useful tests are JSON syntax validation, perf event table generation, `perf list` showing HaswellX virtual-memory aliases, and runtime `perf stat` checks on workloads with controlled TLB pressure. Huge-page versus 4K-page tests should shift the page-size-specific walk aliases. Virtualized workloads should exercise EPT walk cycles, while TLB shootdown tests can validate the flush aliases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswellx/virtual-memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelake/cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelake/cache.json

## Purpose

`icelake/cache.json` defines 109 Intel Ice Lake client core PMU aliases for cache, memory-retirement, offcore-response, prefetch, fill-buffer, store-queue, L2, L3, and load-latency behavior. It is a core event file, not an uncore catalog. It includes both simple event select/umask aliases and offcore-response (`OCR.*`) aliases that require model-specific MSR programming.

## Important APIs, types, and schema

The file uses perf JSON event fields such as `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, and optional `PublicDescription`. Specialized fields are important here: 45 `OCR.*` records use `MSRIndex` and `MSRValue`; 20 records use `Data_LA` to indicate data linear-address support when precise; 5 records use `CounterMask`; one uses `EdgeDetect`; and two `L2_RQSTS` aggregate aliases are marked `Deprecated`.

Major families include `L1D.REPLACEMENT`; `L1D_PEND_MISS.*` for pending misses, fill-buffer full periods, and L2 stalls; `L2_LINES_IN`, `L2_LINES_OUT.*`, `L2_TRANS.L2_WB`, and 15 `L2_RQSTS.*` aliases for code, demand data, RFO, software prefetch, hit, miss, and deprecated aggregate classes; `LONGEST_LAT_CACHE.MISS`; `MEM_INST_RETIRED.*`, `MEM_LOAD_RETIRED.*`, `MEM_LOAD_L3_HIT_RETIRED.*`, and `MEM_LOAD_MISC_RETIRED.UC`; `OFFCORE_REQUESTS.*` and `OFFCORE_REQUESTS_OUTSTANDING.*`; 45 `OCR` offcore-response aliases for demand code, demand data, demand RFO, and hardware prefetch response classes; `SQ_MISC.*`; and `SW_PREFETCH_ACCESS.*`.

## Control flow and integration

There is no runtime control flow in the source file. Build flow maps CPUID patterns `GenuineIntel-6-7[DE]` to `icelake`, then `jevents.py` parses each object. Missing `Unit` means `default_core`; `MSRIndex` is resolved by `lookup_msr()` and `MSRValue` is carried into the generated event string for offcore filters; `CounterMask` and `EdgeDetect` become event modifiers; `Data_LA` and `Errata` style fields augment descriptions; and `Deprecated` is preserved for user-facing deprecation metadata. Runtime perf lookup programs regular core counters and, for OCR aliases, the paired offcore response MSRs such as `0x1a6,0x1a7`.

## State and persistence behavior

The persistent state is the public Ice Lake alias catalog and the offcore filter encodings. `OCR` rows are especially stateful at the hardware level because their alias requires both a core event code pair (`0xB7, 0xBB`) and an MSR filter value. The source file itself remains immutable, but its values drive generated tables that persist in the built perf binary.

## Dependencies

Dependencies include Intel Ice Lake client PMU documentation, perf's JSON schema, `jevents.py` MSR and event encoding support, core PMU counter availability, and Ice Lake mapfile selection. The `Data_LA` records depend on precise-event/address sampling support. Offcore entries depend on kernel and perf support for programming offcore response MSRs without conflicting with other events.

## Risks

Offcore-response aliases are the highest-risk area: an incorrect `MSRValue` can produce plausible but wrong response-class counts. `EventCode` values containing comma-separated alternatives must be parsed correctly by generator code and programmed on a compatible counter path. Deprecated `L2_RQSTS.MISS` and `.REFERENCES` should remain available but should not be treated as preferred metric inputs. `CounterMask` and `EdgeDetect` change event meaning from count-like to cycle/period-like, so dropping those fields silently changes semantics. Address-capable `Data_LA` events need precise sampling context to be useful.

## Test signals

Build checks include JSON syntax and generated PMU table tests. Runtime checks include `perf list` on Ice Lake, `perf stat` with L1/L2 cache stressors, offcore tests that compare broad `OCR.*.ANY_RESPONSE` counts against narrower L3 hit and snoop classes, and sampling tests for `MEM_INST_RETIRED.*` or `MEM_LOAD_*` events that verify address capture when precise sampling is requested. Deprecation metadata should be visible for deprecated aliases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelake/cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelake/counter.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelake/counter.json

## Purpose

`icelake/counter.json` defines PMU counter inventory metadata for the Ice Lake model. Unlike event files, it contains no `EventName` records. Instead it declares the number of fixed and generic counters available for three PMU units: `core`, `ARB`, and `CLOCK`. This metadata helps perf describe or constrain the hardware counter resources for the model.

## Important APIs, types, and schema

The schema is a short JSON array of objects with `Unit`, `CountersNumFixed`, and `CountersNumGeneric`. The records are `core` with 4 fixed and 8 generic counters, `ARB` with 0 fixed and 2 generic counters, and `CLOCK` with 1 fixed and 0 generic counters. Most numeric values are strings, while `CLOCK.CountersNumFixed` is the JSON number `1`; consumers therefore need to tolerate both string and numeric representations, as neighboring x86 model counter files do.

## Control flow and integration

The file has no executable control flow and is not parsed as ordinary event aliases because it lacks `EventName`. It lives in the same model directory selected by `arch/x86/mapfile.csv` for Ice Lake, so any counter metadata consumer in the perf PMU event tooling can associate these limits with the generated Ice Lake PMU tables. It complements event files such as `cache.json` and `floating-point.json` by documenting how many counters can schedule the aliases.

## State and persistence behavior

The persistent behavior is the Ice Lake counter inventory. Changing these counts changes perf's understanding of available model resources and can affect validation, display, or scheduling assumptions. There is no runtime mutable state or generated alias state inside this file.

## Dependencies

Dependencies include Intel Ice Lake PMU counter topology and any perf tooling that reads `counter.json` files alongside model event catalogs. It also depends on the x86 model directory contract and the repository-wide convention for `CountersNumFixed` and `CountersNumGeneric` fields.

## Risks

The largest risk is resource misdescription. Overstating generic counters could make validation or documentation imply that event groups can be scheduled when hardware cannot support them; understating counts hides legitimate concurrency. Mixed numeric/string value types are a compatibility risk for strict parsers. The `ARB` and `CLOCK` units should not be confused with standard core event aliases, since they are resource declarations rather than programmable event records.

## Test signals

Validation should include JSON syntax, schema checks that accept both numeric and string count values, and comparison against adjacent Ice Lake-family counter files such as `rocketlake/counter.json` or `icelakex/counter.json` where appropriate. Runtime-facing confidence comes from perf scheduling behavior and `perf list` or debug output matching the expected 8 generic core counters and 4 fixed counters on Ice Lake client hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelake/counter.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelake/floating-point.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelake/floating-point.json

## Purpose

`icelake/floating-point.json` defines 13 Intel Ice Lake core PMU aliases for floating-point assists and retired floating-point arithmetic instruction classes. The catalog exposes scalar, packed, vector-width, element-count, and aggregate FLOP-oriented encodings for SSE, AVX, and AVX-512 style computational floating-point instructions.

## Important APIs, types, and schema

Entries use `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `BriefDescription`, and usually `PublicDescription`. No `Unit` appears, so `jevents.py` routes all aliases to `default_core`. Every event can use counters `0,1,2,3,4,5,6,7`.

The file has one assist event, `ASSISTS.FP` with event code `0xc1` and mask `0x2`. The remaining 12 aliases use event code `0xc7` under `FP_ARITH_INST_RETIRED.*`. They distinguish scalar single/double and combined scalar events, 128-bit packed single/double, 256-bit packed single/double, 512-bit packed single/double, aggregate `4_FLOPS` and `8_FLOPS` masks, and `VECTOR` with mask `0xfc`. The descriptions repeatedly note that some instructions count twice and that DAZ and FTZ MXCSR flags need to be set when using these events.

## Control flow and integration

Build-time flow maps Ice Lake CPUIDs to the `icelake` model directory, then `jevents.py` parses the JSON records into generated PMU table entries. Runtime perf alias lookup programs the core PMU event select and umask. Because the aliases are retired-instruction events rather than derived metrics, formulas for FLOP rates or operation counts must be provided by users or metric files elsewhere; this file supplies the raw event building blocks.

## State and persistence behavior

The persistent contract is the set of floating-point alias names, event code `0xc7` masks, and sampling periods. Changing aggregate masks such as `4_FLOPS`, `8_FLOPS`, or `VECTOR` would alter derived FLOP accounting without a parser failure. `SampleAfterValue` controls default sampling behavior and overhead. The file has no mutable runtime state.

## Dependencies

Dependencies include Intel Ice Lake core PMU definitions, perf's JSON event schema, the x86 Ice Lake model map, and hardware support for the listed FP arithmetic retired events. The semantic accuracy depends on instruction-set details for SSE, AVX, AVX-512, FMA, DPP, DAZ, FTZ, and microcode floating-point assists.

## Risks

The main risk is incorrect interpretation rather than parsing failure. Counts are instruction-class events, and the descriptions state that each count can represent different numbers of operations depending on vector width and precision. Some instructions count twice, so naive FLOP formulas can overcount or undercount. DAZ/FTZ requirements are easy to miss and can affect reproducibility. Aggregate masks overlap with more specific masks, so users should avoid summing aliases without understanding mask inclusion.

## Test signals

Useful checks are JSON syntax, generated perf table tests, `perf list` on Ice Lake, and microbenchmarks with known scalar, 128-bit, 256-bit, and 512-bit floating-point instruction mixes. Tests should compare specific aliases against aggregate `VECTOR`, `4_FLOPS`, and `8_FLOPS` behavior, and should run with controlled MXCSR DAZ/FTZ settings. Floating-point assist tests can use workloads that trigger denormal or exceptional FP paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelake/floating-point.json -->
