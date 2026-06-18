<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/sb_wdog.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/sb_wdog.c

Purpose: legacy miscdevice driver for SiByte SB1 SoC watchdog timer 1, with interrupt warning and reboot notifier support.

Important APIs, types, and functions: global state includes `sbwd_lock`, kernel/user watchdog MMIO pointers, timeout in microseconds, open gate, and expected close. Key functions are `sbwdog_set()`, `sbwdog_pet()`, file operations, reboot notifier, shared IRQ handler, module init, and exit.

Control flow: module init registers reboot notifier, requests IRQ 1 for the user watchdog, and registers `/dev/watchdog`. Open enforces single user, pins module, writes initial count, and starts hardware. Write scans for magic `V`, pets the watchdog, and release disables only after magic close. IRQ handler logs impending reset for user watchdog or reloads the kernel watchdog. Reboot notifier disables both watchdogs on halt/down.

State and persistence behavior: state is global MMIO registers, user timeout, open bit, and expected-close flag. Hardware has two-stage behavior: first expiry interrupts, second resets.

Dependencies and integration points: depends on SiByte architecture I/O base/register definitions, IRQ 1 sharing, miscdevice watchdog ABI, reboot notifier, and raw MMIO accesses.

Risks and edge cases: raw pointer arithmetic assumes fixed SoC register layout. Timeout is limited to 23 bits. `WDIOC_GETTIMEOUT` returns remaining count rather than configured timeout. Module reference is always taken on open and only put on magic close.

Test signals: IRQ warning path, magic close and unexpected close, timeout upper bound, reboot notifier disabling both dogs, shared IRQ behavior, and user versus kernel watchdog register selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/sb_wdog.c -->
