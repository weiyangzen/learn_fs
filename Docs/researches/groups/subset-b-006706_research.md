# subset-b-006706 Rocket Lake perf PMU event research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/rocketlake/other.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/rocketlake/other.json

## Purpose
This JSON file contributes five Rocket Lake x86 PMU event aliases in the `other` topic for Linux perf's generated PMU event tables. It covers two distinct areas that do not fit cleanly in pipeline, cache, or virtual-memory topics: core power/turbo license level accounting and offcore response counting for miscellaneous and streaming-write transactions.

At build time, `tools/perf/pmu-events/jevents.py` reads this JSON together with the rest of `arch/x86/rocketlake`, converts each object into generated `struct pmu_event` data, and links the generated tables into perf. At runtime, the x86 mapfile entry `GenuineIntel-6-A7,v1.04,rocketlake,core` selects this directory for Rocket Lake CPUs, allowing users and metric expressions to reference event names symbolically.

## Data shape and important fields
The file is a JSON array of 5 objects. The observed keys are `EventName`, `BriefDescription`, `PublicDescription`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `MSRIndex`, and `MSRValue`.

The first three entries are `CORE_POWER.LVL0_TURBO_LICENSE`, `CORE_POWER.LVL1_TURBO_LICENSE`, and `CORE_POWER.LVL2_TURBO_LICENSE`. They all use event code `0x28`, counters `0,1,2,3`, and distinct umasks to distinguish baseline/non-AVX, AVX2-like, and AVX512-like turbo license levels. Their sample period is `200003`.

The remaining entries are `OCR.OTHER.ANY_RESPONSE` and `OCR.STREAMING_WR.ANY_RESPONSE`. They use event codes `0xB7, 0xBB`, counters `0,1,2,3`, and MSR programming through `MSRIndex` `0x1a6,0x1a7`. `jevents.py` maps these MSR indexes to `offcore_rsp=` encodings, so these objects are not just simple event/umask aliases; they require correct offcore response register programming.

## Control flow and integration
There is no executable control flow in the file. The effective flow is declarative:

1. `jevents.py` parses each JSON object into a `JsonEvent`.
2. Event fields are normalized into perf event strings, including `event=`, `umask=`, `period=`, and offcore response fields derived from `MSRIndex` and `MSRValue`.
3. Generated C tables expose the aliases through the `pmu_event` API in `pmu-events.h`.
4. Perf commands such as `perf list`, `perf stat -e CORE_POWER.LVL0_TURBO_LICENSE`, and perf metric evaluation can resolve these aliases on Rocket Lake.

The file also feeds `rkl-metrics.json`: metrics such as turbo license utilization and streaming-store bottleneck estimates reference `CORE_POWER.LVL*_TURBO_LICENSE` and `OCR.STREAMING_WR.ANY_RESPONSE`.

## State, persistence, and dependencies
The file is static source data. It has no runtime persistence, no mutable state, and no direct I/O. Its persisted effect is the generated `pmu-events.c` content produced during perf builds. It depends on the perf PMU JSON schema and on x86 event encoding semantics for `EventCode`, `UMask`, programmable counter masks, sample periods, and offcore response MSR values.

The offcore events depend on the generator's `lookup_msr()` handling for `0x1A6` and `0x1A7`. A schema-valid but semantically wrong MSR value would build successfully yet count the wrong offcore response class.

## Risks
The main risk is semantic drift between Intel event definitions and the encoded values. The turbo license events influence power and throttling metrics, so incorrect umasks would mislead turbo/AVX utilization analysis. The OCR entries carry higher risk than simple core events because the event code list, MSR index list, and MSR value must remain consistent.

Another risk is cross-file dependency breakage. `rkl-metrics.json` references `OCR.STREAMING_WR.ANY_RESPONSE` and all three `CORE_POWER` aliases. Renaming or removing these events without updating metrics will leave perf metrics unresolved even though this file remains valid JSON.

## Test signals
Useful checks are: `jq empty other.json` for JSON syntax; a perf `jevents` build to ensure the offcore encodings are accepted; `perf list --json` on a Rocket Lake-capable build to confirm the five aliases appear; and metric parser tests that resolve formulas using `CORE_POWER.LVL0_TURBO_LICENSE`, `CORE_POWER.LVL1_TURBO_LICENSE`, `CORE_POWER.LVL2_TURBO_LICENSE`, and `OCR.STREAMING_WR.ANY_RESPONSE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/rocketlake/other.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/rocketlake/pipeline.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/rocketlake/pipeline.json

## Purpose
This JSON file defines Rocket Lake core pipeline PMU events for Linux perf. It supplies the symbolic event aliases used for instruction retirement, branch retirement and misprediction, clocks, front-end/back-end activity, dispatch port utilization, issued/executed/retired uops, resource stalls, machine clears, assists, divider activity, and topdown slot accounting.

The file is one of the central event providers for `rkl-metrics.json`: many Topdown Microarchitecture Analysis metrics use its aliases directly, including `TOPDOWN.SLOTS`, `UOPS_RETIRED.SLOTS`, `BR_MISP_RETIRED.*`, `CYCLE_ACTIVITY.*`, `EXE_ACTIVITY.*`, and `UOPS_DISPATCHED.*`.

## Data shape and important fields
The file is a JSON array of 95 event objects. The observed keys are `EventName`, `BriefDescription`, `PublicDescription`, `EventCode`, `UMask`, `Counter`, `CounterMask`, `Invert`, `EdgeDetect`, and `SampleAfterValue`.

The event-name families are:

- `ARITH`: 2 divider activity events.
- `ASSISTS`: 1 microcode assist event.
- `BR_INST_RETIRED`: 9 retired branch classifications.
- `BR_MISP_RETIRED`: 8 mispredicted branch classifications.
- `CPU_CLK_UNHALTED`: 7 clock events, including fixed-counter aliases.
- `CYCLE_ACTIVITY`: 7 load/memory outstanding and stall events.
- `EXE_ACTIVITY`: 5 port-utilization and store-bound events.
- `INST_RETIRED`: 5 retired instruction events.
- `INT_MISC`: 5 recovery, clear/resteer, and uop-dropping events.
- `UOPS_DISPATCHED`: 7 execution port groups.
- `UOPS_EXECUTED`: 12 executed-uop and occupancy events.
- `UOPS_ISSUED` and `UOPS_RETIRED`: 3 events each.
- Smaller families for decode, LSD, machine clears, load blocking, resource stalls, reservation station emptiness, and topdown slots.

Most entries target programmable counters `0,1,2,3,4,5,6,7`; 14 entries are restricted to `0,1,2,3`; fixed counter aliases cover retired instructions and clocks. The file uses `CounterMask` on 29 entries, `Invert` on 6 entries, and `EdgeDetect` on 3 entries, which means tests must cover more than simple event-code/umask emission.

## Control flow and integration
The JSON is consumed by the generic perf PMU event generation flow:

1. `jevents.py` scans `arch/x86/rocketlake/pipeline.json` as a topic file.
2. Each object is converted into a `JsonEvent`; names, descriptions, topic, event encodings, counter constraints, cmasks, invert flags, edge-detect flags, and sample periods are emitted into generated C data.
3. `pmu-events.h` exposes the generated events through `pmu_events_table__for_each_event()` and `pmu_events_table__find_event()`.
4. Runtime perf command paths use the generated table selected by the x86 mapfile to resolve symbolic names.

There are no local functions or branches in the JSON file itself. The control behavior is in perf's parser and event scheduler. Counter restrictions and cmask/invert/edge flags alter how perf programs the PMU and how events can be grouped.

## State, persistence, and dependencies
The file is static declarative input. Its persistent artifact is generated perf event-table C code. It depends on the Rocket Lake PMU programming model, fixed counter availability, topdown slot support, and perf's JSON schema. It also depends on sibling event files because the metrics layer combines pipeline aliases with memory, frontend, cache, offcore, and virtual-memory aliases.

The file has no runtime state, but its event definitions influence perf's runtime PMU programming state when users request the aliases. Fixed-counter aliases such as `CPU_CLK_UNHALTED.THREAD`, `CPU_CLK_UNHALTED.REF_TSC`, and `INST_RETIRED.ANY` affect counter scheduling because they do not consume the same programmable counters as normal events.

## Risks
Incorrect event encodings here have broad blast radius because these events are foundational to TMA and common `perf stat` workflows. Errors in `TOPDOWN.SLOTS`, retired instruction counts, clocks, or branch events will distort high-level metrics rather than only one low-level counter.

Counter-mask and invert semantics are easy to break during maintenance. For example, occupancy-style or "cycles with at least N" events rely on `CounterMask`, and some pipeline utilization events rely on inverted threshold tests. A JSON syntax check will not catch a swapped cmask, missing invert flag, or bad fixed-counter designation.

Cross-file metric consistency is another risk. `rkl-metrics.json` references both present aliases and aliases from other Rocket Lake files. Renaming pipeline aliases or changing their case will break metric formulas because metric expressions match symbolic event names.

## Test signals
Useful signals include `jq empty pipeline.json`, full `jevents.py` generation, and perf's PMU event unit tests. Runtime-facing checks should include `perf list --json` to verify representative aliases from each family, plus `perf stat` smoke tests for fixed counters, programmable events, cmask/invert events, and topdown metrics. Metric parser tests should include formulas using `TOPDOWN.SLOTS`, `BR_MISP_RETIRED.ALL_BRANCHES`, `CYCLE_ACTIVITY.STALLS_MEM_ANY`, `EXE_ACTIVITY.BOUND_ON_STORES`, and `UOPS_RETIRED.SLOTS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/rocketlake/pipeline.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/rocketlake/rkl-metrics.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/rocketlake/rkl-metrics.json

## Purpose
This JSON file defines the Rocket Lake metric catalog for Linux perf. Unlike the event-topic JSON files, it does not program hardware counters directly. It defines named formulas, groups, thresholds, units, and constraints that perf's metric resolver evaluates from PMU event counts, MSR pseudo-events, topdown pseudo-events, constants, runtime helpers, and other metrics.

The file is the high-level analysis layer for Rocket Lake. It covers package/core C-state residency, SMI accounting, TSX transaction metrics, uncore frequency, memory bandwidth and latency estimates, instruction mix, branch behavior, frontend and backend bottlenecks, port utilization, floating-point/vector usage, TLB behavior, and multi-level Topdown Microarchitecture Analysis groups from L1 through L6.

## Data shape and important fields
The file is a JSON array of 243 metric objects. The observed keys are `MetricName`, `MetricGroup`, `MetricExpr`, `BriefDescription`, `PublicDescription`, `MetricThreshold`, `MetricConstraint`, `ScaleUnit`, `MetricgroupNoGroup`, and `DefaultMetricgroupName`.

Important characteristics:

- 219 metrics have no explicit `MetricConstraint`; 24 use `NO_GROUP_EVENTS`, preventing perf from forcing all referenced events into a single group.
- 151 metrics include `MetricThreshold`, which perf and consumers can use to highlight significant bottlenecks.
- 115 metrics use scale unit `100%`; C-state and TMA metrics commonly express fractions as percentages. Other units include SMI counts and cycles per transaction/elision.
- 12 metrics set `MetricgroupNoGroup`, and 4 set `DefaultMetricgroupName`.
- Metric groups are semicolon-separated classification tags, including `TopdownL1` through `TopdownL6`, `TmaL1`/`TmaL2`/`TmaL3mem`, `Backend`, `Frontend`, `MemoryBW`, `MemoryLat`, `Power`, `HPC`, `SMT`, `SoC`, `OS`, `transaction`, and issue-specific tags such as `tma_issueBW`, `tma_issueTLB`, and `tma_issueBM`.

Representative formulas show the range of expression dependencies:

- C-state residency divides `cstate_pkg@...@` or `cstate_core@...@` counters by `msr@tsc@`.
- Topdown L1 metrics use `topdown\-fe\-bound`, `topdown\-bad\-spec`, `topdown\-retiring`, and `topdown\-be\-bound`.
- Pipeline formulas combine event aliases such as `UOPS_RETIRED.SLOTS`, `TOPDOWN.SLOTS`, `BR_MISP_RETIRED.ALL_BRANCHES`, `CYCLE_ACTIVITY.STALLS_MEM_ANY`, and `EXE_ACTIVITY.BOUND_ON_STORES`.
- Memory formulas depend on `MEM_LOAD_RETIRED.*`, `L2_RQSTS.*`, `OFFCORE_REQUESTS_OUTSTANDING.*`, `DTLB_*`, `ITLB_*`, and uncore aliases such as `UNC_ARB_*`.
- Power formulas reference `CORE_POWER.LVL0_TURBO_LICENSE`, `CORE_POWER.LVL1_TURBO_LICENSE`, and `CORE_POWER.LVL2_TURBO_LICENSE` from `other.json`.
- Streaming-store analysis references `OCR.STREAMING_WR.ANY_RESPONSE` from `other.json`.

## Control flow and integration
The effective control flow is the perf metric-generation and metric-evaluation pipeline:

1. `jevents.py` parses metric objects into generated `struct pmu_metric` rows.
2. `MetricExpr` strings are parsed by the perf metric expression parser. The test file `pmu-events/metric_test.py` demonstrates supported arithmetic, comparisons, `min`/`max`, conditional `if ... else`, escaped event names, and event modifier syntax such as `cpu@event\,umask@`.
3. Generated metric tables are exposed through `pmu_metrics_table__for_each_metric()` and `pmu_metrics_table__find_metric()`.
4. Runtime perf resolves metric names, expands formulas into required events and nested metrics, applies constraints, schedules event groups, collects counts, and evaluates expressions.

This file has extensive dependency control flow through nested metric references. Many formulas are defined in terms of other `tma_*` metrics, so perf must resolve a dependency graph rather than a flat list of independent formulas.

## State, persistence, and dependencies
The file is static source data with no local persistence. Its build artifact is generated C metric-table data. Runtime state is external: perf creates event groups, reads PMU/MSR/sysfs counters, computes durations, detects features such as `#SMT_on`, `#num_dies`, or availability via `has_event(...)`, and evaluates expressions.

Dependencies are broad. The file references Rocket Lake event aliases from `pipeline.json`, `virtual-memory.json`, `other.json`, `uncore-interconnect.json`, and `uncore-other.json`, plus sibling event files outside this work item such as cache, memory, frontend, floating-point, offcore, and topdown-related categories. It also depends on perf's expression language, helper variables (`duration_time`, `#SMT_on`, `#num_dies`), pseudo-events (`cycles`, `cycles\-t`, `topdown\-*`), MSR events, cstate PMUs, and event availability guards.

## Risks
The main risk is unresolved or incorrectly grouped metric dependencies. The JSON itself can parse while a formula references a renamed event, a missing sibling event, or a helper unavailable on a particular system. Metrics with `NO_GROUP_EVENTS` constraints can also produce different scheduling behavior from grouped metrics, so constraint changes affect measurement validity.

Formula fragility is high because many expressions divide by other counters or nested metrics. Some formulas use `max(...)`, `min(...)`, and `if has_event(...) else ...` guards, but not every denominator is explicitly protected. Low-count workloads, unsupported events, disabled PMUs, or multiplexing can yield misleading percentages.

Another risk is cross-layer semantic drift. TMA metrics assume particular Rocket Lake slot, pipeline, memory, and uncore semantics. A local edit to one event file can silently change a metric's meaning. Conversely, adding a metric here without adding required event aliases in sibling JSON files breaks perf metric resolution.

## Test signals
Required baseline checks are `jq empty rkl-metrics.json`, a full `jevents.py` generation run, and perf metric parser tests. Stronger checks include running `metric_test.py`, verifying `perf list --json` includes representative `MetricName` rows and their groups, and running `perf stat -M` smoke tests for `tma_backend_bound`, `tma_frontend_bound`, `tma_memory_bound`, `tma_dtlb_load`, `tma_info_system_power`, `C6_Core_Residency`, and TSX metrics on hardware or a test harness with expected event availability.

Cross-file validation should extract all uppercase event references from `MetricExpr` and confirm they resolve somewhere in the Rocket Lake event set or in perf pseudo-event support. It should also check that thresholds and `ScaleUnit` values are preserved in generated `pmu_metric` rows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/rocketlake/rkl-metrics.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/rocketlake/uncore-interconnect.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/rocketlake/uncore-interconnect.json

## Purpose
This JSON file defines eight Rocket Lake uncore interconnect PMU event aliases for perf. The events describe arbitration/coherency tracker request counts and occupancy measurements for the uncore arbiter/data paths. They are used directly by users interested in SoC/interconnect behavior and indirectly by system-level memory and uncore metrics in `rkl-metrics.json`.

## Data shape and important fields
The file is a JSON array of 8 event objects. The observed keys are `EventName`, `BriefDescription`, `EventCode`, `UMask`, `Counter`, `Unit`, `PerPkg`, and `Experimental`.

The aliases are:

- `UNC_ARB_COH_TRK_REQUESTS.ALL`
- `UNC_ARB_DAT_OCCUPANCY.ALL`
- `UNC_ARB_DAT_OCCUPANCY.RD`
- `UNC_ARB_REQ_TRK_OCCUPANCY.DRD`
- `UNC_ARB_TRK_OCCUPANCY.ALL`
- `UNC_ARB_TRK_OCCUPANCY.RD`
- `UNC_ARB_TRK_REQUESTS.ALL`
- `UNC_ARB_TRK_REQUESTS.RD`

All entries use `Unit` `arb` and `PerPkg` `1`, marking them as package-level uncore events rather than per-logical-CPU core events. All entries have `Experimental` `1`, which signals that the definitions may be less stable or less generally supported than normal core aliases. They use uncore counters `0,1,2,3` with event codes such as `0x81`, `0x83`, and `0x84`, and umasks for all/read/demand-read variants.

## Control flow and integration
The file is declarative. `jevents.py` converts each object into a generated `pmu_event` entry with uncore PMU unit metadata. At runtime, perf matches the event's `Unit` to PMUs whose names wildcard-match the unit, exposes the aliases in `perf list`, and programs the relevant uncore arbiter PMU when the user or a metric requests them.

`rkl-metrics.json` references several of these names, including `UNC_ARB_COH_TRK_REQUESTS.ALL`, `UNC_ARB_DAT_OCCUPANCY.RD`, `UNC_ARB_TRK_OCCUPANCY.RD`, `UNC_ARB_TRK_REQUESTS.ALL`, and `UNC_ARB_TRK_REQUESTS.RD`. That creates a direct integration path from this file into memory bandwidth, latency, and SoC-level derived metrics.

## State, persistence, and dependencies
The file has no mutable local state. Its persisted build product is generated event-table data. Runtime state is in the uncore arbiter PMU counters, which are package-scoped and may be shared across CPUs. The `PerPkg` flag matters because aggregation semantics differ from per-thread or per-core events.

The file depends on Rocket Lake exposing an `arb` uncore PMU compatible with these event encodings. It also depends on perf's uncore PMU unit matching and on correct package aggregation in metric evaluation.

## Risks
The `Experimental` marker is the main risk signal. These counters may be unavailable, renamed by kernel PMU drivers, or not stable across steppings. Because the events are package-level, incorrect aggregation can double-count or under-count when metrics are collected per CPU instead of per package.

Metric formulas that combine core and uncore events can be hard to schedule and interpret. If uncore events are missing, formulas in `rkl-metrics.json` may fail resolution or silently fall back only where `has_event(...)` guards exist.

## Test signals
Useful checks include `jq empty uncore-interconnect.json`, generated `jevents` output inspection for `unit = "arb"` and `perpkg = true`, and `perf list` on Rocket Lake to confirm the uncore aliases appear under an uncore arbiter PMU. Runtime smoke tests should pin aggregation to package scope and verify representative events such as `UNC_ARB_TRK_REQUESTS.ALL` and `UNC_ARB_DAT_OCCUPANCY.RD` can be counted. Metric tests should cover formulas that reference these aliases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/rocketlake/uncore-interconnect.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/rocketlake/uncore-other.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/rocketlake/uncore-other.json

## Purpose
This JSON file defines a single Rocket Lake uncore miscellaneous event alias, `UNC_CLOCK.SOCKET`. It gives perf and Rocket Lake metrics a symbolic package-level clock source for uncore/socket timing calculations.

## Data shape and important fields
The file is a JSON array with 1 object. The observed keys are `EventName`, `BriefDescription`, `EventCode`, `Counter`, `Unit`, and `PerPkg`.

The entry uses `EventName` `UNC_CLOCK.SOCKET`, `BriefDescription` `Uncore clockticks`, `EventCode` `0x00`, `Counter` `0,1,2,3`, `Unit` `cbox_0`, and `PerPkg` `1`. The `Unit` ties the event to a C-box uncore PMU instance; the `PerPkg` flag tells perf that aggregation is package-scoped.

## Control flow and integration
The JSON is parsed by `jevents.py` and emitted as one generated `pmu_event`. Runtime perf exposes the alias and programs the matching `cbox_0` uncore PMU. `rkl-metrics.json` references `UNC_CLOCK.SOCKET` for system/socket clock metrics such as socket clocks and uncore-frequency calculations.

There is no local control flow, but the event is a dependency for formula evaluation where uncore clock ticks are normalized by duration, die count, or other system-level denominators.

## State, persistence, and dependencies
The file is static and persists only through generated perf event tables. Runtime state lives in the uncore C-box counter. The definition depends on the kernel exposing a compatible `cbox_0` PMU and on perf's unit matching and package aggregation behavior.

## Risks
This file is small, but it is a single point of failure for metrics that derive uncore/socket frequency or clock totals. A wrong unit name can make the alias disappear even if the event encoding is otherwise correct. A wrong aggregation flag can skew socket-level metrics on multi-core or multi-socket systems.

Because it exposes only `cbox_0`, systems with different C-box naming or topology may need wildcard behavior from perf's PMU matching. If matching is too strict, the metric dependency may not resolve.

## Test signals
Useful checks are `jq empty uncore-other.json`, generated table inspection for `UNC_CLOCK.SOCKET`, and `perf list`/`perf stat` smoke tests against the C-box uncore PMU. Metric validation should run formulas in `rkl-metrics.json` that reference `UNC_CLOCK.SOCKET`, especially uncore frequency and socket clock metrics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/rocketlake/uncore-other.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/rocketlake/virtual-memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/rocketlake/virtual-memory.json

## Purpose
This JSON file defines Rocket Lake virtual-memory and TLB PMU event aliases for perf. It covers first-level and second-level TLB behavior for data loads, data stores, and instruction fetches, including STLB hits, page-walk activity, completed walks by page size, pending walks, and TLB flush events.

The aliases are foundational for memory-translation metrics in `rkl-metrics.json`, including DTLB load/store bottlenecks, ITLB/code STLB misses, page-walk utilization, and page-size breakdowns.

## Data shape and important fields
The file is a JSON array of 22 event objects. The observed keys are `EventName`, `BriefDescription`, `PublicDescription`, `EventCode`, `UMask`, `Counter`, `CounterMask`, and `SampleAfterValue`.

The event families are:

- `DTLB_LOAD_MISSES`: 7 events for load STLB hits, walk activity, completed walks, 1G walks, 2M/4M walks, 4K walks, and pending walks.
- `DTLB_STORE_MISSES`: 7 analogous events for stores.
- `ITLB_MISSES`: 6 events for instruction-side STLB hits and walks, without a 1G-specific completed-walk entry.
- `TLB_FLUSH`: 2 events for DTLB thread flushes and STLB flushes.

All entries use programmable counters `0,1,2,3`. Some events use `CounterMask` to convert an occurrence-style event into a cycles-with-activity or pending-walk occupancy signal. Sample periods are present on normal sampled events.

## Control flow and integration
The file has declarative flow through the perf PMU event generator:

1. `jevents.py` parses the virtual-memory topic JSON.
2. Each object is converted to generated `pmu_event` data with event/umask/cmask encodings.
3. Runtime perf resolves names such as `DTLB_LOAD_MISSES.WALK_ACTIVE` or `ITLB_MISSES.WALK_COMPLETED_4K`.
4. `rkl-metrics.json` uses these aliases in formulas such as `tma_dtlb_load`, `tma_dtlb_store`, `tma_load_stlb_miss`, `tma_store_stlb_miss`, `tma_code_stlb_miss`, and page-size-specific child metrics.

There is no executable logic in the JSON. Interpretation of activity versus completed-walk counts is controlled by event encoding and metric formulas.

## State, persistence, and dependencies
The source file is static. The generated perf event table is the build-time persistence artifact. Runtime state is in core PMU counters programmed for DTLB, ITLB, and TLB flush events.

Dependencies include Rocket Lake's PMU event encodings for TLB miss families, perf's schema support for `CounterMask`, and metric formulas that normalize activity counts by `tma_info_thread_clks` or `tma_info_core_core_clks`. The metrics layer also depends on matching page-size variants; for example, load/store page-walk metrics divide completed 4K, 2M/4M, and 1G counts by the sum of completed walks.

## Risks
The main risk is confusing occurrence counts with cycle/occupancy counts. `WALK_ACTIVE` and `WALK_PENDING` are used as stall or utilization signals, while `WALK_COMPLETED_*` entries are used for page-size breakdowns. Incorrect `CounterMask` or umask values can make metrics look plausible but semantically wrong.

Another risk is denominator fragility in page-size metrics. If no walks complete in a workload, formulas that divide page-size walk counts by total completed walks can become undefined or unstable unless the metric evaluator or caller handles zero counts. Cross-file dependencies also matter because `rkl-metrics.json` combines these events with pipeline clocks and memory activity events.

## Test signals
Useful checks include `jq empty virtual-memory.json`, generated `jevents` output inspection for all 22 aliases, and `perf list --json` checks for DTLB, ITLB, and TLB flush names. Runtime tests should count representative load, store, instruction, and flush events if hardware is available. Metric validation should cover `tma_dtlb_load`, `tma_dtlb_store`, `tma_itlb_misses`, `tma_load_stlb_miss_4k`, `tma_store_stlb_miss_2m`, and `tma_code_stlb_miss_4k`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/rocketlake/virtual-memory.json -->
