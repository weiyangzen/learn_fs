# sources/distributed-fs/ceph-client/drivers/ata/pata_pcmcia.c

## Purpose
Provides a libata driver for PCMCIA ATA/ATAPI cards and adapters, including many legacy product IDs and an 8-bit emulated transfer quirk.

## Important APIs, Types, And Functions
`pcmcia_set_mode()` detects ghost slave devices by comparing IDENTIFY strings. `pcmcia_set_mode_8bit()`, `ata_data_xfer_8bit()`, and `pcmcia_8bit_drain_fifo()` support TI-style 8-bit emulation. `pcmcia_check_one_config()` validates/request IO windows. `pcmcia_init_one()` enables the card, maps IO/control windows, creates one or two ATA ports, and activates the host. `pcmcia_remove_one()` detaches and disables the card.

## Control Flow
PCMCIA probe configures resource flags, applies KME quirks, loops possible CIS configurations, enables the device, maps IO ports, optionally chooses 8-bit ops, allocates an ATA host for one or two ports, fills standard SFF addresses, and activates shared-IRQ PIO operation. Remove detaches the host and disables the PCMCIA device.

## State And Persistence
`pdev->priv` stores the ATA host. PCMCIA resource settings and enabled-device state persist until removal. No separate driver-private allocation is used.

## Dependencies And Integration Points
Uses PCMCIA CIS/config APIs, libata SFF PIO, product/manufacturer ID tables, devm IO port mapping, and standard SCSI host templates.

## Risks And Edge Cases
Ghost master/slave detection may disable a real identical device if serial data is misleading. Some cards need fallback without VCC checking. Two-port support is inferred from IO window size. 8-bit data transfer and FIFO drain paths differ from normal SFF behavior.

## Test Signals
Known PCMCIA IDs, config fallback, KME control quirk, TI 8-bit card path, ghost slave suppression, one-port and two-port windows, card removal while mounted, and shared IRQ behavior.
