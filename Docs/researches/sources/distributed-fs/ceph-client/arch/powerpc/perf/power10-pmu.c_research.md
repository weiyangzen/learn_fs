# sources/distributed-fs/ceph-client/arch/powerpc/perf/power10-pmu.c

Purpose: POWER10 and POWER11 processor PMU backend built on `isa207-common`, with POWER10 raw format documentation, event/sysfs tables, cache maps, branch-history filtering, DD1 differences, and PMU registration.

Important APIs/types/functions: `power10_pmu`, `power11_pmu`, `init_power10_pmu`, `init_power11_pmu`, `power10_compute_mmcr`, `power10_bhrb_filter_map`, `power10_config_bhrb`, `power10_get_alternatives`, `power10_check_attr_config`, event/caps/format attribute groups, generic/cache event tables, and `PERF_REG_EXTENDED_MASK`.

Control flow and state: include-time event list expansion creates constants. Initialization verifies PVR, sets `PPMU_P10_DD1` and DD1-specific events when needed, sets the extended register mask to `PERF_REG_PMU_MASK_31`, registers `power10_pmu`, and advertises EBB. POWER11 clones the POWER10 descriptor and changes the name. Runtime MMCR computation delegates to `isa207_compute_mmcr` then sets `MMCR0_C56RUN`; BHRB filter mapping accepts only supported branch filter modes and programs IFM bits in MMCRA.

State and persistence behavior: no disk persistence. Static PMU descriptors and sysfs attributes persist after registration. `cur_cpu_spec->cpu_user_features2` is updated to expose EBB support. DD1 initialization mutates the global descriptor before registration.

Dependencies and integration points: depends on `isa207-common`, PVR constants, PowerPC perf core, event list header, SPR access, and perf branch sample flags. It integrates with `/sys/bus/event_source/devices/cpu` events, formats, caps, generic perf hardware IDs, cache event translation, BHRB, EBB, and extended PMU register sampling.

Risks: duplicate `GENERIC_EVENT_ATTR` macro names appear for branch/cache aliases but only selected pointers are exported per table; DD1 path must not expose unsupported non-DD1 events; POWER11 currently reuses POWER10 behavior wholesale; branch filters unsupported by hardware return `-1`; raw format fields differ from POWER9 and rely on config1 for threshold compare.

Test signals: boot POWER10 DD1 and non-DD1 plus POWER11 if available; confirm PMU name/events/formats; run generic cycles/instructions/branches/cache events; test raw Power10 fields including threshold compare in config1 and MMCR3 bits; verify BHRB filter acceptance/rejection and extended register sampling.
