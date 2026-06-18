# sources/distributed-fs/ceph-client/drivers/ata/pata_pxa.c

## Purpose
Provides a DMA-capable platform PATA driver for PXA systems using the DMAengine slave API.

## Important APIs, Types, And Functions
`struct pata_pxa_data` stores DMA channel, cookie, and completion. `pxa_qc_prep()` prepares slave SG descriptors and callback. `pxa_bmdma_setup()`, `pxa_bmdma_start()`, `pxa_bmdma_stop()`, and `pxa_bmdma_status()` adapt libata BMDMA hooks to DMAengine. `pxa_ata_probe()` maps resources, configures DMA, and activates the ATA host; `pxa_ata_remove()` releases DMA and detaches.

## Control Flow
Probe validates four resources, maps command/control/DMA windows, derives taskfile addresses from platform `reg_shift`, requests DMA channel `data`, configures 16-bit bus widths and burst size, then activates SFF interrupts. For DMA commands, libata maps SG, `qc_prep` submits descriptors, setup issues the ATA command, start kicks DMAengine, stop waits for completion or error and terminates the channel.

## State And Persistence
Per-port state is `struct pata_pxa_data` in `ap->private_data`. DMA cookies and completions track the active transfer. Mapped register windows and DMA channel persist until remove.

## Dependencies And Integration Points
Depends on platform data `ata-pxa.h`, DMAengine, libata BMDMA/SFF, platform IRQ flags, and devm mappings.

## Risks And Edge Cases
`pxa_qc_prep()` logs descriptor-prep failure but returns `AC_ERR_OK`, which may let later stages see missing DMA setup. ATAPI DMA is unsupported. Probe assumes non-null platform data for `reg_shift` and `irq_flags`. Error after DMA config does not release the channel in all early return paths.

## Test Signals
PIO and MWDMA transfers, DMAengine callback completion, DMA error status, timeout path, ATAPI DMA rejection, missing resources, absent DMA channel, remove after active host, and platform-data validation.
