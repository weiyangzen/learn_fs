<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/lpc18xx_wdt.c -->
# `sources/distributed-fs/ceph-client/drivers/watchdog/lpc18xx_wdt.c`

Purpose: NXP LPC18xx watchdog driver for hardware that cannot be disabled after start, using an internal kernel timer to keep feeding after user-space stop.

Important APIs, types, and functions: `struct lpc18xx_wdt_dev` stores watchdog core device, register/watchdog clocks, MMIO, timer, and spinlock. `lpc18xx_wdt_feed()` writes the `0xaa`/`0x55` feed sequence under irqsave spinlock to avoid abort conditions. `lpc18xx_wdt_stop()` starts periodic internal feeding. Restart deliberately writes a bad feed sequence after enabling reset.

Control flow: probe maps MMIO, enables `reg` and `wdtclk`, computes timeout bounds from 24-bit counter and divide-by-4 prescaler, initializes timeout and hardware TC, sets up the feed timer, sets nowayout and restart priority, installs stop-on-reboot, and registers. Start cancels internal feeding, enables watchdog/reset bits, and performs a valid feed. Remove warns that hardware will likely reboot and deletes the timer.

State and persistence: hardware disable is impossible, so "stop" means kernel-owned periodic feeding at half the timeout. Timeleft is read from `TV` and converted by clock rate. Timer state distinguishes active userspace management from fallback kernel feeding.

Dependencies and integration points: depends on OF compatible `nxp,lpc1850-wwdt`, two clocks, MMIO, watchdog core, timer API, and restart priority.

Risks and test signals: risks include feed sequence interruption, timer fallback being mistaken for hardware stop, removal causing reset, and clock-derived timeout bounds. Test start-stop-start transitions, timer feed cadence, bad-feed restart, get_timeleft conversion, stop-on-reboot, and behavior when userspace closes the watchdog.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/lpc18xx_wdt.c -->
