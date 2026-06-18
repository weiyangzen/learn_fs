# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sapphirerapids/spr-metrics.json

## Purpose

This file is the Intel Sapphire Rapids perf metric catalog. It contains 323 JSON metric records used by Linux `perf` to expose derived measurements for SPR systems, including power and C-state residency, CPI/frequency/utilization, IO and memory bandwidth, NUMA/local/remote memory behavior, TLB and cache misses, SMI and TSX summaries, and a large Intel Topdown Microarchitecture Analysis hierarchy.

The file is declarative data rather than executable code. Its behavior comes from the perf PMU-events build and runtime metric engines: `jevents.py` parses each JSON object, converts `MetricExpr` into perf's metric expression representation, emits generated `pmu-events.c` metadata, and perf later schedules the referenced hardware, uncore, MSR, cstate, and pseudo events when a user asks for these metrics.

## Important APIs, Types, And Fields

Each object is a perf metric record. The effective API is the stable set of JSON keys consumed by `tools/perf/pmu-events/jevents.py`:

- `MetricName`: unique user-facing metric identifier such as `cpi`, `memory_bandwidth_total`, `tma_frontend_bound`, or `upi_data_transmit_bw`.
- `MetricExpr`: expression parsed by `metric.ParsePerfJson(...).Simplify()`. Expressions reference raw event names, pseudo events, constants, helper functions, and other metrics.
- `MetricGroup`: optional semicolon-delimited grouping used by `perf list` and `perf stat -M <group>`. Groups include `TopdownL1`, `TopdownL2`, `TopdownL3`, `TopdownL4`, `TopdownL5`, `TopdownL6`, `Default`, `Power`, `Summary`, `MemoryBW`, `MemoryLat`, `MemoryTLB`, `Offcore`, `Server`, `SoC`, `Flops`, `Branches`, `SMT`, `transaction`, `smi`, and many tuning issue groups such as `tma_issueBW`.
- `BriefDescription` and `PublicDescription`: short and long text shown by perf list/output tooling.
- `ScaleUnit`: optional unit/scaling marker, present on 180 records. Common units are percentages (`100%`), bandwidth (`1MB/s`), frequency (`1GHz`), per-instruction ratios, and cycle/transaction units.
- `MetricThreshold`: optional alert condition, present on 165 records. These strings are not parsed by `jevents.py` with the normal expression parser because logical operators have special precedence in threshold syntax.
- `MetricConstraint`: optional scheduling constraint. This file uses `NO_GROUP_EVENTS` for `tma_data_sharing`, `tma_lock_latency`, and `tma_other_light_ops`; `NO_GROUP_EVENTS_NMI` for `tma_ports_utilization`; and `NO_THRESHOLD_AND_NMI` for `tma_ports_utilized_0` and `tma_ports_utilized_1`.
- `DefaultMetricgroupName` and `MetricgroupNoGroup`: used by the topdown default presentation. They appear on the L1/L2 default metrics, for example `tma_frontend_bound`, `tma_backend_bound`, `tma_bad_speculation`, `tma_retiring`, and the default L2 children.

The expression vocabulary depends on perf metric parser support for arithmetic, comparisons, ternary-style `if ... else`, functions such as `min`, `max`, `has_event`, and `source_count`, constants like `#num_packages`, `#num_dies`, `#SMT_on`, and `#SYSTEM_TSC_FREQ`, and escaped PMU event forms such as `cpu@UOPS_EXECUTED.THREAD\,cmask\=1@`.

## Metric Coverage

The first block defines broad system and memory metrics: C1/C2/C6 residency, uncore frequency, CPI, CPU utilization, DTLB/ITLB walk ratios, IIO and CHA-derived IO bandwidth, L1/L2/LLC miss ratios and latencies, DRAM/PMEM bandwidth, NUMA local/remote reads, SMI counts/cycles, load/store ratios, and TSX transactional cycle summaries.

The majority of the file is the Sapphire Rapids TMA tree. L1 metrics split pipeline slots into `tma_frontend_bound`, `tma_bad_speculation`, `tma_backend_bound`, and `tma_retiring`. L2 and deeper metrics refine these into fetch latency/bandwidth, branch mispredicts and machine clears, memory and core bound, heavy and light operations, cache/TLB levels, DRAM/local/remote memory, lock and sharing effects, port pressure, divider, vector/scalar FP and integer work, microcode sequencer, C0 wait, serializing operations, split accesses, and store bottlenecks.

Several `tma_info_*` records are supporting informational metrics rather than direct topdown nodes. They calculate branch mix, IPC/CPI, core clocks, floating point operations per cycle, memory bandwidth and latency helper ratios, page-walk utilization, SMT utilization, kernel/system utilization, power, and other context used by thresholds or by users interpreting topdown bottlenecks.

## Control Flow

At build time, `tools/perf/pmu-events/Build` includes Intel metric JSON files as dependencies and invokes `jevents.py` to generate `pmu-events/pmu-events.c`. `arch/x86/mapfile.csv` maps `GenuineIntel-6-8F` to the `sapphirerapids` model directory, so these metrics are selected for Sapphire Rapids CPUs.

During generation, each JSON object is loaded into a `JsonEvent` in `jevents.py`. The parser copies descriptions, metric names, groups, constraints, default group fields, scale units, and thresholds. If `MetricExpr` is present, it is parsed and simplified through `metric.ParsePerfJson`. The generated C table is compiled into perf.

At runtime, perf resolves `perf list metrics`, `perf list metricgroups`, or `perf stat -M <metric-or-group>` against the generated table. It expands the metric expression into its event dependencies, schedules events subject to `MetricConstraint`, reads counters over the measurement interval, and evaluates the formulas using current event counts, elapsed `duration_time`, topology constants, and source counts for replicated PMUs.

## State And Persistence Behavior

The file itself stores static metric metadata only. It has no mutable state, no persistence layer, and no runtime side effects. Persistent behavior comes from being compiled into generated perf metadata.

Runtime metric values are ephemeral. They are derived from current hardware counter reads and measurement duration, and can vary with workload, CPU topology, SMT state, counter multiplexing, privilege settings, uncore PMU availability, and kernel support for events and pseudo-events. Some formulas explicitly guard optional events, for example TSX metrics use `has_event(cycles\-t)` to return zero when transactional counters are unavailable.

## Dependencies And Integration Points

This file depends on the surrounding Sapphire Rapids event definitions for every referenced core and uncore counter, including `CPU_CLK_UNHALTED.*`, `INST_RETIRED.*`, `TOPDOWN_*`, `MEM_*`, `BR_*`, `FP_*`, `UOPS_*`, `EXE_ACTIVITY.*`, `CYCLE_ACTIVITY.*`, `UNC_CHA_*`, `UNC_M_*`, `UNC_IIO_*`, `UNC_UPI_*`, `UNC_P_*`, cstate pseudo PMUs, and MSR pseudo events. It also depends on perf's built-in pseudo metrics such as `duration_time`, `topdown-fe-bound`, `topdown-be-bound`, `topdown-bad-spec`, `topdown-retiring`, and system constants.

The main integration points are:

- `pmu-events/arch/x86/mapfile.csv`, which selects the `sapphirerapids` directory for family/model `GenuineIntel-6-8F`.
- `pmu-events/jevents.py`, which parses the JSON schema and emits C metadata.
- `pmu-events/metric.py`, which defines generated metric objects and expression serialization/parsing conventions.
- perf runtime metric grouping and scheduling code, which interprets groups, thresholds, constraints, scale units, and metric references.
- sibling `sapphirerapids` JSON files that provide the raw event names used in formulas.

## Risks

The largest risk is name drift. `MetricExpr` strings are tightly coupled to raw event names and to other metric names; a rename or missing event in sibling JSON files can break parsing, generation, or runtime collection.

The formulas are also topology and PMU sensitive. Uncore formulas divide by `duration_time`, `#num_packages`, `#num_dies`, or `source_count(...)`, so incorrect topology discovery, unavailable uncore boxes, or multiplexing can produce misleading bandwidth and frequency results. Ratios can divide by zero when a workload does not exercise the denominator event.

Thresholds are user-visible guidance but are stored as strings with special parser handling. Syntax mistakes, incorrect precedence assumptions, or stale thresholds can silently reduce diagnostic value even when metric evaluation itself works.

Metric constraints matter for correctness. Metrics marked `NO_GROUP_EVENTS`, `NO_GROUP_EVENTS_NMI`, or `NO_THRESHOLD_AND_NMI` indicate event scheduling or NMI watchdog conflicts; ignoring those constraints can cause unsupported groupings, multiplexing artifacts, or failed measurements.

Many TMA formulas are model-specific approximations. Constants such as fixed latency estimates and derived weighting factors can be useful for bottleneck triage but should not be treated as exact architectural measurements across all workloads, stepping revisions, kernel versions, or virtualization environments.

## Test Signals

Useful static checks include parsing the source with `jq`, running perf PMU-events generation through the normal build rule, and running `tools/perf/pmu-events/metric_test.py` to catch expression parser regressions. High-value integration checks include building generated `pmu-events.c`, verifying `perf list metrics` and `perf list metricgroups` show Sapphire Rapids metrics on a matching host, and running focused commands such as `perf stat -M TopdownL1,cpi,memory_bandwidth_total,tma_memory_bound`.

Runtime validation should exercise both core and uncore paths. CPU-bound workloads should produce coherent topdown L1 percentages, memory streaming workloads should move DRAM bandwidth and memory-bound metrics, branch-heavy workloads should affect branch misprediction metrics, and IO/UPI/PMEM/CXL metrics should be checked only on systems where the relevant uncore PMUs and devices are present.
