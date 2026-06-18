# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power9/nest_metrics.json

## Purpose

This file defines 10 POWER9 nest and memory-bandwidth metrics. It covers chip-level read and write memory bandwidth, PowerBUS frequency, a core-domain 32 MHz cycle metric, per-MCS read/write bandwidth metrics, a powerbus frequency metric, and an aggregate MCS memory-bandwidth metric. Unlike the core metric file, these expressions target uncore-like PMUs such as `hv_24x7`, `nest_mcs01_imc`, `nest_mcs23_imc`, and `nest_powerbus0_imc`.

## APIs, types, and schema

Entries use metric fields: `MetricName`, `MetricGroup`, `MetricExpr`, `ScaleUnit`, and sometimes `AggregationMode`. `jevents.py` maps `AggregationMode` values such as `PerChip` and `PerCore` into generated aggregation enum values, uses `ScaleUnit` as the metric unit, and parses escaped perf PMU expressions. The file contains no raw `EventCode` entries.

## Control flow and integration

The file is part of the POWER9 model directory, but its expressions reference named events exposed by nest or hypervisor PMUs rather than by the default core event table. The generator treats the objects as metric rows and emits them into the POWER9 metric table. At runtime, perf must resolve the PMU-qualified expression syntax, including escaped commas and placeholder selectors such as `chip=?` or `core=?`.

## State, persistence, and dependencies

The file has no mutable state. It persists metric formulas that depend on platform PMU availability, hypervisor support for `hv_24x7`, nest IMC PMU names, scaling units, and aggregation semantics. Hardware topology and firmware exposure can affect whether these metrics are usable on a given POWER9 machine.

## Risks and test signals

Risks are mostly integration-related: missing nest PMUs, changed event names, bad escaping in PMU-qualified expressions, incorrect scale units, or aggregation mismatches. The chip-level bandwidth metrics use `AggregationMode`, so perf aggregation behavior should be checked explicitly. Test signals include JSON parsing, metric parser tests, generated C inspection for `aggr_mode`, and hardware `perf stat -M` runs on systems exposing `hv_24x7` and nest IMC PMUs.
