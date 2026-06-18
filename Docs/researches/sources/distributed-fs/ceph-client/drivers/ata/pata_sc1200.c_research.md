# sources/distributed-fs/ceph-client/drivers/ata/pata_sc1200.c

## Purpose
`pata_sc1200.c` is a libata PCI driver for the National Semiconductor/AMD SC1200 IDE controller. It provides PIO, MWDMA, and UDMA timing programming, works around the controller's shared MWDMA/UDMA selection bit, and serializes command issue across the two channels.

## Important APIs, Types, and Functions
Key callbacks are `sc1200_set_piomode()`, `sc1200_set_dmamode()`, `sc1200_qc_issue()`, `sc1200_qc_defer()`, and `sc1200_init_one()`. `sc1200_clock()` reads chipset I/O ports `0x903c`, `0x903d`, and `0x901e` to select 33/48/66 MHz timing tables. The driver registers `sc1200_port_ops`, `sc1200_sht`, and a PCI table matching `PCI_DEVICE_ID_NS_SCx200_IDE`.

## Control Flow, State, and Persistence
Probe builds a single `ata_port_info` with PIO4, MWDMA2, UDMA2, slave support, and BMDMA ops, then calls `ata_pci_bmdma_init_one()`. Mode-setting callbacks write PCI config timing dwords under the per-channel base `0x40 + 0x10 * port_no`. Command issue consults `ap->private_data` as the previous device and reloads DMA timings when switching between a UDMA and non-UDMA peer. `qc_defer` first applies standard libata deferral, then delays if the opposite channel has active commands.

## Dependencies and Integration Points
The driver depends on PCI config access, legacy x86-style I/O port reads, libata BMDMA helpers, SCSI host registration through `ATA_BASE_SHT`, and dumb PRD preparation via `ata_bmdma_dumb_qc_prep`. It integrates with libata cable/mode negotiation through fixed 40-wire cable reporting and timing callbacks.

## Risks and Test Signals
Risks include wrong clock detection from magic chipset ports, stale `ap->private_data` causing timing reload omissions, unsafe mixed MWDMA/UDMA operation, and throughput loss from host-wide serialization. Useful tests are boot/probe on SC1200 revisions, PIO0-4 and MWDMA/UDMA mode changes on master/slave pairs, alternating UDMA and MWDMA commands, simultaneous activity on both channels, suspend/resume with timing restoration, and dmesg/libata trace checks for deferred commands and DMA errors.
