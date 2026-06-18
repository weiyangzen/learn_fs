# sources/distributed-fs/ceph-client/drivers/watchdog/digicolor_wdt.c

## Purpose
This platform driver controls the Conexant Digicolor watchdog implemented by Timer A. It provides standard watchdog operation plus a restart handler that forces a short timeout.

## Important APIs, types, and functions
`struct dc_wdt` stores MMIO base, clock, and spinlock. Core helpers are `dc_wdt_set`, `dc_wdt_start`, `dc_wdt_stop`, `dc_wdt_set_timeout`, `dc_wdt_get_timeleft`, and `dc_wdt_restart`. The static `dc_wdt_wdd` carries ops, identity, and timeout limits.

## Control Flow
Probe maps the timer registers, obtains a clock, computes `max_timeout` from `U32_MAX / clk_rate`, initializes timeout from module/DT, sets restart priority, and registers the watchdog. Start and set-timeout program count as seconds times clock rate and enable both counter and watchdog bits. Stop clears the control register. Restart programs a count of one and waits for reset.

## State and Persistence
Runtime state is a static watchdog object plus per-device `dc_wdt` private data. Hardware count/control registers contain volatile state. No clock enable call is made beyond obtaining the clock handle, so integration depends on platform clock state.

## Dependencies and Integration Points
The driver depends on OF compatible `cnxt,cx92755-wdt`, platform MMIO resources, the clock framework, watchdog restart priority, and spinlocked MMIO writes.

## Risks and Test Signals
Risks include static watchdog reuse, timeout multiplication overflow if clock rate changes, get_timeleft division by zero if an invalid clock is supplied, and stop not using the spinlock. Tests should cover timeout boundary calculation, start/stop/restart register values, timeleft conversion, missing resource/clock errors, and reboot stop behavior.
