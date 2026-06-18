# sources/distributed-fs/ceph-client/drivers/watchdog/wdt.c

## Purpose
`wdt.c` is the legacy ISA driver for Industrial Computer Source WDT500/501 watchdog cards. It controls counter chips and status registers through fixed I/O ports and exposes `/dev/watchdog` plus an optional temperature device for WDT501.

## Important APIs, types, and functions
Key globals are `io`, `irq`, `heartbeat`, `wd_heartbeat`, `type`, `tachometer`, `wdt_is_open`, `expect_close`, and `wdt_lock`. Important functions are `wdt_ctr_mode`, `wdt_ctr_load`, `wdt_start`, `wdt_stop`, `wdt_ping`, `wdt_set_heartbeat`, `wdt_get_status`, `wdt_get_temperature`, `wdt_interrupt`, file operations, `wdt_notify_sys`, `wdt_init`, and `wdt_exit`.

## Control flow
Init validates card type and heartbeat, requests the I/O region and IRQ, registers a reboot notifier, optionally registers `/dev/temperature`, then registers `/dev/watchdog`. Opening single-opens and programs counters: CTR0 as 100 Hz source, CTR1 as watchdog heartbeat, CTR2 as reset pulse. Writes scan for magic close and reload CTR1. Ioctls expose status, keepalive, and timeout. Interrupts read status and log external, thermal, fan, and power faults. Shutdown notifiers disable the card.

## State and persistence
State is global because only one ISA card is supported. Hardware counter and status state persists while the board is powered. The driver does not pin its module for nowayout and uses legacy open bits rather than watchdog core state.

## Dependencies and integration points
It depends on raw I/O port access, IRQs, miscdevice, reboot notifiers, and the shared `wd501p.h` register map. User integration is the legacy watchdog ioctl ABI.

## Risks and test signals
Risks include unprobeable hardware requiring correct module parameters, I/O/IRQ conflicts, inverted fault bits, interrupt handling under spinlock while printing, magic close not clearing open state on unexpected close, and no modern watchdog-core policies. Test signals include WDT500 and WDT501 hardware, heartbeat bounds, fault input interrupts, tachometer option, temperature read, shutdown/reboot notifier, and unexpected close behavior.
