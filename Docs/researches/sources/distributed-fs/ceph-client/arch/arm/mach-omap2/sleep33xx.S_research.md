# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/sleep33xx.S

## Purpose
Implements AM33xx SRAM-resident WFI and deep-sleep resume code, coordinating cache shutdown, EMIF self-refresh/context save, EMIF clock gating, WKUP_M3 signaling, and resume back to `cpu_resume`.

## APIs, Flow, And State
Exports `am33xx_do_wfi`, `am33xx_resume_offset`, `am33xx_resume_from_deep_sleep`, `am33xx_pm_sram`, `am33xx_pm_ro_sram_data`, and `am33xx_do_wfi_sz`. `am33xx_do_wfi` stores WFI flags in SRAM data, optionally flushes/inhibits caches, enters EMIF self-refresh, saves EMIF context, disables EMIF clock, optionally disables MPU clock mode to wake M3, executes barriers and WFI, then handles abort/late interrupt by re-enabling MPU/EMIF, aborting self-refresh, restoring cache enable, and returning `1`. Deep-sleep resume re-enables EMIF, restores EMIF context, exits self-refresh, and branches to physical `cpu_resume` with `r0 = 0`.

## Dependencies And Integration
Depends on `pm33xx` WFI flags, TI EMIF SRAM function table offsets, CM33xx register addresses, and `pm-asm-offsets.h` for SRAM data layout. Integrates with wkup_m3 firmware and EMIF SRAM helper code.

## Risks And Test Signals
Ordering around cache disable, EMIF self-refresh, and clock gating is critical because DDR may be unavailable. Test signals are AM33xx suspend abort handling, successful deep-sleep resume, EMIF context restoration, WKUP_M3 wake events, and no cache/MMU faults.
