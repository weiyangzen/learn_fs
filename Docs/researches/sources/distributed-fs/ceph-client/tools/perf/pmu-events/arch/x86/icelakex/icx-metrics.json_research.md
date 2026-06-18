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
