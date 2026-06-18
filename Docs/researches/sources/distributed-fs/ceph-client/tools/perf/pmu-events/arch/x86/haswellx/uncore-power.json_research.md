# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswellx/uncore-power.json

## Purpose

`haswellx/uncore-power.json` defines 62 HaswellX PCU uncore PMU aliases for package and core power-management observation. It exposes PCU clock ticks, per-core C-state transition and demotion counts, package C-state residencies, core C-state occupancy filters, PROCHOT thermal throttle cycles, ring frequency transition events, and VR hot cycles. The events are used by perf to report server package power-state behavior via the PCU PMU.

## Important APIs, types, and schema

The file uses JSON event objects with `EventName`, optional `EventCode`, `BriefDescription`, `PublicDescription`, `Counter`, `PerPkg`, and `Unit`. Three occupancy aliases also use `Filter` values such as `occ_sel=1`, `occ_sel=2`, and `occ_sel=3`. All entries use `Unit: PCU`, which maps to `uncore_pcu`, and all allow counters `0,1,2,3`.

Event families include `UNC_P_CLOCKTICKS`; per-core transition events `UNC_P_CORE0_TRANSITION_CYCLES` through `UNC_P_CORE17_TRANSITION_CYCLES`; per-core demotion events `UNC_P_DEMOTIONS_CORE0` through `UNC_P_DEMOTIONS_CORE17`; package residency aliases `UNC_P_PKG_RESIDENCY_C0_CYCLES`, `C1E`, `C2E`, `C3`, `C6`, and `C7`; occupancy aliases `UNC_P_POWER_STATE_OCCUPANCY.CORES_C0`, `.CORES_C3`, and `.CORES_C6`; `UNC_P_PROCHOT_EXTERNAL_CYCLES` and `UNC_P_PROCHOT_INTERNAL_CYCLES`; `UNC_P_TOTAL_TRANSITION_CYCLES`; `UNC_P_UFS_TRANSITIONS_NO_CHANGE` and `UNC_P_UFS_TRANSITIONS_RING_GV`; and `UNC_P_VR_HOT_CYCLES`.

## Control flow and integration

There is no executable flow in the JSON. Perf build flow selects the `haswellx` directory via the x86 mapfile, parses the file with `jevents.py`, converts `Unit: PCU` to `uncore_pcu`, preserves `Filter` strings, and emits generated PMU event table rows. At runtime, perf uses those rows to program PCU counters and, for occupancy events, include the filter terms needed by the uncore PMU driver.

## State and persistence behavior

The persistent state is the alias-to-PCU-encoding mapping. The per-core entries encode a fixed 18-core naming range and event-code sequence, so edits must preserve the association between core number and code. Residency events count cycles in package states and explicitly exclude transition time; transition events count cycles spent entering or leaving C-states. This distinction is a semantic contract for downstream power analysis.

## Dependencies

Dependencies are Intel HaswellX PCU PMU definitions, perf's JSON schema, the uncore PCU kernel PMU, `jevents.py` field handling for `Filter`, and the model mapping for HaswellX. The descriptions depend on Intel C-state, PROCHOT, UFS/ring global voltage/frequency, and SVID VR terminology.

## Risks

The per-core event list is vulnerable to off-by-one or lexicographic-order mistakes because event names are not numerically sorted in every sequence. Occupancy events share event code `0x80` and differ by `Filter`; dropping or changing a filter would make multiple aliases count the same condition. C-state residency and transition-cycle events sound similar but measure different phases, so documentation drift can lead to wrong power conclusions. These are package-level uncore events, not task-attributable per-thread counters.

## Test signals

Validation includes JSON syntax checks, successful `jevents.py` generation, and `perf list` visibility under `uncore_pcu`. Runtime signals include nonzero PCU clock ticks at the fixed PCU clock rate, residency changes under idle versus load, PROCHOT counters staying zero unless thermal throttling is induced or observed, and occupancy filters producing different distributions for C0/C3/C6 states.
