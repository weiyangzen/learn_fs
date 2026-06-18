# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/ivybridge/ivb-metrics.json

## Purpose

`ivb-metrics.json` defines 131 Ivy Bridge perf metrics. It layers formulas over raw PMU aliases to provide package/core residency, SMI, topdown microarchitecture analysis, memory hierarchy, floating-point, pipeline, instruction mix, system utilization, and power/frequency summaries. This file is the main derived-analysis surface for Ivy Bridge in perf.

## Schema And API Surface

Entries are metric objects, not raw events. The key fields are `MetricName`, `MetricExpr`, `MetricGroup`, `BriefDescription`, `PublicDescription`, `ScaleUnit`, `MetricThreshold`, `MetricConstraint`, and `MetricgroupNoGroup`. Representative metrics include `C2_Pkg_Residency`, `UNCORE_FREQ`, `smi_cycles`, `tma_backend_bound`, `tma_frontend_bound`, `tma_memory_bound`, `tma_dram_bound`, `tma_dsb_switches`, `tma_fp_vector_256b`, `tma_info_memory_l1d_cache_fill_bw`, `tma_info_system_dram_bw_use`, and `tma_retiring`. The expression language references PMU aliases, constants, helper variables such as `#SMT_on`, functions such as `min` and `max`, MSR events such as `msr@tsc@`, and raw event syntax such as `cpu@...@`.

## Control Flow And Integration

At build time, `jevents.py` parses metric entries and emits them into generated perf metric tables. At runtime, `perf stat -M <metric>` resolves `MetricExpr` dependencies to event groups, schedules them, computes expressions, applies scale units, and can use `MetricThreshold` for threshold display. `MetricGroup` and `metricgroups.json` drive discoverability in `perf list metrics` and grouped views.

## State And Persistence

The file persists formulas, display grouping, thresholds, and constraints. It has no runtime mutable state, but metric computation depends on current perf counter values, system topology, SMT state, time, MSR availability, and event scheduling. `MetricConstraint` values such as `NO_GROUP_EVENTS` or `NO_GROUP_EVENTS_SMT` influence grouping behavior and help avoid invalid counter groups.

## Dependencies

This file depends on many Ivy Bridge event aliases from cache, memory, frontend, floating-point, branch, pipeline, and uncore files. It also depends on perf's metric expression parser in `pmu-events/metric.py`, generator support in `jevents.py`, runtime metric evaluation, MSR PMUs, cstate PMUs, and metric group descriptions from `metricgroups.json`. Because expressions reference event names directly, alias stability across topic files is critical.

## Risks

The highest risk is formula breakage from missing or renamed events. Many expressions divide by event counts, time, or slots; zero denominators, unsupported MSR/cstate events, or multiplexed groups can produce misleading values if constraints are wrong. Topdown metrics are hierarchical, so an error in a base metric such as `tma_backend_bound` propagates to many descendants. Thresholds are advisory but can bias diagnosis if stale. Metric group spelling must align with `metricgroups.json` for useful discovery.

## Test Signals

Run `pmu-events/metric_test.py` and full `jevents.py` generation. Use `perf list metricgroups` and `perf list metrics` to ensure grouping and descriptions appear. On Ivy Bridge hardware, smoke-test representative metrics with `perf stat -M tma_frontend_bound,tma_backend_bound,tma_memory_bound,tma_info_system_gflops` and verify no missing event, parser, or grouping errors. Formula dependency audits should compare all referenced aliases against generated event tables.
