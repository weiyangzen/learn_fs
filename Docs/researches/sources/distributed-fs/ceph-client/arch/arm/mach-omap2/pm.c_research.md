# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/pm.c

## Purpose
`pm.c` contains common OMAP2+ PM glue shared by SoC-specific PM implementations. It registers platform suspend operations, stores global off-mode policy, exposes oscillator latency data, idles clockdomains, and runs late PM initialization.

## Important APIs, Types, and Functions
Important symbols are global `enable_off_mode`, `omap_pm_soc_init`, `omap_pm_clkdms_setup()`, `omap_pm_get_oscillator()`, `omap_common_suspend_init()`, `omap_pm_nop_init()`, and late init `omap2_common_pm_late_init()`. Suspend callbacks include `omap_pm_begin()`, `omap_pm_enter()`, `omap_pm_end()`, and `omap_pm_wake()`.

## Control Flow
SoC PM code calls `omap_common_suspend_init()` with its suspend function. The generic suspend ops then route `PM_SUSPEND_MEM` into that SoC function, while begin/end toggle CPU idle polling and OMAP3 PRCM IRQ preparation/completion. Late init registers PMIC data, initializes voltage, SmartReflex, calls `omap_pm_soc_init()`, and enables clock autoidle.

## State and Persistence Behavior
Global state includes `enable_off_mode`, the SoC suspend function pointer, optional oscillator latency data, and `omap_pm_soc_init`. Hardware state changes happen through voltage initialization, SmartReflex device init, clockdomain idle permissions, and clock autoidle.

## Dependencies and Integration Points
It depends on suspend core, OPP/voltage code, clockdomain/powerdomain frameworks, OMAP PRCM IRQ helpers, TWL/CPCAP PMIC init, SmartReflex, and SoC-specific PM modules such as `pm34xx.c` and `pm44xx.c`.

## Risks
Ordering is important: PMIC and voltage init must precede SoC PM setup. A missing suspend function causes suspend to return `-ENOENT`; wrong begin/wake handling can lose OMAP3 PRCM wake interrupts.

## Test Signals
Boot OMAP3/4/AMx3 with PM enabled, confirm late init logs no SoC PM failure, suspend-to-RAM enters the SoC path, clock autoidle is enabled, and PRCM wake handling works on OMAP3.
