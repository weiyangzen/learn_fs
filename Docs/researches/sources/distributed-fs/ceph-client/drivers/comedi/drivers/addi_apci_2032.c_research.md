# sources/distributed-fs/ceph-client/drivers/comedi/drivers/addi_apci_2032.c

## Purpose

This driver supports the ADDI-DATA APCI-2032 32-channel digital output board with an ADDI watchdog and two diagnostic interrupt/status channels for VCC and short-circuit/current-condition errors.

## Important APIs, types, and functions

Key functions are `apci2032_do_insn_bits()`, `apci2032_int_insn_bits()`, `apci2032_int_cmdtest()`, `apci2032_int_cmd()`, `apci2032_int_cancel()`, `apci2032_interrupt()`, `apci2032_reset()`, `apci2032_auto_attach()`, and `apci2032_detach()`. `struct apci2032_int_private` tracks async activity and enabled interrupt sources under a spinlock. Watchdog support uses `addi_watchdog_init()` and `addi_watchdog_reset()`.

## Control Flow

Auto-attach enables PCI, sets BAR 1 as the device I/O base, resets outputs/interrupts/watchdog, requests a shared IRQ if present, and allocates DO, watchdog, and diagnostic DI subdevices. The interrupt subdevice is command-capable only with an IRQ. A command builds an enabled-source mask from the channel list, marks the subdevice active, and writes the mask to the interrupt control register. The ISR verifies the device IRQ status, reads diagnostic status, disables triggered level-sensitive sources to prevent interrupt storms, writes packed scan bits corresponding to channel-list indices, and sets end-of-acquisition when finite scans complete.

## State and Persistence

State includes hardware DO register value, interrupt enable/status registers, watchdog registers, and `apci2032_int_private` fields. Triggered diagnostic interrupt sources are intentionally disabled after firing. Detach resets hardware and frees the manually allocated interrupt private data after generic PCI cleanup.

## Dependencies and Integration Points

The driver depends on COMEDI PCI, Linux IRQ/spinlock APIs, generic DIO helpers, async command helpers, and the ADDI watchdog module. It integrates diagnostic status with COMEDI's packed digital async buffer format.

## Risks

The ISR checks `dev->attached` before using subdevices, which avoids early shared IRQ races. Finite-count completion depends on `scans_done` being advanced by COMEDI event handling after samples are written; changes in event ordering could affect EOA timing. Manual `kfree(dev->read_subdev->private)` must not conflict with automatic subdevice private cleanup; the allocation uses raw `kzalloc_obj`, not `comedi_alloc_spriv`, so the explicit free is required. Level-sensitive diagnostic interrupts are not reenabled automatically after firing.

## Test Signals

Validation includes DO writes/readback, watchdog arm/disarm/ping, diagnostic status reads, async commands for each diagnostic channel and both channels, level-sensitive source disabling after interrupt, finite and continuous stop modes, cancel disabling interrupts, and detach freeing private state without leaks.
