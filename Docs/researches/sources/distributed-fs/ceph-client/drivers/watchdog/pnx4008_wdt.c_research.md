# sources/distributed-fs/ceph-client/drivers/watchdog/pnx4008_wdt.c

## Purpose
`pnx4008_wdt.c` drives the NXP PNX4008 watchdog timer and provides a restart handler that can force internal or external resets.

## Important APIs, types, and functions
Global state includes `wdt_base`, `wdt_clk`, `io_lock`, module `heartbeat`, and static `watchdog_device pnx4008_wdd`. Main functions are `pnx4008_wdt_start`, `pnx4008_wdt_stop`, `pnx4008_wdt_set_timeout`, `pnx4008_restart_handler`, and `pnx4008_wdt_probe`.

## Control flow
Probe initializes timeout from module parameter, maps registers, enables the clock, sets bootstatus from reset status, applies nowayout and restart priority, detects already-running hardware, and registers. Start resets the counter, waits for zero, programs match/reset/output/pulse registers, clears interrupt, writes match count from fixed 13 MHz rate, and enables counting with debug stop. Stop clears control. Restart handler interprets optional reboot command first character, then either forces match output/internal reset for soft reset or asserts reset output with a 1 ms pulse for hard reset, then delays for reset.

## State and persistence
Hardware control, match, interrupt, pulse, and reset status registers hold live state. The static watchdog object assumes a single instance. Bootstatus is read from reset status at probe.

## Dependencies and integration points
It depends on OF compatible `nxp,pnx4008-wdt`, clock framework, platform MMIO, watchdog core restart handler, reboot command conventions, and module parameters `heartbeat`/`nowayout`.

## Risks and test signals
Risks include global singleton state, no ping operation despite `WDIOF_KEEPALIVEPING`, fixed counter-rate assumption independent of actual clock, busy wait on counter reset, and restart handler returning after delay if reset fails. Test signals include bootstatus, already-running detection, start register sequence, restart hard/soft command modes, timeout min/max, and clock/map failures.
