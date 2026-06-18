# sources/distributed-fs/ceph-client/drivers/ata/pata_sch.c

## Purpose
`pata_sch.c` supports Intel SCH PATA controllers such as AF82US15W/L and AF82UL11L. It is a compact BMDMA libata PCI driver that programs per-device timing registers documented by the SCH datasheet.

## Important APIs, Types, and Functions
The important callbacks are `sch_set_piomode()`, `sch_set_dmamode()`, and `sch_init_one()`. Register definitions include `D0TIM`, `D1TIM`, masks for PIO/MWDMA/UDMA fields, `PPE` prefetch/post enable, and `USD` synchronous DMA. Static objects include `sch_pata_ops`, `sch_port_info`, `sch_sht`, `sch_pci_tbl`, and `sch_pci_driver`.

## Control Flow, State, and Persistence
Probe prints the driver version and calls `ata_pci_bmdma_init_one()` with one port-info block allowing PIO4, MWDMA2, UDMA5, and slave devices. PIO setup selects `D0TIM` or `D1TIM`, clears PIO and prefetch bits, writes the requested PIO mode, and enables `PPE` only for ATA disk devices. DMA setup reads the same register, sets `USD` and the UDMA field for UDMA, or clears `USD` and writes the MWDMA field for multiword DMA.

## Dependencies and Integration Points
This file depends on PCI config access, standard libata BMDMA port operations, SCSI host setup through `ATA_BMDMA_SHT`, and libata mode negotiation. Cable detection is reported as unknown, leaving libata policy to constrain final modes where needed.

## Risks and Test Signals
Risks include incorrect register bit masking between PIO, MWDMA, UDMA, and prefetch fields; enabling prefetch for ATAPI devices; and mode negotiation beyond a real board's cabling. Tests should cover disk and ATAPI devices, PIO and DMA transitions on both master/slave slots, UDMA5 limiting, suspend/resume through generic PCI ATA hooks, and config-space register inspection after each negotiated mode.
