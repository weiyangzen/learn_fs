<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/sbc7240_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/sbc7240_wdt.c

Purpose: legacy I/O-port watchdog driver for IEI NANO7240 SBC watchdog hardware.

Important APIs, types, and functions: global `wdt_status` bitfield tracks open, enabled, and expected-close states. Key routines are `wdt_enable()`, `wdt_disable()`, `wdt_set_timeout()`, `wdt_keepalive()`, file operations, reboot notifier, init, and unload.

Control flow: module init reserves enable port 0x443, validates and writes timeout, disables hardware, registers reboot notifier, then registers `/dev/watchdog`. Open enforces single user and enables hardware. Write scans for `V` when nowayout is false and keeps alive by reading enable port. Close disables when expected close is set or nowayout is false; otherwise it keeps hardware alive and logs. Ioctl supports enable/disable, keepalive, and timeout.

State and persistence behavior: state is timeout in seconds, status bits, and hardware state toggled by I/O port reads/writes. The disable port 0x043 is not reserved because it overlaps system timer resources.

Dependencies and integration points: depends on I/O port access, miscdevice watchdog ABI, reboot notifier, module parameters, and SBC-specific port semantics.

Risks and edge cases: the `nowayout` description says "Disable watchdog when closing" but the logic treats nowayout as cannot-stop. Hardware disable uses an unreserved port. Close logic disables on any close when nowayout is false, even without magic close.

Test signals: timeout range 1..255, enable/disable port I/O, nowayout false and true close behavior, magic close, reboot notifier, and port conflict handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/sbc7240_wdt.c -->
