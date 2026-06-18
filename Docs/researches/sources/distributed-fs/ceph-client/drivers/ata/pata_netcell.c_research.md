# sources/distributed-fs/ceph-client/drivers/ata/pata_netcell.c

`pata_netcell.c` is a small PCI BMDMA driver for Netcell Revolution PATA RAID controllers. The firmware handles most timing and RAID behavior, so the driver mainly registers generic libata support and fixes incomplete identify data.

`netcell_read_id()` wraps `ata_do_dev_read_id()`. If identify succeeds, it sets bit `0x4000` in `id[ATA_ID_CSF_DEFAULT]` because the firmware forgets to mark command-set words 85-87 valid. Port operations inherit from `ata_bmdma_port_ops`, force 80-wire cable reporting, and override `.read_id`.

Probe enables the PCI device, clears simplex state with `ata_pci_bmdma_clear_simplex()`, and calls `ata_pci_bmdma_init_one()` with PIO4, MWDMA2, UDMA5, and slave possible. Remove and PM use generic libata PCI helpers.

There is no private state; the only driver-side mutation is the in-memory identify buffer correction. Risks are limited but include masking malformed identify data incorrectly and assuming 80-wire behavior because firmware abstracts the real drives. Tests should cover successful and failed identify reads, command-set validity bits, DMA I/O through firmware volumes, simplex clearing, and suspend/resume.
