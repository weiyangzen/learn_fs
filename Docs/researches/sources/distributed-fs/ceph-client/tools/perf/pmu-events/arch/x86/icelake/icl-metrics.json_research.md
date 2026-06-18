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
