<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/sc1200wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/sc1200wdt.c

Purpose: legacy miscdevice watchdog for National Semiconductor PC87307/PC97307 Super I/O watchdogs, with optional ISA PnP discovery.

Important APIs, types, and functions: global state includes timeout in minutes, I/O base/length, open flag, expected close, spinlock, optional PnP device, and nowayout. Key functions are indexed register read/write helpers, `sc1200wdt_start()`, `sc1200wdt_stop()`, `sc1200wdt_status()`, file operations, reboot notifier, ISA/PnP probe/remove, module init, and exit.

Control flow: init optionally registers a PnP driver to discover the I/O base; otherwise it requires `io=`. It reserves ports, probes by checking PMC3 default bits, registers reboot notifier, and registers `/dev/watchdog`. Open enforces single user, clamps timeout, starts hardware by configuring WDCF and WDTO. Write scans magic close and reloads WDTO. Ioctl supports status, enable/disable, keepalive, and timeout seconds converted to minutes.

State and persistence behavior: state is Super I/O PM index/data registers, timeout minutes, bootstatus fixed zero, and open/expected-close bits. Hardware status reads WDO inactive-high state.

Dependencies and integration points: depends on port I/O, optional PNP, miscdevice watchdog ABI, reboot notifier, and Super I/O register semantics.

Risks and edge cases: timeout seconds are divided by 60, so values below 60 become zero and can disable hardware. PnP and manual I/O paths share globals. Probe heuristic can fail if firmware disabled related devices.

Test signals: PnP discovery and manual `io=`, PMC3 probe success/failure, timeout conversion edge cases, magic close, status reporting, reboot notifier stop, and port cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/sc1200wdt.c -->
