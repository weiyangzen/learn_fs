# subset-b-006620 research

Grouped research for the Alder Lake perf PMU event catalogs. Each section preserves the source path and is delimited for the reconciliation lane.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlake/cache.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlake/cache.json

## Purpose

This JSON file is an Alder Lake cache and memory-hierarchy PMU event table consumed by Linux `perf`'s pmu-events tooling. It contains 150 event records split across hybrid core PMU units: 86 `cpu_core` entries and 64 `cpu_atom` entries. The catalog describes L1D pending misses, L2 requests and line movement, last-level cache references and misses, retired memory operations, offcore response filters, prefetches, store-buffer and memory-scheduler behavior, and a small topdown frontend-bound signal. It is data, not executable code, but it forms part of the API that lets users run named events such as `L2_RQSTS.DEMAND_DATA_RD_MISS` instead of hand-encoding event select, unit mask, counters, and model-specific MSR filters.

## Important APIs, Types, and Data

The schema is the standard perf JSON event object shape: `EventName`, `EventCode`, `UMask`, `BriefDescription`, optional `PublicDescription`, `Counter`, `SampleAfterValue`, and `Unit`. Several records also use `CounterMask`, `EdgeDetect`, `Deprecated`, `Errata`, `Data_LA`, `MSRIndex`, and `MSRValue`. `Data_LA` marks precise load-address sampling candidates for PEBS-style data linear-address capture. `MSRIndex`/`MSRValue`, especially `0x1a6,0x1a7`, encode offcore-response request/response filters that perf must program in addition to the architectural event select registers.

The major event families are `L1D`, `L1D_PEND_MISS`, `L2_RQSTS`, `LONGEST_LAT_CACHE`, `MEM_INST_RETIRED`, `MEM_LOAD_RETIRED`, `MEM_LOAD_UOPS_RETIRED`, `MEM_UOPS_RETIRED`, `OCR`, `OFFCORE_REQUESTS`, `OFFCORE_REQUESTS_OUTSTANDING`, and `SW_PREFETCH_ACCESS`. There are duplicate event names across core and atom units where the same user-facing concept maps to different encodings. Two entries are deprecated and three carry errata annotations, so callers must not assume every named record is equally recommended.

## Control Flow

There is no local function control flow. At runtime, perf's pmu-events generator reads this array, validates required fields, converts each object into C tables or runtime JSON-derived descriptors, and exposes aliases under the Alder Lake model. When a user requests an event, perf resolves the active PMU unit (`cpu_core` or `cpu_atom`), selects matching records, programs the listed event select and umask values, and programs any offcore MSR filters before starting the counter. Hybrid systems make the unit field a control-flow input: a cache event may be legal on P-cores, E-cores, or both with different encodings.

## State and Persistence Behavior

The file is persistent source data checked into the tools tree. Runtime counter state lives in PMU hardware and perf event file descriptors, not in this JSON. The persistent contract is the stable set of event names, encodings, descriptions, sampling defaults, and flags. `Deprecated` entries remain as compatibility aliases but should steer users or metrics toward replacements. Offcore MSR values are persistent encoding data and are high risk because a small bit drift changes the semantic filter while leaving JSON syntactically valid.

## Dependencies and Integration Points

This table integrates with `tools/perf/pmu-events` JSON parsing, generated pmu-events C tables, `perf list`, `perf stat`, `perf record`, metric expressions in adjacent Alder Lake metric JSON files, and Intel hybrid PMU naming. It depends on kernel PMU support for Alder Lake core and atom event encodings, PEBS load-address sampling where `Data_LA` is present, and offcore response MSR programming for `OCR` events. Higher-level metrics in `adl-metrics.json` and group labels in `metricgroups.json` can reference these events by name.

## Risks

The main risks are schema-valid but semantically wrong encodings, duplicate event names selecting the wrong hybrid unit, stale deprecated aliases, and offcore MSR filters that do not match Intel documentation. `Data_LA` flags can imply unsupported precise sampling if the corresponding PMU or kernel path lacks support. Counter restrictions matter because many events list limited programmable counters; ignoring `Counter` can produce scheduling failures or multiplexed results. Event families with similar names, such as `MEM_LOAD_RETIRED` versus `MEM_LOAD_UOPS_RETIRED`, must remain separated because they describe different core types and counting domains.

## Test Signals

Useful validation includes `jq`/schema parsing, pmu-events generation, `perf list` on Alder Lake exposing the aliases under the expected PMU units, event-encoding tests comparing generated config/umask/MSR fields to known-good tables, and smoke runs for representative L1, L2, LLC, retired-load, prefetch, and offcore events. Metric tests should confirm that formulas referencing cache events resolve for both core and atom PMUs and skip gracefully when a unit-specific event is unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlake/cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlake/floating-point.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlake/floating-point.json

## Purpose

This file defines 22 Alder Lake floating-point and SIMD-related PMU events for perf. It covers divider activity, floating-point assists, SSE/AVX transition assists, FP arithmetic dispatch by execution port or vector pipe, retired scalar/vector FP arithmetic instructions, FP assist machine clears, and retired FP divider uops. The unit split is 18 `cpu_core` records and 4 `cpu_atom` records, reflecting the different PMU vocabularies of Alder Lake P-cores and E-cores.

## Important APIs, Types, and Data

Each entry is a perf event object with `EventName`, `EventCode`, `UMask`, `Counter`, `Unit`, `BriefDescription`, optional `PublicDescription`, and `SampleAfterValue`. One entry uses `CounterMask`. Event families include `ARITH`, `ASSISTS`, `FP_ARITH_DISPATCHED`, `FP_ARITH_INST_RETIRED`, `MACHINE_CLEARS`, and `UOPS_RETIRED`. The core-side `FP_ARITH_INST_RETIRED.*` entries distinguish scalar single/double, 128-bit packed single/double, 256-bit packed single/double, aggregate scalar, vector, and four-flop accounting. Atom-side `FP_ARITH_DISPATCHED.*` entries measure dispatch to ports or vector pipes rather than the same retired-instruction taxonomy.

## Control Flow

The file has no executable logic. Perf's event-table generation loads the array, emits descriptors, and later resolves user event names or metric dependencies to concrete PMU encodings. Runtime flow depends on `Unit`: a floating-point metric on an Alder Lake hybrid CPU may need one expression branch or event set for `cpu_core` and another for `cpu_atom`. The event table also controls sampling defaults through `SampleAfterValue`.

## State and Persistence Behavior

The persistent state is the event-name-to-encoding mapping. Counts are collected in hardware PMU counters and reset or accumulated by perf sessions. No mutable state is stored in the JSON. The stability of names matters because higher-level metrics and user scripts can refer to `FP_ARITH_INST_RETIRED.*`, `FP_ARITH_DISPATCHED.*`, or `ASSISTS.*` aliases. Changes to `SampleAfterValue` can affect profiling overhead and interrupt frequency, even when event semantics are unchanged.

## Dependencies and Integration Points

This catalog integrates with perf's pmu-events parser, Alder Lake model matching, hybrid PMU routing, `perf list`, `perf stat`, and topdown/HPC metrics that classify compute, FLOPs, vector width, divider bottlenecks, and assists. It depends on kernel exposure of the core and atom PMUs and on perf's support for event names that appear only on one hybrid unit. It also relates to `pipeline.json` because divider activity and assists are shared pipeline bottleneck signals.

## Risks

The largest semantic risk is mixing dispatch-domain atom events with retired-domain core events in one metric without unit-specific formulas. FLOP-style interpretation is also risky: some events count instructions, some count uops, and vector-width-derived FLOP estimates require careful scaling. Assist events are usually rare; low default sample periods or multiplexing can produce noisy data. Counter restrictions can make simultaneous FP breakdown groups unschedulable.

## Test Signals

Validation should include JSON parsing, pmu-events generation, `perf list` display for core-only and atom-only event names, and smoke `perf stat` runs on FP-heavy, SIMD-heavy, divider-heavy, and assist-triggering workloads. Metric tests should verify that FLOP/vector/divider formulas bind the correct event family for each PMU unit and do not combine core and atom encodings as if they were identical.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlake/floating-point.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlake/frontend.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlake/frontend.json

## Purpose

This 46-entry catalog describes Alder Lake frontend PMU events for branch-target clears, decode stalls, decoded-stream-buffer to MITE switches, frontend-retired latency and miss classifications, instruction-cache accesses and misses, instruction-cache tag/data stalls, IDQ delivery by source, IDQ bubbles, and uops-not-delivered cycles. It is primarily a support table for frontend-bound topdown analysis and lower-level frontend debugging in perf.

## Important APIs, Types, and Data

The file uses standard perf event fields plus `CounterMask`, `EdgeDetect`, `Invert`, `MSRIndex`, and `MSRValue` on selected events. It has 43 `cpu_core` records and 3 `cpu_atom` records. `FRONTEND_RETIRED.*` records use MSR `0x3F7` with different values to classify DSB misses, ITLB misses, L1I/L2 misses, latency thresholds from 1 through 512 cycles, microcode-sequencer flows, STLB misses, and unknown branches. `IDQ_BUBBLES.CYCLES_FE_WAS_OK` and `IDQ_UOPS_NOT_DELIVERED.CYCLES_FE_WAS_OK` combine inversion and counter masks to isolate cycles where the frontend was not the limiting condition.

## Control Flow

Perf reads these descriptors during pmu-events table generation and later uses them when a user requests an alias or when a metric expression references a frontend event. Runtime control is driven by the PMU unit and any extra MSR programming. Frontend-retired classifications are especially dependent on the auxiliary MSR value; perf must program both the base event and the classification selector for the result to mean what the alias says.

## State and Persistence Behavior

The JSON persists event semantics, selector values, and sampling periods. Hardware counters hold transient counts per perf session. MSR selector fields are persistent catalog data but transient hardware programming state during measurement. Because many frontend metrics are ratios against slots, cycles, or retired events, name stability and field stability are important for metric reproducibility.

## Dependencies and Integration Points

The table integrates with perf's Alder Lake event alias generation, hybrid PMU selection, `perf list`, topdown frontend metrics, instruction-cache analysis, branch-resteer analysis, and microcode-sequencer diagnostics. It depends on kernel and hardware support for frontend retired classification through MSR `0x3F7`, event qualifiers like `EdgeDetect` and `Invert`, and counter-mask handling. It is tightly related to `pipeline.json` topdown slot events and to `metricgroups.json` frontend/TMA group names.

## Risks

MSR-backed events are vulnerable to selector drift: the JSON can remain syntactically valid while pointing at the wrong frontend class. Hybrid asymmetry is another risk because most entries are `cpu_core`; metrics must not assume atom coverage exists. Counter-mask and invert events can be misread as simple occurrence counts when they are cycle or threshold predicates. Frontend latency threshold events overlap conceptually, so formulas must avoid double-counting without documented hierarchy.

## Test Signals

Tests should include schema validation, generated table checks for MSR selectors, `perf list` alias presence, and targeted workloads that stress I-cache misses, ITLB misses, branch resteers, DSB/MITE transitions, and microcode-heavy instruction sequences. Metric validation should confirm frontend-bound formulas resolve all required aliases on `cpu_core` and either provide atom alternatives or mark the metric unavailable on atom PMUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlake/frontend.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlake/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlake/memory.json

## Purpose

This 38-entry file describes Alder Lake memory-latency and offcore memory PMU events for perf. It covers stalls while cache misses are outstanding, load-head classifications at retirement, memory-ordering machine clears, L1D/L2/L3 miss stalls, retired load-latency thresholds, store sampling, offcore response demand-code/data/RFO/prefetch DRAM and L3-miss filters, and outstanding L3-miss demand reads. The unit split is 21 `cpu_core` records and 17 `cpu_atom` records.

## Important APIs, Types, and Data

Entries use the standard event schema plus `CounterMask`, `Data_LA`, `MSRIndex`, and `MSRValue`. Ten entries have `Data_LA`, mostly load-latency threshold and store-sample records where sampled data addresses are useful. Twenty-two entries use MSR filters, including load-latency MSR `0x3F6` and offcore response MSRs `0x1a6,0x1a7`. Event families include `CYCLE_ACTIVITY`, `LD_HEAD`, `MACHINE_CLEARS`, `MEMORY_ACTIVITY`, `MEM_TRANS_RETIRED`, `OCR`, `OFFCORE_REQUESTS`, and `OFFCORE_REQUESTS_OUTSTANDING`.

## Control Flow

There are no local functions. Perf converts the JSON into event aliases, then resolves user or metric requests into PMU programming. Load-latency events require perf to combine a base retired-memory event with a latency threshold selector. Offcore events require extra MSR programming that chooses request type and response class. During sampling, `Data_LA` can influence whether address data is requested and exposed in samples.

## State and Persistence Behavior

The file persists semantic names and hardware encodings. Runtime state is held in perf event descriptors, PMU counters, PEBS/sample buffers, and model-specific registers. Threshold values in `MSRValue` are durable source data; altering one changes the meaning of aliases such as `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_128`. The same is true for offcore response masks that distinguish DRAM, L3 miss, and local miss categories.

## Dependencies and Integration Points

This file integrates with perf's memory metrics, topdown memory-bound analysis, load-latency profiling, `perf mem`-adjacent workflows, and offcore bandwidth/latency formulas. It depends on Alder Lake PMU support for PEBS/data address capture, latency-threshold MSR programming, offcore-response MSR programming, and hybrid unit routing. It overlaps with `cache.json` because both contain memory hierarchy and offcore response signals, but this file emphasizes latency/stall diagnosis rather than broad cache request accounting.

## Risks

MSR filter mistakes are high impact because they silently count a different memory class. `Data_LA` does not guarantee address sampling is available for every mode, privilege level, or kernel version. Load-latency threshold events are cumulative-style predicates; formulas must handle overlapping thresholds deliberately. Some event names appear with both core and atom encodings, and some have local/DRAM wording that may not map identically across PMUs. Counter masks on stall events can also turn simple-looking events into cycle-qualified predicates.

## Test Signals

Validation should include JSON/schema checks, generated MSR field checks, `perf list` coverage, and smoke measurements on pointer-chasing, streaming read/write, cache-contained, and store-heavy workloads. Tests should verify that load-latency aliases program MSR `0x3F6` with the intended thresholds, offcore aliases program `0x1a6/0x1a7`, and metrics referencing memory events either provide both core and atom paths or fail clearly when a PMU lacks the needed alias.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlake/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlake/metricgroups.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlake/metricgroups.json

## Purpose

This file maps 148 Alder Lake metric group names to human-readable descriptions. Unlike the event catalogs, it is a JSON object rather than an array. Its keys are group identifiers used by perf metric definitions, `perf list --metricgroups`, and metric display organization. The descriptions mostly come from Intel Top-down Microarchitecture Analysis spreadsheets and classify metrics into summary, topdown levels, frontend/backend/memory/retiring categories, issue categories, cache, branch, FLOP, power, OS, server, and TMA subgroups.

## Important APIs, Types, and Data

The API surface is the object mapping from group name to description string. Important groups include legacy or high-level names such as `Backend`, `Bad`, `BadSpec`, `Frontend`, `Mem`, `MemoryBound`, `Pipeline`, `Retire`, `TopdownL1` through `TopdownL6`, and many lower-case TMA groups such as `tma_backend_bound_group`, `tma_fetch_latency_group`, `tma_memory_bound_group`, `tma_ports_utilization_group`, and `tma_store_bound_group`. There are also issue-oriented groups like `tma_issueBW`, `tma_issueFB`, `tma_issueLat`, and `tma_issueTLB`. The file is metadata for metrics, not event encodings.

## Control Flow

The file has no executable control flow. Perf loads it alongside metric definitions and uses the object keys as labels that group metrics for discovery and presentation. When users request a metric group, perf's metric selection flow can match the requested group against these keys and include metrics tagged with that group. The object shape matters: treating it as an array of event records would fail, and the parser must preserve arbitrary group names including mixed case and underscores.

## State and Persistence Behavior

The persistent state is the vocabulary of metric groups and their descriptions. Runtime state is limited to perf's loaded metric table and display filters. Renaming or removing a key can break user workflows that rely on group selection, even though no hardware encoding changes. Description changes affect discoverability and documentation but not the mathematical behavior of metric formulas.

## Dependencies and Integration Points

This file integrates with Alder Lake metric files such as `adl-metrics.json`, event catalogs in the same directory, perf's metric parser, metric group listing, and user-facing documentation generated by `perf list`. It depends on metric definitions using matching group names. It also bridges Intel TMA terminology into perf's command-line UX, so consistency with upstream Intel naming is an integration requirement.

## Risks

Because this is a free-form object, typos create new groups rather than obvious parse failures. Mixed naming conventions (`TopdownL1`, `TmaL1`, `tma_L1_group`) can fragment output if metric definitions use inconsistent labels. Duplicate concepts with slightly different names, such as memory bandwidth/latency variants, need deliberate compatibility handling. Parser code must not assume all pmu-events JSON files are arrays; this file is a useful guard against that assumption.

## Test Signals

Tests should validate JSON object parsing, ensure all metric group references in Alder Lake metric definitions resolve to known descriptions, and confirm `perf list --metricgroups` or equivalent output includes expected topdown and TMA groups. Regression tests should include group names with underscores, mixed case, and issue suffixes so normalizers do not collapse distinct groups accidentally.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlake/metricgroups.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlake/other.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlake/other.json

## Purpose

This small 11-entry catalog holds Alder Lake PMU events that do not fit cleanly into the cache, frontend, memory, floating-point, pipeline, or uncore buckets. It covers hardware and page-fault assists, core power license levels, last-branch-record insertion, streaming-write offcore responses, and XQ full cycles. Seven records target `cpu_core` and four target `cpu_atom`.

## Important APIs, Types, and Data

The entries use the standard perf event schema and selected optional fields: `Deprecated`, `CounterMask`, `MSRIndex`, and `MSRValue`. Event families are `ASSISTS`, `CORE_POWER`, `LBR_INSERTS`, `OCR`, and `XQ`. The `OCR.*STREAMING_WR*` entries use offcore response MSRs `0x1a6,0x1a7`; there are both atom-specific full/partial streaming-write records and a shared `OCR.STREAMING_WR.ANY_RESPONSE` name with core and atom encodings. `LBR_INSERTS.ANY` is deprecated for atom.

## Control Flow

There is no local execution. Perf consumes the JSON into alias tables and later programs PMU events when users request these miscellaneous aliases or when metrics depend on them. For `OCR` records, the runtime path includes model-specific register programming. For power license events, perf counts package/core throttling-license cycles or occurrences through normal programmable counters.

## State and Persistence Behavior

The JSON persists event aliases and encodings. Counts live only in active perf sessions and hardware counters. Deprecated status is persistent compatibility metadata. The offcore response masks are persistent source data and represent the semantic boundary between full, partial, and generic streaming-write events.

## Dependencies and Integration Points

This file integrates with perf's Alder Lake event table generation, hybrid PMU routing, `perf list`, power/performance throttling analysis, assist diagnostics, LBR-related profiling, and offcore streaming-write metrics. It depends on kernel PMU support for the listed core and atom encodings and on offcore response MSR support for `OCR` events.

## Risks

The catch-all nature of the file makes discoverability and metric dependencies easy to miss. Deprecated `LBR_INSERTS.ANY` should not be preferred by new metrics. Streaming-write events rely on MSR filters and can silently change meaning if masks are wrong. `CORE_POWER.LICENSE_*` events can be platform-sensitive and may need careful interpretation under frequency scaling, turbo, thermal throttling, and power-limit policies.

## Test Signals

Validation should cover schema parsing, `perf list` visibility, deprecation display, offcore MSR encoding checks for streaming-write aliases, and smoke measurements on workloads that trigger assists, page faults, power-license transitions, and non-temporal or streaming stores. Metrics using this file should be tested for both core and atom PMU availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlake/other.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlake/pipeline.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlake/pipeline.json

## Purpose

This 208-entry file is the largest Alder Lake event catalog in the group. It defines pipeline, branch, clock, topdown, uop, reservation-station, machine-clear, serialization, arithmetic divider, load-block, and retirement events for perf. It supplies the raw event aliases behind many topdown and pipeline-efficiency metrics. The hybrid split is 121 `cpu_core` entries and 87 `cpu_atom` entries.

## Important APIs, Types, and Data

The file uses the standard perf event object fields plus `CounterMask`, `Deprecated`, `EdgeDetect`, `Invert`, `MSRIndex`, and `MSRValue`. It has 22 deprecated entries, 36 counter-mask records, five edge-detect records, six inverted records, and two MSR-backed records. Major families include `ARITH`, `BR_INST_RETIRED`, `BR_MISP_RETIRED`, `CPU_CLK_UNHALTED`, `CYCLE_ACTIVITY`, `EXE_ACTIVITY`, `INST_RETIRED`, `INT_MISC`, `INT_VEC_RETIRED`, `LD_BLOCKS`, `LSD`, `MACHINE_CLEARS`, `RESOURCE_STALLS`, `RS`, `RS_EMPTY`, `SERIALIZATION`, `TOPDOWN`, `TOPDOWN_BAD_SPECULATION`, `TOPDOWN_BE_BOUND`, `TOPDOWN_FE_BOUND`, `TOPDOWN_RETIRING`, `UOPS_EXECUTED`, `UOPS_ISSUED`, and `UOPS_RETIRED`.

Core-side topdown events include slot accounting such as `TOPDOWN.SLOTS`, `TOPDOWN.BACKEND_BOUND_SLOTS`, `TOPDOWN.BAD_SPEC_SLOTS`, `TOPDOWN.BR_MISPREDICT_SLOTS`, and `TOPDOWN.MEMORY_BOUND_SLOTS`. Atom-side topdown families expose issue-slot categories for frontend bound, backend bound, bad speculation, and retiring. Branch families include both generic and specific taken, conditional, indirect, call, return, and mispredict variants.

## Control Flow

The file is declarative. Perf parses it into alias descriptors, then routes event requests by PMU unit. The runtime measurement flow varies by qualifier: normal records program event select/umask, counter-mask records require threshold configuration, edge/invert records change predicate semantics, and MSR-backed records require selector MSR programming. Topdown metrics combine these aliases with formulas from metric files to compute hierarchy percentages.

## State and Persistence Behavior

The persistent state is the alias set, event encodings, deprecation markers, sampling periods, and topdown vocabulary. Runtime counter state is in PMU hardware and perf session data. Deprecated entries are retained for compatibility but should not drive new metric formulas. Clock events such as `CPU_CLK_UNHALTED.*` are foundational normalization inputs, so changes to their encodings have broad downstream impact.

## Dependencies and Integration Points

This catalog integrates with perf's generated pmu-events tables, `perf stat`, `perf record`, `perf list`, branch analysis, topdown metric formulas, hybrid PMU routing, and metric grouping. It depends on kernel support for Alder Lake fixed and programmable counters, topdown slot events, branch retired/mispred retired events, counter masks, edge detect, and invert semantics. It also provides dependencies for `metricgroups.json` topdown/TMA groups and the adjacent metric expression files.

## Risks

The highest risk is hybrid semantic mismatch: core and atom topdown events use different names and counting domains, so formulas must not blindly combine them. Deprecated branch and divider aliases can preserve old workflows but may produce inconsistent guidance compared with replacement names. Counter-mask/invert events are easy to misinterpret as raw counts. Topdown slot accounting is sensitive to SMT, halted cycles, fixed-counter availability, and multiplexing. Duplicate event names across units require perf to select the intended PMU.

## Test Signals

Tests should include JSON parsing, generated table compilation, `perf list` coverage, and encoding checks for representative branch, clock, topdown, uop, machine-clear, and divider events. Runtime smoke tests should include branch-heavy, branch-mispredict-heavy, divider-heavy, vector/integer pipeline, spin-wait, and backend-stall workloads. Metric tests should verify topdown level percentages are sane, sum constraints hold where expected, and unavailable unit-specific aliases are reported clearly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlake/pipeline.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlake/uncore-interconnect.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlake/uncore-interconnect.json

## Purpose

This 11-entry file describes Alder Lake uncore arbitration/interconnect events for perf. All entries use unit `ARB` and `PerPkg: 1`, meaning they represent package-level uncore activity rather than per-logical-CPU core PMU events. The catalog measures coherency tracker requests, data occupancy and requests, IFA occupancy, request tracker occupancy, demand-read tracker requests, and aggregate tracker occupancy/requests.

## Important APIs, Types, and Data

The schema uses `EventName`, `EventCode`, `UMask`, `Counter`, `Unit`, `PerPkg`, and `BriefDescription`, with optional `Deprecated` and `Experimental`. Event families include `UNC_ARB_COH_TRK_REQUESTS`, `UNC_ARB_DAT_OCCUPANCY`, `UNC_ARB_DAT_REQUESTS`, `UNC_ARB_IFA_OCCUPANCY`, `UNC_ARB_REQ_TRK_OCCUPANCY`, `UNC_ARB_REQ_TRK_REQUEST`, `UNC_ARB_TRK_OCCUPANCY`, and `UNC_ARB_TRK_REQUESTS`. Two entries are deprecated. The `Counter` field is limited to uncore counters `0,1`.

## Control Flow

The file is declarative. Perf parses it into uncore PMU aliases. At runtime, requests for these aliases bind to package-level `ARB` PMU instances rather than `cpu_core` or `cpu_atom`. Because the events are per-package, perf aggregation and display flow differs from per-thread or per-core events; results should be interpreted at socket/package scope.

## State and Persistence Behavior

The JSON persists uncore event names and encodings. Runtime state is held in uncore PMU counters, usually shared by all CPUs in the package. `PerPkg` is important persistent metadata because it tells tooling and users that counts should not be multiplied by active CPUs or interpreted as per-thread measurements. Deprecated markers preserve compatibility while discouraging new use.

## Dependencies and Integration Points

This file integrates with perf's uncore PMU event handling, `perf list` uncore aliases, package-level bandwidth/coherency analysis, and any metrics that use arbitration occupancy or request counts. It depends on kernel exposure of the Alder Lake ARB uncore PMU and proper package aggregation. It is adjacent to `uncore-memory.json`, which supplies memory-controller activity; together they describe off-core traffic pressure.

## Risks

Uncore PMU names and availability can vary by platform, BIOS, and kernel. Per-package events can be misread when measured alongside per-core events, especially under CPU filtering. Deprecated entries should not appear in new metric formulas without explicit compatibility reasons. Limited counters can cause scheduling conflicts if many uncore events are requested together. Occupancy events may require normalization by cycles or requests before they are actionable.

## Test Signals

Validation should include JSON parsing, uncore alias generation, `perf list` visibility under the ARB PMU, and smoke `perf stat` runs that generate memory/coherency traffic. Tests should check package aggregation behavior, counter scheduling with only counters 0 and 1, and deprecation handling for the two deprecated ARB records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlake/uncore-interconnect.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlake/uncore-memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlake/uncore-memory.json

## Purpose

This 25-entry catalog defines Alder Lake uncore memory-controller events. It includes free-running read/write CAS counters for memory controllers 0 and 1, standard integrated-memory-controller request and CAS counts, activation counts, clock ticks, page empty/hit/miss classifications, thermal warm/hot events, precharge/page-miss counts, prefetch reads, and virtual-channel read/write request counts. The file is package-level memory subsystem data for perf.

## Important APIs, Types, and Data

Entries use `EventName`, `EventCode`, `UMask`, `Counter`, `Unit`, `PerPkg`, `BriefDescription`, and optional `PublicDescription`. Units are `iMC` for 21 normal memory-controller events plus `imc_free_running_0` and `imc_free_running_1` for four free-running controller-specific counters. All records are `PerPkg: 1`. Families include `UNC_M_CAS_COUNT_*`, `UNC_M_ACT_COUNT_*`, `UNC_M_DRAM_PAGE_*`, `UNC_M_DRAM_THERMAL_*`, `UNC_M_PREFETCH_RD`, `UNC_M_PRE_COUNT_*`, and `UNC_M_VC*`.

## Control Flow

Perf ingests the JSON as uncore event metadata and exposes package-level memory-controller aliases. At runtime, normal `iMC` events are programmed through memory-controller PMU counters, while `imc_free_running_0/1` entries use free-running counter units with fixed counter `0`. Aggregation is package-level, not per-thread. Users or metrics often normalize CAS counts to bytes by multiplying by cache-line width or compare read/write/page events to memory bandwidth and locality expectations.

## State and Persistence Behavior

The persistent state is the mapping from uncore memory aliases to event encodings and units. Runtime counts persist only for the duration of the perf session and are shared across the package. Free-running counters may have different reset/read semantics from normal programmable counters, so the unit distinction is part of the persistent behavior contract. `PerPkg` prevents accidental per-CPU interpretation.

## Dependencies and Integration Points

This file integrates with perf uncore support, memory-bandwidth metrics, DRAM page-locality analysis, thermal diagnostics, and package-level `perf stat` workflows. It depends on kernel support for Alder Lake iMC and imc free-running PMUs. It complements core memory/cache events by measuring actual controller traffic rather than core-side misses or offcore request filters.

## Risks

Uncore memory PMU availability may vary by SKU, firmware, and kernel. Free-running counters and programmable iMC counters have different scheduling and overflow behavior. CAS-to-bandwidth formulas must account for the 64-byte request granularity described by the free-running events and should avoid double-counting controller 0 and 1. Package-level counts are vulnerable to noise from unrelated processes and other cores. Thermal events can be sparse and platform-policy dependent.

## Test Signals

Validation should include JSON parsing, `perf list` uncore-memory aliases, smoke bandwidth tests with streaming reads and writes, comparison of read/write CAS counts against expected bytes, page hit/miss sensitivity tests, and checks that free-running controller units are exposed separately from normal `iMC` events. Aggregation tests should verify one package-level result per package rather than per logical CPU.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlake/uncore-memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlake/uncore-other.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlake/uncore-other.json

## Purpose

This one-entry file defines the Alder Lake package-level uncore clock event `UNC_CLOCK.SOCKET`. It describes a 48-bit fixed counter that counts UCLK cycles. The event provides a timing/normalization source for uncore measurements.

## Important APIs, Types, and Data

The single event object uses `EventName`, `EventCode`, `Counter`, `Unit`, `PerPkg`, and `BriefDescription`. `EventCode` is `0xff`, `Counter` is `FIXED`, `Unit` is `CLOCK`, and `PerPkg` is `1`. Unlike programmable event catalogs, this record points at a fixed package-level uncore counter rather than a selectable event/umask pair.

## Control Flow

Perf parses the record into an uncore alias. At runtime, selecting `UNC_CLOCK.SOCKET` binds to the uncore clock PMU's fixed counter and reads package-level UCLK cycles for the measurement interval. Metrics can use it to normalize uncore occupancy, request, or memory-controller counts.

## State and Persistence Behavior

The persistent state is the alias and fixed-counter metadata. Runtime state is the hardware fixed counter value, which is package-scoped and may be read over an interval. The 48-bit width matters for long-running sessions because wrap handling must be correct in the kernel/perf read path.

## Dependencies and Integration Points

This file integrates with perf's uncore PMU support, package-level metric normalization, `perf list`, and uncore interconnect/memory analyses. It depends on kernel exposure of the Alder Lake `CLOCK` uncore unit and correct fixed-counter read semantics.

## Risks

The main risks are incorrect aggregation, counter wrap in long intervals, and assuming UCLK is equivalent to core frequency or invariant TSC. Because it is package-level, CPU filters and per-thread interpretations are misleading. If the kernel does not expose the `CLOCK` unit on a platform, metrics depending on this alias must degrade clearly.

## Test Signals

Validation should include JSON parsing, `perf list` visibility, smoke reads over known sleep intervals, wrap-safe long-duration reads where practical, and metric tests that use `UNC_CLOCK.SOCKET` to normalize uncore occupancy or request events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlake/uncore-other.json -->
