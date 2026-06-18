# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/sleep24xx.S

## Purpose
Provides OMAP24xx low-level CPU suspend code that puts SDRC into self-refresh, executes WFI, and restores SDRC/DLL state on wake.

## APIs, Flow, And State
Exports `omap24xx_cpu_suspend` and `omap24xx_cpu_suspend_sz`. Inputs are the pre-sleep DLL control value, `SDRC_DLLA_CTRL`, and `SDRC_POWER` addresses in `r0-r2`. Flow saves registers, issues cache/write barriers, sets SDRC self-refresh-on-idle, waits for interrupt, delays for DPLL/DLL relock, clears self-refresh, touches SDRC memory to restart refresh, rewrites DLLA/DLLB when DDR is used, delays again, and returns.

## Dependencies And Integration
Includes OMAP24xx and SDRC register definitions. This function is copied/called by OMAP2 PM code during deep sleep and relies on SDRC base/timing setup from the SDRC C code.

## Risks And Test Signals
The code depends on fixed delay loops and comments describe early 242x oscillator timing errata. Any wrong register address or DLL value risks memory corruption after wake. Test signals are OMAP24xx deep sleep/resume, DDR vs SDR behavior, and absence of post-resume memory faults.
