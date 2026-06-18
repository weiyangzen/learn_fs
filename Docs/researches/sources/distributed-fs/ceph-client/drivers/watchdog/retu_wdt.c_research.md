<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/retu_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/retu_wdt.c

Purpose: watchdog-core driver for the Nokia Retu MFD watchdog. The hardware cannot be disabled, so the driver either hands feeding to userspace or self-feeds while stopped.

Important APIs, types, and functions: `struct retu_wdt_dev` stores parent `retu_dev`, device pointer, and delayed ping work. Key functions are `retu_wdt_ping_enable()`, `retu_wdt_ping_disable()`, `retu_wdt_ping_work()`, watchdog start/stop/ping/set-timeout operations, and probe.

Control flow: probe allocates watchdog and private state, sets bounds of 0..63 seconds, binds drvdata, creates auto-cancel delayed work, registers the watchdog, then either pings once for nowayout or schedules periodic self-feeding. Start cancels self-feeding and writes the userspace timeout to the Retu register. Stop re-enables self-feeding. Ping and set-timeout write the timeout directly.

State and persistence behavior: state is the delayed work schedule, selected timeout, nowayout flag, and Retu watchdog register. There is no persistent storage; stopped state is emulated by periodically programming the maximum timer.

Dependencies and integration points: depends on the Retu MFD driver, `retu_write()`, devm delayed-work autocancel, watchdog core, and platform device parent data.

Risks and edge cases: because hardware cannot stop, any failure in delayed work scheduling or Retu writes can reset the system unexpectedly. `min_timeout` is zero, which is unusual and should match hardware semantics. In nowayout mode self-feeding is skipped.

Test signals: start/stop transition between userspace and kernel feeding, delayed work cancellation on removal, Retu write failures, timeout bounds, nowayout behavior, and long idle stopped-state survival.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/retu_wdt.c -->
