# sources/distributed-fs/ceph-client/drivers/spi/spi-loongson-pci.c

## Purpose

`spi-loongson-pci.c` is the PCI glue for Loongson SPI controllers. It enables the PCI device, maps BAR0, and delegates controller registration to the shared Loongson core.

## Important APIs, Types, And Functions

The only substantive function is `loongson_spi_pci_register()`. The driver table matches Loongson PCI IDs `0x7a0b` and `0x7a1b`; the `pci_driver` uses Loongson core PM ops.

## Control Flow, State, And Persistence

Probe uses `pcim_enable_device()`, `pcim_iomap_region()` for BAR0, and `loongson_spi_init_controller()`. Devm/pcim resource management owns cleanup. The file maintains no private runtime state beyond PCI driver binding.

## Dependencies And Integration Points

It depends on PCI core and `spi-loongson.h`, and imports namespace `SPI_LOONGSON_CORE`. Its behavior is entirely coupled to the shared core implementation.

## Risks And Test Signals

Risks are mostly resource binding errors: wrong BAR, missing PCI clock assumptions in core, or ID table gaps. Test by probing both supported PCI IDs, unbind/rebind, suspend/resume through the inherited PM ops, and basic SPI transfer after PCI resource mapping.
