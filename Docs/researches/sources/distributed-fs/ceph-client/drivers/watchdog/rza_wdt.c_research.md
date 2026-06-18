<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/rza_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/rza_wdt.c

Purpose: watchdog-core driver for Renesas RZ/A watchdog variants with 3-bit and 4-bit clock selectors and restart support.

Important APIs, types, and functions: `struct rza_wdt` owns watchdog, MMIO base, clock, reload count, and clock selector. Main routines are `rza_wdt_calc_timeout()`, `rza_wdt_start()`, `rza_wdt_stop()`, `rza_wdt_ping()`, `rza_set_timeout()`, `rza_wdt_restart()`, and probe.

Control flow: probe maps registers, gets clock, validates minimum rate, chooses variant data from OF, computes max timeout or max hardware heartbeat, initializes timeout, and registers. Start stops the timer, clears overflow after required dummy read, calculates reload, enables reset, writes counter and control. Ping reloads the saved count. Set-timeout restarts with the new timeout. Restart programs fastest clock and one tick before overflow, then waits.

State and persistence behavior: state is selected `cks`, computed `count`, watchdog timeout, and hardware counter/control/reset registers. No PM or bootstatus state is tracked.

Dependencies and integration points: depends on OF match data, clocks, watchdog core, magic-keyed 16-bit MMIO writes, and restart callback.

Risks and edge cases: 3-bit variants cannot represent even one-second hardware timeouts, so watchdog core must use `max_hw_heartbeat_ms`. Timeout changes restart the timer, which can perturb active timing. Clock rate assumptions drive both max timeout and reload count.

Test signals: both compatibles, clock-rate validation, max timeout/heartbeat calculations, ping reload value, timeout restart while active, and restart reset latency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/rza_wdt.c -->
