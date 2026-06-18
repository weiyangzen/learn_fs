<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/power8-pmu.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/perf/power8-pmu.c

Purpose: registers the POWER8 core PMU with Linux perf, translating generic perf events, cache events, branch-history filters, raw event encodings, and POWER8-specific alternate event codes into the shared PowerISA v2.07 PMU backend.

Important APIs/types/functions: `power8_get_alternatives()` delegates to `isa207_get_alternatives()` with the local alternate-event table; `power8_bhrb_filter_map()` accepts only branch-any or any-call branch history filters; `power8_config_bhrb()` writes the IFM bits into `SPRN_MMCRA`; `power8_cache_events` maps `PERF_COUNT_HW_CACHE_*` tuples; `power8_pmu` is the exported `struct power_pmu`; `init_power8_pmu()` gates registration on `PVR_POWER8E`, `PVR_POWER8NVL`, or `PVR_POWER8`.

Control flow: boot-time PMU probing reads PVR, registers `power8_pmu`, advertises EBB support through `cur_cpu_spec->cpu_user_features2`, and logs the PMAO workaround when active. Runtime perf setup enters through generic powerpc perf code, which uses this file's generic/cache tables, `isa207_compute_mmcr()`, `isa207_get_constraint()`, and BHRB callbacks to program MMCR/MMCRA/MMCRC fields described in the header comment.

State and persistence: all state is static tables plus the registered `power_pmu`; hardware-visible state is in MMCRA and PMU registers programmed by the common ISA207 backend. No allocation or persistent per-event state is created here beyond perf core state.

Dependencies and integration: depends on `isa207-common.h`, `power8-events-list.h`, perf sysfs attribute macros, PVR/cpu feature definitions, and special-register accessors. It integrates with perf event creation, sysfs `events`, `format`, and `caps` groups, EBB exposure, BHRB sampling, memory data source decoding, and generic cache/generic event aliases.

Risks and test signals: event-code or alternate-table mistakes silently count the wrong hardware source; BHRB filter rejection must match hardware limits; raw-event bit fields are dense and SoC-specific. Test with `perf list`, generic events, cache events, marked events, BHRB call filtering, raw events using threshold/cache/sample bits, and POWER8 variant boot detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/power8-pmu.c -->
