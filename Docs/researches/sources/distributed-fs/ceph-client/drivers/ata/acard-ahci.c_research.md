# sources/distributed-fs/ceph-client/drivers/ata/acard-ahci.c

## Purpose
`acard-ahci.c` is a libata low-level PCI driver for the ACard/ARTOP ATP8620 AHCI SATA variant. It reuses the common AHCI implementation but overrides command preparation, result taskfile extraction, and port start behavior for ACard-specific FIS and scatter-gather quirks.

## Important APIs, Types, And Functions
Important definitions include `DRV_NAME`, `DRV_VERSION`, `ACARD_AHCI_RX_FIS_SZ`, `AHCI_PCI_BAR`, `board_acard_ahci`, and `struct acard_sg`. Driver objects include `acard_ahci_sht`, `acard_ops`, `acard_ahci_port_info`, `acard_ahci_pci_tbl`, and `acard_ahci_pci_driver`. Key functions are `acard_ahci_qc_prep`, `acard_ahci_qc_fill_rtf`, `acard_ahci_port_start`, `acard_ahci_init_one`, suspend/resume handlers under `CONFIG_PM_SLEEP`, `acard_ahci_pci_print_info`, and `acard_ahci_fill_sg`.

## Control Flow
PCI probe enables the device, requests regions, allocates AHCI private data, optionally enables MSI, maps BAR 5, saves initial AHCI config, sets NCQ/PMP flags based on capabilities, allocates an ATA host, marks disabled ports dummy, configures DMA mask, resets and initializes the controller, prints controller info, sets bus master, and activates the host. Command prep builds the command table FIS, copies ATAPI CDBs, fills the ACard SG table for DMA, sets AHCI command slot flags, and returns `AC_ERR_OK`. Result taskfile handling uses PIO Setup FIS for successful PIO data-in commands and D2H Reg FIS otherwise. Port start allocates coherent DMA memory with an ACard 128-byte received-FIS stride and resumes the port.

## State And Persistence
Persistent driver state is stored in `ahci_host_priv` for the host and `ahci_port_priv` for each port. Coherent DMA memory stores command slots, received FIS area, and command tables. PCI driver registration persists for module lifetime. The SG table is per command.

## Dependencies
The driver depends on PCI, DMA mapping, libata, SCSI host templates, AHCI shared helpers from `ahci.h`/`libahci.o`, optional power management, and the `CONFIG_SATA_ACARD_AHCI` Kconfig/Makefile entries.

## Integration Points
It inherits most operations from `ahci_ops` and overrides only the ACard-specific pieces. It binds to `PCI_VDEVICE(ARTOP, 0x000d)`, exports module PCI IDs, and participates in libata scanning, error handling, power management, and SCSI presentation.

## Risks
ACard SG entries require an end-of-table bit and maximum 64 KiB segment size; if the DMA mapping layer supplies larger segments without splitting, hardware may misinterpret descriptors. The driver disables NCQ through `AHCI_HFLAG_NO_NCQ`, so enabling NCQ accidentally could expose unsupported behavior. FIS stride differs from standard AHCI, especially with FBS. Suspend/resume must disable interrupts before D3 and reinitialize controller state correctly.

## Test Signals
Build with `CONFIG_SATA_ACARD_AHCI`, confirm module PCI alias for ARTOP 0x000d, probe on ATP8620 hardware, run SATA disk discovery and I/O stress, test ATAPI and PIO data-in result taskfile paths, verify DMA across multi-segment SG lists, suspend/resume cycles, PMP/FBS behavior where supported, and libata error handling after reset.
