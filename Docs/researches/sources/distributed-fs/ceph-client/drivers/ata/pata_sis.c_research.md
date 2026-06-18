# sources/distributed-fs/ceph-client/drivers/ata/pata_sis.c

## Purpose
`pata_sis.c` supports a broad set of SiS PATA controllers, from pre-UDMA chips through ATA133 variants and concealed SiS5518/965/966-style IDs. It selects generation-specific timing ops, cable detection, mode masks, and register mapping at probe time.

## Important APIs, Types, and Functions
Core helpers include `sis_old_port_base()`, `sis_port_base()`, `sis_133_cable_detect()`, `sis_66_cable_detect()`, `sis_pre_reset()`, `sis_set_fifo()`, generation-specific `sis_*_set_piomode()` and `sis_*_set_dmamode()` callbacks, `sis_133_mode_filter()`, `sis_fixup()`, `sis_init_one()`, and `sis_reinit_one()`. `struct sis_chipset` maps host bridge IDs to `ata_port_info`; `struct sis_laptop` lists machines with short ATA40 cable quirks. `sis_info133_for_sata` is exported for the SiS180 SATA driver.

## Control Flow, State, and Persistence
Probe enables PCI, discovers the backing SiS bridge by scanning known IDs or temporarily unmasking concealed IDs, selects a chipset profile, applies generation fixups, and hands the device to `ata_pci_bmdma_init_one()` with the chipset pointer as host private data. Reset validates per-port enable bits in config register `0x4a` and clears FIFO settings before standard SFF probing. PIO and DMA callbacks write different config-space layouts depending on generation: old two-byte timing registers, ATA100 byte layouts, early ATA133 UDMA bytes, or later ATA133 dword timing registers at `0x40` or `0x70` selected by register `0x54`.

## Dependencies and Integration Points
The file depends on PCI bridge discovery, libata BMDMA/SFF reset helpers, exported SiS SATA integration, cable and laptop DMI/subsystem quirks, and mode filtering derived from controller register state. It also uses `host->private_data` on resume to replay fixups.

## Risks and Test Signals
Risks include concealed-ID probing side effects, a likely-sensitive register write in `sis_133_set_piomode()` where a dword timing value is written through a byte accessor, incomplete MWDMA support for some ATA100/early ATA133 paths, laptop cable quirks masking real 80-wire capability, and incorrect mapping between bridge ID and timing layout. Tests should cover every chipset family table bucket, concealed 5518/0180/1180 IDs, register remap at `0x70`, UDMA6 filtering when ATA133 is disabled, port-enable probing, FIFO behavior for ATA versus ATAPI, resume fixups, and libata mode negotiation under 40-wire and 80-wire cable reports.
