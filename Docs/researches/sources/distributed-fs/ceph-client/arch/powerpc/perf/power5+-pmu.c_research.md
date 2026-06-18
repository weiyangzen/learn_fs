# sources/distributed-fs/ceph-client/arch/powerpc/perf/power5+-pmu.c

Purpose: PMU backend for POWER5+/POWER5++ processors, covering event constraints, alternatives, marked-instruction detection, MMCR computation, generic/cache mappings, and registration.

Important APIs/types/functions: `power5p_pmu`, `init_power5p_pmu`, `power5p_get_constraint`, `power5p_compute_mmcr`, `power5p_get_alternatives`, `power5p_limited_pmc_event`, `power5p_marked_instr_event`, `find_alternative_bdecode`, `power5p_disable_pmc`, `unit_cons`, and generic/cache event maps.

Control flow and state: constraints encode fixed PMC use, PMC5/6 limited events, unit mux requirements, GRS selector fields, byte-lane selectors, and counter count. Alternative lookup handles explicit event tables, byte-decode equivalents, add-event encodings, and run-state substitutions while filtering limited PMC events according to scheduler flags. MMCR computation validates bus byte/unit sharing, selects TTM0/TTM1 units, selects byte lanes/GRS muxes, allocates PMCs, sets adder select for high bus bytes, detects marked events for MMCRA sample enable, and writes MMCR0/MMCR1.

State and persistence behavior: no persistent state. Static descriptor registration is gated by `PVR_POWER5p`. Computed register state is per scheduled group.

Dependencies and integration points: depends on `register_power_pmu`, PowerPC PVR helpers, generic PowerPC perf group constraint solver, perf hardware/cache IDs, and MMCR bit definitions from architecture headers. Flags include `PPMU_LIMITED_PMC5_6` and `PPMU_HAS_SSLOT`.

Risks: POWER5+ differs subtly from POWER5 in constraint bit placement, marked LSU masks, and extra decode alternatives; limited PMC filtering can remove all alternatives; bus byte and unit mux conflicts are complex; marked event detection is table-driven and hardware-specific.

Test signals: POWER5+ boot/registration, generic event counting, raw groups that exercise GRS/LSU byte lanes, limited PMC5/6 events with scheduler flags, marked instruction sampling, and impossible group rejection.
