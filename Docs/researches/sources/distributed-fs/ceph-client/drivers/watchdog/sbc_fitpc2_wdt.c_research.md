<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/sbc_fitpc2_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/sbc_fitpc2_wdt.c

Purpose: legacy miscdevice watchdog for Compulab SBC-FITPC2 boards, detected by DMI board name and controlled through command/data I/O ports.

Important APIs, types, and functions: global state includes nowayout, margin, status bits, and `wdt_lock`. Key routines are `wdt_send_data()`, `wdt_enable()`, `wdt_disable()`, file operations, ioctl handler, init, and exit.

Control flow: init checks DMI board name for `SBC-FITPC2`, reserves command and data ports, validates margin 31..255 seconds, and registers `/dev/watchdog`. Open enforces single user and enables. Enable sends interface-on and reboot-timeout commands with sleeps. Write scans for `V` only when nowayout is false, then enables again as keepalive. Close disables only when OK-to-close was set; otherwise it re-enables and logs.

State and persistence behavior: state is status bits, configured margin, and hardware controller state through command/data ports. No bootstatus is tracked.

Dependencies and integration points: depends on DMI, port I/O, mutex serialization, miscdevice watchdog ABI, and board firmware command timing.

Risks and edge cases: when nowayout is true, write returns zero after still refreshing hardware, which may surprise userspace expecting byte count. Command protocol uses fixed sleeps and can be slow. No reboot notifier disables the watchdog on shutdown.

Test signals: DMI match/non-match, margin bounds, command ordering with delays, magic close, nowayout write return, concurrent ioctl/write locking, and port conflict cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/sbc_fitpc2_wdt.c -->
