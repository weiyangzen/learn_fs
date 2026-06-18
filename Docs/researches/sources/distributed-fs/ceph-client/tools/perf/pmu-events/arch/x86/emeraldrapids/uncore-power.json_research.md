# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/emeraldrapids/uncore-power.json

## Purpose

`uncore-power.json` defines 25 Emerald Rapids PCU uncore power events for package clocking, C-state residency, core occupancy by power state, frequency clipping, thermal and power throttling, phase shedding, PROCHOT, voltage-regulator hot cycles, and frequency/C-state transitions. It gives perf package-level visibility into the platform control unit rather than core-local execution.

## Important APIs, Types, and Data Fields

The JSON entries use `EventName`, `EventCode`, `Counter`, `Unit`, `PerPkg`, `BriefDescription`, optional `PublicDescription`, and frequent `Experimental` flags. All rows use `Unit: PCU` and `PerPkg: 1`. Most rows allow counters `0,1,2,3`; `UNC_P_PMAX_THROTTLED_CYCLES` is restricted to counter `0`.

Important families are `UNC_P_CLOCKTICKS`, `UNC_P_PKG_RESIDENCY_*`, `UNC_P_POWER_STATE_OCCUPANCY_CORES_*`, `UNC_P_FREQ_*`, `UNC_P_FIVR_PS_*`, `UNC_P_MEMORY_PHASE_SHEDDING_CYCLES`, `UNC_P_PROCHOT_*`, `UNC_P_VR_HOT_CYCLES`, and transition/demotion events.

## Control Flow and Data Flow

There is no executable flow in the file. Perf ingests the rows as PCU PMU aliases, then programs package-level PCU counters for selected events. Users typically compare clockticks to residency, occupancy, and throttling-cycle events to identify whether performance is limited by idle residency, power limits, thermal limits, AVX frequency clipping, voltage-regulator limits, or transition overhead.

## State and Persistence Behavior

The file persists event encodings and package-scope metadata only. Runtime residency and throttling counters persist only for the measurement interval. Several rows describe cycles in a state, while occupancy rows count number of cores in a C-state over time; those values need normalization by elapsed PCU clock cycles to become percentages or averages.

## Dependencies and Integration Points

This catalog depends on Emerald Rapids PCU uncore PMU support in perf and the kernel. It integrates with power tuning, thermal diagnostics, AVX workload analysis, idle-state validation, memory phase-shedding investigations, and package-level performance analysis. It pairs naturally with core frequency metrics, RAPL/power telemetry, and `uncore-memory.json` memory power-state rows.

## Risks and Edge Cases

Most entries are marked `Experimental`, so availability and semantics may vary across steppings, firmware, or kernel support. Package-level PCU counters include all cores and system activity on the package. Cycle counts do not directly equal percentages without an appropriate denominator. Occupancy counters may require thresholding or normalization to derive average core counts. Counter restriction on `UNC_P_PMAX_THROTTLED_CYCLES` can create scheduling conflicts with other PCU events.

## Test Signals

Validation should include JSON parsing, generated perf table success, and `perf list` exposure of PCU aliases. Idle and busy workloads should change package residency and core C0 occupancy. AVX-heavy workloads should be checked against AVX frequency clipping rows. Thermal or power-limited stress tests should move thermal, power, PROCHOT, and VR-hot counters when the platform allows safe observation. Counter scheduling tests should verify the counter-0-only row is handled correctly.
