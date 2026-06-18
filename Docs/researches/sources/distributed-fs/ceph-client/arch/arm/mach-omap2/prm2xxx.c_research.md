# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm2xxx.c

## Purpose
Implements OMAP2xxx-specific PRM operations: reset-source mapping, DPLL reset reboot, wake status clearing, clockdomain sleep/wakeup, and OMAP2 powerdomain operation callbacks.

## APIs, Flow, And State
Key exported functions are `omap2xxx_clkdm_sleep()`, `omap2xxx_clkdm_wakeup()`, and `omap2xxx_prm_init()`. Static flow maps `PRM_RSTST_WKUP` bits to standard reset IDs, converts OMAP24xx reversed power-state encodings to common `PWRDM_POWER_*` values, toggles `OMAP_RST_DPLL3_MASK` for reboot, and clears module wake status by writing back masked `PM_WKST` bits. `omap2_pwrdm_operations` binds set/read next/current power state, memory state operations from the shared OMAP2/3 file, and transition waits.

## Dependencies And Integration
Depends on `powerdomain`, `clockdomain`, `prm2xxx.h`, `cm2xxx_3xxx.h`, and OMAP24xx bit definitions. Registers its `prm_ll_data` with `prm_register()`, supplying hardreset callbacks from `prm2xxx_3xxx.c`.

## Risks And Test Signals
OMAP2 power-state encodings differ from OMAP3+, making conversion correctness important. DPLL reset and wake-status clear code writes hardware directly. Test signals are OMAP2 clockdomain sleep/wakeup, powerdomain state reads, reboot through DPLL reset, and accurate reset-source bits.
