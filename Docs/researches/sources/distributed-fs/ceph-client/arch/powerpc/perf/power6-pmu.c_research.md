# sources/distributed-fs/ceph-client/arch/powerpc/perf/power6-pmu.c

Purpose: PMU backend for POWER6 processors, implementing event-bus constraints, PMC assignment, marked instruction sampling, alternatives, generic/cache event maps, and CPU registration.

Important APIs/types/functions: `power6_pmu`, `init_power6_pmu`, `p6_compute_mmcr`, `p6_get_constraint`, `p6_get_alternatives`, `p6_limited_pmc_event`, `power6_marked_instr_event`, `p6_disable_pmc`, `direct_event_is_marked`, `marked_bus_events`, and generic/cache tables.

Control flow and state: `p6_compute_mmcr` rejects collisions and more than six events, assigns fixed PMCs or free PMC1-4 slots, configures event-bus byte unit selectors and nest subunit selectors, sets load-lookahead and address-select bits, toggles PMCxSEL encodings for PMC3/4 bus select differences, marks sampling events, and returns MMCR0/MMCR1/MMCRA. Constraint generation mirrors those resources as adder/select fields. Alternatives come from a binary-searched presorted table plus sum-event transforms and run-state substitutions.

State and persistence behavior: no persistent state. Runtime state is a static `power_pmu` descriptor registered on `PVR_POWER6` and per-group computed MMCR values.

Dependencies and integration points: depends on PowerPC perf core, PVR detection, MMCR definitions, and scheduler flags for limited PMC filtering (`PPMU_LIMITED_PMC5_6`, `PPMU_LIMITED_PMC_OK`, `PPMU_LIMITED_PMC_REQD`, `PPMU_ONLY_COUNT_RUN`). Generic/cache maps translate perf standard events to POWER6 raw codes.

Risks: marked event detection mixes direct-event table classes with bus-event masks; limited PMC5/6 alternatives must be filtered correctly; event-bus byte conflicts and nest subunit conflicts are easy to misencode; PMCxSEL rewrites for PMC3/4 are hardware-specific.

Test signals: POWER6 boot registration, generic and raw event counting, run-state-only alternatives, limited PMC scheduling tests, marked sampling tests, and conflicting event-bus group rejection.
