# sources/distributed-fs/ceph-client/drivers/watchdog/wdt_pci.c

## Purpose
`wdt_pci.c` is the PCI variant driver for ICS PCI-WDT500/501 cards. It uses the shared WDT register definitions but obtains I/O resources and IRQs through PCI probing.

## Important APIs, types, and functions
Global state includes `dev_count`, `open_lock`, `wdtpci_lock`, `expect_close`, `io`, `irq`, `heartbeat`, `wd_heartbeat`, `type`, and `tachometer`. Important functions mirror the ISA driver: `wdtpci_ctr_mode`, `wdtpci_ctr_load`, `wdtpci_start`, `wdtpci_stop`, `wdtpci_ping`, `wdtpci_set_heartbeat`, `wdtpci_get_status`, `wdtpci_get_temperature`, `wdtpci_interrupt`, file operations, reboot notifier, `wdtpci_init_one`, and `wdtpci_remove_one`.

## Control flow
PCI probe enforces one supported device, validates type, enables the PCI device, requests BAR 2, records I/O base and IRQ, registers a shared IRQ, validates heartbeat, registers reboot notifier, optional temperature miscdevice, and watchdog miscdevice. Start disables and pets the card, programs clock and counters, disables buzzer/opto outputs, then enables the watchdog. Writes and keepalive reload counter 1. Interrupts report board faults.

## State and persistence
The driver supports only one global device because `/dev/watchdog` is singular. Hardware counter/output state persists while powered. Nowayout pins the module but the legacy state model remains outside watchdog core.

## Dependencies and integration points
It depends on PCI IDs for AccessIO WDG-CSM, BAR 2 I/O port access, shared IRQs, miscdevice, reboot notifier, and `wd501p.h`. User integration is the standard legacy watchdog ioctl interface plus optional `/dev/temperature`.

## Risks and test signals
Risks include global state with PCI hotplug, `dev_count` leaks on early probe failures, BAR/IRQ mismatch, timing-sensitive `udelay(8)` programming, only-one-device limitation, and unexpected close keeping hardware running. Test signals include PCI probe/remove cycles, heartbeat bounds, WDT500/501 status and tachometer options, temperature read, shared IRQ behavior, reboot notifier stop, and failure-path cleanup.
