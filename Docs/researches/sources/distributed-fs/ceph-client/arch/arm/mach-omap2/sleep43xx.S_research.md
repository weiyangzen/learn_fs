# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/sleep43xx.S

## Purpose
Implements AM43xx low-level suspend and deep-sleep resume code, extending AM33xx-style EMIF handling with L2X0 cache state, MPU clockdomain sleep, RTC-only power-down support, and EMIF hardware leveling on resume.

## APIs, Flow, And State
Exports `am43xx_do_wfi`, `am43xx_resume_offset`, `am43xx_resume_from_deep_sleep`, `am43xx_emif_sram_table`, `am43xx_pm_sram`, `am43xx_pm_ro_sram_data`, and `am43xx_do_wfi_sz`. Entry flow stores flags, optionally obtains L2 base, flushes/invalidates caches and L2 state into SRAM data, refreshes RTC virtual address translations for RTC-only mode, enters EMIF self-refresh and saves context, disables EMIF, optionally programs RTC PMIC power/wakeup and waits, optionally signals WKUP_M3 by disabling MPU and setting MPU CLKSTCTRL to SW_SLEEP, then WFI. Abort path restores MPU/EMIF/cache and aborts self-refresh. Deep resume sets MPU CLKSTCTRL back to HW_AUTO, powers down EMIF until context restore, re-enables EMIF, restores/exits self-refresh, disables EMIF poweroff, runs hardware leveling, restores/enables L2 via secure monitor calls, and jumps to `cpu_resume`.

## Dependencies And Integration
Depends on AM43xx CM/PRM offsets, `pm33xx` flags, EMIF SRAM helpers, L2X0 registers, OMAP4 secure monitor indices, RTC PMIC registers, and `pm-asm-offsets.h` SRAM layouts.

## Risks And Test Signals
RTC-only mode intentionally powers down via PMIC and waits on RTC seconds, so register accessibility and TLB priming matter. L2 restore depends on secure monitor services. Test signals are AM43xx RTC+DDR and deep-sleep resume, EMIF hardware leveling, L2 cache enable path, WKUP_M3 wake, and abort return path with `r0 = 1`.
