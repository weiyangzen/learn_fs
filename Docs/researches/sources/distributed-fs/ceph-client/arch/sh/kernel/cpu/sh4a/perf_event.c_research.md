# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/perf_event.c

Purpose: implements the SH-4A hardware performance-counter backend for Linux perf. It maps generic and cache perf events to SH-4A raw event codes and provides register operations for two hardware counters.

Important APIs, types, and functions: `sh4a_pmu_init()` registers `sh4a_pmu` with `register_sh_pmu()` during `early_initcall`. `sh4a_event_map()`, `sh4a_pmu_read()`, `sh4a_pmu_enable()`, `sh4a_pmu_disable()`, `sh4a_pmu_enable_all()`, and `sh4a_pmu_disable_all()` implement `struct sh_pmu`. The event tables are `sh4a_general_events` and `sh4a_cache_events`.

Control flow: init first checks `boot_cpu_data.flags & CPU_HAS_PERF_COUNTER`; unsupported CPUs get software events only. Perf event setup uses the generic map or cache matrix to select `hwc->config`; enabling a counter clears the corresponding PMCAT overflow/clear bit, writes the event code into `PPC_CCBR(idx)`, enables command/counting bits, then sets `CCBR_DUC`.

State and persistence: counter state lives in hardware registers `PPC_CCBR`, `PPC_PMCTR`, and `PPC_PMCAT`. `PPC_PMCAT` has a SH-X3-specific address under `CONFIG_CPU_SHX3`. The static PMU advertises two counters and a `raw_event_mask` of `0x3ff`.

Dependencies and integration points: integrates with Linux perf through SuperH `register_sh_pmu()`, `<linux/perf_event.h>`, and `<asm/processor.h>`. Raw MMIO helpers access fixed CPU counter registers.

Risks: comments note undocumented SH-X3 PMCAT relocation found by trial and error, so CPU revisions may differ. Unsupported generic events use `-1`, and several cache matrix entries use `0`, which must match generic SH PMU interpretation. Writes must preserve emulator-reserved PMCAT bits via `PMCAT_EMU_CLR_MASK`.

Test signals: `perf stat` for cycles, instructions, branch instructions, and L1 cache events should produce counts on CPUs with `CPU_HAS_PERF_COUNTER`; unsupported events should fail cleanly; SH-X3 testing should confirm counters clear and count using the alternate PMCAT address.
