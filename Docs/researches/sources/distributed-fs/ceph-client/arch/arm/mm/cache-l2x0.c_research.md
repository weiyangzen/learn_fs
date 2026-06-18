# sources/distributed-fs/ceph-client/arch/arm/mm/cache-l2x0.c

Purpose: implements the ARM L2x0 outer-cache controller framework for L2C-210, L2C-220, PL310/L2C-310, Marvell Aurora, Broadcom PL310 variants, and Tauros3. It initializes controllers from platform code or device tree, installs `outer_cache` callbacks, applies errata workarounds, saves registers for resume, and registers PMU support.

Important APIs/types/functions: key data includes `struct l2c_init_data`, global `l2x0_base`, `l2x0_data`, `l2x0_lock`, `l2x0_way_mask`, `l2x0_size`, `sync_reg_offset`, `l2x0_saved_regs`, `l2x0_bresp_disable`, and `l2x0_flz_disable`. Core functions include `l2c_wait_mask`, `l2c_write_sec`, `l2c_enable`, `l2c_disable`, `l2c_resume`, L2C-210/220 range operations, PL310 erratum handlers and config/save/enable/fixup paths, `__l2c_init`, `l2x0_init`, DT parsers `l2x0_of_parse` and `l2c310_of_parse`, Aurora/Broadcom/Tauros3 variant callbacks, and `l2x0_of_init`.

Control flow: platform or DT init maps the controller, chooses an `l2c_init_data`, saves current register state, parses DT properties if the controller is disabled, computes ways and size from AUX/cache ID, copies and patches `outer_cache` callbacks, applies errata or `nosync`, enables the controller if needed, saves final state for resume, logs configuration, and calls `l2x0_pmu_register`. Runtime cache maintenance callbacks perform line, way, or range operations with controller-specific locking and sync behavior. Suspend/resume uses saved registers and PMU suspend/resume.

State and persistence: MMIO base, selected controller data, way mask, size, sync offset, and saved register block are global runtime state. `outer_cache` becomes the global integration point for DMA and cache maintenance. DT-derived aux/prefetch/power/filter settings persist in saved registers and hardware until reset.

Dependencies and integration points: depends on ARM CP15 helpers, device tree, secure register write hooks (`outer_cache.write_sec`), optional platform configure hook, CPU hotplug for PL310 full-line-zero, PMU registration, and hardware headers for L2X0/Aurora/Tauros3. It is selected by `CACHE_L2X0`.

Risks: this file touches secure/non-secure registers and hardware errata. Wrong AUX mask/value handling can corrupt reserved bits or mis-size the cache. Range operations must respect cache-line alignment and controller background-operation constraints. Some systems require disabling outer sync for I/O coherency; enabling it can deadlock on affected platforms. Broadcom address remapping and Aurora page/range limits are SoC-specific and easy to regress.

Test signals: boot and DMA coherency tests on L210, L220, PL310, Aurora, Broadcom, and Tauros3 DTs; suspend/resume register restore checks; errata configuration tests for PL310 revisions; `arm,io-coherent` and `arm,outer-sync-disable` scenarios; CPU hotplug for Cortex-A9 full-line-zero; and perf PMU registration where supported.
