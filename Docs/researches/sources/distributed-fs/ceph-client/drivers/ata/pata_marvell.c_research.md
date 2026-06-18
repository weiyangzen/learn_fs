# sources/distributed-fs/ceph-client/drivers/ata/pata_marvell.c

`pata_marvell.c` is a simple legacy-mode libata driver for Marvell ATA controllers with PATA functionality. It uses generic PCI BMDMA support and adds only active-port detection, cable detection, and AHCI deferral logic.

`marvell_pata_active()` checks whether the PATA port is active. For device `0x6145`, it maps BAR5, reads register `0x0c`, and checks bit `0x10`; for other devices it assumes active. `marvell_pre_reset()` skips inactive 6145 PATA port 0. `marvell_cable_detect()` reports PATA40/PATA80 from BMDMA byte bit 0 for port 0, unknown if BMDMA is unavailable, and SATA for port 1.

`marvell_init_one()` defines PATA and legacy-SATA port-info records, uses a dummy second port for `0x6101`, and when AHCI is enabled returns `-ENODEV` if the PATA port is inactive so AHCI can own the hardware. Otherwise it calls `ata_pci_bmdma_init_one()`.

The driver has no private state. Dependencies are PCI BAR mapping, libata BMDMA/SFF, and optional AHCI cooperation. Risks include treating unknown devices as active, BAR5 mapping errors, and cable bit interpretation. Tests should cover 6145 active/inactive states, AHCI deferral, 6101 dummy port, PATA and SATA cable reporting, missing BMDMA fallback, and generic PCI PM.
