# sources/distributed-fs/ceph-client/drivers/uio/uio_aec.c

## Purpose
`uio_aec.c` is a UIO PCI driver for the Adrienne Electronics Corporation VITC/LTC time-code device. It exposes the device's I/O port BAR to userspace and provides a small interrupt handler that validates and acknowledges device interrupt state enough for UIO event delivery.

## Important APIs, Types, And Functions
The PCI ID table matches vendor `0xaecb`, device `0x6250`. `probe()` allocates `struct uio_info`, enables the PCI device, requests regions, maps BAR0 with `pci_iomap()`, fills `info->port[0]`, installs `aectc_irq()`, registers the UIO device, and enables/masks device interrupts. `remove()` disables interrupts, reads the mailbox to drop IRQ state, unregisters UIO, releases regions, disables PCI, and unmaps.

## Control Flow And State
The IRQ handler reads `INTA_DRVR_ADDR`; if interrupts are enabled and active, it reads `MAILBOX` and returns `IRQ_HANDLED`, allowing the UIO core to notify userspace. Userspace is expected to write to the device port to request subsequent interrupts. Driver state is the `uio_info` stored in PCI drvdata and the BAR mapping in `info->priv`.

## Dependencies And Integration Points
The driver depends on PCI core, I/O port/MMIO accessors, and UIO core registration. It uses a UIO port region rather than `uio_mem`, so userspace needs port I/O tooling rather than normal mmap.

## Risks And Edge Cases
Error paths return `-ENODEV` broadly, losing precise failure causes. Interrupt handling is shared and device-specific; false positives can disturb shared IRQ lines if register semantics are misunderstood. Remove ordering disables interrupts before unregister, which is necessary because userspace controls much of device behavior.

## Test Signals
Test PCI probe/remove, sysfs port attributes, interrupt enable/mask registers, shared IRQ filtering, mailbox read acknowledgement, userspace re-enable behavior, and cleanup after failed BAR mapping or UIO registration.
