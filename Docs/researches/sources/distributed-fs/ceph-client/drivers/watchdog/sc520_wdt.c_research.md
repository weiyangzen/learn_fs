<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/sc520_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/sc520_wdt.c

Purpose: legacy miscdevice watchdog for AMD Elan SC520 MMCR watchdog. It uses a kernel timer to service a short hardware timeout while userspace supplies a longer heartbeat.

Important APIs, types, and functions: global state includes mapped `wdtmrctl`, kernel timer, next heartbeat, open bit, expected close, timeout, nowayout, and spinlock. Key functions are `wdt_timer_ping()`, `wdt_config()`, `wdt_startup()`, `wdt_turnoff()`, `wdt_keepalive()`, `wdt_set_heartbeat()`, file operations, reboot notifier, init, and unload.

Control flow: init validates timeout, maps MMCR watchdog control register at a fixed physical address, registers reboot notifier, and registers `/dev/watchdog`. Open enforces single user, pins module if nowayout, starts kernel timer and configures hardware for reset with a 2-second-ish hardware expiry. Timer writes the service sequence while userspace heartbeat is fresh. Close stops only on magic close; otherwise it leaves hardware active.

State and persistence behavior: software state is the emulated heartbeat deadline; hardware state is MMCR watchdog control and service/config unlock sequences. Unload disables only when nowayout is false.

Dependencies and integration points: depends on fixed SC520 MMCR mapping, raw MMIO service sequences, miscdevice watchdog ABI, reboot notifier, and Linux timers.

Risks and edge cases: fixed physical address can be wrong on unsupported hardware. Timer deletion on unexpected close stops kernel feeding, deliberately causing reset. Configuration unlock sequence must be exact. No explicit request_mem_region is used.

Test signals: ioremap failure, service/config write sequence, heartbeat expiry, magic close and nowayout, reboot notifier, timeout bounds, and timer cleanup on unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/sc520_wdt.c -->
