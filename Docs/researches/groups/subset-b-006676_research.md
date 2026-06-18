# subset-b-006676 grouped research

This grouped report covers the Ice Lake Xeon x86 perf PMU metrics, memory events, metric-group descriptions, and miscellaneous events under the Ceph client copy of Linux `tools/perf`. Each section preserves the source path and is intended for reconciliation into the matching source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelakex/icx-metrics.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelakex/icx-metrics.json

## Purpose

This file is the Ice Lake Xeon metric catalog for Linux `perf`. It contains 302 derived metrics for the `icelakex` model directory selected by the x86 mapfile row `GenuineIntel-6-6[AC]`. The metrics turn raw PMU event aliases, uncore event aliases, software counters, MSR counters, and perf metric helper functions into user-facing formulas for top-down microarchitecture analysis, memory hierarchy diagnosis, power and frequency reporting, TSX transaction analysis, UPI bandwidth, NUMA locality, SMI activity, instruction mix, and cache/TLB behavior.

The file is data rather than executable code, but it is a major behavioral surface for `perf stat -M`, `perf list`, and metric-group expansion. It provides the Ice Lake server-specific version of broad metrics such as `cpi`, `cpu_operating_frequency`, `memory_bandwidth_*`, `tma_backend_bound`, `tma_frontend_bound`, `tma_retiring`, `tma_memory_bound`, `tma_l1_bound`, `tma_l2_bound`, `tma_l3_bound`, `tma_fp_vector_*`, `tma_store_stlb_miss_*`, `tsx_*`, `uncore_frequency`, and `upi_data_*_bw`.

## Important APIs, Types, And Data

The effective API is the perf metric JSON schema consumed by `tools/perf/pmu-events/jevents.py` and then by perf's metric parser. Records use fields including `MetricName`, `MetricExpr`, `MetricGroup`, `BriefDescription`, `PublicDescription`, `ScaleUnit`, `MetricThreshold`, `MetricConstraint`, `DefaultMetricgroupName`, and `MetricgroupNoGroup`.

`MetricExpr` is the main contract. Expressions reference event aliases from sibling Ice Lake Xeon event JSON files and generic perf events, including `CPU_CLK_UNHALTED.THREAD`, `INST_RETIRED.ANY`, top-down pseudo events such as `topdown-retiring`, offcore-response aliases such as `OCR.*`, uncore aliases such as `UNC_M_*`, `UNC_CHA_*`, `UNC_UPI_*`, cstate aliases, and transaction aliases such as `cycles-t`. Expressions also use perf metric language functions and constants such as `has_event(...)`, `source_count(...)`, `duration_time`, `#num_packages`, `#num_dies`, `#SMT_on`, `#SYSTEM_TSC_FREQ`, `max(...)`, and `min(...)`.

`MetricGroup` binds each metric into semicolon-separated groups. This file heavily uses Topdown groups (`TopdownL1` through `TopdownL6`, `tma_L*_group`, `TmaL1`, `TmaL2`, and `TmaL3mem`), analysis-domain groups (`Mem`, `MemoryBW`, `MemoryLat`, `MemoryTLB`, `Offcore`, `Server`, `Power`, `SoC`, `Flops`, `Branches`, `Pipeline`, `Frontend`, `Backend`, `Retire`), bottleneck-view groups (`Bv*`), and issue tags such as `tma_issueBW`, `tma_issueLat`, `tma_issueTLB`, and `tma_issueSyncxn`.

`ScaleUnit` describes output units such as `100%`, `1per_instr`, `1GHz`, `1MB/s`, `1ns`, `1SMI#`, and `1per_sec`. `MetricThreshold` encodes advisory bottleneck thresholds, for example top-down fractions that exceed meaningful cutoffs or informational ratios below a useful bound. `MetricConstraint` values such as `NO_GROUP_EVENTS` prevent unsafe automatic grouping for metrics whose events are too numerous, mutually constrained, or otherwise unsuitable for simultaneous scheduling. `DefaultMetricgroupName` and `MetricgroupNoGroup` tune default top-down presentation and raw grouping behavior for high-level metrics.

## Control Flow

At build time, `jevents.py` walks the Ice Lake Xeon model directory, parses this JSON array, normalizes metric records, and emits compact generated C tables used by perf. Metric names and expressions are not evaluated during JSON parsing; they are serialized into generated metadata and later parsed by perf's metric expression engine.

At runtime, `perf list` exposes these metrics and their groups. `perf stat -M <metric>` resolves the metric name, parses `MetricExpr`, expands referenced aliases into events, schedules required PMU counters subject to `MetricConstraint`, evaluates helper functions and constants, and prints the scaled result with the configured unit. When a user asks for a metric group, group membership from `MetricGroup` and descriptions from `metricgroups.json` drive expansion and display.

The top-down metrics form a dependency graph. Level 1 metrics such as `tma_retiring`, `tma_bad_speculation`, `tma_frontend_bound`, and `tma_backend_bound` are based on top-down pseudo events. Deeper metrics then divide those high-level categories into frontend latency/bandwidth, branch misprediction, machine clears, core bound, memory bound, L1/L2/L3/DRAM/remote-memory categories, TLB walks, FP/vector execution, port utilization, and store/load bottlenecks. Informational `tma_info_*` metrics supply denominators, derived rates, and context used by the higher-level estimates.

## State And Persistence Behavior

The file persists static metric definitions in source control. It stores no samples, counter values, or mutable state. Runtime state is created by perf when it schedules PMU events and evaluates expressions over a measurement interval.

The closest state-like behavior is declarative: thresholds persist advisory classification rules, scale units persist presentation semantics, and `NO_GROUP_EVENTS` persists scheduling constraints. `has_event(...)` guards make some metrics conditional on PMU support, especially TSX transaction metrics that should evaluate to zero rather than fail on systems where transaction aliases are unavailable.

## Dependencies And Integration Points

This file depends on event aliases defined in the Ice Lake Xeon event JSON set and on generic perf aliases. Important sibling dependencies include core pipeline, cache, frontend, virtual-memory, uncore-memory/interconnect/cache, and this work item's `memory.json` and `other.json`. It also depends on metric group names documented in `metricgroups.json`; mismatches do not break JSON parsing but degrade group descriptions and user navigation.

Integration points include `tools/perf/pmu-events/jevents.py`, generated `pmu-events.c`, `util/metricgroup.c`, `util/expr.c`, `builtin-stat.c`, `builtin-list.c`, `python/ilist.py`, `Documentation/perf-stat.txt`, `Documentation/perf-list.txt`, and shell tests such as `tests/shell/stat_all_metricgroups.sh`. The generated entries are selected for Ice Lake Xeon via `arch/x86/mapfile.csv`.

## Risks And Edge Cases

Formula correctness is the main risk. Many expressions divide by event counts that can be zero on tiny workloads, depend on model-specific constants, or estimate cycles from fixed latency multipliers. Incorrect alias names, stale event names, or missing sibling events can cause metric parse failures at runtime. Because many top-down metrics depend on other metrics, an error in a base metric such as `tma_info_thread_slots`, `tma_info_thread_clks`, or a level-1 top-down fraction can contaminate many derived categories.

Scheduling is another risk. Metrics tagged with `NO_GROUP_EVENTS` are explicitly sensitive to grouped collection; ignoring that constraint can overcommit counters, multiplex incompatible events, or mix uncore and core measurements in misleading ways. Expressions that combine package-level uncore counters with per-thread or per-core counters require careful denominators such as `#num_packages`, `#num_dies`, `source_count(...)`, and `duration_time`.

Hardware feature variability matters. TSX metrics use `has_event(...)`; uncore, UPI, PMM/CXL, SNC, SMI, and power metrics may be unavailable or semantically different on a given platform configuration. Top-down and offcore-derived formulas also assume Ice Lake server event semantics and may be wrong if copied to a different x86 model without adjustment.

## Test Signals

Useful validation starts with `jq empty` and a full x86 `jevents.py` generation. Runtime-facing tests should include `perf list metricgroups`, `perf list metric`, and `perf stat -M` smoke tests for representative metrics: `cpi`, `memory_bandwidth_total`, `tma_backend_bound`, `tma_frontend_bound`, `tma_dram_bound`, `tma_fp_vector_512b`, `tsx_transactional_cycles`, `uncore_frequency`, and UPI bandwidth metrics.

Expression tests should cover missing-event guards, zero or near-zero denominators, `NO_GROUP_EVENTS` behavior, and grouped top-down collection. Workload tests can use CPU-bound loops, pointer chasing, memory bandwidth stress, branch-mispredict stress, AVX/AVX-512 kernels, TSX-enabled checks where available, and NUMA/remote-memory traffic to confirm that related metrics move in expected directions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelakex/icx-metrics.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelakex/memory.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelakex/memory.json

## Purpose

This file defines 64 Ice Lake Xeon core PMU events focused on memory behavior, offcore responses, L3 miss pressure, transactional memory, and memory ordering. It complements the higher-level metric formulas in `icx-metrics.json` by providing raw event aliases used to diagnose load latency, demand data/code/RFO misses, prefetch traffic, streaming stores, local versus remote DRAM/PMM placement, SNC-local versus SNC-distant memory, outstanding offcore requests, RTM commits and aborts, and TSX abort causes.

The event families are `CYCLE_ACTIVITY`, `MACHINE_CLEARS`, `MEM_TRANS_RETIRED`, `OCR`, `OFFCORE_REQUESTS`, `OFFCORE_REQUESTS_OUTSTANDING`, `RTM_RETIRED`, `TX_EXEC`, and `TX_MEM`. The largest family is `OCR.*`, with 38 offcore-response aliases that program Intel offcore response MSRs for specific request and response filters.

## Important APIs, Types, And Data

The file uses the perf PMU event JSON schema consumed by `jevents.py`. Fields include `EventName`, `EventCode`, `UMask`, `Counter`, `CounterMask`, `SampleAfterValue`, `MSRIndex`, `MSRValue`, `Data_LA`, `Deprecated`, `BriefDescription`, and `PublicDescription`.

`EventName` is the user-facing alias. `EventCode`, `UMask`, `Counter`, and optional `CounterMask` become the perf config string. `SampleAfterValue` provides default sampling periods, commonly `100003` for memory and offcore events, `200003` for transactional events, and `1000003` for `TX_EXEC` entries. `MSRIndex` and `MSRValue` are critical for `OCR.*` and `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_*`: they program offcore response MSRs `0x1a6,0x1a7` or load-latency MSR `0x3F6`. `Data_LA` on load-latency entries marks load-address precise sampling support. `Deprecated` marks `OFFCORE_REQUESTS_OUTSTANDING.L3_MISS_DEMAND_DATA_RD` as a compatibility alias that should no longer be preferred.

The load-latency family uses `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_4`, `_8`, `_16`, `_32`, `_64`, `_128`, `_256`, and `_512` with the same event selector and different MSR latency thresholds. The offcore-response aliases distinguish demand code reads, demand data reads, demand RFOs, L1D/software prefetches, L3 hardware prefetches, ITOMs, miscellaneous traffic, all prefetches, reads to core, streaming writes, and write-estimate traffic across DRAM, PMM/remote memory, local/remote sockets, and SNC-specific placement.

## Control Flow

At build time, `jevents.py` parses the JSON array into generated PMU event entries for the Ice Lake Xeon table. It lowercases aliases, converts `EventCode` and `UMask` into event config fields, preserves `CounterMask` as `cmask`, preserves default periods, and records MSR programming requirements.

At runtime, `perf list` displays these aliases. `perf stat -e` or metrics from `icx-metrics.json` can request the aliases, after which perf resolves them to PMU events and asks the kernel to program the hardware counter and any required offcore/load-latency MSR filter. For `OCR.*`, the same base event code pair `0xB7, 0xBB` and `UMask 0x1` is specialized almost entirely through `MSRValue`, so correct runtime behavior depends on preserving that extra register programming metadata.

## State And Persistence Behavior

The JSON file persists static event metadata only. Runtime counter values, load-latency samples, TSX abort counts, and offcore response counts live in hardware PMU state and perf file descriptors. MSR filters are not persisted by this file at runtime; they are declarative fields that perf applies when the event is opened.

`Deprecated` is persistent metadata for user-facing compatibility. It keeps an older alias visible while signaling that `OFFCORE_REQUESTS_OUTSTANDING.L3_MISS_DEMAND_DATA_RD_GE_6` or `CYCLES_WITH_L3_MISS_DEMAND_DATA_RD` provide clearer semantics.

## Dependencies And Integration Points

This file integrates with `icx-metrics.json`, especially memory bandwidth, latency, NUMA, store, streaming-store, and top-down memory-bound formulas. It also integrates with `jevents.py`, generated `pmu-events.c`, perf alias lookup, kernel x86 PMU support for Ice Lake server, offcore response MSR handling, precise load-latency sampling support, and TSX event availability.

The model mapping in `arch/x86/mapfile.csv` selects this directory for Ice Lake Xeon model IDs. User-facing paths include `perf list`, `perf stat -e OCR.*`, `perf mem`-style workflows where precise load address matters, and `perf stat -M` metrics that indirectly expand these events.

## Risks And Edge Cases

The highest risk is incorrect MSR filter metadata. Most `OCR.*` entries share event selectors, so a wrong `MSRValue` silently counts the wrong request or response class. SNC, local socket, remote socket, DRAM, PMM, and CXL-style memory distinctions are topology-sensitive; descriptions must remain precise because the same alias can mean different locality scopes when Sub-NUMA Cluster mode is enabled.

Load-latency events use randomized load selection and threshold MSR programming, so users can misread them as exact counts of all loads above a threshold. TSX events may be unavailable or disabled on some systems. Deprecated aliases should remain parseable but should not be used as the preferred semantic source. Counter masks on outstanding-request events distinguish "at least one" from "at least six" outstanding L3-miss demand reads; losing `CounterMask` changes event meaning.

## Test Signals

Validation includes `jq empty`, x86 `jevents.py` generation, `perf test pmu-events`, and generated event-string inspection for `MSRIndex`/`MSRValue`, `CounterMask`, `Data_LA`, and `Deprecated`. Runtime smoke tests should check `perf list` visibility for representative aliases such as `MEM_TRANS_RETIRED.LOAD_LATENCY_GT_128`, `OCR.DEMAND_DATA_RD.LOCAL_DRAM`, `OCR.READS_TO_CORE.REMOTE_MEMORY`, `OFFCORE_REQUESTS_OUTSTANDING.L3_MISS_DEMAND_DATA_RD_GE_6`, `RTM_RETIRED.START`, and `TX_MEM.ABORT_CONFLICT`.

Behavioral checks should run memory-locality and memory-bandwidth workloads, pointer-chasing latency tests, TSX tests on TSX-capable systems, and SNC or multi-socket locality tests where hardware is available. For non-hardware CI, generated-table and alias-expansion tests are the main signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelakex/memory.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelakex/metricgroups.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelakex/metricgroups.json

## Purpose

This file defines 139 metric-group descriptions for Ice Lake Xeon perf metrics. It is a lookup table from group name to human-readable description, used to make `perf list metricgroups` and grouped metric output understandable. The groups mirror the group tags used by `icx-metrics.json`, especially Intel top-down microarchitecture analysis groups and issue-oriented bottleneck categories.

The file covers broad categories such as `Backend`, `Frontend`, `Bad`, `Mem`, `Offcore`, `Pipeline`, `Power`, `Server`, `SoC`, `Summary`, and `HPC`; top-down levels `TopdownL1` through `TopdownL6` and `tma_L1_group` through `tma_L6_group`; and many specific top-down contributor groups such as `tma_memory_bound_group`, `tma_fetch_latency_group`, `tma_ports_utilization_group`, `tma_dtlb_load_group`, `tma_store_stlb_miss_group`, and `tma_issue*` groups.

## Important APIs, Types, And Data

Unlike event and metric files, this JSON is an object rather than an array. Keys are metric group names and values are descriptions. Most values are either "Grouping from Top-down Microarchitecture Analysis Metrics spreadsheet", "Metrics for top-down breakdown at level N", "Metrics contributing to <category> category", or "Metrics related by the issue $<issue>".

The effective API is the `_metricgroups` dictionary built by `jevents.py`. The loader treats files ending in `metricgroups.json` specially, reading each key/value pair into a generated string table. Metric and event records are not created from this file; it provides descriptive metadata consumed by perf list and metric group UI paths.

## Control Flow

At build time, `jevents.py` detects `metricgroups.json`, parses the object, and stores each group description in a process-global metric-group map. Later it emits a generated `metricgroups` lookup table and `describe_metricgroup(...)` helper that binary-searches sorted group names in the generated C string table.

At runtime, `perf list metricgroups` and metric-list paths use the generated descriptions when displaying groups. When a metric in `icx-metrics.json` references a group through its `MetricGroup` field, this file gives that group a label. It does not decide group membership; membership remains in each metric record.

## State And Persistence Behavior

The file persists static group-description metadata only. It stores no counter state and no generated state. At build time, its contents are folded into generated C tables. At runtime, the generated table is read-only.

Because keys are stable user-facing names, edits are persistent compatibility changes. Removing or renaming a group description does not remove the metrics themselves, but it can make group discovery less useful and can affect scripts that inspect `perf list --raw-dump metricgroups`.

## Dependencies And Integration Points

The primary dependency is consistency with `MetricGroup` values in `icx-metrics.json`. The file also integrates with `jevents.py`, generated `pmu-events.c`, `builtin-list.c`, `python/ilist.py`, `Documentation/perf-list.txt`, `Documentation/perf-stat.txt`, and tests that iterate all metric groups, including `tests/shell/stat_all_metricgroups.sh`.

The group names reflect Intel's top-down spreadsheet taxonomy, so they depend on the naming conventions used by Intel metric generation scripts and manually maintained perf metrics. The descriptions are model-local in the `icelakex` directory but include generic top-down category names used across Intel server generations.

## Risks And Edge Cases

Schema shape is a risk: this file must remain a JSON object, not an array. Duplicate keys cannot be represented reliably in JSON and would be collapsed by parsers. A typo in a key creates a description for a group that no metric uses, while a typo in `icx-metrics.json` can leave a real group without a description.

There are intentionally similar names, including `MachineClears` and `Machine_Clears`, `MemoryBW` and `Memory_BW`, `MemoryLat` and `Memory_Lat`, plus `TopdownL*`, `TmaL*`, and `tma_L*_group`. Simplifying or deduplicating those names could break existing group references. The many `tma_issue*` keys contain issue tags such as `$issueBW` and `$issueSyncxn`; these are descriptions, not expression variables.

## Test Signals

Use `jq type` to confirm the file is an object and run x86 `jevents.py` generation to confirm metric-group table emission. Runtime checks include `perf list metricgroups`, `perf list --raw-dump metricgroups`, and `perf stat -M` for representative groups such as `TopdownL1`, `TopdownL4`, `MemoryBW`, `Offcore`, `tma_memory_bound_group`, and `tma_issueBW`.

Cross-file validation should compare the set of `MetricGroup` tokens in `icx-metrics.json` against keys in this file and flag missing or unused descriptions. Tests should preserve case-sensitive distinct group names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelakex/metricgroups.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelakex/other.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelakex/other.json

## Purpose

This file defines five miscellaneous Ice Lake Xeon core PMU events that do not fit cleanly into the main cache, pipeline, frontend, virtual-memory, or memory event files. Three events report AVX/turbo license level residency through `CORE_POWER.*`, and two events provide offcore-response aliases for miscellaneous requests and streaming writes with any response.

The events are `CORE_POWER.LVL0_TURBO_LICENSE`, `CORE_POWER.LVL1_TURBO_LICENSE`, `CORE_POWER.LVL2_TURBO_LICENSE`, `OCR.OTHER.ANY_RESPONSE`, and `OCR.STREAMING_WR.ANY_RESPONSE`. They support power/frequency analysis and derived store/offcore metrics in `icx-metrics.json`, including AVX license utilization and streaming-store bottleneck estimates.

## Important APIs, Types, And Data

The file uses the standard perf PMU event JSON array schema. Fields include `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `MSRIndex`, `MSRValue`, `BriefDescription`, and `PublicDescription`.

The `CORE_POWER.*` entries share `EventCode 0x28` and counters `0,1,2,3`, with masks `0x7`, `0x18`, and `0x20` for license levels 0, 1, and 2. Their descriptions distinguish baseline/non-AVX and lower-current vector code, high-current AVX2 or low-current AVX-512 behavior, and high-current AVX-512 behavior.

The `OCR.*.ANY_RESPONSE` entries share the offcore response event codes `0xB7, 0xBB`, `UMask 0x1`, counters `0,1,2,3`, and offcore MSRs `0x1a6,0x1a7`. `OCR.OTHER.ANY_RESPONSE` uses `MSRValue 0x18000`; `OCR.STREAMING_WR.ANY_RESPONSE` uses `MSRValue 0x10800`.

## Control Flow

At build time, `jevents.py` parses the five records, converts selector fields into generated event strings, and preserves MSR programming metadata for the offcore entries. At runtime, perf resolves the aliases from the generated Ice Lake Xeon event table.

The power events are counted directly by the core PMU. The offcore entries require perf/kernel handling for the offcore response MSRs, just like the `OCR.*` entries in `memory.json`. Metrics in `icx-metrics.json` can then consume these aliases as formula inputs.

## State And Persistence Behavior

The file stores static metadata only. Runtime residency cycles and offcore request counts are produced by hardware counters during a perf measurement interval. The MSR fields are declarative and are applied when perf opens the event; they are not persistent runtime state in this JSON.

## Dependencies And Integration Points

This file integrates with `icx-metrics.json` power and streaming-store formulas, `jevents.py`, generated `pmu-events.c`, perf alias lookup, and kernel PMU/offcore MSR support. It is selected through the `icelakex` x86 mapfile entry and exposed through `perf list` and `perf stat -e`.

The `CORE_POWER.*` entries are semantically tied to Intel AVX turbo license behavior. The `OCR.*` entries share the same offcore response machinery and risks as `memory.json`.

## Risks And Edge Cases

For power-license events, users can confuse residency in a license level with actual package frequency or throttling; these counters indicate the class of power delivery/turbo schedule in use, not a complete power model. Incorrect masks would swap license levels and mislead AVX frequency analysis.

For `OCR.*.ANY_RESPONSE`, the main risk is MSR filter correctness. The base event selectors are not enough to identify miscellaneous or streaming-write traffic, so `MSRValue` must be preserved. These events may compete with other offcore-response events for limited counters and MSR filter slots.

## Test Signals

Validation includes `jq empty`, `jevents.py` generation, and generated-table checks for masks and MSR metadata. Runtime smoke tests should verify that `perf list` exposes the three `CORE_POWER` aliases and two `OCR` aliases on Ice Lake Xeon tables. Workload tests can compare license-level counts under scalar, AVX2, and AVX-512 kernels, and compare streaming-write counts under non-temporal store workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelakex/other.json -->
