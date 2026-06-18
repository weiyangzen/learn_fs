<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pm.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pm.c

Purpose: generic PXA platform suspend operations that dispatch to SoC-specific PM function tables.

Important APIs/functions: global `pxa_cpu_pm_fns` points to SoC PM callbacks. `pxa_pm_enter()` handles iWMMXt disable, optional register save, checksum validation, low-level enter, and restore. `pxa_pm_prepare()` and `pxa_pm_finish()` call optional SoC hooks. `pxa_pm_init()` allocates the save buffer and installs `platform_suspend_ops`.

Control flow: SoC init assigns `pxa_cpu_pm_fns`; `device_initcall(pxa_pm_init)` verifies it, allocates `sleep_save`, and registers suspend ops. On suspend, state validity and enter are delegated to SoC code.

State and persistence: static `sleep_save` persists after init. Checksum failure loops indefinitely re-entering the low-power state, waiting for hardware reset.

Dependencies and integration: depends on `pm.h`, Linux suspend core, and SoC implementations in `pxa25x.c`, `pxa27x.c`, or `pxa3xx.c`.

Risks and test signals: if no SoC function table is installed before device init, PM registration fails. Checksum detects corrupted sleep-save memory but recovery is hard reset only. Test `mem` and `standby` suspend per SoC, iWMMXt builds, and error paths for missing PM hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pm.c -->
