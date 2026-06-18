# sources/distributed-fs/ceph-client/drivers/ata/pata_rdc.c

## Purpose
Supports later RDC PATA controllers conforming to ATA host adapter standards, with cable detection, port enable checks, timing programming, and IOCFG restoration.

## Important APIs, Types, And Functions
`struct rdc_host_priv` saves IOCFG. `rdc_pata_cable_detect()` decodes saved cable bits. `rdc_pata_prereset()` checks PCI enable bits. `rdc_set_piomode()` and `rdc_set_dmamode()` program PIO, MWDMA, and UDMA timing under `rdc_lock`. `rdc_init_one()` prepares a two-port BMDMA32 host; `rdc_remove_one()` restores saved IOCFG before generic removal.

## Control Flow
Probe enables the PCI device, saves config dword `0x54`, prepares two libata ports, enables INTx, marks parallel scan, and activates BMDMA interrupts. Mode setup uses a global spinlock because timing and UDMA registers contain fields for multiple ports/devices.

## State And Persistence
Saved IOCFG persists in `host->private_data` for cable detect and detach restore. Hardware state persists in PCI timing/UDMA registers. No per-command state is cached.

## Dependencies And Integration Points
Uses libata BMDMA32 operations, PCI managed setup, DMI headers, PCI config bit helpers, and generic PM hooks.

## Risks And Edge Cases
Multi-field PCI config updates require locking to avoid cross-port corruption. IOCFG must be restored on remove. Cable detection trusts firmware-saved bits. MWDMA uses PIO-derived timing and may force DMA-only behavior when device PIO capability is slower.

## Test Signals
Both RDC PCI IDs, 40/80-wire cable detect, disabled port prereset, PIO/MWDMA/UDMA mode programming, concurrent two-port mode changes, remove restoring IOCFG, and suspend/resume.
