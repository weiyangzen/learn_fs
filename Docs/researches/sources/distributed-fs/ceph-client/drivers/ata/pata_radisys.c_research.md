# sources/distributed-fs/ceph-client/drivers/ata/pata_radisys.c

## Purpose
Supports Radisys R82600 PATA controllers, a PIIX-like single-channel controller with shared PIO/MWDMA timing and limited UDMA switching.

## Important APIs, Types, And Functions
`radisys_set_piomode()` programs PCI config word `0x40` for PIO timing. `radisys_set_dmamode()` handles MWDMA-derived PIO timing and UDMA enable/mode bits. `radisys_qc_issue()` reloads shared timing when issuing to a different device. `radisys_init_one()` registers the BMDMA host.

## Control Flow
Probe creates a single-port BMDMA host. Mode setup writes timing registers and stores the currently programmed device in `ap->private_data`. Command issue reloads timing for PIO/MWDMA or non-DMA cases when switching devices, then delegates to `ata_bmdma_qc_issue()`.

## State And Persistence
State is PCI config timing/UDMA bits plus `ap->private_data` as the current timing owner. No heap private data is used.

## Dependencies And Integration Points
Uses libata BMDMA ops, PCI config access, Radisys PCI IDs, and standard PCI PM helpers.

## Risks And Edge Cases
Shared non-UDMA timing creates the same mixed-device risk as early PIIX. The code treats UDMA timing as not shared, so command issue skips reload for UDMA-capable paths. Cable type is unknown.

## Test Signals
PIO and MWDMA timing, UDMA2/4 selection, alternating master/slave command issue, ATA-only and ATAPI devices, suspend/resume, and R82600 PCI matching.
