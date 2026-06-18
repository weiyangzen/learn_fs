# sources/distributed-fs/ceph-client/arch/powerpc/perf/isa207-common.c

Purpose: shared helper implementation for PowerISA v2.07+ PMUs, including POWER8/9/10 style raw event validation, constraint construction, MMCR programming, marked sampling setup, memory data-source decoding, sample weight calculation, alternatives, and reserved field checks.

Important APIs/types/functions: exported helpers `isa207_get_constraint`, `isa207_compute_mmcr`, `isa207_disable_pmc`, `isa207_get_alternatives`, `isa207_get_mem_data_src`, `isa207_get_mem_weight`, `isa3XX_check_attr_config`, and `isa207_pmu_format_group`. Important internal helpers include `is_event_valid`, `mmcra_sdar_mode`, `p10_thresh_cmp_val`, `thresh_cmp_val`, `isa207_find_source`, and threshold/cache/radix constraint helpers.

Control flow and state: event validation selects the valid mask by CPU feature level. Constraint building encodes PMC uniqueness, counter count, cache/L1/L2/L3 grouping, threshold fields, EBB and BHRB requirements, radix scope, and Power10 config1 threshold compare. MMCR computation first records fixed PMC usage, then assigns unpinned events to PMC1-4, sets MMCR1 unit/combine/PMCSEL, MMCRA marked sampling and threshold fields, MMCR2 privilege/idle filters and L2/L3 select, and MMCR3 Power10 event extension fields. Memory source decoding maps SIER fields to perf `PERF_MEM_*` source bits; weight decoding uses MMCRA threshold mantissa/exponent and Power10 SIER2 cycles.

State and persistence behavior: no persistent state. It reads CPU feature flags and SPRs (`MMCRA`, `SIER`, `SIER2`) and writes computed values into caller-provided `mmcr_regs`, `hwc`, data source, and weight structures.

Dependencies and integration points: used by ISA207-family PMU files such as Power8/9/10. It depends on `isa207-common.h`, perf event attributes, PowerPC CPU feature bits, PMU flags (`PPMU_HAS_SIER`, `PPMU_HAS_ATTR_CONFIG1`, `PPMU_ONLY_COUNT_RUN`), and the generic PowerPC perf scheduler's constraint solver.

Risks: bitfield layouts differ across POWER8, POWER9, and POWER10; threshold compare encoding can reject or clamp values; BHRB is only valid with EBB-style requests in raw encoding; guest kernels cannot program some HV-only cache selector state; `pevents[i]` must be valid for branch/exclude/config1 checks; mistakes here affect all newer POWER PMUs.

Test signals: unit-style validation through perf raw events for invalid masks/reserved sample modes, group scheduling tests with conflicting PMCs/cache selectors, `perf mem` source/weight sampling on POWER8/9/10, BHRB sampling tests, and architecture boot tests confirming known generic events count.
