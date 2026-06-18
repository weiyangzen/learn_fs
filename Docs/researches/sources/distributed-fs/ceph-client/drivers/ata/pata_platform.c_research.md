# sources/distributed-fs/ceph-client/drivers/ata/pata_platform.c

## Purpose
Implements the generic platform-device PATA helper and driver for simple PIO ATA interfaces described by platform resources.

## Important APIs, Types, And Functions
`pata_platform_set_mode()` forces enabled devices to PIO0 without hardware reprogramming. `pata_platform_setup_port()` expands taskfile addresses from a command base plus shift. `__pata_platform_probe()` is exported for platform and OF wrappers; it maps IO or MMIO resources, creates per-device port ops, configures PIO polling when no IRQ exists, and activates the host. `pata_platform_probe()` validates resources and calls the helper.

## Control Flow
Probe requires command and control resources plus optional IRQ, determines IO versus MMIO, allocates one ATA host, creates a devm `ata_port_operations` inheriting SFF ops, selects 16- or 32-bit data transfer behavior, maps resources, computes register addresses, and activates with either `ata_sff_interrupt` or polling.

## State And Persistence
Device-managed mappings and per-device operations persist for the platform device lifetime. The module parameter `pio_mask` controls supported PIO modes for non-OF platform devices.

## Dependencies And Integration Points
Exports `__pata_platform_probe()` for `pata_of_platform.c`, uses platform resources, libata SFF, `ata_platform_remove_one`, and `pata_platform_info` platform data.

## Risks And Edge Cases
The helper assumes both command and control resources are both IO or both MEM. It never programs hardware timing, so firmware/platform setup must be correct. No IRQ means polling. `use16bit=false` selects 32-bit data transfer, which must match wiring.

## Test Signals
IO and MMIO resources, two-resource and three-resource devices, no-IRQ polling, IRQ trigger flags, shifted registers, platform `pio_mask`, 16-bit wrapper use, and mapping failure unwinds.
