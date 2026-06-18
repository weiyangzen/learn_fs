# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellde/uncore-power.json

## Purpose

`uncore-power.json` defines Broadwell-DE PCU uncore PMU aliases for package power, frequency-limit, C-state transition, residency, demotion, PROCHOT, VR-hot, and related power-controller behavior. It lets perf expose hardware counters with names such as `UNC_P_CLOCKTICKS`, `UNC_P_FREQ_MAX_POWER_CYCLES`, `UNC_P_PKG_RESIDENCY_C6_CYCLES`, and `UNC_P_DEMOTIONS_CORE0`.

The file contains 57 records, all scoped to `Unit: "PCU"` and `PerPkg: "1"`. The PCU clock event has no `EventCode`, and none of the events use `UMask`; instead, each selector is either a single code or, for `UNC_P_POWER_STATE_OCCUPANCY.*`, a shared event code with a `Filter` value that distinguishes core C-state occupancy classes.

## Important APIs, Types, and Data Shape

The table uses perf PMU event JSON fields `EventName`, `EventCode`, `Counter`, `Unit`, `PerPkg`, `BriefDescription`, `PublicDescription`, and for three occupancy aliases `Filter`. `jevents.py` converts these records into generated C PMU-event rows, and perf's PMU alias layer later binds them to PCU uncore PMUs discovered from the kernel.

Important event groups include:

- `UNC_P_CLOCKTICKS`, the fixed 1 GHz PCU clock domain used as a wall-time-like baseline.
- `UNC_P_CORE{0..17}_TRANSITION_CYCLES`, per-core C-state transition-cycle counters.
- `UNC_P_DEMOTIONS_CORE{0..17}`, per-core C-state demotion counters.
- `UNC_P_FREQ_MAX_LIMIT_THERMAL_CYCLES`, `UNC_P_FREQ_MAX_POWER_CYCLES`, `UNC_P_FREQ_MAX_OS_CYCLES`, `UNC_P_FREQ_MIN_IO_P_CYCLES`, and `UNC_P_FREQ_TRANS_CYCLES`, which identify frequency-limit and transition causes.
- `UNC_P_PKG_RESIDENCY_C{0,1E,2E,3,6,7}_CYCLES` for package C-state residency.
- `UNC_P_POWER_STATE_OCCUPANCY.CORES_C0`, `.CORES_C3`, and `.CORES_C6`, all using event code `0x80` with different filters.
- `UNC_P_PROCHOT_INTERNAL_CYCLES`, `UNC_P_PROCHOT_EXTERNAL_CYCLES`, `UNC_P_VR_HOT_CYCLES`, `UNC_P_TOTAL_TRANSITION_CYCLES`, `UNC_P_MEMORY_PHASE_SHEDDING_CYCLES`, and `UNC_P_UFS_TRANSITIONS_RING_GV` for platform throttling and power-state transitions.

The lack of masks is meaningful: reviewers should not assume every PMU event row requires a `UMask`. For the filter-based occupancy rows, `Filter` is the field that selects the subcondition.

## Control Flow

Runtime behavior is produced by the standard PMU-event path:

1. Broadwell-DE CPU matching selects the `broadwellde` PMU-event directory.
2. The build reads this JSON through `jevents.py`.
3. The generator emits PCU aliases into generated `pmu-events.c`.
4. Perf discovers PCU uncore PMUs and matches `Unit: "PCU"` aliases to them.
5. `perf list` and event parsing expose the aliases; `perf stat` opens package PCU counters and reports counts for the enabled interval.

The core-indexed transition and demotion aliases are enumerated as individual records rather than being parameterized. That keeps runtime alias lookup simple, but means additions or corrections must update every affected literal row.

## State and Persistence Behavior

The file stores static metadata only. Generated build artifacts persist the compiled alias table. Runtime state is in hardware PCU counters and perf's opened file descriptors for the measurement interval. `PerPkg: "1"` makes these counters package-level; even per-core demotion and transition aliases are exposed through the package PCU uncore device rather than through ordinary per-core programmable counters.

No persistent measurements are stored by this file. Description and encoding changes affect future builds and may alter user-visible `perf list` output and scripted event names.

## Dependencies and Integration Points

This file depends on the Broadwell-DE CPU map, perf's PMU-event generator, the Intel PCU uncore kernel PMU, and perf alias matching. It integrates with power and frequency investigations in `perf stat`, `perf list --unit PCU`, JSON event output, and any higher-level metrics that use PCU clock or residency counters as denominators.

The event semantics depend on PCU firmware/hardware definitions: fixed 1 GHz PCU clocking, package C-state residency accounting, core C-state demotion rules, PROCHOT source accounting, and frequency limit causes. Correct interpretation may also depend on BIOS power settings and workload residency behavior.

## Risks and Edge Cases

The three `UNC_P_POWER_STATE_OCCUPANCY.*` rows share `EventCode: "0x80"` and differ by `Filter`; dropping or mishandling the `Filter` field would collapse distinct aliases into the same encoding. `UNC_P_CLOCKTICKS` has no `EventCode`, which must be accepted as a clock event. Because none of the rows uses `UMask`, schema validators that require masks for all non-clock events would reject valid PCU entries.

Core-numbered aliases cover cores 0 through 17. Broadwell-DE SKUs with fewer active cores may expose counters whose corresponding logical core is absent or inactive; users must interpret zero or unsupported counts in the context of the actual package. Package-level power counters are also workload-shared, so they are sensitive to background activity and platform firmware.

Descriptions are concise and repetitive for core transition/demotion rows. That is good for generated list readability but increases the chance that a single code change in the sequence goes unnoticed. Tests should verify monotonic code mapping for core indices rather than relying only on JSON syntax.

## Test Signals

Useful validation includes JSON parsing, duplicate-name detection, generator rebuild, and explicit checks that `Filter` survives generation for `UNC_P_POWER_STATE_OCCUPANCY.*`. Runtime smoke tests on Broadwell-DE should include `perf list --unit PCU`, `perf stat -e UNC_P_CLOCKTICKS`, one package residency alias, one frequency-limit alias, one PROCHOT/VR-hot alias, and one per-core transition or demotion alias. Review tests should compare the core-indexed `EventCode` sequences for cores 0-17 against the Intel table.
