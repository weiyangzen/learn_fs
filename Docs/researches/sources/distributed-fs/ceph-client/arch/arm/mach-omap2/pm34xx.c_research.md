# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/pm34xx.c

## Purpose
`pm34xx.c` implements OMAP3 power management: idle entry, suspend-to-RAM, powerdomain target setup, PRCM wake IRQ handling, context save/restore, errata handling, secure RAM save, and OMAP3-specific PM initialization.

## Important APIs, Types, and Functions
Key exported symbols are `pm34xx_errata`, `omap_sram_idle()`, `omap3_pm_off_mode_enable()`, `omap3_pm_get_suspend_state()`, `omap3_pm_set_suspend_state()`, `omap_push_sram_idle()`, and `omap3_pm_init()`. Internal functions include `omap3_core_save_context()`, `omap3_core_restore_context()`, PRCM IRQ handlers, `omap34xx_save_context()`, `omap3_pm_suspend()`, `pwrdms_setup()`, and `pm_errata_configure()`.

## Control Flow
`omap3_pm_init()` configures errata, PRCM registers, wake/io IRQs, PMIC off-mode policy, powerdomain target list, clockdomain idle setup, powerdomain lookups, generic suspend registration, idle hook, wake dependencies, secure RAM save, and scratchpad save. Idle reads target states, prepares transitions, saves core/SDRC/INTC/control context when needed, configures PMIC signaling, enters SRAM WFI or CPU suspend, restores context, and updates powerdomain transition state.

## State and Persistence Behavior
State includes `pwrst_list`, `mpu_pwrdm`, `neon_pwrdm`, `core_pwrdm`, `per_pwrdm`, `omap3_do_wfi_sram`, `pm34xx_errata`, secure RAM storage, and saved suspend targets. Hardware state spans PRCM IRQ status, powerdomain targets, INTC/control/CM/SDRC/SRAM context, PMIC signaling, and wake dependencies.

## Dependencies and Integration Points
It depends on CPU PM, suspend, cpuidle, clockdomain/powerdomain, PRM/CM/control/SDRC, SRAM function copy, secure services, VC PMIC signaling, OMAP interrupt controller, and generic `pm.c` suspend registration.

## Risks
OMAP3 off-mode is sensitive to silicon errata i582/i583/i608, secure device ROM behavior, and PMIC DT nodes. Failing context save/restore or PRCM IRQ ordering can hang resume or lose wakeups. Debugfs can alter target states at runtime.

## Test Signals
Boot OMAP3430/3630/AM35x variants, verify PRCM IRQ request success, idle and suspend target states, off-mode enable detection from TWL power nodes, secure RAM save on HS/EMU devices, wake from IO and PRCM events, and no context loss after repeated suspend/resume.
