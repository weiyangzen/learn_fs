# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlake/adl-metrics.json

## Purpose

This file is the Alder Lake PMU metric table consumed by Linux `perf`'s `pmu-events` build pipeline. It is not executable source code; it is data-driven performance-analysis logic expressed as JSON records. Each record defines a derived metric that `perf stat -M ...` or metric groups can expose on Alder Lake systems mapped by `tools/perf/pmu-events/arch/x86/mapfile.csv` to the `alderlake` event directory.

The file contains 332 metric records. The first unscoped records cover package/core C-state residency, SMI accounting, and TSX transaction summaries. The bulk of the file defines Intel Top-Down Microarchitecture Analysis metrics for Alder Lake hybrid CPUs:

- `cpu_atom` metrics for E-core/Atom PMU domains, including Level 1 through Level 3 topdown categories and Atom-specific info metrics.
- `cpu_core` metrics for P-core/Core PMU domains, including Topdown L1 through L6, frontend/backend/memory/branch/core bottleneck trees, system summary metrics, and detailed info metrics.
- Uncore, MSR, power, and synthetic symbols inside metric expressions, such as `msr@tsc@`, `power@energy-pkg@`, `UNC_CLOCK.SOCKET`, and `duration_time`.

## Important Schema Fields

The records follow the perf PMU events JSON schema parsed by `tools/perf/pmu-events/jevents.py`:

- `MetricName`: stable metric identifier. There are 318 unique names; 14 names intentionally appear twice because the same logical metric is defined separately for `cpu_atom` and `cpu_core` domains, such as `tma_backend_bound`, `tma_bad_speculation`, `tma_frontend_bound`, and `tma_retiring`.
- `MetricExpr`: perf metric expression. It can reference raw PMU events, MSR events, power events, uncore events, constants, runtime variables, helper predicates, and other metrics by name.
- `MetricGroup`: semicolon-separated group tags used for discovery and group selection. Common groups include `TopdownL4`, `tma_L4_group`, `TopdownL3`, `Mem`, `Offcore`, `MemoryTLB`, `Fed`, `Pipeline`, `MemoryBW`, and `Power`.
- `MetricThreshold`: boolean expression used by perf to flag noteworthy metric values. `jevents.py` stores this string without parsing it because threshold precedence differs from normal metric expression precedence.
- `ScaleUnit`: presentation scaling, most often `100%` for ratios.
- `Unit`: PMU domain selector, mainly `cpu_atom` or `cpu_core`. Records without `Unit` are package/MSR/power-style metrics that are not limited to a single hybrid core PMU domain.
- `MetricgroupNoGroup` and `DefaultMetricgroupName`: control default group behavior for high-level Topdown and Default metrics.
- `MetricConstraint`: event scheduling constraints. This file uses `NO_GROUP_EVENTS`, `NO_GROUP_EVENTS_NMI`, and `NO_THRESHOLD_AND_NMI` on metrics whose underlying counters should not be scheduled in normal grouped or threshold/NMI contexts.
- `BriefDescription` and `PublicDescription`: user-facing metric help. `PublicDescription` is present on many complex Core metrics and explains sampling hints or tuning interpretations.

## Metric Families

The opening platform metrics calculate power-state and interrupt summaries:

- Package/core C-state residency metrics divide `cstate_pkg@...@` or `cstate_core@...@` residency counters by `msr@tsc@`.
- SMI metrics expose SMI count and a percentage of cycles lost to SMI using `msr@smi@`, `msr@aperf@`, and `cycles`.
- TSX metrics use conditional expressions and `has_event(...)` checks to avoid referencing unavailable transaction events on unsupported systems.

The `cpu_atom` block defines the Atom-side topdown model. Level 1 metrics derive retiring, frontend bound, backend bound, and bad speculation from `TOPDOWN_*` events divided by `5 * CPU_CLK_UNHALTED.CORE`. Lower levels split these into branch mispredicts, machine clears, resource/core bound, frontend latency/bandwidth, ITLB/Icache issues, scheduler limits, serialization, and related info metrics such as IPC, CPI, uops per instruction, branch mix, memory mix, and load/store bottlenecks.

The `cpu_core` block is larger and encodes the P-core hierarchy. It starts with uncore frequency and Topdown L1 categories, then expands into synthetic bottleneck totals such as `tma_bottleneck_big_code`, `tma_bottleneck_mispredictions`, `tma_bottleneck_data_cache_memory_bandwidth`, `tma_bottleneck_data_cache_memory_latency`, `tma_bottleneck_memory_data_tlbs`, `tma_bottleneck_memory_synchronization`, `tma_bottleneck_compute_bound_est`, `tma_bottleneck_irregular_overhead`, and `tma_bottleneck_useful_work`. It then defines detailed frontend, memory hierarchy, branch, compute, floating-point, integer-vector, port utilization, store, TLB, synchronization, and system-info metrics.

## Control Flow and Evaluation

The JSON itself has no runtime control flow, but its expressions form a dependency graph evaluated by perf's metric engine.

Build-time flow:

1. `tools/perf/pmu-events/Build` generates `$(OUTPUT)pmu-events/pmu-events.c` by running `pmu-events/jevents.py`.
2. `jevents.py` traverses `pmu-events/arch/<arch>`, ignores non-JSON files and `metricgroups.json`, and loads this file as part of the `alderlake` model directory.
3. For each JSON record, `JsonEvent` copies schema fields and parses `MetricExpr` with `metric.ParsePerfJson(...).Simplify()`.
4. The generated C table is compiled into perf and mapped to Alder Lake CPUID patterns through `arch/x86/mapfile.csv`, currently `GenuineIntel-6-(97|9A|B7|BA|BF),v1.37,alderlake,core`.

Runtime flow:

1. perf identifies the running CPU and selects the generated metric table.
2. A requested metric or metric group pulls in its `MetricExpr`.
3. The metric parser resolves raw event aliases, PMU names, runtime variables, and references to other metrics.
4. perf schedules the underlying events subject to PMU domain, grouping, and `MetricConstraint` restrictions.
5. After counting, perf evaluates expressions and threshold strings, applies `ScaleUnit`, and prints metric values.

The expressions include inline conditional control logic, for example `A if condition else B`, `has_event(...)`, `#SMT_on`, `max(...)`, and `min(...)`. This is important because many entries are approximations that guard unavailable events, SMT-specific formulas, or values that must not become negative.

## State and Persistence

This file persists metric definitions in the source tree. It does not maintain runtime state, write files, or mutate system counters. Its persistent effects are indirect:

- During a perf build, parsed definitions are embedded into generated `pmu-events.c`.
- At runtime, perf uses the embedded table to choose event encodings and formulas for the active CPU.
- Metric values are ephemeral results of current PMU/MSR/uncore/power counter readings and `duration_time`.

Because this is declarative state, changes to names, groups, expressions, or units are user-visible API changes for perf users and scripts that invoke metrics by name.

## Dependencies and Integration Points

Primary integration points are:

- `tools/perf/pmu-events/jevents.py`: loads records, maps fields, parses `MetricExpr`, stores thresholds, and emits C data.
- `tools/perf/pmu-events/metric.py`: parses and simplifies the metric expression language used in `MetricExpr`.
- `tools/perf/pmu-events/pmu-events.h`: defines generated metric table structures consumed by perf.
- `tools/perf/pmu-events/arch/x86/mapfile.csv`: maps Alder Lake CPUIDs to this directory.
- Neighboring Alder Lake event files, such as `cache.json`, `frontend.json`, `memory.json`, `pipeline.json`, `virtual-memory.json`, `uncore-memory.json`, and `metricgroups.json`, which must provide event aliases and group descriptions referenced by these metric expressions.
- perf metric runtime code under `tools/perf`, especially metric group parsing and event scheduling, which resolves generated table entries and schedules PMU events.

The file depends on several counter namespaces:

- Hybrid PMUs: `cpu_atom@...@` and `cpu_core@...@`.
- MSR PMU aliases: `msr@tsc@`, `msr@aperf@`, `msr@smi@`.
- C-state PMUs: `cstate_pkg@...@` and `cstate_core@...@`.
- RAPL/power PMU: `power@energy-pkg@`.
- Uncore aliases: `UNC_*` symbols used in memory bandwidth, latency, and uncore frequency metrics.
- perf synthetic variables: `duration_time`, `#SMT_on`, `#num_cpus_online`, and `#num_dies`.

## Risks and Edge Cases

- Hybrid duplicate names are intentional but risky. A shared name like `tma_backend_bound` can mean different formulas depending on `Unit`; expression resolution must keep `cpu_atom` and `cpu_core` contexts separate.
- Cross-metric dependency errors can break large groups. Many high-level bottleneck metrics depend on lower-level `tma_*` names; renaming or deleting one metric can invalidate unrelated groups.
- Division by zero is common in performance formulas. Some entries use `if`, `max`, or `min` guards, but many ratios assume nonzero denominator counters. perf's metric evaluator must handle zero or missing counts gracefully.
- Event availability varies by kernel, PMU exposure, privilege, BIOS, TSX availability, uncore driver support, and hybrid core type. The `has_event(...)` guards cover TSX cases, but most hardware-event references assume correct Alder Lake PMU alias availability.
- Scheduling pressure is high. Complex metrics and groups pull many counters, which can trigger multiplexing. The file includes `tma_info_system_mux` as an accuracy signal, and several `MetricConstraint` fields try to avoid invalid grouping.
- Threshold strings are not parsed by `jevents.py`. Syntax or precedence mistakes may only surface later in perf metric handling.
- Some formulas are heuristics or approximations, noted in descriptions for metrics like memory bandwidth, memory latency, DTLB, split loads, false sharing, and bottleneck totals. They can exceed parent categories or overlap sibling categories.
- Uncore and power metrics rely on system-wide counters. On machines without the expected uncore PMUs or with restricted permissions, SoC, DRAM bandwidth, power, and uncore frequency metrics may be missing or misleading.

## Test Signals

Useful validation signals for this file are:

- JSON validity: `jq empty sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlake/adl-metrics.json`.
- Record and schema sanity: `jq 'length'` should report 332 records, and `MetricName` should be present on every record.
- Expression parsing: a perf build or direct `jevents.py` generation should parse every `MetricExpr` through `metric.ParsePerfJson(...).Simplify()` without exceptions.
- Duplicate-name review: duplicates should remain limited to cross-domain `cpu_atom`/`cpu_core` metrics, not accidental same-domain duplicates.
- PMU alias resolution: `perf list metric` and `perf list TopdownL1` on Alder Lake should expose expected Default/Topdown groups.
- Runtime metric smoke tests: `perf stat -M tma_backend_bound,tma_frontend_bound,tma_retiring -- sleep 1` should resolve on the relevant PMU domains.
- Multiplexing quality: `tma_info_system_mux` near 1.0 indicates acceptable PerfMon multiplexing accuracy; large deviations indicate counter pressure.
- Topdown consistency: Level 1 categories should generally sum close to 1 for a PMU domain, allowing for formula approximations, guards, and multiplexing noise.
- Constraint-sensitive metrics should be tested with and without grouped scheduling to verify `NO_GROUP_EVENTS`, `NO_GROUP_EVENTS_NMI`, and `NO_THRESHOLD_AND_NMI` behavior.
