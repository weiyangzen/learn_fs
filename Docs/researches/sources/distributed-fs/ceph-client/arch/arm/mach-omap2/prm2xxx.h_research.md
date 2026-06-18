# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm2xxx.h

## Purpose
Declares OMAP2xxx PRM register address macros, global PRCM register offsets, module-specific PRM offsets, OMAP24xx-specific wake/IRQ offsets, and OMAP2 PRM init/clockdomain APIs.

## APIs, Flow, And State
Address macros `OMAP2420_PRM_REGADDR()` and `OMAP2430_PRM_REGADDR()` generate MMIO addresses. The header provides revision/sysconfig/IRQ/voltage/clock source/clock output/voltage setup/polarity offsets, common module registers (`RM_RSTCTRL`, `RM_RSTST`, `PM_PWSTCTRL`, `PM_WKEN`, `PM_WKST`, `PM_WKDEP`), and OMAP24xx second wake registers. It declares `omap2xxx_clkdm_sleep()`, `omap2xxx_clkdm_wakeup()`, and `omap2xxx_prm_init()`.

## Dependencies And Integration
Includes `prcm-common.h`, `prm.h`, and `prm2xxx_3xxx.h`. Used by OMAP2 PRM implementation, assembly/SDRC code, and clockdomain code.

## Risks And Test Signals
The same offset names are shared with OMAP3 but some OMAP2 global registers carry PRCM names, so call sites must use the right base/register accessor. Test signals are OMAP2420/2430 boot, PRCM IRQ access, voltage setup writes, and reset/wakeup register reads.
