# sources/distributed-fs/ceph-client/arch/powerpc/perf/power5-pmu.c

Purpose: PMU backend for original POWER5 processors, implementing POWER5-specific event constraints, alternatives, marked event detection, MMCR programming, generic/cache event mapping, and PVR-gated registration.

Important APIs/types/functions: `power5_pmu`, `init_power5_pmu`, `power5_get_constraint`, `power5_compute_mmcr`, `power5_get_alternatives`, `power5_marked_instr_event`, `find_alternative_bdecode`, `power5_disable_pmc`, `unit_cons`, `grsel_shift`, and generic/cache tables.

Control flow and state: constraints track fixed PMCs, PMC1/2 vs PMC3/4 grouping, required TTM units, GRS mux fields, byte-lane selectors, unit conflicts, and total PMC1-4 use. MMCR computation first validates fixed PMC collisions, bus byte/unit compatibility, and PMC group pressure, then selects TTM muxes, byte lanes, GRS selectors, adder bits, and PMCSEL fields. Marked-event detection sets `MMCRA_SAMPLE_ENABLE` for selected direct and LSU bus events.

State and persistence behavior: no persistent state. The file exposes one static `power_pmu` descriptor and computes per-event-group MMCR values.

Dependencies and integration points: integrates with the PowerPC perf core through `register_power_pmu` when `PVR_POWER5` is detected. It depends on shared `struct power_pmu`, perf generic/cache IDs, MMCR bit definitions, and the group constraint solver's `add_fields`/`test_adder` values.

Risks: POWER5 bus muxing is highly constrained; LSU1 low-word byte remapping and GRS selector handling can reject valid events or accept bad ones if bitfields drift; PMC5/6 only support specific run/instruction events; original POWER5 differs from POWER5+ in both constraints and marked masks.

Test signals: boot on POWER5, verify PMU registration, run generic cycles/instructions/cache/branch events, schedule multi-event groups across byte lanes and units, validate marked sampling, and confirm unsupported groups fail instead of misprogramming MMCRs.
