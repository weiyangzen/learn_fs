# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power9/memory.json

## Purpose

This POWER9 file defines 25 memory-oriented PMU events. The set includes nest reference clock, PMC overflow and rewind events, dispatch address request queue occupancy, data reload sources from local and distant caches, run counters, DERAT miss reloads, completed loads, and synchronous marked events. It provides raw counters used for memory hierarchy analysis and for general denominator or control signals in POWER9 perf measurements.

## APIs, types, and schema

The entries use the raw event schema consumed by `JsonEvent`: `EventName`, `EventCode`, and `BriefDescription`. The generator maps each object to a default core PMU event and emits compact metadata in generated C. This file does not define `MetricExpr` objects, but its event names are relevant to broader POWER9 metric formulas.

## Control flow and integration

Build integration is the standard `pmu-events/Build` path: include POWER9 JSON sources, optionally copy them to the output tree, run metric syntax tests, and invoke `jevents.py` to generate `pmu-events.c`. Runtime integration is through the generated POWER9 PMU event table selected by the PowerPC PVR map. The event names become available to `perf list`, `perf stat -e`, and metric expressions.

## State, persistence, and dependencies

The file is static hardware metadata. It depends on valid POWER9 event codes, the perf JSON schema, and kernel PMU support for memory, run, and PMC-control counters. Some counters are core resources rather than purely per-thread measures, so the measurement context affects interpretation.

## Risks and test signals

Risks include confusing run-state counters with memory-source counters, misinterpreting queue occupancy as per-thread state, or breaking formulas by renaming event symbols. `PM_NEST_REF_CLK` is especially descriptive-sensitive because its description says to multiply by 4 to obtain PB cycles. Test signals are syntax validation, generated C regeneration, duplicate-name checks, metric parse coverage, and on-hardware comparison of memory-source counts against expected workload locality.
