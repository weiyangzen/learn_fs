# sources/distributed-fs/ceph-client/drivers/ata/pata_piccolo.c

## Purpose
Adds Toshiba Piccolo ATA controller support as a small PCI BMDMA libata driver with Toshiba-specific timing tables.

## Important APIs, Types, And Functions
`tosh_set_piomode()` programs PIO timing in PCI config word `0x50`. `tosh_set_dmamode()` programs MWDMA/UDMA timing in config dword `0x5C`. `ata_tosh_init_one()` registers a one-port host, using a dummy second port entry.

## Control Flow
The PCI driver matches Toshiba Piccolo device IDs, constructs a single active ATA port profile with PIO5/MWDMA2/UDMA2 masks, and lets generic PCI BMDMA setup handle resource mapping and activation. Mode changes write the appropriate timing table values.

## State And Persistence
Only PCI config timing state is persisted by the driver. There is no private data allocation.

## Dependencies And Integration Points
Uses libata BMDMA port operations, Toshiba PCI IDs, and generic PCI suspend/resume helpers.

## Risks And Edge Cases
The driver intentionally claims only one port. Timing data comes from external documentation and masks off preserved bits, so register layout mistakes would corrupt unrelated config bits. Cable type is unknown.

## Test Signals
Each Piccolo PCI ID, single-port enumeration, PIO0-5 timing writes, MWDMA and UDMA timing writes, suspend/resume, and dummy second-port non-enumeration.
