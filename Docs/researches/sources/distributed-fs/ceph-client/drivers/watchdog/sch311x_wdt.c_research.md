<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/sch311x_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/sch311x_wdt.c

Purpose: legacy Super I/O watchdog driver for SMSC SCH3112/SCH3114/SCH3116 chips, using platform-device wrapping after manual Super I/O detection.

Important APIs, types, and functions: global `sch311x_wdt_data` stores runtime base, boot status, and I/O lock. Key routines are Super I/O enter/exit/read/write helpers, `sch311x_detect()`, `sch311x_wdt_set_timeout()`, start/stop/keepalive/status helpers, file operations, platform probe/remove/shutdown, module init, and exit.

Control flow: module init scans common Super I/O config ports, validates device ID or `force_id`, selects logical device 0x0a, reads runtime base, registers a platform driver and synthetic platform device. Probe reserves runtime register regions, stops hardware, disables keyboard/mouse interaction in WDT config, validates timeout, captures boot status, and registers `/dev/watchdog`. Open starts hardware by setting timeout and routing GP60 to WDT function. Keepalive rewrites timeout. Close stops only after magic `V`.

State and persistence behavior: state is runtime register base, boot status from WDT control bit, timeout rounded to seconds or minutes, open/expected-close flags, and Super I/O register configuration.

Dependencies and integration points: depends on port I/O, Super I/O configuration protocol, platform driver/device framework, miscdevice watchdog ABI, and shutdown callback.

Risks and edge cases: detection writes to Super I/O config ports and can be affected by `force_id`. Timeouts above 255 seconds round up to minutes. Remove stops only when nowayout is false, but shutdown always stops. No reboot notifier is used outside platform shutdown.

Test signals: detection on all config ports, forced ID, runtime base zero handling, timeout rounding up to minutes, bootstatus status bit, open/magic close, shutdown stop, and region cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/sch311x_wdt.c -->
