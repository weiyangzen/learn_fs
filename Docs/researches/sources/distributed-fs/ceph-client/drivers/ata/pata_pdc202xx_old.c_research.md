# sources/distributed-fs/ceph-client/drivers/ata/pata_pdc202xx_old.c

## Purpose
Supports older Promise PDC20246 and PDC20262/263/265/267 controllers with PCI-config timing, BMDMA quirks, cable detection, and clock switching for high UDMA modes.

## Important APIs, Types, And Functions
`pdc2026x_cable_detect()` reads cable state from PCI config. `pdc202xx_exec_command()` adds a 400 ns command delay. `pdc202xx_irq_check()` reads Promise interrupt bits. `pdc202xx_set_piomode()` and `pdc202xx_set_dmamode()` program timing. `pdc2026x_bmdma_start()` and `pdc2026x_bmdma_stop()` handle clock switching and ATAPI/LBA48 length registers. `pdc2026x_dev_config()` limits sectors, and `pdc2026x_port_start()` enables burst mode.

## Control Flow
PCI probe selects one of three port-info profiles by device ID and avoids claiming PDC20265 behind Promise I2O RAID bridges. Normal command flow follows libata BMDMA, with PDC2026x start/stop wrapping DMA to adjust clocks and state-machine helper registers.

## State And Persistence
State lives in PCI config timing registers, BMDMA registers, clock selection bits, and ATAPI/LBA48 byte-count helper registers. No heap private data is used.

## Dependencies And Integration Points
Uses libata BMDMA/SFF, PCI config and I/O resources, Promise PCI IDs, and generic PCI PM helpers.

## Risks And Edge Cases
Timing registers are shared between PIO and DMA programming. ATAPI DMA is disabled on old Promise. LBA48/ATAPI DMA needs special byte-count setup or the state machine may not complete. Clock bits are shared across channels and rely on host-level locking.

## Test Signals
All supported PCI IDs, I2O RAID exclusion, UDMA2/4/5 profiles, clock switch on UDMA3+, ATAPI DMA rejection, LBA48 DMA, cable detection, burst-mode enable, and interrupt status bits.
