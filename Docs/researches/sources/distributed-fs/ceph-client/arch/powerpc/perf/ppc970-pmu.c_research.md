<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/ppc970-pmu.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/perf/ppc970-pmu.c

Purpose: implements perf PMU support for PPC970/970FX/970GX/970MP processors, including direct and bus-event constraint solving, MMCR0/MMCR1/MMCRA programming, generic/cache event aliases, and marked-instruction sampling enablement.

Important APIs/types/functions: `p970_marked_instr_event()` detects events requiring `MMCRA_SAMPLE_ENABLE`; `p970_get_constraint()` encodes PMC, unit, byte lane, SPCSEL, and group constraints; `p970_get_alternatives()` supplies LSU-empty alternates; `p970_compute_mmcr()` assigns PMCs and multiplexer fields for up to eight events; `p970_disable_pmc()` disables a counter by selecting `0x08`; `ppc970_pmu` is the registered PMU descriptor; `init_ppc970_pmu()` gates on PPC970-family PVRs.

Control flow: perf event grouping first queries constraints, then `p970_compute_mmcr()` performs a resource-use pass to reject conflicting PMCs, bus bytes, TTM selectors, and PMC group overuse. A second pass assigns free counters, sets PMCx selectors and adder bits, enables marked sampling when needed, and returns MMCR values. Initialization only registers for supported PVR versions.

State and persistence: static arrays model adder-bit positions, marked direct events, unit constraints, generic events, and cache events. Runtime state is in perf event hardware fields and MMCR register values; there is no dynamic allocation in this file.

Dependencies and integration: depends on core perf headers, PPC special register definitions, `internal.h`, `register_power_pmu()`, and generic powerpc perf event scheduling. It exposes no sysfs named-event group of its own, unlike newer POWER PMUs.

Risks and test signals: constraint packing is dense; off-by-one PMC numbering or group selection can reject valid groups or program wrong counters. Marked-event detection combines direct, add, decode, and LSU/VPU mask logic. Test with multiple grouped events, direct PMC-pinned events, LSU alternative events, marked sampling, generic perf events, cache aliases, and unsupported groups larger than eight events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/ppc970-pmu.c -->
