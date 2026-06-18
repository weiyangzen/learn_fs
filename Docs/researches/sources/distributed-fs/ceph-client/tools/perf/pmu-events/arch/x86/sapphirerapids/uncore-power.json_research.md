# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sapphirerapids/uncore-power.json

## Purpose

This 25-entry table defines Sapphire Rapids uncore power-control-unit events for perf. All records use the `PCU` unit and expose package-level telemetry for PCU clockticks, core/package C-state residency and transitions, frequency transitions and clipping, phase shedding, thermal and power throttling, PROCHOT conditions, voltage-regulator heat, and core C-state occupancy. It is the named-event catalog for diagnosing power-management effects on package performance.

## Important APIs, Types, and Data

Entries use `EventName`, `EventCode`, `Counter`, `Unit`, `PerPkg`, `BriefDescription`, optional `PublicDescription`, and frequent `Experimental: 1` markers. Most events can use counters `0,1,2,3`; `UNC_P_PMAX_THROTTLED_CYCLES` is restricted to counter `0`. Key families include `UNC_P_FREQ_*`, `UNC_P_PKG_RESIDENCY_*`, `UNC_P_POWER_STATE_OCCUPANCY_*`, `UNC_P_FIVR_PS_*`, `UNC_P_PROCHOT_*`, `UNC_P_TOTAL_TRANSITION_CYCLES`, and `UNC_P_MEMORY_PHASE_SHEDDING_CYCLES`.

## Control Flow

Perf reads the JSON as static PMU metadata and exposes the aliases when the Sapphire Rapids PCU PMU is present. A `perf stat` or metric request programs the PCU event select onto an allowed package-level counter. Analysts typically compare these cycle counters to `UNC_P_CLOCKTICKS` or wall time to compute residency or throttling ratios. Occupancy events can be used directly for averages or with thresholding modes when supported by the PMU.

## State and Persistence Behavior

The persistent state is the alias set and encoding metadata. Runtime values are package-wide PCU counter values for the active perf session. Residency events explicitly exclude transition time, while transition events count time spent changing frequency or C-states. Most entries are marked experimental, so their behavior is less stable than architectural core events and may vary across steppings, firmware policy, and kernel driver support.

## Dependencies and Integration Points

This file integrates with the perf uncore PCU driver, generated pmu-events tables, power and thermal diagnosis workflows, and top-level performance investigations that correlate memory/core stalls with package frequency policy. It complements core pipeline and uncore memory counters by explaining whether observed throughput changes coincide with frequency caps, thermal limits, package C-state behavior, memory phase shedding, or VR/PROCHOT events.

## Risks

Experimental events can be renamed, unavailable, or have unclear semantics on some systems. Package-level PCU counters cannot attribute throttling to one workload on a shared host. Some cycle events require normalization against PCU clockticks rather than CPU core cycles. Firmware power policy, BIOS settings, and platform sensors can change whether thermal, VR, and external PROCHOT events appear. Counter restrictions, especially the single-counter PMAX event, can cause scheduling failures if metrics overbook PCU counters.

## Test Signals

Validation should include schema parsing, `perf list` exposure of `UNC_P_*` aliases, and simple `perf stat` runs for clockticks and package residency. Stress tests can use AVX, thermal, and power-limited workloads to check frequency clipping and throttling aliases. Idle/active transitions should affect C-state residency and occupancy events. Tests should also confirm experimental events fail gracefully when unavailable and that counter scheduling respects the `Counter` field.
