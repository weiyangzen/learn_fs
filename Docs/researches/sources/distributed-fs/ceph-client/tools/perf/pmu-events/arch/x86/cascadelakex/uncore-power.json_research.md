# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/cascadelakex/uncore-power.json

Purpose: Defines 25 Cascade Lake X package-control-unit power and residency PMU aliases for perf. The events expose PCU fixed-clock time, frequency-limit causes, package C-state residency, power-state occupancy, phase shedding, PROCHOT, VR hot, and transition-cycle accounting.

Important APIs/types/functions: The schema is the perf PMU event JSON object consumed by `jevents.py`. Every record uses `Unit: PCU`, `PerPkg: 1`, and counters `0,1,2,3`; most are marked `Experimental: 1`. `EventName` families include `UNC_P_CLOCKTICKS`, `UNC_P_FREQ_MAX_LIMIT_THERMAL_CYCLES`, `UNC_P_FREQ_MAX_POWER_CYCLES`, `UNC_P_FREQ_MIN_IO_P_CYCLES`, `UNC_P_FREQ_TRANS_CYCLES`, `UNC_P_PKG_RESIDENCY_C0/C2E/C3/C6_CYCLES`, `UNC_P_POWER_STATE_OCCUPANCY.CORES_C0/C3/C6`, `UNC_P_PROCHOT_*`, and `UNC_P_VR_HOT_CYCLES`.

Control flow: During perf generation, each JSON object becomes a PCU alias in the Cascade Lake X generated table. At runtime, perf selects this table through the x86 mapfile, resolves the alias to the PCU PMU, and programs the listed `EventCode`/`UMask` values. The PCU clock event has no explicit `EventCode` and is described as a fixed 1 GHz pclk cycle source, which users can combine with residency or limit cycles to compute percentages.

State and persistence behavior: This file is static metadata. Hardware state represented by the events is package-wide and persistent across cores while the counters are enabled: package C-state residency excludes transition time, transition events count frequency or core/package state changes, and occupancy events report the number of cores in selected C-states. No data is stored by the JSON at runtime beyond generated perf tables.

Dependencies: Depends on perf's uncore event schema, the generated x86 Cascade Lake X event map, and kernel exposure of the PCU uncore PMU. The descriptions assume Cascade Lake X PCU semantics, including 1 GHz pclk, package residency states C0/C2E/C3/C6, FIVR phase-shedding states, and PROCHOT/VR hot throttling sources.

Integration points: Integrates with `perf list` and `perf stat` for package-level power diagnosis. It complements `uncore-memory.json`: PCU throttling and memory phase-shedding events help explain memory-controller latency or bandwidth drops observed through iMC counters. Occupancy and transition events can be paired with core workload counters to separate idle policy from workload bottlenecks.

Risks: Nearly every event is experimental, so names or encodings may lag vendor documentation. Several rows have terse descriptions only, making user interpretation depend on external PCU documentation. Package-wide events can be misread as per-process metrics. Events without `UMask` rely on perf generating a valid event string from only the event code and PMU unit; `UNC_P_CLOCKTICKS` additionally relies on special uncore handling for clockticks.

Test signals: JSON parse and x86 `jevents.py` generation should succeed. `perf list` should expose PCU aliases under Cascade Lake X. On hardware, `UNC_P_CLOCKTICKS` should scale close to elapsed wall time at 1 GHz while enabled; residency and transition events should respond to idle-state and frequency-policy changes; thermal/power/PROCHOT events should stay near zero on an unconstrained system and increase under controlled throttling.
