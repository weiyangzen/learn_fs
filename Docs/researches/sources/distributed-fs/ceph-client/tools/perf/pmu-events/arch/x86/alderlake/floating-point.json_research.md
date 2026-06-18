# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/alderlake/floating-point.json

## Purpose

This file defines 22 Alder Lake floating-point and SIMD-related PMU events for perf. It covers divider activity, floating-point assists, SSE/AVX transition assists, FP arithmetic dispatch by execution port or vector pipe, retired scalar/vector FP arithmetic instructions, FP assist machine clears, and retired FP divider uops. The unit split is 18 `cpu_core` records and 4 `cpu_atom` records, reflecting the different PMU vocabularies of Alder Lake P-cores and E-cores.

## Important APIs, Types, and Data

Each entry is a perf event object with `EventName`, `EventCode`, `UMask`, `Counter`, `Unit`, `BriefDescription`, optional `PublicDescription`, and `SampleAfterValue`. One entry uses `CounterMask`. Event families include `ARITH`, `ASSISTS`, `FP_ARITH_DISPATCHED`, `FP_ARITH_INST_RETIRED`, `MACHINE_CLEARS`, and `UOPS_RETIRED`. The core-side `FP_ARITH_INST_RETIRED.*` entries distinguish scalar single/double, 128-bit packed single/double, 256-bit packed single/double, aggregate scalar, vector, and four-flop accounting. Atom-side `FP_ARITH_DISPATCHED.*` entries measure dispatch to ports or vector pipes rather than the same retired-instruction taxonomy.

## Control Flow

The file has no executable logic. Perf's event-table generation loads the array, emits descriptors, and later resolves user event names or metric dependencies to concrete PMU encodings. Runtime flow depends on `Unit`: a floating-point metric on an Alder Lake hybrid CPU may need one expression branch or event set for `cpu_core` and another for `cpu_atom`. The event table also controls sampling defaults through `SampleAfterValue`.

## State and Persistence Behavior

The persistent state is the event-name-to-encoding mapping. Counts are collected in hardware PMU counters and reset or accumulated by perf sessions. No mutable state is stored in the JSON. The stability of names matters because higher-level metrics and user scripts can refer to `FP_ARITH_INST_RETIRED.*`, `FP_ARITH_DISPATCHED.*`, or `ASSISTS.*` aliases. Changes to `SampleAfterValue` can affect profiling overhead and interrupt frequency, even when event semantics are unchanged.

## Dependencies and Integration Points

This catalog integrates with perf's pmu-events parser, Alder Lake model matching, hybrid PMU routing, `perf list`, `perf stat`, and topdown/HPC metrics that classify compute, FLOPs, vector width, divider bottlenecks, and assists. It depends on kernel exposure of the core and atom PMUs and on perf's support for event names that appear only on one hybrid unit. It also relates to `pipeline.json` because divider activity and assists are shared pipeline bottleneck signals.

## Risks

The largest semantic risk is mixing dispatch-domain atom events with retired-domain core events in one metric without unit-specific formulas. FLOP-style interpretation is also risky: some events count instructions, some count uops, and vector-width-derived FLOP estimates require careful scaling. Assist events are usually rare; low default sample periods or multiplexing can produce noisy data. Counter restrictions can make simultaneous FP breakdown groups unschedulable.

## Test Signals

Validation should include JSON parsing, pmu-events generation, `perf list` display for core-only and atom-only event names, and smoke `perf stat` runs on FP-heavy, SIMD-heavy, divider-heavy, and assist-triggering workloads. Metric tests should verify that FLOP/vector/divider formulas bind the correct event family for each PMU unit and do not combine core and atom encodings as if they were identical.
