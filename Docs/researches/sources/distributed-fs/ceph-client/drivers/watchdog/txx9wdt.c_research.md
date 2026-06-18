# sources/distributed-fs/ceph-client/drivers/watchdog/txx9wdt.c

## Purpose
`txx9wdt.c` drives TXx9 SoC timer hardware in watchdog mode. It programs timer compare, divider, mode, and watchdog-control registers using the IM bus clock.

## Important APIs, types, and functions
Global state includes mapped `txx9wdt_reg`, clock `txx9_imclk`, and spinlock `txx9_lock`. Watchdog ops are `txx9wdt_ping()`, `txx9wdt_start()`, `txx9wdt_stop()`, and `txx9wdt_set_timeout()`. Probe/remove/shutdown manage the clock, MMIO mapping, timeout bounds, and registration.

## Control flow
Probe gets and enables `imbus_clk`, maps timer registers, validates timeout against `WD_MAX_TIMEOUT`, initializes the static watchdog, applies nowayout, and registers. Start writes compare as `WD_TIMER_CLK * timeout`, sets clock divider and watchdog timer mode, clears pending interrupt, enables counting, and pings. Ping writes watchdog interrupt enable/clear. Stop writes watchdog disable and clears timer enable. Timeout changes stop and restart.

## State and persistence behavior
The driver uses singleton globals and a static watchdog. Hardware timer state persists in TXx9 timer registers until stop/reset. Clock state is enabled for the lifetime of the registered driver.

## Dependencies and integration points
It depends on `<asm/txx9tmr.h>` register layout/macros, platform MMIO, clock framework, raw MMIO access, and watchdog core.

## Risks and test signals
Risks include division by zero if clock rate is bad, singleton assumptions, timeout max computed from runtime clock, and raw register access ordering. Tests should cover clock failures, timeout clamp to default, start/stop/ping register writes, set-timeout restart, remove clock cleanup, shutdown stop, and max-timeout math for board clocks.
