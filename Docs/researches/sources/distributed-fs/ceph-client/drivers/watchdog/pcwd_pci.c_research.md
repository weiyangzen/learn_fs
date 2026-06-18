# sources/distributed-fs/ceph-client/drivers/watchdog/pcwd_pci.c

## Purpose
`pcwd_pci.c` is the Berkshire PCI-PC Watchdog driver. It binds a QuickLogic PCI watchdog card, sends command bytes through I/O ports, manages watchdog and temperature miscdevices, and supports time-left/status/temperature ioctls.

## Important APIs, types, and functions
Global `pcipcwd_private` stores temperature support, boot status, I/O base, lock, and PCI device. Key functions are `send_command`, `pcipcwd_start`, `pcipcwd_stop`, `pcipcwd_keepalive`, `pcipcwd_set_heartbeat`, `pcipcwd_get_status`, `pcipcwd_clear_status`, `pcipcwd_get_temperature`, `pcipcwd_get_timeleft`, file operations, reboot notifier, `pcipcwd_card_init`, and `pcipcwd_card_exit`.

## Control flow
PCI probe enables the device, requests BAR regions, reads and clears boot status, disables the card, detects temperature support, reads firmware and DIP switches, selects heartbeat, registers reboot notifier and miscdevices. Commands write data to ports 4/5, command to port 6, poll `WRSP`, then read response bytes. Open starts and keepalives; writes scan for magic `V` and keepalive; release stops only after magic close. Reboot notifier stops on halt/down. Remove stops unless nowayout and tears down miscdevices, notifier, regions, and PCI device.

## State and persistence
Hardware stores watchdog timeout, status, trip, relay, and temperature state. Boot/trip status is cleared at probe. Software single-open and magic-close state is global.

## Dependencies and integration points
It depends on PCI ID `11e3:5030`, I/O BAR access, reboot notifier, miscdevice `WATCHDOG_MINOR` and `TEMP_MINOR`, watchdog ioctl ABI, and module parameters `debug`, `heartbeat`, and `nowayout`.

## Risks and test signals
Risks include one-card global design, command timeout handling that returns boolean rather than errno, temperature byte-size userspace copies, active watchdog behavior on unplug/remove with nowayout, and lack of watchdog core integration. Test signals include PCI enable/region errors, firmware command timeout, DIP heartbeat, status clear/reset count, magic close, reboot notifier, temperature ioctl/device, and time-left command.
