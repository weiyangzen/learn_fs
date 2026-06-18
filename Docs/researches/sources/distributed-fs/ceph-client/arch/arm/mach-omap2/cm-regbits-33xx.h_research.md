# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/cm-regbits-33xx.h

Purpose: Defines AM33xx CM register bit masks and shifts, generated from hardware data.

Important APIs/types/functions: Provides CLKOUT2, DPLL divider/multiplier/enable, HSDIVIDER, IDLEST, MODULEMODE, CLKTRCTRL, optional clock enable, STM/TRC, and DPLL status fields. Key values used by `cm33xx.c` are `AM33XX_IDLEST_MASK`, `AM33XX_IDLEST_SHIFT`, `AM33XX_MODULEMODE_MASK`, `AM33XX_MODULEMODE_SHIFT`, `AM33XX_CLKTRCTRL_MASK`, and `AM33XX_CLKTRCTRL_SHIFT`.

Control flow: No executable flow. AM33xx CM code uses these macros to poll module state, enable/disable module mode, and save/restore clockdomain transition mode.

State and persistence: No software state; represents hardware register fields.

Dependencies: Standalone guarded header included by `cm33xx.h`, `cm33xx.c`, and AM33xx/TI81xx clockdomain data.

Integration points: Critical to AM33xx module readiness/idle waits, CLKSTCTRL mode writes, and module enable/disable through CM_*_CLKCTRL registers.

Risks: Generated definitions must remain synchronized with AM33xx hardware databases. Misusing masks with OMAP34xx mode constants is intentional in this code but requires matching field encoding.

Test signals: AM33xx/TI81xx boot with module enable/disable should avoid CM timeouts and imprecise external aborts. Build tests should include suspend-enabled and non-suspend configurations.
