# subset-b-006667 Research

Grouped source research for x86 perf PMU event JSON files under Granite Rapids and Haswell. Each source file has a marker-delimited section so reconciliation can split or verify the report into source-tree-aligned per-file documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/graniterapids/uncore-interconnect.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/graniterapids/uncore-interconnect.json

## Purpose
This JSON file defines 203 Intel Granite Rapids uncore interconnect PMU events for perf's `pmu-events` database. It covers mesh/interconnect and socket fabric units including B2CMI, B2HOT, B2UPI, IRP/`UNC_I`, MDF, UBOX, and UPI. The data is declarative input to perf's event-table generation path, not executable code. The source was read as a complete 1,979-line JSON array.

## Important APIs, Types, and Functions
The schema is the perf x86 PMU event JSON schema. Every row has `EventName`, `EventCode`, `BriefDescription`, `Counter`, `PerPkg`, and `Unit`; 192 rows also carry `UMask`, 11 rows include `PublicDescription`, and many rows mark `Experimental: "1"`. There are 203 unique event names and 35 unique event codes, with encodings differentiated primarily by unit masks and uncore units. Unit coverage is `B2CMI` 79 events, `UPI` 67, `MDF` 37, `IRP` 13, `UBOX` 5, and one clock event each for `B2HOT` and `B2UPI`.

Important event families include `UNC_B2CMI_DIRECTORY_*`, `UNC_B2CMI_IMC_READS/WRITES`, `UNC_B2CMI_TAG_*`, `UNC_I_*`, `UNC_MDF_RxR/TxR_*`, `UNC_UPI_RxL/TxL_*`, and `UNC_U_EVENT_MSG.*`. The `Counter` field limits events to uncore programmable counters, usually `0,1,2,3` or `0,1`; `PerPkg: "1"` tells perf these events are package scoped. There are no local functions, classes, or runtime APIs in the file; the effective API is the event-name and encoding contract consumed by perf.

## Control Flow, State, and Persistence
There is no in-file control flow. Build-time control flow comes from `tools/perf/pmu-events/jevents.py`, which walks model directories, parses each JSON object, validates and normalizes fields, and emits generated C event tables. At runtime, perf resolves aliases such as `UNC_UPI_RxL_FLITS.DATA` into raw uncore PMU selectors and passes the event attributes to the kernel perf PMU driver.

The only state in this file is static event metadata: event code, unit mask, counter constraints, package scope, unit selection, and descriptions. Persistence happens through generated `pmu-events.c` tables built into perf; runtime counter values are transient perf session data. Because these are uncore events, runtime state is package- or unit-wide rather than per-thread, so consumers must interpret counts against the topology and active socket/unit selection.

## Dependencies and Integration Points
The file depends on the perf PMU event JSON schema, Granite Rapids CPU model mapping, Intel uncore PMU event semantics, `jevents.py`, and kernel uncore PMU drivers exposing matching units. It integrates with `perf list` for discoverability and `perf stat -e` for measurement. The unit names are critical integration points because perf maps JSON `Unit` values to PMU names; a mismatch would make an otherwise valid event unreachable or misleading.

This file also integrates with other Granite Rapids event tables in the same model directory. Memory and I/O events can be correlated with B2CMI/UPI traffic, while power events can contextualize throttling or low-power link behavior. There are no metric expressions in this file, so derived ratios are expected to be defined elsewhere or by users.

## Risks and Test Signals
Risks include event encoding drift against Intel documentation, broad `Experimental` coverage, uncore unit-name mismatches, and incorrect interpretation of package-scoped counts as core-local values. Duplicate event codes are intentional but make `UMask` correctness essential. Some events represent occupancy or cycles rather than simple transaction counts, so downstream metrics must avoid mixing incompatible semantics.

Test signals include JSON syntax validation with `jq`, successful `jevents.py` generation, generated-table diffs, `perf list` visibility for representative `UNC_B2CMI`, `UNC_MDF`, `UNC_UPI`, and `UNC_U` names, and smoke tests on Granite Rapids hardware using package-scoped `perf stat` runs. Counter scheduling tests should verify `Counter` constraints and that multiple events from the same uncore unit can be grouped only when hardware counter availability permits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/graniterapids/uncore-interconnect.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/graniterapids/uncore-io.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/graniterapids/uncore-io.json

## Purpose
This JSON file defines 168 Intel Granite Rapids integrated I/O uncore PMU events for perf. The events cover IIO completion-buffer activity, CPU-to-I/O and I/O-to-CPU data and transaction requests, IOMMU lookup/cache behavior, outstanding request occupancy, request target breakdowns, and posted write table occupancy. The source was read as a complete 1,925-line JSON array.

## Important APIs, Types, and Functions
The file uses perf's x86 PMU event schema. All 168 rows have `EventName`, `EventCode`, `BriefDescription`, `Counter`, `PerPkg`, `PortMask`, and `Unit`; most rows also have `UMask`, and selected rows have `FCMask`, `Experimental`, or `Deprecated`. `Unit` is always `IIO`, so the differentiation comes from event code, unit mask, port mask, filter mask, and event name. There are 168 unique event names and 14 unique event codes.

Important event families include `UNC_IIO_COMP_BUF_INSERTS/OCCUPANCY.CMPD.*`, `UNC_IIO_DATA_REQ_BY_CPU.*`, `UNC_IIO_DATA_REQ_OF_CPU.*`, `UNC_IIO_TXN_REQ_BY_CPU.*`, `UNC_IIO_TXN_REQ_OF_CPU.*`, `UNC_IIO_IOMMU0/1/3.*`, `UNC_IIO_NUM_OUTSTANDING_REQ_*`, `UNC_IIO_NUM_REQ_OF_CPU_BY_TGT.*`, and `UNC_IIO_PWT_OCCUPANCY`. Part-specific names such as `PART0` through `PART7` use `PortMask` to select IIO partitions, while `ALL_PARTS` names aggregate with wider masks. The file marks `UNC_IIO_NUM_OUSTANDING_REQ_FROM_CPU.TO_IO` deprecated, preserving the misspelled alias next to the corrected `UNC_IIO_NUM_OUTSTANDING_REQ_FROM_CPU.TO_IO`.

## Control Flow, State, and Persistence
There is no executable control flow. `jevents.py` parses the array during perf build generation, serializes it into generated event tables, and runtime perf lookup maps event aliases to raw IIO PMU selectors. The row order is useful for maintainers, but runtime lookup is by generated event name and PMU metadata.

Static state is encoded in the JSON fields. `PerPkg: "1"` makes these package-level uncore events, while `PortMask` and `FCMask` are hardware filter controls that change what traffic is counted. Occupancy events and outstanding-request events count cycles or queue depth proxies, not necessarily completed transactions, so state interpretation depends on event family. Persistence is limited to generated perf tables; measurements themselves are session-local.

## Dependencies and Integration Points
The file depends on the perf PMU JSON schema, Granite Rapids IIO PMU support in the kernel, and Intel's IIO event definitions. It integrates with `perf list` and `perf stat -e` for uncore IIO PMUs, and it complements memory/interconnect event files for system-level traffic diagnosis. IOMMU events are integration points for virtualization, DMA, and device assignment analysis because they expose IOTLB, context-cache, PASID-cache, and second-level paging cache behavior from the IIO block.

The deprecated misspelled outstanding-request event is a compatibility integration point. Removing it could break existing scripts, while keeping it requires downstream tooling to handle aliases carefully.

## Risks and Test Signals
Risks include incorrect `PortMask` or `FCMask` filters, confusion between per-part and all-part aliases, the deprecated misspelled event being selected accidentally, and broad experimental coverage across completion-buffer, IOMMU, and request events. Because all rows share `Unit: "IIO"`, a unit naming mismatch would invalidate the whole table at runtime. Another risk is semantic overloading: similarly named `DATA_REQ` and `TXN_REQ` families may not count the same hardware boundary.

Test signals include `jq` validation, `jevents.py` generation, `perf list` checks for both deprecated and corrected outstanding-request names, and Granite Rapids hardware smoke tests for representative IIO transaction, IOMMU, and occupancy events. Tests should also verify that per-part `PortMask` events produce plausible differences across active IIO partitions and that `ALL_PARTS` events are schedulable with available IIO counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/graniterapids/uncore-io.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/graniterapids/uncore-memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/graniterapids/uncore-memory.json

## Purpose
This JSON file defines 94 Intel Granite Rapids integrated memory controller uncore PMU events for perf. It covers DRAM activation, CAS read/write counts for scheduler channels, refresh and self-refresh behavior, power-down and throttling cycles, read/write queue inserts and occupancy, and memory-controller clock events. The source was read as a complete 890-line JSON array.

## Important APIs, Types, and Functions
All entries use perf's x86 event JSON schema with `EventName`, `EventCode`, `BriefDescription`, `Counter`, `PerPkg`, `UMask`, and `Unit`. `Unit` is always `IMC`, `Counter` is consistently `0,1,2,3`, and `PerPkg` is consistently `1`. Two entries include `PublicDescription`, and many are flagged `Experimental: "1"`. The file has 94 unique event names and 30 unique event codes.

Important event families include `UNC_M_ACT_COUNT.*`, `UNC_M_CAS_COUNT_SCH0.*`, `UNC_M_CAS_COUNT_SCH1.*`, `UNC_M_CLOCKTICKS`, `UNC_M_HCLOCKTICKS`, `UNC_M_MNTCMD_REFRATE.*`, `UNC_M_MR4_2XREF_CYCLES.*`, `UNC_M_PDC_MR4ACTIVE_CYCLES.*`, `UNC_M_POWERDOWN_CYCLES.*`, `UNC_M_POWER_*`, `UNC_M_PRE_COUNT.*`, `UNC_M_RDB_*`, `UNC_M_RPQ_*`, `UNC_M_WPQ_*`, `UNC_M_SELF_REFRESH.*`, and `UNC_M_THROTTLE_*`. The naming encodes scheduler, pseudo-channel, DIMM, rank, and slot dimensions directly in the event name.

## Control Flow, State, and Persistence
The file has no direct control flow. During the perf build, `jevents.py` reads the JSON array and emits generated C event metadata. Runtime perf commands resolve aliases into IMC uncore PMU event selectors and collect package-scoped hardware counts.

The declarative state is the mapping from event aliases to raw event code/unit mask pairs plus counter and scope constraints. Many event names expose hardware substructure such as `SCH0`, `SCH1`, `PCH0`, `PCH1`, DIMM indices, ranks, and throttle slots. These dimensions are persistent metadata in the generated perf tables; observed counts are transient. Since these are memory-controller events, state is not tied to a task context and should be interpreted with system-wide collection semantics.

## Dependencies and Integration Points
Dependencies include the perf PMU JSON schema, Granite Rapids model selection, Intel IMC event definitions, `jevents.py`, and kernel uncore IMC PMU support. The file integrates with `perf list` for IMC event discovery and `perf stat` for socket/package-level memory-controller analysis. It is a natural integration partner for uncore interconnect events, IIO traffic events, and power events when diagnosing bandwidth, throttling, refresh overhead, or memory power-management behavior.

There are no metric expressions here. Any bandwidth or utilization metric must be built externally from CAS counts, queue occupancy, clockticks, and platform-specific scaling factors such as channel width and memory transfer rate.

## Risks and Test Signals
Risks include experimental event semantics, channel/pseudo-channel naming drift, incorrect unit masks for aggregate versus channel-specific counts, and mixing occupancy/cycle events with transaction counts. Power and throttle events can be highly platform-policy dependent, so they may be valid but zero or hard to interpret on systems without the relevant throttling or memory power states.

Test signals include JSON validation, successful event-table generation, `perf list` visibility for `UNC_M_CAS_COUNT_SCH*`, `UNC_M_RPQ_*`, `UNC_M_WPQ_*`, and throttle events, and hardware smoke tests under memory read/write stress. Plausibility checks should compare read-heavy workloads against `RD` events, write-heavy workloads against `WR` events, and idle or low-power scenarios against self-refresh and power-down residency events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/graniterapids/uncore-memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/graniterapids/uncore-power.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/graniterapids/uncore-power.json

## Purpose
This JSON file defines 11 Intel Granite Rapids PCU uncore PMU events for package power, frequency-limit, package C-state, core power-state occupancy, and PROCHOT analysis in perf. It is static event metadata for the package control unit rather than executable code. The source was read as a complete 109-line JSON array.

## Important APIs, Types, and Functions
All rows have `EventName`, `EventCode`, `BriefDescription`, `PublicDescription`, `Counter`, `PerPkg`, and `Unit`. `Unit` is always `PCU`, `Counter` is `0,1,2,3`, and `PerPkg` is `1`. Each event has a unique event code. The event names are `UNC_P_CLOCKTICKS`, `UNC_P_FREQ_MAX_LIMIT_THERMAL_CYCLES`, `UNC_P_FREQ_MAX_POWER_CYCLES`, `UNC_P_FREQ_TRANS_CYCLES`, `UNC_P_PKG_RESIDENCY_C2E_CYCLES`, `UNC_P_PKG_RESIDENCY_C6_CYCLES`, `UNC_P_POWER_STATE_OCCUPANCY_CORES_C0`, `UNC_P_POWER_STATE_OCCUPANCY_CORES_C3`, `UNC_P_POWER_STATE_OCCUPANCY_CORES_C6`, `UNC_P_PROCHOT_EXTERNAL_CYCLES`, and `UNC_P_PROCHOT_INTERNAL_CYCLES`.

Eight non-clock events are marked `Experimental: "1"`, including thermal/power limit cycles, frequency transition cycles, package C-state residency cycles, C3 core occupancy, and internal/external PROCHOT cycles. There are no unit masks, metric expressions, or MSR filter fields in this file.

## Control Flow, State, and Persistence
There is no in-file control flow. Build-time processing is the standard `jevents.py` path from JSON rows to generated perf C tables. Runtime perf resolves aliases to PCU uncore PMU selectors and collects package-scoped counts. The events expose PCU state over the measurement interval: clockticks provide the time base, frequency-limit events count cycles constrained by thermal or power limits, residency events count package C-state cycles, and occupancy events count how many cores are in selected C-states.

Persistence is only through generated perf metadata. Hardware values are sampled during perf sessions and are not persisted by this file. Because the events are package-scoped, task-level attribution is not meaningful without careful workload isolation.

## Dependencies and Integration Points
The file depends on Granite Rapids PCU PMU support in the kernel, perf's PMU event schema, `jevents.py`, and Intel PCU event definitions. It integrates with `perf stat -e` for package-level power-management diagnostics and complements RAPL energy readings, scheduler/idle metrics, memory throttling events, and UPI low-power link events.

The public descriptions make these events visible and understandable in `perf list`, which matters because power-management counters are easy to misinterpret without explicit cycle or occupancy wording.

## Risks and Test Signals
Risks include experimental semantics, platform firmware policy differences, package-level attribution mistakes, and zero counts on systems that do not enter the relevant C-states or throttling paths. Core occupancy events are not the same as elapsed cycles; derived metrics must normalize with PCU clockticks or another appropriate time base.

Test signals include `jq` validation, event-table generation, `perf list` visibility for all 11 names, and Granite Rapids smoke tests under idle, CPU stress, thermal or power constrained, and frequency-transition workloads. A basic sanity check is that `UNC_P_CLOCKTICKS` increments during any package-level measurement and that C-state residency increases during idle intervals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/graniterapids/uncore-power.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/graniterapids/virtual-memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/graniterapids/virtual-memory.json

## Purpose
This JSON file defines 20 Intel Granite Rapids core PMU events for virtual-memory translation behavior in perf. The events cover DTLB load misses, DTLB store misses, and ITLB misses, including second-level TLB hits, completed page walks by page size, active page-walk cycles, and pending page-walk counts. The source was read as a complete 185-line JSON array.

## Important APIs, Types, and Functions
All rows have `EventName`, `EventCode`, `UMask`, `BriefDescription`, `PublicDescription`, `Counter`, and `SampleAfterValue`; entries for active or pending page walks include `CounterMask: "1"`. `Counter` is `0,1,2,3`, and `SampleAfterValue` is consistently `100003`. There are 20 unique event names and three event codes: `0x11` for `ITLB_MISSES.*`, `0x12` for `DTLB_LOAD_MISSES.*`, and `0x13` for `DTLB_STORE_MISSES.*`.

Important aliases include `*.STLB_HIT`, `*.WALK_ACTIVE`, `*.WALK_COMPLETED`, page-size-specific `*.WALK_COMPLETED_1G`, `*.WALK_COMPLETED_2M_4M`, `*.WALK_COMPLETED_4K`, and `*.WALK_PENDING`. `WALK_ACTIVE` and `WALK_PENDING` share unit mask `0x10` within their respective families but differ by counter mask semantics and descriptions, so the full row metadata is required to preserve meaning.

## Control Flow, State, and Persistence
The file is declarative. Build-time flow is `jevents.py` parsing and generated table emission. Runtime flow is perf alias lookup, event scheduling on core programmable counters, and sampling/counting based on the encoded event selector. Unlike the Granite Rapids uncore files, these events are core PMU events and can be used with task, CPU, or system-wide perf modes subject to normal PMU scheduling.

Static state is the alias-to-event-code mapping plus sample-after values and counter masks. `CounterMask: "1"` changes cycle-style interpretations for active/pending page-walk events. The file persists only as generated perf metadata; runtime virtual-memory behavior remains workload and address-space dependent.

## Dependencies and Integration Points
Dependencies include perf's JSON schema, Granite Rapids core PMU definitions, `jevents.py`, and kernel core PMU support. The file integrates with `perf list`, `perf stat`, and potentially `perf record` sampling through the `SampleAfterValue` defaults. It is a source of low-level signals for TLB miss metrics, page-size tuning, huge-page analysis, instruction-fetch pressure, and page-walk overhead investigation.

The event names are shared in style with earlier Intel x86 generations, so external tooling may reference familiar aliases. Maintaining exact names helps scripts compare virtual-memory behavior across CPU models, but semantics must still be checked per generation.

## Risks and Test Signals
Risks include duplicate event-code/unit-mask combinations that depend on counter-mask semantics, stale sample-after defaults, and confusion between completed walks, active cycles, and pending walk occupancy. Page-size-specific aliases are not interchangeable with the aggregate `WALK_COMPLETED` alias, whose unit mask aggregates multiple page sizes. ITLB lacks a 1G page-specific completed event in this file while DTLB load/store include one, which downstream scripts should not assume is a typo without hardware documentation.

Test signals include JSON validation, generated perf table checks, `perf list` visibility for DTLB and ITLB aliases, and workload smoke tests using random memory access, huge pages, and instruction-cache/code-footprint stress. Plausibility checks should show TLB walk events increase with sparse memory access and decrease when huge pages reduce page-walk pressure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/graniterapids/virtual-memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswell/cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswell/cache.json

## Purpose
This JSON file defines 94 Intel Haswell core PMU cache, memory, offcore, and memory-uop events for perf. It covers L1D replacement and pending misses, L2 line/request/transaction activity, lock and split-lock behavior, retired load/store memory uops, offcore request and outstanding-request events, and offcore response filters for L3 hit and peer-core snoop outcomes. The source was read as a complete 926-line JSON array.

## Important APIs, Types, and Functions
The file uses perf's x86 event JSON schema. Every row has `EventName`, `EventCode`, `UMask`, `BriefDescription`, `Counter`, and `SampleAfterValue`; 51 rows include `PublicDescription`. Specialized fields include `PEBS`, `Data_LA`, `AnyThread`, `CounterMask`, `Errata`, `MSRIndex`, and `MSRValue`. There are 94 unique event names and 19 unique event codes. Most events use generic counters `0,1,2,3`, while `OFFCORE_RESPONSE` rows use counter `2`, reflecting Haswell offcore response constraints.

Key families include `L1D.*`, `L1D_PEND_MISS.*`, `L2_LINES_IN/OUT.*`, `L2_RQSTS.*`, `L2_TRANS.*`, `LOCK_CYCLES.*`, `LONGEST_LAT_CACHE.*`, `MEM_LOAD_UOPS_*`, `MEM_UOPS_RETIRED.*`, `OFFCORE_REQUESTS.*`, `OFFCORE_REQUESTS_BUFFER.*`, `OFFCORE_REQUESTS_OUTSTANDING.*`, `OFFCORE_RESPONSE.*`, and `SQ_MISC.SPLIT_LOCK`. PEBS-capable rows are concentrated in retired load and memory-uop events. Twenty offcore response rows program MSRs `0x1a6,0x1a7` with specific `MSRValue` filters.

## Control Flow, State, and Persistence
There is no executable control flow in the JSON. During build generation, `jevents.py` records standard event fields and Haswell-specific MSR filter metadata. Runtime perf resolves aliases, schedules events on core counters, and programs extra offcore-response MSR filters when `MSRIndex`/`MSRValue` is present. PEBS and data linear-address fields influence sampling behavior for supported events.

Static state includes event encodings, sample periods, counter masks, errata annotations, offcore filter MSR programming values, and PEBS capabilities. Persistence is through generated perf event tables. Runtime counts and PEBS samples are session data and depend on workload, privilege mode, and CPU stepping.

## Dependencies and Integration Points
Dependencies include Haswell PMU definitions, perf's JSON schema, `jevents.py`, kernel x86 PMU and PEBS support, and offcore response MSR programming support. The file integrates with `perf list`, `perf stat`, `perf record`, top-down or memory-analysis workflows, and user scripts that rely on stable Intel event aliases.

Offcore response events are a major integration point: they combine the generic `OFFCORE_RESPONSE` event with model-specific MSR filters to classify L3 hits, HITM, and no-forward peer-core outcomes for demand reads, RFOs, code reads, prefetches, and all requests. Memory-retired PEBS events integrate with data address sampling and are useful for load-latency and memory locality investigations.

## Risks and Test Signals
Risks include extensive errata coverage, especially for `MEM_LOAD_UOPS_*`, `MEM_UOPS_RETIRED.*`, `L2_RQSTS.*`, and `OFFCORE_REQUESTS_OUTSTANDING.*`; offcore MSR filter mistakes; PEBS/Data_LA exposure on unsupported kernels; and counter scheduling constraints for offcore response aliases. `AnyThread` and `CounterMask` fields change event interpretation, and sample-after values vary from `20011` through multi-million defaults.

Test signals include JSON validation, `jevents.py` generation, generated-table inspection for MSR fields, `perf list` visibility, `perf stat` smoke tests for L1/L2/offcore families, and `perf record` tests for PEBS-capable memory events. Hardware validation should compare cache-sensitive workloads, streaming memory, locked operations, and cross-core sharing workloads against the relevant aliases while checking errata notes for the tested Haswell stepping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswell/cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswell/counter.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswell/counter.json

## Purpose
This JSON file declares counter inventory metadata for Intel Haswell PMU units in perf. Unlike event files, it does not define event aliases or encodings; it tells the PMU event tooling how many fixed and generic counters exist for selected units. The source was read as a complete 21-line JSON array.

## Important APIs, Types, and Functions
The schema fields are `Unit`, `CountersNumFixed`, and `CountersNumGeneric`. The four rows are `core` with 3 fixed and 4 generic counters, `CBOX` with 0 fixed and 2 generic counters, `ARB` with 0 fixed and 2 generic counters, and `cbox_0` with 1 fixed and 0 generic counters. The first three rows store counter counts as strings, while `cbox_0` stores `CountersNumFixed` as a numeric JSON value, so consumers must tolerate both string and numeric forms.

There are no `EventName`, `EventCode`, unit masks, descriptions, metrics, functions, or classes in this file. Its public contract is PMU unit capacity metadata.

## Control Flow, State, and Persistence
The file has no control flow. Build-time perf tooling parses it with the rest of the Haswell model directory and incorporates counter-count metadata into generated tables or lookup structures used by perf. Runtime perf uses PMU driver capabilities and event metadata for scheduling; this file provides model-specific counter inventory context.

Static state is the declared counter capacity by unit. The generated perf artifacts persist this metadata. Runtime counter allocation remains dynamic and depends on active events, grouping, pinned/exclusive requests, kernel constraints, and PMU driver behavior.

## Dependencies and Integration Points
Dependencies include perf's PMU event JSON support for counter metadata, Haswell unit naming, and `jevents.py` or related generation code that recognizes counter inventory rows. It integrates with Haswell event files that reference `core`, CBOX-like, and ARB units, and with perf scheduling diagnostics where available counter counts affect whether event groups can be placed together.

The file is especially relevant for uncore or box PMUs whose counter counts differ from core PMU defaults. Incorrect counts can lead to misleading scheduling expectations even if event encodings are correct.

## Risks and Test Signals
Risks include mixed numeric/string count representation, stale unit names, and mismatches between declared counts and kernel PMU driver capabilities. Because `cbox_0` differs from `CBOX`, tooling must not normalize unit names in a way that collapses distinct rows accidentally. This file also has no descriptions, so the meaning of each unit depends on external Haswell PMU knowledge.

Test signals include JSON validation, successful event-table generation, generated metadata inspection for counter counts, and perf grouping tests that attempt to schedule more events than available counters on core, CBOX, and ARB units. A parser regression test should cover both string and numeric counter-count values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswell/counter.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswell/floating-point.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswell/floating-point.json

## Purpose
This JSON file defines 10 Intel Haswell core PMU events for floating-point, SIMD, AVX/SSE transition, and SIMD move-elimination analysis in perf. The source was read as a complete 93-line JSON array.

## Important APIs, Types, and Functions
Every row has `EventName`, `EventCode`, `UMask`, `BriefDescription`, `Counter`, and `SampleAfterValue`; eight rows include `PublicDescription`. Some rows include `CounterMask`, and the AVX/SSE transition events include `Errata: "HSD56, HSM57"`. There are 10 unique event names over four event codes: `AVX_INSTS.ALL` (`0xC6`), `FP_ASSIST.*` (`0xCA`), `MOVE_ELIMINATION.SIMD_*` (`0x58`), and `OTHER_ASSISTS.*` (`0xC1`). Counters are generic `0,1,2,3`.

The event set includes approximate AVX instruction counting, SIMD and x87 FP assists for input/output values, SIMD move-elimination candidates that were eliminated or not eliminated, and transition penalties from AVX-256 to legacy SSE or from SSE to AVX-256. There are no metric expressions or uncore fields.

## Control Flow, State, and Persistence
The file is declarative. `jevents.py` parses it during build generation and emits generated event metadata. Runtime perf resolves aliases to core PMU selectors and counts or samples them with the configured sample-after defaults.

Static state is the event selector mapping, sample period, counter mask, and errata metadata. `FP_ASSIST.ANY` aggregates multiple assist unit masks, while the specific `SIMD_INPUT`, `SIMD_OUTPUT`, `X87_INPUT`, and `X87_OUTPUT` aliases break down causes. Persistence is through generated perf tables; observed assist and transition counts are workload-local.

## Dependencies and Integration Points
Dependencies include Haswell PMU definitions, perf's JSON schema, `jevents.py`, and kernel core PMU support. The file integrates with `perf list`, `perf stat`, and sampling workflows for floating-point-heavy applications. It is useful with compiler vectorization analysis, numerical workloads, AVX/SSE mixed-code investigations, and microarchitecture tuning.

These events integrate conceptually with frontend/backend and retirement events, since FP assists and AVX/SSE transitions can create pipeline penalties not visible from instruction count alone.

## Risks and Test Signals
Risks include approximate semantics for `AVX_INSTS.ALL`, errata on `OTHER_ASSISTS.AVX_TO_SSE` and `OTHER_ASSISTS.SSE_TO_AVX`, and confusion between assist cycles and assist occurrences depending on the specific event. Transition events may depend on code generation, OS XSAVE behavior, and library mixing, so zero counts do not necessarily mean the event is broken.

Test signals include JSON validation, generated event-table checks, `perf list` visibility, and targeted Haswell workloads: AVX2 loops for `AVX_INSTS.ALL`, denormal or exceptional FP inputs for assist events, register move-heavy SIMD code for move elimination, and mixed AVX/SSE call paths for transition assists. Errata should be reviewed against the exact CPU stepping used for validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswell/floating-point.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswell/frontend.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswell/frontend.json

## Purpose
This JSON file defines 29 Intel Haswell core PMU frontend events for branch resteers, DSB-to-MITE switches, instruction-cache behavior, instruction decode queue delivery, microcode sequencer activity, and frontend under-delivery. The source was read as a complete 275-line JSON array.

## Important APIs, Types, and Functions
Every row has `EventName`, `EventCode`, `UMask`, `BriefDescription`, `Counter`, and `SampleAfterValue`; 16 rows include `PublicDescription`. Specialized fields include `CounterMask`, `EdgeDetect`, `Invert`, and `Errata`. There are 29 unique event names over five event codes: `BACLEARS.ANY` (`0xe6`), `DSB2MITE_SWITCHES.PENALTY_CYCLES` (`0xAB`), `ICACHE.*` (`0x80`), `IDQ.*` (`0x79`), and `IDQ_UOPS_NOT_DELIVERED.*` (`0x9C`).

Important families include `ICACHE.HIT/MISSES/IFETCH_STALL/IFDATA_STALL`, DSB and MITE delivery cycle/uop events, microcode sequencer delivery/switch events, `IDQ.EMPTY`, and `IDQ_UOPS_NOT_DELIVERED.*` aliases. Several aliases intentionally share event code and unit mask but differ by counter masks, edge detection, invert, or descriptive semantics; for example IDQ cycle and uop views use overlapping selectors with different interpretation.

## Control Flow, State, and Persistence
The file has no executable control flow. Build-time generation is handled by `jevents.py`, which preserves event fields in generated perf tables. Runtime perf schedules the events on core programmable counters and applies edge, invert, and counter-mask settings when present.

Static state includes frontend event encodings, counter masks, edge-detect/invert modifiers, errata annotations, and sample-after values. Persistence is generated perf metadata only. Runtime counts depend heavily on workload instruction footprint, branch behavior, decode path selection, microcode usage, SMT state, and backend stalls because several frontend-delivery events are defined relative to whether the backend is stalled.

## Dependencies and Integration Points
Dependencies include Haswell PMU definitions, perf's JSON event schema, `jevents.py`, and kernel x86 PMU support for event modifiers. The file integrates with `perf list`, `perf stat`, and frontend performance analysis. It is an input to top-down-style diagnosis even though this file itself contains no metric expressions.

The events complement cache, branch, pipeline, and instruction-retirement event files. For example, instruction-cache misses can be correlated with ITLB/cache events, IDQ under-delivery with backend stall metrics, and microcode sequencer events with complex instruction or assist-heavy workloads.

## Risks and Test Signals
Risks include errata `HSD135` on `IDQ.EMPTY` and all `IDQ_UOPS_NOT_DELIVERED.*` rows, modifier mistakes for `CounterMask`, `EdgeDetect`, or `Invert`, and ambiguous aliases such as `ICACHE.IFDATA_STALL` and `ICACHE.IFETCH_STALL` sharing the same selector. Frontend under-delivery events are easy to misread without considering backend stall conditions. Events with shared selectors may produce identical raw counts while representing different documented viewpoints.

Test signals include JSON validation, generated-table checks for edge/invert/counter-mask fields, `perf list` visibility, and Haswell hardware smoke tests with branch-mispredict, large instruction footprint, DSB-friendly tight-loop, MITE-heavy decode, and microcoded-instruction workloads. Validation should compare event behavior against expected frontend stress patterns and review errata for the tested stepping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswell/frontend.json -->
