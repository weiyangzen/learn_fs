# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/graniterapids/uncore-power.json

## Purpose
This JSON file defines 11 Intel Granite Rapids PCU uncore PMU events for package power, frequency-limit, package C-state, core power-state occupancy, and PROCHOT analysis in perf. It is static event metadata for the package control unit rather than executable code. The source was read as a complete 109-line JSON array.

## Important APIs, Types, and Functions
All rows have `EventName`, `EventCode`, `BriefDescription`, `PublicDescription`, `Counter`, `PerPkg`, and `Unit`. `Unit` is always `PCU`, `Counter` is `0,1,2,3`, and `PerPkg` is `1`. Each event has a unique event code. The event names are `UNC_P_CLOCKTICKS`, `UNC_P_FREQ_MAX_LIMIT_THERMAL_CYCLES`, `UNC_P_FREQ_MAX_POWER_CYCLES`, `UNC_P_FREQ_TRANS_CYCLES`, `UNC_P_PKG_RESIDENCY_C2E_CYCLES`, `UNC_P_PKG_RESIDENCY_C6_CYCLES`, `UNC_P_POWER_STATE_OCCUPANCY_CORES_C0`, `UNC_P_POWER_STATE_OCCUPANCY_CORES_C3`, `UNC_P_POWER_STATE_OCCUPANCY_CORES_C6`, `UNC_P_PROCHOT_EXTERNAL_CYCLES`, and `UNC_P_PROCHOT_INTERNAL_CYCLES`.

Eight non-clock events are marked `Experimental: "1"`, including thermal/power limit cycles, frequency transition cycles, package C-state residency cycles, C3 core occupancy, and internal/external PROCHOT cycles. There are no unit masks, metric expressions, or MSR filter fields in this file.

## Control Flow, State, and Persistence
There is no in-file control flow. Build-time processing is the standard `jevents.py` path from JSON rows to generated perf C tables. Runtime perf resolves aliases to PCU uncore PMU selectors and collects package-scoped counts. The events expose PCU state over the measurement interval: clockticks provide the time base, frequency-limit events count cycles constrained by thermal or power limits, residency events count package C-state cycles, and occupancy events count how many cores are in selected C-states.

Persistence is only through generated perf metadata. Hardware values are sampled during perf sessions and are not persisted by this file. Because the events are package-scoped, task-level attribution is not meaningful without careful workload isolation.

## Dependencies and Integration Points
The file depends on Granite Rapids PCU PMU support in the kernel, perf's PMU event schema, `jevents.py`, and Intel PCU event definitions. It integrates with `perf stat -e` for package-level power-management diagnostics and complements RAPL energy readings, scheduler/idle metrics, memory throttling events, and UPI low-power link events.

The public descriptions make these events visible and understandable in `perf list`, which matters because power-management counters are easy to misinterpret without explicit cycle or occupancy wording.

## Risks and Test Signals
Risks include experimental semantics, platform firmware policy differences, package-level attribution mistakes, and zero counts on systems that do not enter the relevant C-states or throttling paths. Core occupancy events are not the same as elapsed cycles; derived metrics must normalize with PCU clockticks or another appropriate time base.

Test signals include `jq` validation, event-table generation, `perf list` visibility for all 11 names, and Granite Rapids smoke tests under idle, CPU stress, thermal or power constrained, and frequency-transition workloads. A basic sanity check is that `UNC_P_CLOCKTICKS` increments during any package-level measurement and that C-state residency increases during idle intervals.
