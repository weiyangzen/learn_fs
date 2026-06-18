<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/rtd119x_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/rtd119x_wdt.c

Purpose: built-in watchdog-core driver for Realtek RTD129x/RTD119x style watchdog registers.

Important APIs, types, and functions: `struct rtd119x_watchdog_device` stores watchdog, MMIO base, and clock. Important functions are `rtd119x_wdt_start()`, `rtd119x_wdt_stop()`, `rtd119x_wdt_ping()`, `rtd119x_wdt_set_timeout()`, and probe.

Control flow: probe maps registers, enables the clock, initializes watchdog bounds from the clock rate, stops on reboot, clears the watchdog, programs the default timeout, stops hardware, and registers. Start and stop replace the low enable byte in `TCWCR` with magic enable/disable values. Ping writes the clear bit then calls start. Timeout writes seconds multiplied by clock rate into overflow register.

State and persistence behavior: state is entirely MMIO plus selected timeout; the driver is built in with `builtin_platform_driver()`. No bootstatus or nowayout handling is present.

Dependencies and integration points: depends on platform MMIO, enabled clock, OF compatible `realtek,rtd1295-watchdog`, and watchdog core.

Risks and edge cases: multiplication of timeout by clock rate is written as 32-bit and relies on max-timeout calculation to avoid overflow. `watchdog_info.options` is zero even though operations support timeout and ping. No `watchdog_init_timeout()` means DT timeout property is ignored.

Test signals: default timeout programming, max timeout from clock, start/stop magic values, ping re-enabling behavior, stop-on-reboot, and DT timeout ignored/regression awareness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/rtd119x_wdt.c -->
