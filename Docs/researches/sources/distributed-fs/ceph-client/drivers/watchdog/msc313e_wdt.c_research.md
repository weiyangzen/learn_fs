# sources/distributed-fs/ceph-client/drivers/watchdog/msc313e_wdt.c

## Purpose
`msc313e_wdt.c` is a platform watchdog driver for the MStar MSC313e block. It programs a clock-derived watchdog period into two 16-bit registers, clears the counter to service it, and exposes the device through the Linux watchdog core.

## Important APIs, types, and functions
The private `struct msc313e_wdt_priv` carries the MMIO base, input clock, and embedded `watchdog_device`. Operations are `msc313e_wdt_start`, `msc313e_wdt_stop`, `msc313e_wdt_ping`, and `msc313e_wdt_settimeout`; probe uses `devm_platform_ioremap_resource`, `devm_clk_get`, `watchdog_init_timeout`, `watchdog_stop_on_reboot`, `watchdog_stop_on_unregister`, and `devm_watchdog_register_device`.

## Control flow
Probe maps registers, obtains the clock, computes `max_timeout` from `U32_MAX / clk_rate`, detects a bootloader-running watchdog by checking the period registers, and registers the watchdog. Start enables the clock, writes the requested period split across low/high registers, and clears the counter. Ping only writes the clear register. Stop zeroes period and clear registers and disables the clock. Suspend stops an active watchdog and resume restarts it.

## State and persistence
Runtime state is the watchdog core status plus `timeout`, MMIO registers, and clock enable state. Hardware may persist a nonzero period from firmware, represented with `WDOG_HW_RUNNING`; there is no disk persistence.

## Dependencies and integration points
It depends on platform device probing, OF compatible `mstar,msc313e-wdt`, the clock framework, MMIO accessors, and the watchdog core. Module parameter `timeout` feeds `watchdog_init_timeout`.

## Risks and test signals
Risks include zero or unstable clock rates, overflow in timeout-to-cycle conversion if clock changes after probe, and suspend/resume stopping a watchdog that `nowayout` policy might expect to remain alive. Test signals include DT probe, inherited-running watchdog detection, timeout boundary checks, clock enable failure injection, ping/start/stop sequencing, and suspend/resume with an active watchdog.
