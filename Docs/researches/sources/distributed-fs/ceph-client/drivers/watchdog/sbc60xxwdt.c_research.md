<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/sbc60xxwdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/sbc60xxwdt.c

Purpose: legacy I/O-port watchdog driver for 60xx single-board computers. It emulates a longer userspace heartbeat by pinging short hardware from a kernel timer.

Important APIs, types, and functions: global state includes start/stop port parameters, timer, next heartbeat, open bit, expected close, timeout, and nowayout. Key functions are `wdt_timer_ping()`, `wdt_startup()`, `wdt_turnoff()`, `wdt_keepalive()`, file operations, reboot notifier, init, and unload.

Control flow: init validates timeout, reserves configured I/O ports, registers reboot notifier, and registers `/dev/watchdog`. Open enforces single user, optionally pins the module, starts the kernel timer. The timer reads from the start port every quarter second while userspace heartbeat is fresh. Writes update `next_heartbeat` and scan for `V`. Close disables only with magic close; otherwise it stops the kernel timer and leaves hardware to expire.

State and persistence behavior: software state is timer and heartbeat deadline; hardware state is controlled by reads from start/stop I/O ports. Timeout is an emulated userspace supervision interval, not hardware timeout.

Dependencies and integration points: depends on x86-style port I/O, miscdevice watchdog ABI, kernel timers, reboot notifier, and manually configured module ports.

Risks and edge cases: hardware parameters cannot be probed, so wrong ports can affect unrelated hardware. Unexpected close deletes the ping timer, intentionally allowing reset. Stop port 0x45 may be unreserved because the kernel already owns it.

Test signals: port reservation paths, timer ping cadence, heartbeat expiry, magic close, nowayout module pinning, reboot notifier, and timeout bounds 1..3600.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/sbc60xxwdt.c -->
