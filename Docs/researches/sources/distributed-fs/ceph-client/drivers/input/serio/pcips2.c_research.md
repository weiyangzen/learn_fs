<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/pcips2.c -->
# sources/distributed-fs/ceph-client/drivers/input/serio/pcips2.c

## Purpose
`pcips2.c` is a PCI PS/2 keyboard/mouse serio driver, originally for Mobility Electronics docking hardware. It maps a PCI I/O BAR with simple control/status/data registers and exposes a single PS/2 serio port per PCI function.

## Important APIs, types, and functions
- `struct pcips2_data` stores the serio port, I/O base, and PCI device.
- `pcips2_write()` busy-waits until `PS2_STAT_TXEMPTY` and writes a byte to the data register.
- `pcips2_interrupt()` drains all available RX bytes, handles all-ones disconnect/status sentinel, computes parity flags, and calls `serio_interrupt()`.
- `pcips2_flush_input()` drains pending input before enabling IRQs.
- `pcips2_open()` enables the controller, flushes input, requests the shared PCI IRQ, and enables RX interrupts.
- `pcips2_close()` disables the controller and frees the IRQ.
- PCI probe enables the device, requests regions, allocates driver/serio state, fills serio fields, records BAR 0 base, and registers the port.

## Control flow
The PCI driver matches Mobility device IDs `0x0123` keyboard and `0x0124` mouse with input class constraints. Probe performs PCI enable and region claim, creates the serio port, stores driver data, and registers the port. Open enables hardware and IRQ delivery. Interrupt drains bytes until RX empty. Remove unregisters the serio port, frees state, releases PCI regions, and disables the device.

## State and persistence
State is per PCI function and stored in `pcips2_data`. Hardware control bits are enabled on open and cleared on close. No persistent settings are saved.

## Dependencies and integration points
It depends on the PCI subsystem, legacy I/O port access through `inb()`/`outb()`, shared IRQs, hweight parity computation, and serio core.

## Risks
- `pcips2_write()` has no timeout while waiting for TX empty, so wedged hardware can spin indefinitely.
- Open writes control state before IRQ request; failure leaves the controller disabled through the final control write.
- Parity interpretation depends on both hardware parity status and computed byte parity.
- The driver assumes BAR 0 is an I/O port resource with the expected register layout.

## Test signals
- Build with PCI and serio support.
- Hardware or emulation tests should cover both PCI IDs/classes, PCI enable/request failure, open IRQ failure, RX drain, parity flag reporting, all-ones sentinel handling, write under TX-busy conditions, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/serio/pcips2.c -->
