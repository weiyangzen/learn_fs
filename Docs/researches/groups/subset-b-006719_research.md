# Research: subset-b-006719 Skylake perf PMU event JSON files

This grouped report covers the Skylake PMU event descriptor files under `sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylake/`. The files are declarative data consumed by Linux `perf` PMU event tooling rather than executable Ceph client code. Their effective API is the perf JSON schema: event names, hardware encodings, counter constraints, descriptions, PEBS/MSR metadata, errata tags, metric group names, and grouped taxonomy strings.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylake/cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylake/cache.json

## Purpose

`cache.json` defines 243 Skylake core PMU events focused on cache hierarchy behavior, load/store retirement, prefetch activity, offcore request/response classification, and split-lock/prefetch side events. It gives `perf list` and `perf stat/record -e` the Skylake-specific names and encodings needed to program model-specific performance counters for cache analysis.

The file is dominated by offcore response variants: 173 `OFFCORE_RESPONSE.*` records combine request type (`DEMAND_CODE_RD`, `DEMAND_DATA_RD`, `DEMAND_RFO`, `OTHER`), supplier state (`L3_HIT`, `L3_HIT_E/M/S`, `L4_HIT_LOCAL_L4`, `SUPPLIER_NONE`), and snoop result (`ANY_SNOOP`, `SNOOP_HITM`, `SNOOP_MISS`, `SNOOP_NONE`, `SNOOP_NOT_NEEDED`, `SPL_HIT`). Smaller clusters cover L1D fill-buffer pressure, L2 requests and evictions, retired load/store classes, L3 hit snoop outcomes, outstanding offcore request occupancy, and software prefetch accesses.

## Important schema/API surface

Each array entry is a perf event descriptor. Important fields include:

- `EventName`: public event selector, for example `L1D.REPLACEMENT`, `L2_RQSTS.ALL_DEMAND_MISS`, `MEM_LOAD_RETIRED.L3_MISS`, and the many `OFFCORE_RESPONSE.*` combinations.
- `EventCode` and `UMask`: raw event select and unit-mask encodings programmed into the generic PMU event-select MSRs.
- `Counter`: allowed generic counter list, usually `0,1,2,3`.
- `CounterMask`, `AnyThread`, `EdgeDetect`, `Invert`: optional hardware qualifier bits for cycle/threshold style events.
- `MSRIndex` and `MSRValue`: offcore response filter programming. Most `OFFCORE_RESPONSE.*` records use `MSRIndex` `0x1a6,0x1a7` with a request/supplier/snoop-specific `MSRValue`.
- `PEBS` and `Data_LA`: mark precise load/store events, notably `MEM_INST_RETIRED.*`, `MEM_LOAD_RETIRED.*`, `MEM_LOAD_L3_HIT_RETIRED.*`, and `MEM_LOAD_MISC_RETIRED.UC`.
- `Errata` and `Deprecated`: annotate known hardware caveats, such as `LONGEST_LAT_CACHE.*` with `SKL057` and `L2_LINES_OUT.USELESS_PREF` as deprecated in favor of `L2_LINES_OUT.USELESS_HWPF`.
- `BriefDescription`, `PublicDescription`, and `SampleAfterValue`: user-facing event help and sampling defaults.

## Control flow and integration

There is no runtime control flow in the file itself. At build or runtime, perf's PMU event table generator/parser reads this JSON, associates it with the Skylake CPU model map, and exposes the event names through the perf event alias layer. When a user asks for an event by name, perf resolves the descriptor to a raw event encoding, applies optional qualifiers, writes any required offcore filter MSR, and opens the hardware event via `perf_event_open`.

Offcore response events have the most important integration behavior. The base event is not sufficient: perf must also program one of the offcore response MSRs listed in `MSRIndex` with the descriptor's `MSRValue`. That makes this data coupled to kernel support for offcore-response extra registers and to counter scheduling rules that avoid incompatible simultaneous offcore filters.

## State and persistence behavior

The file is static architecture metadata. It persists only in the source tree and generated perf event tables; it does not mutate at runtime and has no local storage. Runtime state is in hardware PMU registers selected from the JSON values, plus perf's in-memory event aliases and measurement buffers.

## Dependencies

The descriptors depend on Skylake architectural PMU semantics, Intel event documentation, perf's JSON schema, perf's Skylake CPU model mapping, and kernel PMU support for PEBS, data linear address capture, generic counter masks, and offcore-response MSR filters. The many events using fixed `0x1a6,0x1a7` MSR filters also depend on the kernel allowing those extra registers for this CPU family.

## Risks and maintenance notes

The largest risk is encoding drift. A one-bit error in `MSRValue` or `UMask` can silently report the wrong memory supplier or snoop class. The offcore matrix is repetitive, so copy/paste mistakes are easy and may not be caught by JSON syntax validation.

Deprecated and errata-tagged events need clear preservation. Removing `L2_LINES_OUT.USELESS_PREF` would break users with old scripts, while failing to surface its deprecation would keep steering users to stale naming. `LONGEST_LAT_CACHE.*` carries `SKL057`, so analysis tools should treat it as hardware-caveated rather than universally reliable.

Precise events marked with `PEBS`/`Data_LA` can fail or degrade on kernels, privilege settings, or virtualized environments that do not expose the required precise sampling support. Reports should distinguish "event not known" from "event known but unavailable on this host".

## Test signals

Useful validation includes `jq empty` for syntax, schema checks that all array entries have `EventName`, `EventCode`, `UMask`, and descriptions, duplicate-name checks within the Skylake event set, and perf table generation tests. Runtime smoke tests on Skylake hardware should verify representative aliases: `L1D.REPLACEMENT`, `L2_RQSTS.MISS`, `MEM_LOAD_RETIRED.L3_MISS`, one `OFFCORE_REQUESTS_OUTSTANDING.*`, and several `OFFCORE_RESPONSE.*` aliases that require MSR filter programming.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylake/cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylake/counter.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylake/counter.json

## Purpose

`counter.json` describes the basic Skylake PMU counter inventory rather than individual events. It contains four records that declare available counter resources for the `core`, `CBOX`, `ARB`, and `cbox_0` PMU units. The core PMU row advertises 3 fixed counters and 4 generic programmable counters; the uncore-style `CBOX` and `ARB` rows advertise 2 generic counters each; `cbox_0` advertises 1 fixed counter and 0 generic counters.

This file helps perf and related tooling understand counter capacity and unit naming for the Skylake PMU map. It is a small but central companion to the event files because event constraints such as `Counter: 0,1,2,3` only make sense when the architecture's generic/fixed counter counts are known.

## Important schema/API surface

The API is a compact JSON array with fields different from normal event descriptors:

- `Unit`: PMU unit name, specifically `core`, `CBOX`, `ARB`, and `cbox_0`.
- `CountersNumFixed`: fixed-function counter count, with values `3`, `0`, `0`, and numeric `1`.
- `CountersNumGeneric`: programmable generic counter count, with values `4`, `2`, `2`, and `0`.

No `EventCode`, `UMask`, or `EventName` fields are present because this file does not program a specific event.

## Control flow and integration

Perf's PMU event metadata loader treats this file as architecture capacity metadata. The data is integrated with the same Skylake map as event categories such as `cache.json`, `frontend.json`, and `pipeline.json`. Scheduling and display paths can use it to explain that Skylake exposes four generic core counters and three fixed counters, while specific event descriptors name the counters they can use.

The uncore-style `CBOX`, `ARB`, and `cbox_0` rows are integration signals that consumers must not assume every row describes the core programmable PMU. Tools should key counter capacity by `Unit`.

## State and persistence behavior

The file is persistent static metadata. It has no runtime mutation and no per-host state. At runtime the real counter availability can still be affected by kernel PMU support, privilege settings, NMI watchdog usage, pinned events, virtualization, and already scheduled perf sessions.

## Dependencies

The file depends on perf's PMU event JSON parser recognizing counter inventory fields and on the Skylake PMU implementation having 3 fixed counters and 4 generic counters. It also depends on downstream tools handling `Unit` rows without event encodings.

## Risks and maintenance notes

The main risk is confusing this schema with event-list schema. Generic validators that require `EventName` or `EventCode` would incorrectly reject this file. Conversely, event loaders that iterate every JSON file as an event array without checking row shape could try to expose bogus aliases.

Counter counts are simple values but high impact. If `CountersNumGeneric` or `CountersNumFixed` is wrong, scheduling diagnostics and event multiplexing expectations become misleading. The mixed string and numeric representation of counts (`"3"` versus `1`) is also worth preserving or normalizing deliberately in consumers.

## Test signals

Validation should check that the file is valid JSON, has four rows, includes `CountersNumFixed: "3"` and `CountersNumGeneric: "4"` for `core`, includes the `CBOX`, `ARB`, and `cbox_0` rows, and does not require event-specific fields. Integration tests should run perf's PMU event table generation and confirm no bogus event aliases are emitted from this file.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylake/counter.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylake/floating-point.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylake/floating-point.json

## Purpose

`floating-point.json` defines 10 Skylake events for floating-point arithmetic retirement and floating-point/SSE assist cycles. The primary purpose is to expose FP operation mix and assist overhead to perf users profiling numerical workloads.

Most entries are variants of `FP_ARITH_INST_RETIRED.*`, all using event code `0xC7` with different unit masks for scalar, 128-bit packed, 256-bit packed, vector aggregate, and mixed four-flop classes. These records encode Intel's operation-count semantics in descriptions, including the fact that some DPP and FMA/FMS instructions count twice.

## Important schema/API surface

Important records include:

- `FP_ARITH_INST_RETIRED.SCALAR`, `.SCALAR_SINGLE`, `.SCALAR_DOUBLE`, `.128B_PACKED_SINGLE`, `.128B_PACKED_DOUBLE`, `.256B_PACKED_SINGLE`, `.256B_PACKED_DOUBLE`, `.4_FLOPS`, and `.VECTOR`.
- `FP_ASSIST.ANY`, event code `0xCA`, unit mask `0x1e`, `CounterMask: 1`, counting cycles with SSE/x87 assists.
The key fields are `EventName`, `EventCode`, `UMask`, `Counter`, `CounterMask`, `BriefDescription`, `PublicDescription`, and `SampleAfterValue`. The FP arithmetic descriptions are part of the effective API because consumers need them to convert instruction counts to operation counts correctly.

## Control flow and integration

Perf loads the file as a Skylake event category and exposes the names as aliases. Selecting one of the FP arithmetic names programs a generic counter with event code `0xC7` and the corresponding mask. The same base event with multiple masks is intentional and lets users break down scalar versus vector width and precision.

The FP assist event uses a counter mask to count cycles rather than simple occurrences. That affects how perf users interpret results: it is a stall/assist duration signal, not a retired-instruction count.

## State and persistence behavior

The file is static metadata. Runtime state resides in PMU counters and sampled perf records. There is no persistence beyond the source JSON and generated perf alias tables.

## Dependencies

The descriptors depend on Skylake's SIMD FP event semantics, MXCSR behavior, and perf's schema support. Several public descriptions state that DAZ and FTZ flags in MXCSR need to be set when using the FP arithmetic events, so measurement accuracy depends on workload floating-point environment as well as PMU programming.

## Risks and maintenance notes

Interpretation risk is high for FLOP counting. Event increments are not always equal to one arithmetic operation: vector width changes element count, packed single/double have different element counts, and some DPP/FMA/FMS instructions count twice. A downstream metric that treats raw event counts uniformly will misreport FLOPs.

`FP_ARITH_INST_RETIRED.VECTOR` lacks a detailed public description compared with the width-specific variants, so users may need to prefer the more specific events for documentation-rich analyses. Category-based tooling can treat this file as focused on FP arithmetic/assist coverage.

## Test signals

Syntax and schema validation should confirm all 10 entries have valid names and encodings. Alias smoke tests should include one scalar event, one 128-bit packed event, one 256-bit packed event, and `FP_ASSIST.ANY`. Documentation validation should preserve the MXCSR DAZ/FTZ notes and the doubled-count behavior for DPP/FMA/FMS instructions.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylake/floating-point.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylake/frontend.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylake/frontend.json

## Purpose

`frontend.json` defines 49 Skylake frontend PMU events for instruction fetch, decode, decoded-stream-buffer delivery, MITE delivery, microcode sequencer delivery, frontend latency, and under-delivery of uops to the backend. It supports top-down and direct frontend bottleneck analysis through perf aliases.

The major clusters are `FRONTEND_RETIRED.*` latency and miss events, `IDQ.*` instruction-decode-queue delivery events, `IDQ_UOPS_NOT_DELIVERED.*` backend supply shortfall events, instruction-cache tag/data events, and DSB-to-MITE switch penalties.

## Important schema/API surface

The descriptor entries use normal perf event fields:

- `EventName`: examples include `BACLEARS.ANY`, `DECODE.LCP`, `DSB2MITE_SWITCHES.COUNT`, `FRONTEND_RETIRED.LATENCY_GE_16`, `ICACHE_64B.IFTAG_MISS`, `IDQ.DSB_UOPS`, `IDQ.MITE_UOPS`, and `IDQ_UOPS_NOT_DELIVERED.CORE`.
- `EventCode`/`UMask`: raw PMU event selector and mask. `FRONTEND_RETIRED.*` entries use MSR-based precise frontend latency filtering rather than ordinary masks alone.
- `MSRIndex`/`MSRValue`: `FRONTEND_RETIRED.*` entries use MSR index `0x3F7` with latency/miss-specific values.
- `PEBS`: precise frontend-retired events are marked with PEBS levels, with `LATENCY_GE_1` carrying `PEBS: 2` and most other frontend-retired variants carrying `PEBS: 1`.
- `CounterMask`, `AnyThread`, `EdgeDetect`, and `Invert`: used by cycle-style IDQ and delivery events.
- `BriefDescription`, `PublicDescription`, and `SampleAfterValue`: expose frontend-analysis semantics to users.

## Control flow and integration

The file is consumed by perf's Skylake event alias layer. When a user selects frontend aliases, perf programs generic PMU counters. For `FRONTEND_RETIRED.*` aliases, perf must also program frontend latency/miss filtering through the `0x3F7` MSR value. That extra-register path is comparable to offcore-response events in `cache.json` and `memory.json`, but it targets frontend retirement qualification rather than memory suppliers.

The event set integrates strongly with top-down microarchitecture analysis. `IDQ_UOPS_NOT_DELIVERED.*` and `IDQ.*` provide frontend-bound signals that can feed higher-level metrics, while `ICACHE_*`, `DECODE.LCP`, and `DSB2MITE_SWITCHES.*` help decompose fetch latency, decode stalls, and uop-cache transitions.

## State and persistence behavior

The JSON is static metadata. Runtime state consists of selected PMU counters, optional frontend MSR filters, PEBS records when sampling precise events, and perf's event scheduling metadata. No state is persisted by this file.

## Dependencies

The file depends on Skylake frontend PMU semantics, kernel support for PEBS and the frontend event extra register, perf's JSON schema, and the CPU model map selecting this file only for compatible Skylake systems. Some event meanings also depend on SMT and pipeline delivery width assumptions used by top-down metrics.

## Risks and maintenance notes

The most important risk is extra-register correctness. Incorrect `MSRValue` values for `FRONTEND_RETIRED.LATENCY_GE_*` or miss events would silently change the latency threshold or miss class being sampled. Because many latency entries differ by small mask changes, tests need to inspect values rather than only names.

Precise sampling requirements can make frontend-retired aliases unavailable or approximate on some kernels or virtual machines. Tools should preserve the `PEBS` markings and should not assume every frontend event is equally usable in counting and sampling modes.

Naming drift is another risk: `IDQ.ALL_*`, `IDQ.*`, and `IDQ_UOPS_NOT_DELIVERED.*` sound similar but measure different delivery conditions. Metric expressions should reference exact event names and not pattern-match broad prefixes without checking definitions.

## Test signals

Validation should include JSON syntax, required field checks, and generated perf alias tests. Runtime smoke tests on Skylake hardware should cover `IDQ_UOPS_NOT_DELIVERED.CORE`, `IDQ.MITE_UOPS`, `IDQ.DSB_UOPS`, `ICACHE_64B.IFTAG_MISS`, and at least one `FRONTEND_RETIRED.LATENCY_GE_*` event that exercises MSR index `0x3F7`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylake/frontend.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylake/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylake/memory.json

## Purpose

`memory.json` defines 131 Skylake PMU events for memory latency, L3 miss behavior, transactional memory, memory ordering clears, offcore response classes, and load-latency precise events. It complements `cache.json`: `cache.json` includes broad cache-hit and offcore-hit coverage, while this file emphasizes L3 misses, local DRAM miss classes, transactional abort causes, and load latency thresholds.

The largest cluster is 88 `OFFCORE_RESPONSE.*` entries for L3 miss and local DRAM combinations across demand code reads, demand data reads, demand RFOs, and other requests. Other clusters cover `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_*`, `HLE_RETIRED.*`, `RTM_RETIRED.*`, `TX_EXEC.*`, `TX_MEM.*`, `CYCLE_ACTIVITY.*`, and `MACHINE_CLEARS.MEMORY_ORDERING`.

## Important schema/API surface

Key entries and fields:

- `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_4` through `LOAD_LATENCY_GT_512`: precise load latency threshold events using MSR index `0x3F6`, `PEBS: 2`, and `Data_LA: 1`.
- `OFFCORE_RESPONSE.*.L3_MISS*` and `.L3_MISS_LOCAL_DRAM.*`: offcore response events using MSR index `0x1a6,0x1a7` and detailed `MSRValue` filters.
- `CYCLE_ACTIVITY.CYCLES_L3_MISS` and `STALLS_L3_MISS`: cycle/stall signals for L3 miss impact.
- `HLE_RETIRED.*`, `RTM_RETIRED.*`, `TX_EXEC.*`, and `TX_MEM.*`: transactional synchronization and TSX abort/commit diagnostics.
- `MACHINE_CLEARS.MEMORY_ORDERING`: memory-ordering machine-clear event with `Errata: SKL089`.

Normal fields include `EventName`, `EventCode`, `UMask`, `Counter`, `CounterMask`, `PEBS`, `MSRIndex`, `MSRValue`, `Data_LA`, `Errata`, descriptions, and sample defaults.

## Control flow and integration

Perf exposes these descriptors as Skylake aliases. Load-latency threshold events require programming the PEBS load-latency extra register through `MSRIndex` `0x3F6`, while offcore-response events require programming `0x1a6`/`0x1a7`. Transactional events use ordinary event encodings but are only meaningful when the processor and kernel expose the relevant TSX/HLE behavior.

The file integrates with memory-bound top-down analysis and with lower-level troubleshooting. Users can combine `CYCLE_ACTIVITY.*` stall signals, `MEM_TRANS_RETIRED.*` latency thresholds, and `OFFCORE_RESPONSE.*` supplier/snoop filters to identify whether stalls are due to local DRAM, snoop/coherency behavior, or transactional aborts.

## State and persistence behavior

The file has no mutable state. Runtime state lives in PMU counters, extra MSR filters, PEBS records with data addresses for eligible events, and perf's scheduling state. Hardware and kernel capabilities determine which descriptors can be used at measurement time.

## Dependencies

Dependencies include Skylake PMU definitions, perf's parser for extra MSR fields, kernel support for PEBS load-latency sampling, offcore response filtering, TSX/HLE event exposure, and CPU model selection. The load latency events also rely on memory-latency threshold semantics encoded in the `MSRValue` field.

## Risks and maintenance notes

Offcore response encodings are repetitive and high risk. The `.L3_MISS`, `.L3_MISS_LOCAL_DRAM`, `.SNOOP_NON_DRAM`, and related variants differ by bitmask combinations; a wrong `MSRValue` can produce plausible but wrong measurements.

TSX/HLE events can be confusing on systems where transactional memory is disabled by microcode, BIOS, kernel mitigations, or virtualization. The aliases may still exist as metadata but produce unsupported or zero-like behavior in practice.

`MACHINE_CLEARS.MEMORY_ORDERING` carries `SKL089`, so consumers should preserve the errata tag. Load latency threshold events depend on PEBS/data-address support and privilege settings; they should be tested separately from ordinary counting events.

## Test signals

Static checks should verify JSON validity, all 131 event records, valid `MSRIndex`/`MSRValue` pairs, and unique `EventName` values within the file. Runtime smoke tests should cover a `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_*` precise event, one `OFFCORE_RESPONSE.DEMAND_DATA_RD.L3_MISS_LOCAL_DRAM.*` alias, one `CYCLE_ACTIVITY.*` event, and at least one TSX/HLE alias with expected behavior documented when TSX is unavailable.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylake/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylake/metricgroups.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylake/metricgroups.json

## Purpose

`metricgroups.json` maps 137 Skylake metric group names to human-readable group descriptions. Unlike the event files, it is a JSON object rather than an array of event descriptors. It supplies taxonomy for perf metrics, especially top-down microarchitecture analysis groups and issue-oriented groupings.

The file includes broad groups such as `Backend`, `Frontend`, `Retire`, `MemoryBound`, `Flops`, `HPC`, `Power`, and `Summary`; top-down levels such as `TopdownL1` through `TopdownL6` and `tma_L1_group` through `tma_L6_group`; and detailed TMA categories such as `tma_backend_bound_group`, `tma_fetch_latency_group`, `tma_l1_bound_group`, `tma_ports_utilization_group`, and `tma_store_bound_group`.

## Important schema/API surface

The schema is a string-to-string map:

- Keys are metric group identifiers used by metric descriptors in adjacent architecture metric files.
- Values are descriptions shown by tools such as `perf list --metricgroups` or used by documentation/index generation.

Many values are repeated as `Grouping from Top-down Microarchitecture Analysis Metrics spreadsheet`, indicating imported taxonomy from Intel's TMA spreadsheet. Others give explicit descriptions, for example `TopdownL1` as metrics for top-down breakdown at level 1 and `tma_fp_arith_group` as metrics contributing to the `tma_fp_arith` category.

## Control flow and integration

Perf loads this file as metric taxonomy, not as event aliases. Metric descriptors elsewhere reference these group names through `MetricGroup` fields; this file gives those names display text and grouping semantics. A metric query can use these groups to list related metrics, filter output, or organize top-down analysis views.

Because the file is an object, generic event-list code must branch on schema shape. Treating it as an array of events would fail or emit meaningless aliases.

## State and persistence behavior

The file is static taxonomy. It has no runtime state. Persistence is limited to the JSON file and generated metric-group tables.

## Dependencies

The mapping depends on metric descriptors using exactly matching group names. It also depends on perf's metric parser recognizing `metricgroups.json` as a group-description object. Its content depends on Intel top-down microarchitecture analysis terminology and the local Skylake metric files that consume the group identifiers.

## Risks and maintenance notes

Name drift is the main risk. The file contains both legacy-style names (`TopdownL1`, `Frontend`, `MemoryBound`) and lower-case TMA names with `_group` suffixes (`tma_frontend_bound_group`, `tma_memory_bound_group`). If a metric descriptor references a group key not present here, tools may still compute the metric but lose organized display or documentation.

The repeated spreadsheet-derived description is useful as provenance but not very specific. More precise descriptions should be added carefully because existing tools or tests may compare exact strings. Case sensitivity matters for group lookup.

## Test signals

Validation should assert that the JSON root is an object with 137 keys, all values are strings, and expected top-down keys are present. Integration tests should cross-check metric descriptors' `MetricGroup` references against this map and verify `perf list` can show representative groups such as `TopdownL1`, `Frontend`, `MemoryBound`, and `tma_l1_bound_group`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylake/metricgroups.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylake/other.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylake/other.json

## Purpose

`other.json` contains two miscellaneous Skylake PMU event descriptors that do not fit cleanly into the other category files. The events are `HW_INTERRUPTS.RECEIVED`, counting hardware interrupts received by the processor, and `MEMORY_DISAMBIGUATION.HISTORY_RESET`, counting memory-disambiguation history resets.

## Important schema/API surface

The two array entries use standard event descriptor fields:

- `HW_INTERRUPTS.RECEIVED`: event code `0xCB`, unit mask `0x1`, generic counters `0,1,2,3`, and descriptions for processor hardware interrupt receipt.
- `MEMORY_DISAMBIGUATION.HISTORY_RESET`: event code `0x09`, unit mask `0x1`, generic counters `0,1,2,3`, with a minimal matching description.

Both records include `EventName`, `EventCode`, `UMask`, `Counter`, descriptions, and `SampleAfterValue`. They do not need MSR filters, PEBS, errata tags, or metric groups.

## Control flow and integration

Perf loads these as ordinary Skylake event aliases. Selecting either event programs a generic counter using only the raw event code and unit mask. They integrate as low-level diagnostics: interrupts can explain OS noise or workload disruption, while memory-disambiguation resets can point to speculative load/store ordering behavior.

## State and persistence behavior

The file is static metadata with no mutable state. Runtime state is limited to PMU counter values gathered by perf.

## Dependencies

The descriptors depend on Skylake's core PMU encodings and perf's standard event JSON parser.

## Risks and maintenance notes

The descriptions are short, especially for `MEMORY_DISAMBIGUATION.HISTORY_RESET`; downstream documentation may need external Intel references for detailed interpretation. Because this category is miscellaneous, future additions should avoid becoming a dumping ground for events that would be better placed in pipeline, memory, or frontend files.

## Test signals

Static validation should check syntax, exactly two entries, and required fields. Runtime smoke tests can run `perf stat -e HW_INTERRUPTS.RECEIVED` and `perf stat -e MEMORY_DISAMBIGUATION.HISTORY_RESET` on Skylake hardware.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylake/other.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylake/pipeline.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylake/pipeline.json

## Purpose

`pipeline.json` defines 101 Skylake PMU events for branch behavior, clock cycles, cycle activity, execution port utilization, load-blocking, machine clears, resource stalls, reservation-station state, uop dispatch/issue/execute/retire, and retired instruction classes. It is the main low-level pipeline behavior event catalog for Skylake.

Major clusters include branch retired/mispredict events, `CPU_CLK_UNHALTED.*`, `CYCLE_ACTIVITY.*`, `EXE_ACTIVITY.*`, `INST_RETIRED.*`, `INT_MISC.*`, `LD_BLOCKS.*`, `LSD.*`, `MACHINE_CLEARS.*`, `UOPS_DISPATCHED_PORT.PORT_0` through `.PORT_7`, `UOPS_EXECUTED.*`, `UOPS_ISSUED.*`, and `UOPS_RETIRED.*`.

## Important schema/API surface

Important fields are standard perf event descriptor fields:

- `EventName`: public aliases such as `BR_INST_RETIRED.ALL_BRANCHES`, `BR_MISP_RETIRED.ALL_BRANCHES`, `CPU_CLK_UNHALTED.THREAD`, `CYCLE_ACTIVITY.STALLS_TOTAL`, `EXE_ACTIVITY.1_PORTS_UTIL`, `INST_RETIRED.ANY`, `RESOURCE_STALLS.SB`, and `UOPS_RETIRED.RETIRE_SLOTS`.
- `EventCode`/`UMask`: raw PMU selector and unit mask.
- `Counter`, `CounterMask`, `AnyThread`, `EdgeDetect`, and `Invert`: counter constraints and qualifier bits, especially for cycles, stalls, and thresholded uop counts.
- `PEBS`: precise sampling support for selected retired branch and instruction events, including PEBS variants named explicitly such as `BR_INST_RETIRED.ALL_BRANCHES_PEBS` and `BR_MISP_RETIRED.ALL_BRANCHES_PEBS`.
- `BriefDescription`, `PublicDescription`, `SampleAfterValue`: visible perf documentation and default sampling periods.

## Control flow and integration

Perf exposes these descriptors as Skylake aliases and uses them for direct event selection and metric formulas. Many top-down metrics rely on this file's events: clocks, instructions, uops retired, bad speculation, port utilization, and stall counters are foundational to throughput and pipeline-breakdown calculations.

Events are programmed through generic PMU counters without the offcore or frontend MSR-filter complexity seen in the cache/memory/frontend files. The control-flow complexity is instead in counter scheduling: port events, uop-cycle thresholds, and stall events may compete for the same limited generic counters.

## State and persistence behavior

The JSON has no mutable state. Runtime state is PMU counter values, optional PEBS samples for precise events, and perf's multiplexing/scheduling state. Because this file includes core throughput events, measurements can be sensitive to SMT, frequency scaling, NMI watchdog reservations, and multiplexing.

## Dependencies

The file depends on Skylake PMU encodings, perf's event parser, CPU model mapping, PEBS support for precise retired events, and kernel scheduling of constrained events. Top-down metrics in adjacent files depend on these aliases retaining stable names and semantics.

## Risks and maintenance notes

Semantic overlap is a key risk. For example, `CPU_CLK_THREAD_UNHALTED.*` and `CPU_CLK_UNHALTED.*` variants differ in thread/core/reference semantics; choosing the wrong alias changes normalization. `INST_RETIRED.ANY`, `.ANY_P`, `TOTAL_CYCLES_PS`, and `PREC_DIST` are similarly specialized.

Some branch events have PEBS-specific variants and non-PEBS variants. Tooling should not collapse names just because descriptions are similar. Uop and port utilization events are often used in ratios; wrong counter masks, any-thread flags, or event aliases can distort top-down calculations.

Counter pressure is likely in real profiles because this file exposes many desirable events but Skylake has only four generic counters. Users and tests should expect multiplexing unless event sets are carefully chosen or fixed counters are used for cycles/instructions where available.

## Test signals

Static validation should check JSON syntax, required fields for all 101 entries, unique event names, and valid counter lists. Runtime smoke tests should include `CPU_CLK_UNHALTED.THREAD`, `INST_RETIRED.ANY`, `UOPS_RETIRED.RETIRE_SLOTS`, one `UOPS_DISPATCHED_PORT.PORT_*`, one branch retired event, and one `CYCLE_ACTIVITY.*` event. Metric integration tests should verify top-down formulas still resolve their pipeline aliases after any rename or encoding update.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylake/pipeline.json -->
