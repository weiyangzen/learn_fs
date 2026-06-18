# sources/distributed-fs/ceph-client/arch/arm/mach-imx/system.c

Purpose: i.MX restart/watchdog reset support and optional PL310 prefetch tuning.

Important APIs/types/functions: Defines `mxc_restart()`, `mxc_arch_reset_init()`, optional `imx1_reset_init()`, and `imx_init_l2cache()`.

Control flow: Reset init stores watchdog MMIO base, gets/prepares `imx2-wdt.0` clock, and optionally adjusts the watchdog control bit for i.MX1. Restart enables the watchdog clock, writes the reset bit three times for i.MX6Q erratum ERR004346, waits, logs failure, then falls back to `soft_restart(0)`. L2 init finds `arm,pl310-cache`, maps it, and if disabled configures double linefill, instruction/data prefetch, and offset 15.

State and persistence: Global state is `wdog_base`, `wdog_clk`, and `wcr_enable`. Hardware state is watchdog control, watchdog clock, and PL310 prefetch registers.

Dependencies and integration points: Depends on ARM machine restart path, clock framework, i.MX relaxed 16-bit writes, DT PL310 node, and L2X0 definitions.

Risks: If watchdog base is not initialized, restart relies on fragile jump-to-zero fallback. Clock prepare/enable error handling is minimal. Triple writes are broad across platforms. PL310 tuning only occurs when cache is disabled and assumes register compatibility.

Test signals: Invoke reboot on supported boards and confirm hardware reset. Build/test `CONFIG_CACHE_L2X0` and validate PL310 register programming only on matching systems.
