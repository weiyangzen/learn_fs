# sources/distributed-fs/ceph-client/drivers/usb/misc/cypress_cy7c63.c

Purpose: Generic sysfs driver for AK Modul-Bus Cypress CY7C63xxx "Port-Chip" devices, exposing two simple I/O ports as `port0` and `port1` attributes.

Important APIs and types: `struct cypress` stores `udev` and cached port values. `vendor_command()` sends vendor control reads, `write_port()` validates decimal byte input and sends `CYPRESS_WRITE_PORT`, while `read_port()` sends `CYPRESS_READ_PORT` and formats the cached byte. The USB driver uses `dev_groups = cypress_groups`.

Control flow: probe allocates state and stores it in interface data. Sysfs reads allocate an 8-byte transfer buffer, issue a vendor IN control request, update `dev->port[]` from `iobuf[1]`, and return the value. Sysfs writes parse 0..255 and send a vendor command with the port ID and byte value.

State and persistence: cached port values are in memory only; actual device state is owned by firmware. Disconnect clears intfdata after sysfs removal and frees state. Risks include no mutex around sysfs access, `read_port()` ignoring negative command results when formatting cached data, legacy `sprintf()`, and ambiguous `USB_RECIP_OTHER` vendor control recipient. Test signals include sysfs read/write return values, invalid input, short control responses, disconnect racing with sysfs access, and validation on both supported port IDs.
