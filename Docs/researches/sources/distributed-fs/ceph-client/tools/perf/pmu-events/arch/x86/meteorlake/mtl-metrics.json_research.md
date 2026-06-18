# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/meteorlake/mtl-metrics.json

## Purpose

`mtl-metrics.json` is the Meteor Lake metric catalog for Linux `perf`'s `pmu-events` pipeline. It is declarative source data, not executable code: each object defines a derived performance metric that can be exposed through `perf list`, `perf stat -M`, metric groups, and generated Python/perf APIs. The x86 PMU map binds `GenuineIntel-6-(AA|AC|B5),v1.20` to the `meteorlake` directory, so this file supplies the metric layer for those Meteor Lake models.

The file contains 340 metric objects. Ten entries have no `Unit` and cover package/core C-state residency, SMI accounting, and uncore frequency style values. The rest are hybrid PMU metrics: 87 entries target `cpu_atom` and 243 entries target `cpu_core`. The Atom block encodes E-core topdown and info metrics; the Core block is a larger P-core hierarchy with Topdown L1-L6, frontend, backend, memory, branch, compute, port, system, and bottleneck summaries.

## Important APIs, Types, And Data

The records use the standard perf metric JSON schema consumed by `tools/perf/pmu-events/jevents.py`:

- `MetricName`: stable user-visible identifier. There are 324 unique names; 16 names appear twice by design because the same logical metric is defined separately for `cpu_atom` and `cpu_core`, including `tma_backend_bound`, `tma_bad_speculation`, `tma_frontend_bound`, `tma_retiring`, `tma_branch_mispredicts`, `tma_core_bound`, `tma_icache_misses`, `tma_itlb_misses`, and system summary names.
- `MetricExpr`: expression language parsed by `metric.ParsePerfJson(...).Simplify()`. Expressions reference raw PMU aliases, MSR/cstate/power/uncore events, perf runtime variables, constants, helper functions, and other metrics.
- `MetricGroup`: semicolon-separated discovery and selection tags. Common groups include `Default`, `TopdownL1` through deeper `TopdownL*`, `tma_L*_group`, `Mem`, `MemoryBW`, `MemoryTLB`, `FetchBW`, `FetchLat`, `Pipeline`, `Power`, `Summary`, `Flops`, and issue-class tags.
- `MetricThreshold`: threshold string used for highlighting suspicious values. This file has 192 thresholds. `jevents.py` stores the threshold text without normal metric parsing because threshold operators have different precedence behavior.
- `ScaleUnit`: presentation scaling, often `100%` for ratios. Perf metric validation treats `1%` and `100%` metrics as percentage-range candidates.
- `Unit`: PMU domain selector. The values are mainly `cpu_atom` and `cpu_core`; absent units are package/MSR/system style metrics.
- `MetricConstraint`: event scheduling constraints. Meteor Lake uses `NO_GROUP_EVENTS` on `tma_data_sharing`, `tma_lock_latency`, and `tma_other_light_ops`; `NO_GROUP_EVENTS_NMI` on `tma_ports_utilization`; and `NO_THRESHOLD_AND_NMI` on `tma_ports_utilized_0` and `tma_ports_utilized_1`.
- `MetricgroupNoGroup` and `DefaultMetricgroupName`: default grouping controls for high-level Topdown and Default presentations.
- `BriefDescription` and `PublicDescription`: user-facing help text; public descriptions on complex metrics document interpretation limits and tuning meaning.

Metric families include power-state residency, SMI percentage/count, Atom topdown slot accounting, Atom branch/frontend/backend/resource/memory subtrees, Atom info ratios, Core uncore frequency, Core Topdown L1 summaries, synthetic bottleneck groups, frontend fetch bandwidth/latency, DSB/MITE/LSD, branch resteers and mispredicts, memory hierarchy and TLB breakdowns, synchronization/false-sharing/lock metrics, floating-point and integer-vector mix, port utilization, store/load operation utilization, and system summary metrics such as CPU utilization, SMT utilization, DRAM bandwidth, power, elapsed time, and multiplexing.

## Control Flow

The JSON has no local execution, but its expressions form a dependency graph evaluated by perf.

Build-time flow:

1. The perf build runs `tools/perf/pmu-events/jevents.py` for the x86 architecture.
2. `jevents.py` walks `pmu-events/arch/x86/meteorlake`, loads JSON records, and instantiates `JsonEvent` for each metric object.
3. `JsonEvent` copies metric fields, converts `MetricConstraint` with `convert_metric_constraint()`, parses `MetricExpr` via `metric.ParsePerfJson(...).Simplify()`, keeps `MetricThreshold` as text, and emits generated C strings for metric tables.
4. Generated `pmu-events.c` is compiled into perf and selected for Meteor Lake through `arch/x86/mapfile.csv`.

Runtime flow:

1. perf identifies the CPU model and chooses the Meteor Lake PMU table.
2. A requested metric or group resolves to one or more `MetricExpr` trees.
3. The metric engine resolves PMU-qualified events such as `cpu_core@...@` and `cpu_atom@...@`, MSR/cstate aliases such as `msr@tsc@`, and cross-metric references such as `tma_frontend_bound`.
4. perf schedules the required counters subject to PMU unit, hybrid core type, grouping limits, and `MetricConstraint` fields.
5. After sampling/counting, perf evaluates expressions, applies `ScaleUnit`, and evaluates threshold strings for display hints.

The expressions contain inline control behavior through conditionals and helpers such as `if ... else`, `max(...)`, `min(...)`, `has_event(...)`, `#SMT_on`, `#num_cpus_online`, `#num_dies`, and `duration_time`. That control is important for SMT-aware formulas, availability checks, negative-value clamps, and ratios that need bounded outputs.

## State And Persistence Behavior

This file persists metric definitions in the source tree. It does not write files, mutate kernel state, or hold runtime state. Its persistent effect occurs when the perf build embeds the parsed table into generated C data. Runtime metric values are ephemeral computations over current PMU, MSR, cstate, uncore, power, and wall-clock counter readings.

The metric names, groups, units, thresholds, constraints, and expressions are user-visible API. Scripts may call metrics by name or group, and users may rely on reported units and thresholds. Renames or formula changes are therefore behavior changes even though the file is declarative.

## Dependencies And Integration Points

Primary integration points are `tools/perf/pmu-events/jevents.py`, `tools/perf/pmu-events/metric.py`, generated `pmu-events.c`, `tools/perf/pmu-events/pmu-events.h`, `tools/perf/util/metricgroup.*`, `tools/perf/builtin-list.c`, and the x86 PMU mapfile. `builtin-list.c` can print `MetricGroup`, `MetricName`, `MetricExpr`, `MetricThreshold`, `ScaleUnit`, and descriptions back out as JSON, so this file influences both runtime counting and discovery output.

The file depends on neighboring Meteor Lake event catalogs for raw event aliases: `cache.json`, `frontend.json`, `memory.json`, `pipeline.json`, `floating-point.json`, `virtual-memory.json`, `other.json`, and uncore files. It also depends on `metricgroups.json` for group descriptions and on kernel PMU exposure for hybrid `cpu_core`/`cpu_atom` PMUs, MSR PMUs, cstate PMUs, RAPL/power PMUs, and uncore PMUs.

Important counter namespaces in expressions include `cpu_atom@...@`, `cpu_core@...@`, `msr@tsc@`, `msr@aperf@`, `msr@smi@`, `cstate_pkg@...@`, `cstate_core@...@`, uncore aliases such as `UNC_CLOCK.SOCKET`, power events such as package energy, and synthetic perf variables including `duration_time`.

## Risks And Edge Cases

Hybrid duplicate metric names are intentional but fragile. Any resolver or validation logic that ignores `Unit` can mix Atom and Core formulas for names like `tma_backend_bound` or `tma_retiring`.

Cross-metric dependencies make local edits high blast-radius. High-level bottleneck metrics reference lower-level `tma_*` names; deleting or renaming one metric can break many groups even if JSON syntax remains valid.

Many formulas divide by cycle, instruction, event, or elapsed-time denominators. Some expressions clamp or guard values, but many assume nonzero counts. Idle workloads, unsupported events, permission restrictions, or multiplexing can produce zero or missing inputs.

Counter pressure is high for deep metric groups. The file includes `tma_info_system_mux` as an accuracy signal and uses several `MetricConstraint` fields, but complex Topdown and memory/system groups can still multiplex heavily or fail grouping.

Threshold strings are not parsed by `jevents.py`, so precedence mistakes or stale metric names may only surface during later perf metric handling.

Uncore, power, cstate, and MSR inputs are platform and privilege sensitive. Missing uncore PMUs, BIOS restrictions, disabled counters, hybrid topology differences, or containerized execution can make SoC, power, DRAM, C-state, and SMI metrics unavailable or misleading.

Several metrics are documented heuristics rather than exact partitions. Sibling bottleneck metrics can overlap, exceed parents, or depend on workload shape, SMT state, and event availability.

## Test Signals

Useful validation signals include:

- JSON validity: `jq empty sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/meteorlake/mtl-metrics.json`.
- Record sanity: `jq 'length'` should report 340 and every object should contain `MetricName`, `MetricExpr`, and `BriefDescription`.
- Domain sanity: current counts are 87 `cpu_atom`, 243 `cpu_core`, and 10 records without `Unit`.
- Duplicate-name review: duplicates should remain limited to the intended cross-domain Atom/Core metrics.
- Expression parsing: a perf build or direct `jevents.py` run should parse all `MetricExpr` values without exceptions.
- Constraint coverage: the six `MetricConstraint` entries should still map to valid enum values in generated data.
- Discovery smoke: `perf list --json` and `perf list TopdownL1` on a Meteor Lake-capable build should show the expected metric groups, descriptions, scale units, and thresholds.
- Runtime smoke: `perf stat -M tma_backend_bound,tma_frontend_bound,tma_retiring -- sleep 1` should resolve on available Meteor Lake PMU domains.
- Accuracy signals: Topdown L1 categories should generally sum close to 1 per PMU domain, and `tma_info_system_mux` should indicate low multiplexing error for validation workloads.
