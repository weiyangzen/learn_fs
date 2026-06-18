# subset-b-006704 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/pantherlake/cache.json -->
## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/pantherlake/cache.json

**Purpose:** Panther Lake cache topic with 151 PMU event records for data-cache replacement, L1D miss pressure, L2 line/request accounting, longest-latency cache references, memory-bound stalls, retired memory load/store/uop classifications, load source attribution, offcore/OCR responses, software prefetches, bus locks, and atom frontend-bound I-cache slots. The file is declarative input for perf's x86 PMU event table generator rather than executable runtime logic.

**Schema and important records:** Each array object is a perf PMU event definition keyed primarily by `EventName`, `EventCode`, `UMask`, and `Unit`. Most records also carry `Counter`, `SampleAfterValue`, and human-readable descriptions. `CounterMask` is used for cycle-presence variants such as `L1D_PENDING.LOAD_CYCLES` and `OFFCORE_REQUESTS_OUTSTANDING.CYCLES_*`. `Data_LA` marks load-address-capable precise events in the `MEM_INST_RETIRED.*`, `MEM_LOAD_RETIRED.*`, and latency families. `MSRIndex`/`MSRValue` appear on OCR/offcore response selectors and on atom load-latency threshold events. The file intentionally contains duplicate `EventName` values split by `Unit`, for example `L2_REQUEST.ALL`, `L2_REQUEST.MISS`, `LONGEST_LAT_CACHE.MISS`, `LONGEST_LAT_CACHE.REFERENCE`, `OCR.DEMAND_DATA_RD.ANY_RESPONSE`, and `OCR.DEMAND_RFO.ANY_RESPONSE` have separate `cpu_atom` and `cpu_core` encodings.

**Control flow and integration:** At build time, perf's PMU event tooling parses this JSON, validates the object schema, and emits Panther Lake `pmu_event` table entries under the cache topic. At runtime, `perf list` exposes the names and descriptions, while `perf stat`/`perf record` convert fields into raw event selectors, counter constraints, offcore MSR programming, PEBS/load-address attributes, and sample periods. Core and atom unit separation is the key routing mechanism on Panther Lake hybrid systems; consumers must preserve the `Unit` field instead of treating `EventName` as globally unique.

**State and persistence:** The file stores static hardware metadata only. Persistent state consists of event selector encodings, counter allow-lists, OCR MSR values, and default sample periods baked into generated perf tables. Measurement counts, samples, PEBS records, and offcore MSR programming are session-scoped runtime state controlled by perf and the kernel PMU driver.

**Dependencies:** Depends on the Panther Lake core/atom PMU model, perf's x86 JSON schema, the `counter.json` counter counts, and the kernel's ability to program core, atom, OCR, PEBS/load-latency, and offcore outstanding events. Downstream metric files and user scripts may refer to exact names such as `MEM_LOAD_RETIRED.L3_MISS`, `OFFCORE_REQUESTS.DEMAND_DATA_RD`, `L2_RQSTS.REFERENCES`, and `TOPDOWN_FE_BOUND.ICACHE`.

**Risks:** Duplicate event names across units are easy to collapse accidentally in tooling that indexes only by name. OCR records are high risk because `MSRIndex`/`MSRValue` mistakes can produce plausible but wrong offcore counts. Several records use aliases (`L2_REQUEST.*` and `L2_RQSTS.*`) where renaming or deduplication can break compatibility. Threshold events require matching MSR threshold values; wrong encodings silently move events between latency buckets. Some records have sparse descriptions or no `UMask` where the event code itself is meaningful, so schema validation must not assume every event has all optional fields.

**Test signals:** Validate JSON syntax and schema with the perf PMU event build. Confirm generated tables keep all 151 cache records and preserve both `cpu_core` and `cpu_atom` duplicates. `perf list cache` on Panther Lake should show the topic names with descriptions. Runtime smoke tests should cover ordinary raw events, counter-mask cycle variants, PEBS/load-address events, and OCR/offcore events that program `0x1a6/0x1a7`. Metric tests should check that aliases and exact event names referenced by Panther Lake metrics remain resolvable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/pantherlake/cache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/pantherlake/counter.json -->
## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/pantherlake/counter.json

**Purpose:** Panther Lake counter topology metadata. It declares how many fixed and generic counters perf should expect for `cpu_atom`, `cpu_core`, and `iMC` PMU units. This small file informs scheduling capacity and validation for the larger event JSON files in the same Panther Lake directory.

**Schema and important records:** The file is a three-object JSON array. `cpu_atom` declares `CountersNumFixed: 7` and `CountersNumGeneric: 8`; `cpu_core` declares `CountersNumFixed: 4` and `CountersNumGeneric: 10`; `iMC` declares `CountersNumFixed: 0` and `CountersNumGeneric: 5`. The fields are numeric strings, matching the perf pmu-events convention used by generated tables.

**Control flow and integration:** Perf's event generation reads this as unit-level metadata rather than as countable events. The resulting tables help perf understand available counter resources when it schedules events from `cache.json`, `frontend.json`, `floating-point.json`, `memory.json`, `other.json`, and any uncore/iMC topic files. The unit names must match the `Unit` fields used by event definitions.

**State and persistence:** Static topology data only. No runtime counters are created here; the generated value persists as compiled metadata and is compared with runtime PMU discovery when perf schedules events.

**Dependencies:** Depends on Panther Lake hybrid PMU naming (`cpu_core`, `cpu_atom`) and integrated memory-controller PMU naming (`iMC`). It must remain consistent with event `Counter` allow-lists: atom events commonly list counters `0..7`, core events list `0..9`, and iMC events rely on the uncore memory-controller capacity.

**Risks:** Wrong counts can cause perf to over-schedule events, reject valid groups, or produce misleading multiplexing behavior. Unit-name drift is especially risky because all nearby event files depend on exact string matching. Treating the string values as free-form text instead of numeric metadata can hide malformed counter declarations.

**Test signals:** JSON/schema validation should confirm exactly three unit records and numeric string counter counts. Generated PMU tables should expose counter capabilities for `cpu_atom`, `cpu_core`, and `iMC`. Runtime grouped `perf stat` tests should verify that core and atom events can be scheduled within their declared generic-counter limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/pantherlake/counter.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/pantherlake/floating-point.json -->
## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/pantherlake/floating-point.json

**Purpose:** Panther Lake floating-point and vector execution event topic with 40 PMU records. It covers FP divider activity, FP assists, core vector-arithmetic dispatch ports, retired FP arithmetic operation classes, atom retired FP instruction/FLOP classes, atom FP/vector-integer execution ports, and FP assist machine clears.

**Schema and important records:** Standard PMU fields include `EventName`, `EventCode`, `UMask`, `Unit`, `Counter`, `CounterMask`, `SampleAfterValue`, and descriptions. `ARITH.FPDIV_ACTIVE` is intentionally duplicated for atom and core with different event codes and semantics. Core `FP_ARITH_OPS_RETIRED.*` records classify scalar, vector, 128-bit, 256-bit, single, double, and combined FLOP-width groups, with descriptions warning that DAZ/FTZ MXCSR flags should be set and that some FMA/DPP instructions count as multiple operations. Atom records use `FP_FLOPS_RETIRED.*`, `FP_INST_RETIRED.*`, and `FP_VINT_UOPS_EXECUTED.*` to expose equivalent but unit-specific accounting.

**Control flow and integration:** The perf generator converts each object into a Panther Lake floating-point event. Runtime selection is unit-routed: core users see core FP arithmetic and dispatch events, atom users see atom FP instruction/FLOP and execution-port events. Counter masks on divider active events make them cycle-style occupancy/presence measurements. The records integrate with perf's topic filtering (`perf list floating-point`) and with metrics that estimate FP intensity, vector width mix, divide pressure, and assist overhead.

**State and persistence:** Static event metadata. Runtime FP counts depend on programmed counters and workload instruction mix. There is no local persistence beyond generated PMU tables and default sample periods.

**Dependencies:** Depends on Panther Lake core/atom FP pipelines and perf's x86 event parser. Correct interpretation also depends on architectural state noted in descriptions, especially MXCSR DAZ/FTZ flags for core `FP_ARITH_OPS_RETIRED.*`. Counter availability comes from `counter.json`.

**Risks:** FLOP-style events are easy to misinterpret as instruction counts because vector width and FMA/DPP weighting differ by record. Core and atom use different event families, so cross-unit comparisons need normalization. Missing or altered descriptions would remove important caveats about DAZ/FTZ and multi-count operations. Duplicate `ARITH.FPDIV_ACTIVE` must not be collapsed across units.

**Test signals:** Build-time JSON validation should preserve all 40 records. `perf list floating-point` should show both core and atom families. Runtime smoke tests can run scalar, vector, and divide-heavy loops and verify that corresponding retire/dispatch/divider counters move. Metric tests should check any FP throughput formulas against vector-width weighting and atom/core unit selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/pantherlake/floating-point.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/pantherlake/frontend.json -->
## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/pantherlake/frontend.json

**Purpose:** Panther Lake frontend event topic with 56 records for branch-address clears, decode and microcode-sequencer activity, DSB/MITE transitions, frontend-retired latency attribution, instruction-cache and instruction-TLB misses, IDQ delivery paths, frontend bubbles, and atom microsequencer decoded events.

**Schema and important records:** The file uses standard event fields plus several precise-distribution selectors. `FRONTEND_RETIRED.*` core records share `EventCode: 0xc6`, `UMask: 0x3`, and use `MSRIndex: 0x3F7` with distinct `MSRValue` encodings to tag retired instructions by frontend source or latency threshold. Atom records include direct `FRONTEND_RETIRED.ITLB_MISS` and `FRONTEND_RETIRED_SOURCE.*` definitions without the same MSR selector pattern. `IDQ.*` and `IDQ_BUBBLES.*` use `CounterMask`, `Invert`, and `EdgeDetect` for cycle, switch, and starvation-style measurements. `BACLEARS.ANY` is duplicated across atom and core with different event codes and meanings.

**Control flow and integration:** Perf builds these records into the Panther Lake frontend topic. At runtime, plain events program event code/umask pairs, while frontend-retired core events also program MSR-based selector values. These events feed top-down frontend-bound analysis, instruction-cache miss diagnosis, branch predictor resteer analysis, and DSB/MITE/MS delivery breakdowns. The `Unit` field controls whether the core or atom frontend pipeline encoding is used.

**State and persistence:** Static JSON metadata only. Generated perf tables persist event selectors and MSR values; runtime state consists of programmed counters and optional frontend-retired tagging controlled by the kernel PMU driver.

**Dependencies:** Depends on Panther Lake frontend PMU encodings, PEBS/PDist-style retired tagging support, perf's MSR selector handling, and counter availability from `counter.json`. It also integrates with top-down metrics that use `IDQ_BUBBLES.*`, `FRONTEND_RETIRED.*`, and instruction-cache events.

**Risks:** Frontend-retired records are high risk because many names differ only by `MSRValue`; a wrong selector will still count but attribute stalls to the wrong source or latency threshold. `CounterMask`, `Invert`, and `EdgeDetect` fields must survive generation for cycle and transition events. Duplicate names across atom/core must be retained by unit. Several descriptions are short, so downstream documentation may need to rely on names and encodings rather than prose.

**Test signals:** Validate JSON and generated table count for all 56 records. `perf list frontend` should expose BACLEARS, DSB/MITE, frontend-retired, ICACHE, IDQ, and MS_DECODED names. Runtime tests should include instruction-cache pressure, branch-heavy code, and microcode-heavy instructions to confirm representative event movement. A build or parser test should assert that all `MSRIndex: 0x3F7` records preserve their intended `MSRValue`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/pantherlake/frontend.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/pantherlake/memory.json -->
## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/pantherlake/memory.json

**Purpose:** Panther Lake memory topic with 29 records focused on atom load-head stalls, memory-ordering machine clears, core sampled load latency thresholds, store PEBS sampling, misaligned page splits, OCR demand data/RFO L3-miss and DRAM responses, and core offcore L3-miss demand-data outstanding/request events.

**Schema and important records:** Atom `LD_HEAD.*` records use `EventCode: 0x05` with different umasks to distinguish L1 misses, WCB-full conditions, and retirement-stalled variants. `MACHINE_CLEARS.MEMORY_ORDERING` is duplicated for atom and core. `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_*` core records use `Data_LA: 1`, `MSRIndex: 0x3F6`, threshold-specific `MSRValue`, and varied `SampleAfterValue` defaults; they count randomly selected loads above thresholds from 4 to 2048 cycles. `MEM_TRANS_RETIRED.STORE_SAMPLE` is a store-latency PEBS trigger on counters 0 and 1. OCR records use `MSRIndex: 0x1a6,0x1a7` with unit-specific `MSRValue` encodings for atom event `0xB7` and core events `0x2A,0x2B`.

**Control flow and integration:** The perf generator emits these into the Panther Lake memory topic. Runtime use splits into ordinary stall/clear counters, PEBS load/store sampling, OCR offcore response selectors, and offcore outstanding counters. The latency-threshold records depend on programming the threshold MSR, and OCR records depend on offcore response MSRs. These records complement `cache.json`: this file emphasizes sampled latency and L3-miss/DRAM response attribution, while `cache.json` contains broader cache-level request and retired-load families.

**State and persistence:** Static metadata only. Generated tables persist threshold and OCR selector values. Runtime state includes programmed PEBS threshold MSRs, offcore response MSRs, sampled data addresses, and measured counter values for each perf session.

**Dependencies:** Depends on Panther Lake core and atom PMU support, PEBS load/store latency facilities, OCR/offcore MSR programming, and counter limits from `counter.json`. Descriptions reference Intel SDM store-latency facility behavior; kernel support must expose the required precise sampling capabilities.

**Risks:** Threshold records are high risk because `MSRValue` controls the bucket and `SampleAfterValue` differs widely to tune sampling rates. OCR atom and core records have the same event names but different event codes and selector values; collapsing by name or copying selectors between units would corrupt measurements. The core load-latency records report dispatch-to-completion latency, not pure memory latency, which can mislead analysis if omitted from documentation.

**Test signals:** JSON/schema validation should preserve all 29 records and all threshold MSR values. Runtime PEBS smoke tests should exercise `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_128` and `STORE_SAMPLE` with data-address capture. OCR tests should verify both atom and core L3-miss/DRAM selectors program successfully. `perf list memory` should show load-head, machine-clear, latency, misalignment, OCR, and offcore outstanding events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/pantherlake/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/pantherlake/other.json -->
## sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/pantherlake/other.json

**Purpose:** Panther Lake miscellaneous event topic with five records that do not fit the cache, frontend, memory, or floating-point buckets. It covers hardware/page-fault assists, streaming-write OCR responses, atom BTB clears, and core uncore-request backpressure.

**Schema and important records:** `ASSISTS.HARDWARE` and `ASSISTS.PAGE_FAULT` are core events on `EventCode: 0xc1` with different umasks. `OCR.STREAMING_WR.ANY_RESPONSE` is a core offcore/OCR event using `EventCode: 0x2A,0x2B`, `MSRIndex: 0x1a6,0x1a7`, and `MSRValue: 0x10800`. `PREDICTION.BTCLEAR` is an atom branch-prediction event on event `0xe8`. `XQ.FULL` is a core cycle event with `CounterMask: 1` for cycles where uncore cannot accept further requests.

**Control flow and integration:** Perf's PMU event build places these records under the Panther Lake `other` topic. Runtime handling is mixed: assists and BTCLEAR are ordinary event-code/umask counters, `OCR.STREAMING_WR.ANY_RESPONSE` requires OCR MSR selector programming, and `XQ.FULL` uses counter-mask cycle counting. These events provide supporting diagnostics for hardware assists, streaming-store traffic, BTB behavior, and uncore queue pressure.

**State and persistence:** Static event metadata. Generated perf tables persist the raw selector fields and sample periods. Runtime state consists of programmed counters, OCR MSR state for streaming writes, and per-session counts.

**Dependencies:** Depends on Panther Lake core/atom PMU encodings and OCR support. `XQ.FULL` complements cache and memory offcore events by indicating uncore request acceptance pressure. Assist events overlap conceptually with floating-point assist events but intentionally count broader hardware and page-fault assist categories.

**Risks:** The small file can be overlooked by topic-based validation, leaving miscellaneous but useful events missing from generated tables. `ASSISTS.HARDWARE` has a broad definition and should not be compared directly with narrow FP assists. `OCR.STREAMING_WR.ANY_RESPONSE` has the same OCR selector risk as cache/memory OCR records. `XQ.FULL` requires `CounterMask` retention to remain a cycle-presence event.

**Test signals:** Validate all five records appear under `perf list other` for Panther Lake. Runtime smoke tests should check ordinary assist counters, atom BTCLEAR availability, OCR streaming-write selector programming, and `XQ.FULL` movement under memory/uncore pressure. Schema tests should retain `CounterMask` and OCR `MSRIndex`/`MSRValue` fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/pantherlake/other.json -->
