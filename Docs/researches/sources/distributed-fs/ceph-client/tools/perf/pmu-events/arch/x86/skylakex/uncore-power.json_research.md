# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylakex/uncore-power.json

## Purpose

`uncore-power.json` is the Skylake-X package power-control-unit PMU catalog for perf. It contains 25 package-scoped `PCU` events that expose package clock ticks, frequency transition cycles, thermal and power limit cycles, prochot and VR-hot conditions, FIVR phase shedding, memory phase shedding, package C-state residency, core C-state occupancy, and core transition/demotion activity. The file gives perf static aliases for power and residency signals outside the core PMUs.

## Important APIs, Types, and Data Fields

The JSON array uses perf event object fields including `EventName`, `EventCode`, `UMask`, `BriefDescription`, `PublicDescription`, `Counter`, `Unit`, `PerPkg`, and optional `Experimental`. All rows target `Unit: "PCU"`, are package scoped with `PerPkg: "1"`, and use counters `0,1,2,3`. `UNC_P_CLOCKTICKS` is the baseline PCU clock-cycle event. `UNC_P_POWER_STATE_OCCUPANCY.CORES_C0`, `.CORES_C3`, and `.CORES_C6` share `EventCode: "0x80"` with different `UMask` values to classify core C-state occupancy. Other named rows cover frequency maximum/minimum limit cycles, package C0/C2E/C3/C6 residency, prochot, VR hot, phase shedding, and transition cycles.

## Control Flow and Data Flow

The file has no executable control flow. Perf's event-table generation reads these records, associates the `PCU` unit with the platform uncore PMU, and exposes aliases for runtime selection. During profiling, perf programs PCU counters and returns package-level cycle or occupancy counts. Analysis generally compares limit, transition, residency, and hot-condition cycles to `UNC_P_CLOCKTICKS` or to workload phases to understand power-management behavior.

## State and Persistence Behavior

The only persistent state is the static alias metadata. Runtime package power state, C-state occupancy, thermal limits, and transition counts are hardware state sampled by perf and are not persisted in this JSON. `PerPkg` means values describe the whole package. Counter records are mostly raw count/cycle definitions and do not define `MetricExpr` formulas in this file, so any percentage conversion is left to users or higher-level tooling.

## Dependencies and Integration Points

This file depends on Skylake-X PCU uncore PMU support in the Linux kernel and perf's pmu-events generator. It integrates with `uncore-memory.json` when memory traffic and memory phase shedding or throttling need to be correlated, and with core event files when CPU stalls must be connected to package-level power limits. It is consumed by `perf list`, `perf stat`, power/thermal diagnostics, frequency transition analysis, and package C-state residency studies.

## Risks and Edge Cases

The data is package-scoped, so results include all package activity and can be misleading on shared systems. Many events are cycle-like residency or limit signals rather than event occurrences; consumers need a denominator such as `UNC_P_CLOCKTICKS` for ratios. Some event descriptions are terse and repeat the event name, so external Intel PMU documentation may be needed for exact semantics. The `UNC_P_CLOCKTICKS` row has no explicit `EventCode`/`UMask` fields in the JSON, which is intentional for this catalog but can expose assumptions in parsers that require those fields for every event.

## Test Signals

Static tests should verify JSON parsing and generated perf tables, including acceptance of `UNC_P_CLOCKTICKS` without an explicit event code. Runtime smoke tests on Skylake-X should check that `perf list` exposes `UNC_P_*` PCU aliases and that `UNC_P_CLOCKTICKS` advances. Idle and sleep-friendly workloads should affect package C-state residency; CPU load should increase C0 occupancy; frequency scaling, thermal stress, or power-limit scenarios should move frequency-limit, prochot, VR-hot, and transition-cycle rows.
