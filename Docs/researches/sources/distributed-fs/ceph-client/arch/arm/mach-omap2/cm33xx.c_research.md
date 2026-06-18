# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm33xx.c

Purpose: Implements AM33xx CM register access, module enable/disable, module readiness/idle polling, clockdomain operations, and clockdomain context save/restore.

Important APIs/types/functions: Internal helpers include `am33xx_cm_read_reg()`, `am33xx_cm_write_reg()`, `am33xx_cm_rmw_reg_bits()`, `_clkctrl_idlest()`, `_is_module_ready()`, `_clktrctrl_write()`, hwsup/force sleep/wakeup helpers, module enable/disable functions, and xlate. Exports `struct clkdm_ops am33xx_clkdm_operations` and registers `am33xx_cm_ll_data` through `am33xx_cm_init()`.

Control flow: Common CM dispatch calls AM33xx functions for module mode writes and IDLEST polling. Generic clockdomain calls map to CLKSTCTRL writes through `cm_inst` and `clkdm_offs`. Clock disable may force sleep if the domain is not in hardware-supervised mode; standby mode avoids forcing flagged domains asleep.

State and persistence: Hardware state lives in AM33xx CM registers. `am33xx_clkdm_save_context()` stores CLKTRCTRL bits into `clkdm->context`, and restore dispatches to deny idle, sleep, wakeup, or allow idle.

Dependencies: Includes AM33xx CM offsets, AM33xx/OMAP34xx regbits, PRM33xx, clockdomain APIs, and optionally suspend state.

Integration points: Used by AM33xx and TI81xx clockdomain data and by common CM APIs for hwmod module control.

Risks: Module access before `_is_module_ready()` can cause imprecise external aborts, which this file explicitly guards against. Standby-specific L4LS handling depends on `pm_suspend_target_state` and correct flags. The code assumes `cm_base.va` is initialized.

Test signals: AM33xx module enable/disable should reach functional/disabled IDLEST within timeout. Standby and suspend/resume should preserve clockdomain mode and avoid L4LS sleep-related wake failures.
