# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/pm.h

## Purpose
`pm.h` is the central private PM header for mach-omap2. It declares OMAP idle/suspend entry points, shared globals, SRAM routines, errata flags, PMIC init hooks, oscillator latency access, and common suspend registration.

## Important APIs, Types, and Functions
Key declarations include `omap3_idle_init()`, `omap4_idle_init()`, `omap_sram_idle()`, `omap_pm_clkdms_setup()`, `omap3_pm_get_suspend_state()`, `omap3_pm_set_suspend_state()`, `enable_off_mode`, OMAP24xx/34xx suspend assembly hooks, AM33xx SRAM address structures, `pm34xx_errata`, `pm44xx_errata`, `omap_devinit_smartreflex()`, `omap3_twl_init()`, `omap4_twl_init()`, `omap4_cpcap_init()`, `omap_pm_get_oscillator()`, and `omap_common_suspend_init()`.

## Control Flow
The header controls build-time availability with configuration stubs. Callers can invoke PMIC or SmartReflex initialization without scattering `#ifdef`s; disabled features return `-EINVAL` or no-op.

## State and Persistence Behavior
It owns no definitions except macros and stubs, but it exposes global PM state and errata masks used to decide suspend paths and workarounds.

## Dependencies and Integration Points
It includes `powerdomain.h` and is used by `pm.c`, `pm34xx.c`, `pm44xx.c`, `pm33xx-core.c`, PMIC files, powerdomain code, and assembly support.

## Risks
Header stubs define behavior when subsystems are disabled; changing return values can alter init error handling. Errata macro changes affect low-power safety paths across SoCs.

## Test Signals
Build with combinations of `CONFIG_PM`, `CONFIG_SUSPEND`, `CONFIG_CPU_IDLE`, `CONFIG_TWL4030_CORE`, `CONFIG_MFD_CPCAP`, `CONFIG_POWER_AVS_OMAP`, and SoC options. Verify no missing symbols and expected PM feature enable/disable behavior.
