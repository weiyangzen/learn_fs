<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/power9-pmu.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/perf/power9-pmu.c

Purpose: registers the POWER9 core PMU with Linux perf, including POWER9 raw-format fields, generic/cache event aliases, branch-history filtering, MMCR programming via the ISA207 backend, DD-level event blacklists, and extended register capture support.

Important APIs/types/functions: `power9_get_alternatives()` provides alternate raw event encodings; `power9_check_attr_config()` rejects unsupported sample-mode value `0xC` and delegates ISA3xx checks; `power9_bhrb_filter_map()` and `power9_config_bhrb()` handle BHRB IFM bits; `power9_cache_events` and `power9_generic_events` map generic perf requests; `power9_pmu` is the registered `struct power_pmu`; `init_power9_pmu()` performs PVR gating and DD blacklist selection.

Control flow: initialization accepts only `PVR_POWER9`, chooses blacklist arrays for non-Cumulus DD2.1 or DD2.2 PVRs, sets `PERF_REG_EXTENDED_MASK` to `PERF_REG_PMU_MASK_300`, registers the PMU, and advertises EBB. During event setup, perf uses the file's format group for raw config bits, validates attributes, maps generic/cache events, computes MMCRs with `isa207_compute_mmcr()`, and applies the cache PMC4 group constraint.

State and persistence: persistent state is static tables plus mutable fields in `power9_pmu` for blacklist pointer/count during init. Hardware state is programmed through the common backend and the BHRB callback writes MMCRA. No heap allocation occurs here.

Dependencies and integration: depends on `isa207-common.h`, `power9-events-list.h`, perf sysfs macros, PVR helpers, CPU feature flags, and the shared Power PMU registration layer. It integrates with perf sysfs `events`, POWER9-specific `format`, cache/generic events, BHRB, EBB, extended sample registers, and memory data source/weight helpers.

Risks and test signals: blacklist selection relies on precise PVR bit interpretation; raw format differs from POWER8 in threshold compare and `sdar_mode`; unsupported sample modes must be rejected before programming hardware. Test on POWER9 DD2.1/DD2.2/Cumulus, verify blacklisted raw events fail, exercise generic/cache/memory events, BHRB call filtering, extended register sampling, and raw events with `sdar_mode`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/power9-pmu.c -->
