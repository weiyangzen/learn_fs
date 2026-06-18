# sources/distributed-fs/ceph-client/drivers/watchdog/armada_37xx_wdt.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/watchdog/armada_37xx_wdt.c` is a watchdog-core driver for Marvell Armada 37xx SoC timer counters. It uses counter 1 as the watchdog and counter 0 as a retrigger source to ping counter 1 without disabling it. The complete 359-line source was read for this report.

## Important APIs, Types, and Functions

`struct armada_37xx_watchdog` stores `watchdog_device`, CPU misc syscon regmap, MMIO counter registers, computed timeout ticks, clock rate, and clock handle. Helpers include `get_counter_value()`, `set_counter_value()`, `counter_enable()`, `counter_disable()`, `init_counter()`, and `armada_37xx_wdt_is_running()`. Watchdog operations are `armada_37xx_wdt_ping()`, `armada_37xx_wdt_get_timeleft()`, `armada_37xx_wdt_set_timeout()`, `armada_37xx_wdt_start()`, and `armada_37xx_wdt_stop()`. Probe and PM hooks are `armada_37xx_wdt_probe()`, `armada_37xx_wdt_suspend()`, and `armada_37xx_wdt_resume()`.

## Control Flow

Probe obtains the system controller phandle, maps timer registers, enables the clock, initializes min/max/default timeout, computes the counter value, checks if hardware is already running, applies nowayout and stop-on-reboot, then registers the watchdog. Start selects counter 1 as the watchdog in CPU misc registers, initializes counter 0 as one-shot retrigger, initializes counter 1 in hardware-signal mode triggered by the previous counter, loads timeout, enables counter 1, and fires counter 0. Ping disables/enables counter 0 to force a retrigger. Stop disables both counters and clears watchdog selection.

## State and Persistence Behavior

Timeout state is stored both in `wdd->timeout` and `dev->timeout` in clock ticks. Hardware state lives in the counters and CPU misc watchdog selection register. Running hardware from a bootloader is detected and represented as `WDOG_HW_RUNNING`.

## Dependencies and Integration Points

It depends on OF compatible `marvell,armada-3700-wdt`, a `marvell,system-controller` syscon phandle, clock framework, regmap, MMIO access, and watchdog core.

## Risks and Edge Cases

The design deliberately avoids counters 2 and 3 because firmware may enable them before U-Boot. Suspend unconditionally stops the watchdog and resumes only if watchdog core marks it active, so boot-running-but-not-open scenarios need framework coverage. Timeout calculation uses 64-bit counters and `do_div`; clock rate zero is rejected.

## Test Signals

Test syscon lookup, clock failures, boot-running detection, timeout conversion, counter low/high consistency, ping without disabling counter 1, suspend/resume active-state handling, and DT binding coverage.
