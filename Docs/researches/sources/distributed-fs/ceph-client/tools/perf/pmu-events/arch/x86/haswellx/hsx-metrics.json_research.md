<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswellx/hsx-metrics.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswellx/hsx-metrics.json

## Purpose

`hsx-metrics.json` defines 162 derived metric records for the Haswell-X/Haswell-EP x86 PMU model used by `perf stat -M`, metric groups, and top-down microarchitecture analysis. It turns raw architectural, model-specific, uncore, C-state, and synthetic perf events into human-oriented ratios, percentages, bandwidth values, frequencies, latencies, and top-down bottleneck categories.

The file is not runtime code. Its effective API is the perf PMU metric JSON schema: each array element may provide `MetricName`, `MetricExpr`, `BriefDescription`, `PublicDescription`, `MetricGroup`, `MetricgroupNoGroup`, `MetricConstraint`, `MetricThreshold`, and `ScaleUnit`. During the perf build, PMU event tooling parses these fields into generated metric tables for the `haswellx` architecture directory.

## Important schema entries and metric families

The highest-level metrics include package/core C-state residency (`C2_Pkg_Residency`, `C3_Core_Residency`, `C6_Pkg_Residency`, `C7_Core_Residency`), CPI/frequency/utilization (`cpi`, `cpu_operating_frequency`, `cpu_utilization`, `UNCORE_FREQ`, `uncore_frequency`), cache/TLB miss-per-instruction metrics, memory and I/O bandwidth metrics, NUMA locality metrics, SMI counters, and the full TMA hierarchy.

Top-down level 1 metrics are represented by `tma_frontend_bound`, `tma_bad_speculation`, `tma_retiring`, and `tma_backend_bound`. They depend on raw events such as `IDQ_UOPS_NOT_DELIVERED.CORE`, `UOPS_RETIRED.RETIRE_SLOTS`, `UOPS_ISSUED.ANY`, `BR_MISP_RETIRED.ALL_BRANCHES`, and synthetic helper metrics like `tma_info_thread_slots`. Lower levels break down frontend issues, speculation, backend memory/core bounds, DRAM/local/remote memory, port utilization, assists, machine clears, lock latency, store forwarding, split loads/stores, TLB behavior, and instruction mix.

Uncore formulas are important integration points. Examples include `memory_bandwidth_total = (UNC_M_CAS_COUNT.RD + UNC_M_CAS_COUNT.WR) * 64 / 1e6 / duration_time`, `qpi_data_transmit_bw = UNC_Q_TxL_FLITS_G0.DATA * 8 / 1e6 / duration_time`, and LLC miss latency expressions using `cbox@UNC_C_TOR_OCCUPANCY...@`, `cbox@UNC_C_TOR_INSERTS...@`, `UNC_C_CLOCKTICKS`, `#num_cores`, and `#num_packages`.

## Control flow and evaluation model

There is no imperative control flow in the JSON. Perf's generated metric engine treats `MetricExpr` as an expression graph. Raw event aliases, constants, runtime variables such as `duration_time`, topology variables such as `#num_cores`, `#num_packages`, and `#SMT_on`, and references to other metric names are resolved while a metric group is scheduled and evaluated.

Some expressions contain conditional forms, for example `if #SMT_on` and `if tma_info_thread_ipc > 1.8 else ...`, plus `min(...)` and arithmetic over multiple raw events. This makes dependency ordering and grouping significant: helper metrics such as `tma_info_thread_slots`, `tma_info_thread_ipc`, `tma_info_system_time`, and uncore frequencies feed many visible metrics.

## State and persistence behavior

The file persists static performance model metadata in the source tree. It does not store measured counter values, machine state, or user configuration. State at runtime lives in perf's event scheduler, counters, topology detection, and metric expression evaluator. `MetricConstraint: NO_GROUP_EVENTS` appears on metrics that cannot safely be scheduled as a normal grouped event set, which affects how perf multiplexes and validates counters during collection.

## Dependencies and integration points

Metrics depend on event aliases defined in neighboring Haswell-X JSON files, common x86 PMU event files, and uncore PMUs exposed by the kernel. Important dependencies include core events from `pipeline.json`, memory/offcore events from `memory.json`, OS/lock events from `other.json`, and group names described in `metricgroups.json`.

The `MetricGroup` field integrates metrics with user-facing group selectors. It includes legacy group names such as `Summary`, `Power`, `Mem`, `MemoryBW`, `Offcore`, `Pipeline`, `TopdownL1` through `TopdownL6`, and TMA-specific groups such as `tma_L1_group`, `tma_backend_bound_group`, `tma_issueBW`, and `tma_issueSyncxn`. `MetricgroupNoGroup` is used to expose top-down group placement while avoiding automatic grouping for selected entries.

## Risks and maintenance notes

Metric correctness is tightly coupled to event encodings and Haswell-X microarchitecture details. If a raw event alias is renamed or removed in another JSON file, dependent `MetricExpr` strings fail late in perf metric parsing or at runtime. Uncore formulas are especially topology-sensitive because they use socket/core variables and PMU-specific aliases.

Expression complexity is a risk. Several TMA formulas nest conditionals, `min(...)`, SMT-sensitive paths, and helper metrics. Small syntax errors in escaped event names, filter syntax, or parentheses can break metric generation. Thresholds are advisory but user-visible; stale thresholds can mislead performance triage even when event collection works.

Multiplexing and grouping are also risk areas. `tma_info_system_mux` explicitly measures multiplexing accuracy, while `NO_GROUP_EVENTS` warns that some formulas should avoid strict grouped scheduling. Tests should verify both JSON validity and actual `perf stat -M` scheduling on Haswell-X-compatible systems or fixtures.

## Test signals

Useful validation includes JSON parsing with `jq`, perf's PMU event table generation, metric expression parser tests, and command-level smoke tests such as `perf list metric`, `perf stat -M TopdownL1`, `perf stat -M memory_bandwidth_total`, and `perf stat -M tma_info_system_mux` on matching hardware. Cross-file tests should confirm every event alias referenced by `MetricExpr` is resolvable and every `MetricGroup` name has an expected description in `metricgroups.json` or is intentionally implicit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswellx/hsx-metrics.json -->
