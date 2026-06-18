# sources/distributed-fs/ceph-client/drivers/watchdog/visconti_wdt.c

## Purpose
`visconti_wdt.c` drives Toshiba Visconti watchdog hardware. It uses a clock-derived divider to run the watchdog at 2 MHz, programs min/max/count/control registers, and supports time-left reporting.

## Important APIs, types, and functions
`struct visconti_wdt_priv` embeds watchdog, MMIO base, and divider. Watchdog ops are `visconti_wdt_start()`, `visconti_wdt_stop()`, `visconti_wdt_ping()`, `visconti_wdt_get_timeleft()`, and `visconti_wdt_set_timeout()`. Probe maps registers, enables clock, computes divider, and registers.

## Control flow
Probe maps MMIO, gets/enables the clock, derives `div = clk_freq / 2MHz`, initializes timeout bounds from the 32-bit max counter, applies nowayout and stop-on-unregister, initializes optional timeout, and registers. Start writes divider, min zero, max as `timeout * 2MHz`, clears control, and writes the start/stop command. Stop writes control stop state and command. Ping writes clear command. Timeout changes clear the counter before updating max to avoid immediate expiry.

## State and persistence behavior
Software stores divider and timeout; hardware counter/control/max state persists until changed. The clock is devm-enabled for device lifetime.

## Dependencies and integration points
It depends on DT compatible `toshiba,visconti-wdt`, platform MMIO, clock framework, watchdog core, and devm resources.

## Risks and test signals
Risks include divider truncation when clock is not an integer multiple of 2 MHz, timeout multiplication overflow if bounds are wrong, no stop-on-reboot, and author string typo being harmless metadata. Tests should cover zero clock rejection, divider calculation, start/stop/ping command writes, timeout update while active, get-timeleft conversion, and max-timeout boundary.
