# sources/distributed-fs/ceph-client/drivers/ata/pata_jmicron.c

`pata_jmicron.c` handles JMicron IDE-class controllers in non-AHCI mode. The SATA ports are normally handled by AHCI, while this driver maps and probes PATA ports that firmware may expose as primary or secondary IDE channels.

The main logic is `jmicron_pre_reset()`. It reads config dword `0x40` to test logical port enablement, determine whether a logical channel maps to SATA or PATA0, and apply firmware channel swapping. It reads config dword `0x80` for JMB365/JMB366 PATA1 mapping. After resolving the physical port, it validates the relevant enable bit and sets `ap->cbl` to PATA40, PATA80, or SATA. No custom PIO/DMA timing callbacks are needed.

`jmicron_init_one()` creates a BMDMA port-info record with PIO4, MWDMA2, UDMA5, and `ATA_FLAG_SLAVE_POSS`, then delegates to `ata_pci_bmdma_init_one()`. The PCI ID table matches JMicron IDE-class storage functions broadly.

The driver has no private state; all decisions come from PCI config at reset time. Dependencies are PCI class matching and libata BMDMA/SFF helpers. Risks are bit interpretation and logical/physical port mapping, which can hide real PATA ports or misreport cable type. Tests should cover JMB361/363 layouts, JMB365/366 PATA1 mapping, logical channel swap, disabled ports, SATA cable reporting, and generic PCI suspend/resume.
