# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/snowridgex/uncore-power.json

## Purpose
`uncore-power.json` defines Snow Ridge package power-control-unit events. Its 26 records describe PCU clock ticks, core/package C-state residency, frequency transitions, thermal and power clipping, FIVR phase shedding, PROCHOT assertions, demotions, and power-state occupancy. These events let perf users correlate performance with package-level power management decisions.

## Important APIs, Types, and Fields
The schema uses perf event fields including `EventName`, `BriefDescription`, `EventCode`, `UMask`, `Counter`, `Unit`, `PerPkg`, and optional `PublicDescription` and `Experimental`. `Unit` is consistently `PCU`, binding these definitions to the uncore power control unit PMU. `UNC_P_CLOCKTICKS` has no explicit `EventCode`, implying special handling or a counter-native PCU clock event. Almost every other event is marked `Experimental`, so users and maintainers should treat exact encodings as hardware-stepping-sensitive.

## Control Flow and Data Flow
The file is parsed by perf's PMU event build tooling into Snow Ridge event tables. At runtime, perf resolves a requested name such as `UNC_P_FREQ_MAX_POWER_CYCLES` or `UNC_P_PKG_RESIDENCY_C6_CYCLES`, maps it to the PCU PMU, and programs one of counters `0,1,2,3` using the encoded event selector and unit mask. There is no procedural control flow in the JSON; all behavior is driven by event lookup and hardware counter sampling.

## State and Persistence Behavior
No persistent state is stored in the file. The measured state is package-level PCU counter state over the perf measurement interval. `PerPkg: 1` means results are package scoped. Residency and throttling cycle events represent time spent in power states, while transition events represent count-like behavior; consumers must not mix them without normalizing by `UNC_P_CLOCKTICKS` or elapsed time.

## Dependencies and Integration Points
The definitions depend on Snow Ridge PCU PMU support in the kernel and perf's uncore event table generation. They integrate with `perf list` and `perf stat` for package-level power diagnostics and with any higher-level metric formulas that may reference PCU events. The file should remain consistent with adjacent Snow Ridge uncore files so model matching exposes a coherent set of PCU, iMC, and core events.

## Risks and Edge Cases
Because 25 of 26 events are experimental, encodings may be less stable than architectural events. Several names are terse and mirror internal hardware concepts, such as `UNC_P_TOTAL_TRANSITION_CYCLES` and `UNC_P_MEMORY_PHASE_SHEDDING_CYCLES`; incorrect user interpretation is likely without Intel documentation. The lack of `PublicDescription` on some records reduces discoverability in `perf list --details`. Power and thermal limit events can be zero on idle or unconstrained systems, which is expected and should not be treated as event failure.

## Test Signals
Syntax validation with `jq empty` and perf PMU table generation are baseline tests. On Snow Ridge hardware, `perf list` should show `UNC_P_CLOCKTICKS`, `UNC_P_FREQ_MAX_POWER_CYCLES`, `UNC_P_PROCHOT_INTERNAL_CYCLES`, and package residency events. Runtime checks should compare PCU clock ticks with residency/throttling events over idle and loaded intervals and confirm package-scoped aggregation rather than per-core duplication.
