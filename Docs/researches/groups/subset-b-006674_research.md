# subset-b-006674 grouped research

This grouped report covers Intel Ice Lake x86 perf PMU event and metric JSON files from the Ceph client copy of Linux `tools/perf`. Each section preserves the original source path and is wrapped for reconciliation into the corresponding source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelake/frontend.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelake/frontend.json

## Purpose

This file is the Ice Lake client frontend-event catalog for Linux `perf`. It contains 39 core PMU event records used to diagnose instruction fetch, decode, decoded-stream-buffer delivery, MITE delivery, microcode sequencer delivery, instruction-cache/tag stalls, and frontend-retired latency buckets. The x86 mapfile selects this `icelake` directory for `GenuineIntel-6-7[DE]` model matches, so these aliases become the frontend part of Ice Lake perf event tables.

## Important APIs, Types, And Data

The file is data, not executable code. Its API is the perf PMU JSON event schema consumed by `tools/perf/pmu-events/jevents.py`: `EventName`, `EventCode`, `UMask`, `Counter`, `CounterMask`, `EdgeDetect`, `MSRIndex`, `MSRValue`, `SampleAfterValue`, `BriefDescription`, and `PublicDescription`. Representative event families are `BACLEARS`, `DECODE`, `DSB2MITE_SWITCHES`, `FRONTEND_RETIRED`, `ICACHE_16B`, `ICACHE_64B`, `ICACHE_DATA`, `ICACHE_TAG`, `IDQ`, and `IDQ_UOPS_NOT_DELIVERED`.

Several entries have special programming fields. `FRONTEND_RETIRED.*` events share `EventCode` `0xc6`/`UMask` `0x1` and distinguish DSB, ITLB, L1I, L2, STLB, and latency-threshold behaviors through `MSRIndex` `0x3F7` and different `MSRValue` encodings. `DSB2MITE_SWITCHES.COUNT` and `IDQ.MS_SWITCHES` use edge detection, while cycle-qualified IDQ and uop-delivery events use `CounterMask` values to count cycles meeting a delivery threshold rather than simple occurrences.

## Control Flow

Build-time control starts in the perf PMU event build rules, which invoke `pmu-events/jevents.py` over the x86 architecture tree. `jevents.py` loads this JSON array, normalizes each object into a generated event record, lowercases aliases, translates `EventCode`, `UMask`, `CounterMask`, `EdgeDetect`, `MSRIndex`, `MSRValue`, and sample period fields into perf event strings, and emits compact C tables in generated `pmu-events.c`.

Runtime perf commands do not parse this JSON. `perf list` displays generated aliases and descriptions, while `perf stat -e`/`perf record -e` resolve frontend event names through the compiled table and program the CPU PMU with the generated config and MSR filter fields.

## State And Persistence Behavior

The JSON persists static hardware-event metadata in source control. Mutable state is external: hardware counters, PEBS/frontend filters, and perf file descriptors exist only while perf is running. The default `SampleAfterValue` and frontend MSR filter values persist into generated aliases and affect sampling/programming defaults, but no counter samples or derived state are stored in this file.

## Dependencies And Integration Points

This file integrates with `arch/x86/mapfile.csv`, `pmu-events/Build`, `pmu-events/jevents.py`, generated `pmu-events.c`, `pmu-events.h`, `builtin-list.c`, `builtin-stat.c`, and metric expressions in `icl-metrics.json` that reference frontend events such as `IDQ_UOPS_NOT_DELIVERED.CORE`, `IDQ.DSB_UOPS`, `IDQ.MITE_UOPS`, `DSB2MITE_SWITCHES.PENALTY_CYCLES`, `ICACHE_DATA.STALLS`, and `FRONTEND_RETIRED.*`. It also supports the user-facing top-down frontend-bound, fetch-latency, fetch-bandwidth, DSB, MITE, and microcode-sequencer metrics.

## Risks And Edge Cases

The highest-risk fields are the `MSRIndex`/`MSRValue` encodings for `FRONTEND_RETIRED.*`; a bad value can silently select the wrong latency or miss qualifier while still producing counts. `CounterMask` and `EdgeDetect` fields change event meaning from counts to threshold cycles or transitions. Frontend events often share selectors, so duplicate or near-duplicate aliases rely on the full generated configuration being preserved. Metrics that subtract or divide frontend subcategories can become misleading if any raw event is unavailable, multiplexed heavily, or programmed on the wrong Ice Lake model.

## Test Signals

Useful checks include `jq empty frontend.json`, `jevents.py` generation for x86 Ice Lake, `perf test pmu-events`, and `perf list` checks for aliases such as `frontend_retired.latency_ge_64`, `idq.dsb_uops`, and `idq_uops_not_delivered.core`. Runtime signals include frontend-stressing workloads, instruction-cache pressure tests, and metric expansion tests for top-down frontend categories. Generated output should preserve MSR filters for all `FRONTEND_RETIRED` records and edge/cmask fields for switch and delivery-cycle events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelake/frontend.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelake/icl-metrics.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelake/icl-metrics.json

## Purpose

This file defines 240 derived metrics for Ice Lake client perf. It is the model-specific Top-Down Microarchitecture Analysis and performance-analysis layer above the raw event catalogs. It includes power residency, SMI, top-down level 1 through level 6 breakdowns, bottleneck estimates, memory latency and bandwidth estimates, branch and bad-speculation diagnostics, frontend fetch latency/bandwidth diagnostics, retiring and instruction-mix metrics, port utilization, FLOP/vector metrics, SMT/system information, and uncore frequency helpers.

## Important APIs, Types, And Data

Each entry follows the perf metric JSON schema with `MetricName`, `MetricExpr`, `MetricGroup`, `ScaleUnit`, and `BriefDescription`. `MetricExpr` is parsed by `pmu-events/metric.py` through `jevents.py`, simplified, and embedded into generated tables for runtime metric expansion. Expressions reference raw PMU aliases, synthetic top-down slots such as `topdown-fe-bound`, `topdown-be-bound`, `topdown-retiring`, and `topdown-bad-spec`, MSR aliases such as `msr@tsc@`, `msr@aperf@`, and `msr@smi@`, cstate PMUs, constants, conditional expressions, and helper variables such as `#num_dies`, `duration_time`, and `#SMT_on`.

Important metric families include `tma_frontend_bound`, `tma_backend_bound`, `tma_bad_speculation`, `tma_retiring`, `tma_fetch_latency`, `tma_fetch_bandwidth`, `tma_memory_bound`, `tma_core_bound`, `tma_dram_bound`, `tma_l1_bound`, `tma_l2_bound`, `tma_l3_bound`, `tma_store_bound`, `tma_branch_mispredicts`, `tma_machine_clears`, `tma_microcode_sequencer`, `tma_ports_utilization`, `tma_fp_vector`, and `tma_info_*` helper metrics. Metric groups are semicolon-separated and include broad user-facing groups (`Default`, `Frontend`, `Backend`, `MemoryBW`, `MemoryLat`, `Branches`, `Power`, `Summary`) plus hierarchical groups (`TopdownL1` through `TopdownL6`, `tma_L*_group`) and issue taxonomy groups (`tma_issueBW`, `tma_issueTLB`, `tma_issueBM`, and others).

## Control Flow

At build time, `jevents.py` reads the metrics array and detects `MetricExpr`. Each expression is parsed by the metric expression parser, simplified, associated with its groups and scale unit, and emitted into generated PMU metric tables. `metricgroups.json` supplies descriptions for many groups referenced here.

At runtime, `perf list metricgroup` and `perf list --details` expose metric names, groups, descriptions, and expressions. `perf stat -M <metric-or-group>` expands selected metrics into required raw events and helper metrics, schedules the underlying events, then computes the expression tree from collected counts. Metrics can recursively reference other metric names, so perf must resolve dependencies such as `tma_backend_bound` before computing bottleneck metrics that depend on it.

## State And Persistence Behavior

The file persists formulas and display metadata. No sampled values are stored here. Runtime state is the metric expression graph, event scheduling group, collected counter values, and computed results held by perf during a command. Scale units such as `100%`, `1SMI#`, or empty units persist into output formatting and strongly influence how users read the computed number.

## Dependencies And Integration Points

This file depends on the raw Ice Lake event catalogs in the same directory and sibling files not in this work item, because expressions reference frontend, pipeline, memory, cache, TLB, branch, offcore, power, and MSR event names. It integrates with `pmu-events/metric.py`, `pmu-events/metric_test.py`, `jevents.py`, generated `pmu-events.c`, `builtin-list.c`, `builtin-stat.c`, Python event listing, and perf's metricgroup expansion code. It also integrates with `metricgroups.json`, which gives descriptions to groups such as `TopdownL1`, `Mem`, `Offcore`, `FetchLat`, `BvML`, and `tma_*_group`.

## Risks And Edge Cases

Metric expressions are fragile because they combine many raw events and derived metrics. Risks include division by zero, negative residuals from subtraction, event-name drift between JSON files, unavailable MSR/cstate/offcore events, SMT-dependent formulas, multiplexing distortion, and formulas that rely on `max`, `min`, and conditional guards being parsed exactly as intended. Some expressions use escaped perf raw event syntax such as `cpu@INST_DECODED.DECODERS\\,cmask\\=1@`; escaping mistakes break parsing or select the wrong event. Recursive metric dependencies can also hide cycles or missing symbols until metric tests or runtime expansion.

## Test Signals

Validation should include `jq empty icl-metrics.json`, `python pmu-events/metric_test.py` or the build target that writes `metric_test.log`, full `jevents.py` generation, and `perf test pmu-events`. Runtime checks should run `perf stat -M Default`, `perf stat -M TopdownL1`, and targeted groups such as `Frontend`, `MemoryBW`, `MemoryLat`, `Branches`, and `Power` on Ice Lake or a representative PMU fixture. `perf list --details metrics` should show parsable expressions and correct group membership. Regression checks should cover expressions with escaped event modifiers, MSR references, recursive `tma_*` dependencies, and scale-unit formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelake/icl-metrics.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelake/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelake/memory.json

## Purpose

This file is the Ice Lake client memory and transactional-memory event catalog for perf. It contains 60 raw event records covering L3-miss cycles and stalls, Hardware Lock Elision and RTM transaction starts/commits/aborts, memory-ordering machine clears, load-latency thresholds, offcore response categories, L3-miss demand-data requests, outstanding L3 misses, and transactional abort causes.

## Important APIs, Types, And Data

The records use the perf event JSON schema: `EventName`, `EventCode`, `UMask`, `Counter`, `CounterMask`, `MSRIndex`, `MSRValue`, `SampleAfterValue`, `BriefDescription`, and `PublicDescription`. Important families are `CYCLE_ACTIVITY`, `HLE_RETIRED`, `MACHINE_CLEARS`, `MEM_TRANS_RETIRED`, `OCR`, `OFFCORE_REQUESTS`, `OFFCORE_REQUESTS_OUTSTANDING`, `RTM_RETIRED`, `TX_EXEC`, and `TX_MEM`.

The `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_*` entries share event `0xcd` and use `MSRIndex` `0x3F6` with threshold-specific `MSRValue` values from `0x4` through `0x200`. The `OCR.*` entries share offcore response event selectors `0xB7, 0xBB` and program offcore MSRs `0x1a6,0x1a7` with response masks for demand code reads, demand data reads, RFO, L1D/software prefetch, L2 data reads, L2 RFO, other requests, and streaming writes against DRAM, local DRAM, or L3-miss responses. `CYCLE_ACTIVITY.*` and outstanding-request events use `CounterMask` to count cycles meeting stall or miss thresholds.

## Control Flow

During perf build, `jevents.py` parses each memory event record into generated PMU event-table entries. Event selector, umask, counter mask, sample period, and offcore or latency MSR programming fields are carried into generated config strings. At runtime, perf resolves aliases from the compiled table and programs the CPU PMU and any required extra MSR filters before reading or sampling the counter.

Metrics in `icl-metrics.json` then use these raw events to derive memory-bound, DRAM-bound, L3-bound, memory bandwidth, memory latency, synchronization, data sharing, contested access, store bound, false sharing, and transactional diagnostics.

## State And Persistence Behavior

The file persists static memory-event metadata and default sample periods only. Runtime state includes hardware counter values, offcore-response MSR state, latency-threshold MSR state, and perf aggregation state. Transactional-memory events reflect CPU execution state only while measured; no transaction state is persisted in the JSON.

## Dependencies And Integration Points

This file integrates with Ice Lake model selection, `jevents.py`, generated `pmu-events.c`, perf event alias resolution, and metrics that reference `CYCLE_ACTIVITY.STALLS_L3_MISS`, `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_*`, `OCR.*`, `OFFCORE_REQUESTS.*`, `RTM_RETIRED.*`, `HLE_RETIRED.*`, and `TX_MEM.*`. It depends on kernel support for programming offcore response MSRs and on the raw event encodings matching Ice Lake client hardware.

## Risks And Edge Cases

Offcore response events are the highest-risk area because one alias requires both normal PMU selector fields and model-specific MSR response masks. Incorrect `MSRValue` can produce plausible but wrong traffic categories. `LOCAL_DRAM` and `DRAM` masks are identical in this file for several request classes, which may be intentional for this model but is easy to misread during edits. Transactional-memory events may be unsupported or low-value on systems where TSX is disabled by firmware, microcode, or kernel policy. Counter masks convert events into cycle counts rather than occurrence counts, and multiplexing can skew derived memory-bound metrics.

## Test Signals

Use `jq empty memory.json`, x86 `jevents.py` generation, `perf test pmu-events`, and generated-table inspection for `offcore_rsp`/MSR fields. Runtime validation includes pointer-chasing or memory-bandwidth workloads for L3/DRAM metrics, checks that `mem_trans_retired.load_latency_gt_64` and related thresholds are visible in `perf list`, and TSX-focused tests only on systems where HLE/RTM are enabled. Metric tests should verify that `MemoryBW`, `MemoryLat`, `Offcore`, and `LockCont` groups still expand.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelake/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelake/metricgroups.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelake/metricgroups.json

## Purpose

This file supplies descriptions for 138 Ice Lake metric groups. It is the companion metadata for `icl-metrics.json`, making metric group listings readable in `perf list metricgroup` and related output. The groups cover general analysis buckets, Intel Top-Down Microarchitecture Analysis levels, bottleneck-view groups, issue-taxonomy groups, and per-category child groups.

## Important APIs, Types, And Data

Unlike the event JSON files, this file is a JSON object rather than an array. Each key is a metric group name and each value is its description string. Keys include broad groups such as `Backend`, `Frontend`, `Mem`, `Offcore`, `Power`, `Pipeline`, `Summary`, `Branches`, `Compute`, `Flops`, `MemoryBW`, `MemoryLat`, `MemoryTLB`, and `LockCont`; Top-Down groups such as `TopdownL1` through `TopdownL6`, `TmaL1`, `TmaL2`, `TmaL3mem`, and `tma_L*_group`; bottleneck-view groups such as `BvBC`, `BvBO`, `BvCB`, `BvFB`, `BvMB`, `BvML`, `BvMP`, `BvMS`, `BvMT`, `BvOB`, and `BvUW`; and issue groups such as `tma_issueBW`, `tma_issueTLB`, `tma_issueBM`, `tma_issueFB`, and `tma_issueSyncxn`.

Most values are standardized descriptions such as "Grouping from Top-down Microarchitecture Analysis Metrics spreadsheet", "Metrics for top-down breakdown at level N", "Metrics contributing to ... category", or "Metrics related by the issue $...".

## Control Flow

`jevents.py` treats files ending in `metricgroups.json` specially. It loads the object mapping, stores group-description pairs in its metricgroup map, and emits sorted generated metadata into `pmu-events.c`. The normal event-loop path intentionally skips `metricgroups.json` so these entries are not interpreted as events or metrics.

At runtime, perf list and metricgroup display code can look up a group name and print the generated description. Metric computation still comes from metric entries in `icl-metrics.json`; this file only documents and organizes the group namespace.

## State And Persistence Behavior

The file persists descriptive metadata only. Runtime state is the generated group-description lookup table compiled into perf. There is no mutable state, no counters, and no formulas. A stale description can mislead users but does not change the measured values.

## Dependencies And Integration Points

This file depends on the group names used by `icl-metrics.json`; a group description has user value only if metrics reference the same string in their semicolon-separated `MetricGroup` fields. It integrates with `jevents.py` metricgroup parsing, generated `pmu-events.c`, `builtin-list.c`, and any command that prints metric group descriptions. The build also generates `extra-metricgroups.json` for some architectures, so this static file shares the same group-description contract.

## Risks And Edge Cases

Shape is the main schema risk: converting this object into an array like normal event files would break metricgroup parsing. Misspelled keys do not necessarily break builds, but they create orphan descriptions or leave active metric groups undescribed. Similar names such as `MemoryBW` and `Memory_BW`, `MemoryLat` and `Memory_Lat`, or `MachineClears` and `Machine_Clears` are intentional compatibility/user-facing surfaces and should not be normalized casually. Descriptions containing `$issue...` tokens are documentation strings, not variables to expand.

## Test Signals

Validate with `jq empty metricgroups.json`, then run `jevents.py` generation and `perf test pmu-events`. `perf list metricgroup` or `perf list --details` should show descriptions for representative groups such as `TopdownL1`, `Frontend`, `MemoryBW`, `BvML`, and `tma_issueTLB`. Cross-checking active groups from `icl-metrics.json` against keys in this file is a useful orphan/missing-description test.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelake/metricgroups.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelake/other.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelake/other.json

## Purpose

This small file defines five Ice Lake miscellaneous core PMU events that do not fit the frontend, memory, or pipeline catalogs. It covers turbo-license residency levels and two offcore response classes for "other" and streaming-write request types with any response.

## Important APIs, Types, And Data

The entries use the standard event JSON fields `EventName`, `EventCode`, `UMask`, `Counter`, `MSRIndex`, `MSRValue`, `SampleAfterValue`, `BriefDescription`, and `PublicDescription`. `CORE_POWER.LVL0_TURBO_LICENSE`, `CORE_POWER.LVL1_TURBO_LICENSE`, and `CORE_POWER.LVL2_TURBO_LICENSE` share selector `0x28` with umasks `0x7`, `0x18`, and `0x20`. `OCR.OTHER.ANY_RESPONSE` and `OCR.STREAMING_WR.ANY_RESPONSE` use offcore selectors `0xB7, 0xBB`, umask `0x1`, MSRs `0x1a6,0x1a7`, and response masks `0x18000` and `0x10800`.

## Control Flow

Build-time handling is the normal `jevents.py` event path: parse the array, normalize each object, convert selector/mask/MSR fields into generated perf aliases, and emit them into the Ice Lake table. Runtime perf resolves the generated aliases and programs either normal core power-license events or offcore-response-filtered events.

## State And Persistence Behavior

The file persists static alias definitions and descriptions. Turbo-license residency and offcore response counts are hardware state sampled during a perf run. No runtime values are persisted in the source tree. Default sample periods become generated alias metadata.

## Dependencies And Integration Points

The turbo-license entries integrate with power and frequency analysis workflows and may complement `icl-metrics.json` power/system metrics, though cstate residency metrics mostly use MSR/cstate aliases. The OCR entries integrate with offcore and memory bottleneck analysis. All entries depend on Ice Lake model selection, `jevents.py`, generated event tables, and kernel support for the relevant core PMU/offcore MSR programming.

## Risks And Edge Cases

The file is small but semantically mixed. Power-license events count cycles under turbo-license constraints, which users may confuse with frequency or package residency metrics. The OCR entries share offcore programming behavior with `memory.json`, so wrong MSR masks can silently change request categorization. Because this file is often treated as a catch-all, future edits risk duplicating events already present in more specific catalogs.

## Test Signals

Validate with `jq empty other.json`, run x86 PMU event generation, and inspect `perf list` for `core_power.lvl*_turbo_license` and `ocr.*.any_response`. Runtime tests should compare turbo-license counts under frequency-sensitive workloads and ensure offcore entries program response MSRs without conflicting with `memory.json` OCR aliases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelake/other.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelake/pipeline.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelake/pipeline.json

## Purpose

This file is the Ice Lake client pipeline-event catalog for perf. It contains 95 core PMU event records covering arithmetic divider activity, assists, retired branches and mispredictions, CPU clocks, memory-stall cycle activity, execution activity, decode/retire events, recovery cycles, load blocks, loop stream detector activity, machine clears, resource stalls, reservation-station emptiness, top-down slots, uop decode/dispatch/execute/issue/retire behavior, and related pipeline bottleneck signals.

## Important APIs, Types, And Data

Records use the standard event schema with `EventName`, `EventCode`, `UMask`, `Counter`, `CounterMask`, `EdgeDetect`, `SampleAfterValue`, `BriefDescription`, and `PublicDescription`. Major families include `ARITH`, `ASSISTS`, `BR_INST_RETIRED`, `BR_MISP_RETIRED`, `CPU_CLK_UNHALTED`, `CYCLE_ACTIVITY`, `EXE_ACTIVITY`, `ILD_STALL`, `INST_DECODED`, `INST_RETIRED`, `INT_MISC`, `LD_BLOCKS`, `LD_BLOCKS_PARTIAL`, `LOAD_HIT_PREFETCH`, `LSD`, `MACHINE_CLEARS`, `MISC_RETIRED`, `RESOURCE_STALLS`, `RS_EVENTS`, `TOPDOWN`, `UOPS_DECODED`, `UOPS_DISPATCHED`, `UOPS_EXECUTED`, `UOPS_ISSUED`, and `UOPS_RETIRED`.

Important qualifier fields are common. `CounterMask` turns many events into cycle-threshold measurements, for example `CYCLE_ACTIVITY.*`, `LSD.CYCLES_*`, `UOPS_EXECUTED.CYCLES_GE_*`, and `UOPS_RETIRED.TOTAL_CYCLES`. `EdgeDetect` marks transition/count events such as `INT_MISC.CLEARS_COUNT`, `MACHINE_CLEARS.COUNT`, and `RS_EVENTS.EMPTY_END`. Top-down events provide slot-level inputs via `TOPDOWN.SLOTS`, `TOPDOWN.SLOTS_P`, and `TOPDOWN.BACKEND_BOUND_SLOTS`.

## Control Flow

At build time, the perf PMU event generator reads this JSON, validates and normalizes the event records, lowercases aliases, and emits the generated Ice Lake pipeline event table. Runtime perf uses those generated aliases for direct event selection and as dependencies for derived metrics. Metric expansion in `perf stat -M` draws heavily from this file for top-down, branch, bad-speculation, backend, retiring, port-utilization, divider, and instruction-mix formulas.

## State And Persistence Behavior

The file persists static hardware encoding metadata and default sampling periods. Runtime pipeline state, branch predictor state, uop queues, reservation stations, and counter values live in hardware and perf file descriptors only while a measurement is active. Generated aliases preserve semantic qualifiers such as `cmask` and `edge`, but no measured values are stored.

## Dependencies And Integration Points

This file integrates with `icl-metrics.json` more heavily than any other raw catalog in this work item. Metrics reference `BR_INST_RETIRED.*`, `BR_MISP_RETIRED.*`, `CPU_CLK_UNHALTED.*`, `CYCLE_ACTIVITY.*`, `EXE_ACTIVITY.*`, `INST_RETIRED.*`, `INT_MISC.*`, `LD_BLOCKS*`, `MACHINE_CLEARS.*`, `RS_EVENTS.*`, `TOPDOWN.*`, and many `UOPS_*` events. It also integrates with `jevents.py`, generated `pmu-events.c`, `perf list`, `perf stat`, and top-down documentation/metric tests.

## Risks And Edge Cases

Pipeline event semantics are easy to corrupt because the same base selector can represent occurrences, cycles, slots, or thresholded cycles depending on umask/cmask/edge fields. Top-down slot metrics must remain consistent with Ice Lake's pipeline width and perf's top-down event handling. Branch and machine-clear metrics feed several higher-level formulas, so a small encoding mistake can distort many derived bottleneck categories. Counter availability also matters: many entries list only programmable counters `0,1,2,3`, while others include fixed or wider counter sets; changing those fields can make scheduling fail or overconstrain perf.

## Test Signals

Use `jq empty pipeline.json`, run `jevents.py` generation, and run `perf test pmu-events` plus metric parser tests. `perf list` should expose representative aliases such as `topdown.slots`, `br_misp_retired.all_branches`, `uops_dispatched.port_0`, `cycle_activity.stalls_mem_any`, and `int_misc.clear_resteer_cycles`. Runtime tests should include branch-misprediction, divider-heavy, memory-stall, and uop-throughput workloads, plus `perf stat -M TopdownL1,TopdownL2,Pipeline,PortsUtil`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelake/pipeline.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelake/uncore-interconnect.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelake/uncore-interconnect.json

## Purpose

This file defines two Ice Lake client uncore interconnect events for the ARB PMU. They count coherent tracker requests and tracker requests at package scope, giving perf aliases for basic uncore fabric/request-tracking activity.

## Important APIs, Types, And Data

Each record uses `EventName`, `EventCode`, `UMask`, `Counter`, `Unit`, `PerPkg`, and `BriefDescription`. `UNC_ARB_COH_TRK_REQUESTS.ALL` uses event `0x84`, umask `0x1`, counter `1`; `UNC_ARB_TRK_REQUESTS.ALL` uses event `0x81`, umask `0x1`, counter `1`. `Unit` is `ARB`, which `jevents.py` maps to an uncore PMU table name, and `PerPkg` is `1`, marking package-scoped events.

## Control Flow

Build-time generation follows the same event path as core records, with the additional unit-to-PMU mapping for `ARB`. The generated aliases are emitted under an uncore PMU table rather than the default core table. At runtime, perf resolves the aliases against kernel-exposed uncore ARB PMU devices and programs the package-level counter.

## State And Persistence Behavior

The file persists static uncore alias metadata. Counter state is maintained by uncore hardware and read by perf during a command. Package aggregation and multi-socket behavior are runtime perf/kernel concerns; the JSON only declares `PerPkg` scope.

## Dependencies And Integration Points

Dependencies include the Ice Lake x86 mapfile row, `jevents.py` unit conversion, generated `pmu-events.c`, perf uncore PMU discovery, and kernel support for an ARB uncore PMU. These events integrate with uncore interconnect analysis and can support higher-level system or memory-traffic investigations, even though `icl-metrics.json` focuses more on core/offcore-derived metrics.

## Risks And Edge Cases

The main risk is PMU naming and scope. If `Unit` does not match perf's uncore naming convention for Ice Lake ARB devices, aliases can disappear from `perf list` or bind incorrectly. `PerPkg` mistakes can produce confusing aggregation on multi-package systems. Both events use counter `1`; tests should catch whether this is a hardware restriction and whether scheduling two aliases concurrently is possible.

## Test Signals

Validate the JSON, run x86 `jevents.py` generation, and inspect generated aliases for `unc_arb_coh_trk_requests.all` and `unc_arb_trk_requests.all` under the ARB uncore PMU. On hardware or a fixture, `perf list` should show package-scoped uncore aliases, and concurrent scheduling should respect the shared counter constraint.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelake/uncore-interconnect.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelake/uncore-other.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelake/uncore-other.json

## Purpose

This one-entry file defines the Ice Lake client uncore socket clock alias `UNC_CLOCK.SOCKET`. It provides a package-level uncore clock reference counter for perf users and for sanity-checking uncore measurements.

## Important APIs, Types, And Data

The entry uses `EventName`, `EventCode`, `Counter`, `Unit`, `PerPkg`, and `BriefDescription`. `EventCode` is `0xff`, `Counter` is `FIXED`, `Unit` is `CLOCK`, and `PerPkg` is `1`. The description identifies it as a 48-bit UCLK fixed counter.

## Control Flow

`jevents.py` parses the single JSON object, maps `Unit` `CLOCK` to the generated uncore clock PMU table, and emits the fixed-counter alias into `pmu-events.c`. At runtime, perf resolves `unc_clock.socket` against matching uncore clock PMU devices and reads the fixed package clock counter.

## State And Persistence Behavior

The JSON persists only the alias and description. The 48-bit uncore clock count is hardware state and can wrap during long measurements depending on frequency and read interval. Perf handles runtime reads and aggregation; this file stores no samples.

## Dependencies And Integration Points

This event depends on Ice Lake model selection, uncore unit mapping in `jevents.py`, generated PMU tables, and kernel exposure of the uncore clock PMU. It integrates with `perf list`, `perf stat`, and uncore workflows where a socket-clock denominator or liveness check is useful.

## Risks And Edge Cases

Fixed counters may have different programming semantics from programmable uncore counters. The 48-bit width matters for long-running sessions and should not be lost from the description. Unit-name drift would make the alias undiscoverable, and `PerPkg` aggregation must remain package-scoped rather than per-core.

## Test Signals

Use `jq empty uncore-other.json`, x86 event generation, and `perf test pmu-events`. On compatible systems, `perf list` should show `unc_clock.socket` under an uncore clock PMU, and `perf stat` should report a monotonically increasing package-level count without requiring programmable counter slots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelake/uncore-other.json -->
