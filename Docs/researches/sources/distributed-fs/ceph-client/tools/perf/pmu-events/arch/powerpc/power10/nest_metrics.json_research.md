# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power10/nest_metrics.json

## Purpose

This file defines 70 POWER10 nest and fabric metrics derived from `hv_24x7` counters. It focuses on PowerBus pump retries, local/group/remote/near node pump traffic, XLink and ALink utilization, PCI data transfer, memory-controller read/write bandwidth, aggregate memory bandwidth per chip, and PowerBus frequency.

## APIs, types, and schema

Entries use the perf metric schema with `MetricName`, `MetricExpr`, `ScaleUnit`, and `AggregationMode`; all entries have `AggregationMode: PerChip`. Some entries also include `MetricGroup`, but the dominant contract is chip-scoped nest aggregation. Expressions reference `hv_24x7@EVENT\,chip\=?@`, which binds events from the hypervisor 24x7 PMU with a wildcard or supplied chip selector. The file does not define raw events or descriptions.

## Control flow and integration

`jevents.py` parses this JSON during perf build and emits metric table entries. Runtime evaluation differs from core metrics because formulas read `hv_24x7` event syntax rather than ordinary core PMU events. Pump retry ratios divide retry counters by pump counters, total pump metrics normalize pump counts by `PM_PAU_CYC`, link utilization metrics combine odd/even data or total utilization lanes and divide by available cycles, and bandwidth metrics expose raw or summed MCS and PCI transfer counters.

## State and persistence

The file has no local mutable state. Persistent behavior is the set of named chip-level metrics available to perf users on POWER10 systems with the `hv_24x7` PMU. The `chip=?` selector is part of the persistent query contract: it allows perf to aggregate per chip, but it also means incorrect selector parsing would break all metrics in this file.

## Dependencies

The metrics depend on kernel and hypervisor support for `hv_24x7`, chip-scoped PMU events such as `PM_PB_*`, `PM_XLINK*_OUT_*`, `PM_ALINK*_OUT_*`, `PM_MCS_*`, `PM_PCI*_32B_INOUT`, and `PM_PAU_CYC`, plus perf metric parsing for escaped commas and `@...@` event syntax. Integration points are `pmu-events/jevents.py`, `pmu-events/metric.py`, and metricgroup/runtime event scheduling code.

## Risks

Most ratio denominators are raw event counts; some utilization and retry formulas add `1` to avoid division by zero, while several local/group pump ratios do not. Metrics without `BriefDescription` place more burden on metric names for user understanding. All formulas are `PerChip`, so accidental system-wide aggregation can mislead users. Syntax is fragile because escaped commas and `chip=?` selectors must survive JSON parsing, metric parsing, and runtime event opening.

## Test signals

Validation should include `jq`, metric parser tests for escaped `hv_24x7@...\,chip\=?@` syntax, perf PMU event generation, and runtime `perf stat -M` checks on POWER10 systems with accessible `hv_24x7` counters. Specific tests should cover zero or missing chip counters, per-chip aggregation, and formulas that combine odd/even link counters.
