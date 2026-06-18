# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sierraforest/uncore-power.json

## Purpose
Defines Sierra Forest package control unit power-management PMU events for perf. The 11-entry JSON array exposes `UNC_P_*` aliases for PCU clockticks, thermal/power frequency limits, frequency transition cycles, package C-state residency, core C-state occupancy, and PROCHOT throttling sources.

## Important APIs, Types, And Event Groups
Each object follows the perf PMU event schema with `EventName`, `EventCode`, `BriefDescription`, `PublicDescription`, `Counter`, `PerPkg`, and `Unit`. `Unit` is `PCU`, `Counter` allows slots `0,1,2,3`, and `PerPkg: "1"` marks package scope. Several entries carry `Experimental: "1"`, including thermal/power limit and package C-state residency events.

Important aliases include `UNC_P_CLOCKTICKS` as a fixed-rate PCU time base, `UNC_P_FREQ_MAX_LIMIT_THERMAL_CYCLES`, `UNC_P_FREQ_MAX_POWER_CYCLES`, `UNC_P_FREQ_TRANS_CYCLES`, `UNC_P_PKG_RESIDENCY_C2E_CYCLES`, `UNC_P_PKG_RESIDENCY_C6_CYCLES`, `UNC_P_POWER_STATE_OCCUPANCY_CORES_C0/C3/C6`, and internal/external PROCHOT cycle counters.

## Control Flow
The file is data-only. Perf's event-table generator parses it into aliases; perf runtime resolves a selected alias to a PCU uncore event selector. The descriptions encode intended analysis flow: use clockticks as a constant-rate denominator, compare frequency limit or PROCHOT cycles against elapsed PCU cycles, and combine occupancy/residency events with thresholding or edge detect where supported.

## State And Persistence
No local runtime state is persisted by this JSON. The repository persists hardware metadata. Measurement state is maintained by perf event file descriptors, the kernel PCU PMU driver, and hardware counters while a profiling session is active. PCU clockticks are described as a fixed 1 GHz pclk counter, making them useful for wall-time normalization.

## Dependencies And Integration Points
The file depends on Sierra Forest PCU uncore PMU support and perf's architecture-specific map selection. It integrates with power and thermal analysis workflows where perf counters are correlated with workload phases, C-state residency, and throttling behavior. It also complements IMC and IIO uncore files by covering package-management state rather than traffic counts.

## Risks
These counters are easy to misread as per-core metrics even though they are package-scoped. Residency events exclude transition times, and occupancy events measure number of cores in a state over time rather than entry counts unless threshold or edge features are applied externally. Experimental flags mean the exact semantics may need hardware-documentation confirmation.

## Test Signals
JSON validation and perf event-table generation are basic tests. On Sierra Forest systems, `perf list` should show PCU aliases and `perf stat` should open `UNC_P_CLOCKTICKS` plus at least one residency, occupancy, frequency-limit, and PROCHOT event. Sanity checks include nonzero clockticks during measurement and plausible increases in throttling counters only under induced thermal or power pressure.
