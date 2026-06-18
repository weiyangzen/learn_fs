# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/jaketown/jkt-metrics.json

## Purpose
This JSON file defines Jake Town derived perf metrics. Its 72 metric descriptors compute package and core C-state residency, uncore frequency, SMI activity, top-down microarchitecture categories, memory and frontend bottlenecks, floating-point mix, pipeline information ratios, and summary signals. Unlike event files, this file combines raw events, constants, conditionals, and thresholds into named metrics for `perf stat -M` style workflows.

## Important APIs, Types, And Functions
The file is declarative metric metadata. Key fields are `MetricName`, `MetricExpr`, `MetricGroup`, `MetricThreshold`, `MetricConstraint`, `MetricgroupNoGroup`, `ScaleUnit`, `BriefDescription`, and `PublicDescription`. Metric groups include `Power`, `SoC`, `smi`, `TopdownL1` through `TopdownL5`, `Backend`, `Frontend`, `MemoryBound`, `FetchLat`, `FetchBW`, `Compute`, `Flops`, `HPC`, `Pipeline`, and summary categories. Many metrics use `tma_` names and reference other metrics, creating a dependency graph rather than independent event aliases.

## Control Flow
There is no imperative control flow, but metric evaluation has dependency flow. Perf parses `MetricExpr`, schedules the referenced events and prerequisite metrics, evaluates arithmetic and conditionals such as SMT-aware formulas, applies scaling units, and can compare results to `MetricThreshold`. Parent top-down metrics such as `tma_backend_bound`, `tma_bad_speculation`, `tma_frontend_bound`, and `tma_retiring` feed lower-level metrics including branch mispredicts, DSB switches, DTLB load cost, DRAM bound, FP vector mix, and port utilization.

## State And Persistence
The file persists formulas, grouping labels, constraints, and thresholds. It does not store measured results or previous evaluations. Runtime metric state is produced by perf from active counter values, duration, topology constants, and model helper variables such as `#SMT_on`, `#num_dies`, and top-down slot denominators. Constraints such as `NO_GROUP_EVENTS` and `NO_GROUP_EVENTS_SMT` affect scheduling policy rather than persistent state.

## Dependencies And Integration Points
The metrics depend on Jake Town event aliases from cache, frontend, floating-point, pipeline, branch, memory, and MSR/cstate sources. Expressions reference raw events such as `BR_MISP_RETIRED.ALL_BRANCHES`, `MACHINE_CLEARS.COUNT`, `FP_COMP_OPS_EXE.*`, `DTLB_LOAD_MISSES.*`, `MEM_LOAD_UOPS_RETIRED.*`, `DSB2MITE_SWITCHES.PENALTY_CYCLES`, MSR aliases, and synthetic top-down helper metrics. The file integrates with perf's metric parser, event scheduler, threshold display, and metric group selection.

## Risks And Edge Cases
Metric dependency and naming consistency are the main risks. A referenced event missing from the Jake Town set will make the metric unusable even though this JSON is syntactically valid. Formulas can divide by zero or produce misleading values when workloads do not retire relevant events; some use conditionals to mitigate that. SMT-specific formulas and constraints must match hardware behavior. Several FP metrics note possible overcounting, so users should not treat them as exact FLOP rates. Thresholds are heuristic guidance, not pass/fail correctness.

## Test Signals
Validation includes JSON syntax checks, perf metric parser acceptance, no unresolved event or metric references, and successful `perf list --metrics` output for Jake Town. Runtime tests should run representative `perf stat -M` groups, verify top-down L1 categories sum sensibly, confirm Power and SMI metrics resolve MSR dependencies, and exercise metrics with SMT on and off. Regression tests should include expression parsing for escaped cstate names, conditionals, `min()`, constants such as `#num_dies`, and metric constraints.
