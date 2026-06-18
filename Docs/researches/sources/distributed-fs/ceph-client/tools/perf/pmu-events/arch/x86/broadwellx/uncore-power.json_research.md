# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellx/uncore-power.json

## Purpose

This file is the BroadwellX package-control-unit power and residency PMU event table for Linux `perf`. It contains 57 event records, all with `Unit: "PCU"` and `PerPkg: "1"`. `jevents.py` maps the unit to generated PMU name `uncore_pcu`, exposing package-level PCU aliases for power-management analysis.

The events cover PCU clock ticks, per-core C-state transition cycles, per-core C-state demotions, frequency-limit cycles, frequency-transition cycles, memory phase shedding, package C-state residency, power-state occupancy filters, PROCHOT and VR hot cycles, total transition cycles, and ring global-voltage/frequency transitions.

## Schema And Public API

Each object is a perf alias record. Common fields are `EventName`, `EventCode`, `Counter`, `Unit`, `PerPkg`, `BriefDescription`, and usually `PublicDescription`. Unlike most other BroadwellX PMU files, this file does not use `UMask`; instead, three `UNC_P_POWER_STATE_OCCUPANCY.*` entries use `Filter` values (`occ_sel=1`, `occ_sel=2`, `occ_sel=3`) that `jevents.py` appends verbatim to the generated event encoding.

Important families are `UNC_P_CLOCKTICKS`, `UNC_P_CORE{0..17}_TRANSITION_CYCLES`, `UNC_P_DEMOTIONS_CORE{0..17}`, frequency max/min limit cycles, frequency transition cycles, package residency cycles, filtered power-state occupancy, PROCHOT/VR hot cycles, total transition cycles, and ring GV transitions.

## Control Flow And Integration

At build time, the PMU-events generator loads the JSON array and constructs one `JsonEvent` per record. `Unit: "PCU"` becomes `uncore_pcu`; `Filter` terms are appended to the event string; descriptions are embedded in generated compact string storage; `PerPkg` is preserved. At runtime, perf maps the BroadwellX table to PCU uncore PMUs and resolves user aliases to the generated encodings.

The primary integration points are `jevents.py`, generated `pmu-events.c`, `pmu-events.h`, uncore PMU matching in `tools/perf/util/pmu.c`, `perf list`, `perf stat`, and any BroadwellX metric groups that use PCU power or residency denominators.

## State And Persistence

There is no mutable state inside this file. Its persistent effect is the compiled alias table in perf. The hardware state being observed is package and per-core power-management state, but the JSON only describes how to program counters for that state.

The per-core transition and demotion events are source-level expansions up to core 17. They encode a BroadwellX core-count assumption into public aliases. All records are package-level uncore aliases through `PerPkg: "1"`.

## Dependencies, Risks, And Test Signals

The table depends on BroadwellX PCU uncore PMU support, sysfs PMU format support for event selectors and the `occ_sel` filter, the x86 BroadwellX mapfile, and the perf PMU-events generator. Correct interpretation also depends on processor power-management behavior, C-state availability, thermal throttling, OS power policy, and package/ring frequency transition mechanisms.

The highest-risk field is `Filter` on `UNC_P_POWER_STATE_OCCUPANCY.*`, because it is appended verbatim by the generator and must match the kernel PMU format. `UNC_P_CLOCKTICKS` lacks an `EventCode`; this is accepted now but should be preserved intentionally. Useful checks are `jq empty`, `jq 'length'` returning 57, generator output preserving `occ_sel`, and runtime tests for `UNC_P_CLOCKTICKS`, `UNC_P_CORE0_TRANSITION_CYCLES`, `UNC_P_DEMOTIONS_CORE0`, `UNC_P_PKG_RESIDENCY_C6_CYCLES`, and `UNC_P_POWER_STATE_OCCUPANCY.CORES_C0`.
