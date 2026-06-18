# sources/distributed-fs/ceph-client/drivers/scsi/arm/arxescsi.c

## Purpose

`arxescsi.c` is the ARXE 16-bit SCSI expansion-card driver. It is a board-specific wrapper around the generic FAS216 core and supplies card resource mapping, FAS216 timing/configuration, pseudo-DMA data movement, host-template callbacks, and expansion-card registration.

## Important APIs, Types, and Functions

`struct arxescsi_info` overlays `FAS216_Info` with the expansion card and base MMIO pointer. The card-specific DMA hooks are `arxescsi_dma_setup()`, `arxescsi_dma_pseudo()`, `arxescsi_pseudo_dma_write()`, and `arxescsi_dma_stop()`. User-visible reporting uses `arxescsi_info()` and `arxescsi_show_info()`. Lifecycle is `arxescsi_probe()`, `arxescsi_remove()`, `init_arxe_scsi_driver()`, and `exit_arxe_scsi_driver()`.

## Control Flow

Probe claims the expansion card, maps MEMC space, allocates a SCSI host, fills FAS216 register base, clock, select timeout, async period, sync depth, disconnect, and pseudo-DMA callbacks, configures expansion-card IRQ status fields, initializes the FAS216 core, and calls `fas216_add()`. Runtime command flow is delegated to `fas216_noqueue_command`, meaning the FAS216 core polls progress rather than using a registered IRQ for this board.

Pseudo DMA always advertises `fasdma_pseudo`. Reads and writes poll FAS216/card status, move 16-bit words through `DMADATA_OFFSET`, and stop early when the FAS216 interrupt bit is observed.

## State and Persistence Behavior

State is per host in `struct arxescsi_info` plus the embedded `FAS216_Info`. No settings persist. The pseudo-DMA code uses the current `struct scsi_pointer` buffer and does not retain additional transfer state outside FAS216's active command state.

## Dependencies and Integration Points

The file depends on ARM expansion-card APIs, MMIO helpers, Linux SCSI host APIs, and `fas216.h`. It integrates with the generic FAS216 state machine through DMA callbacks and the `scsi_host_template`.

## Risks and Edge Cases

The header comment says the driver is based on experimentation, so hardware assumptions are explicitly fragile. The inline ARM assembly write path is architecture-specific and assumes 256-byte chunks and particular register behavior. The read path has a conditional bulk-read branch tied to `transfer & 255`, which should be tested for short and unaligned transfers. Since no IRQ is used, progress relies on polling in `fas216_noqueue_command`.

## Test Signals

Signals include successful probe of `MANU_ARXE/PROD_ARXE_SCSI`, FAS216 chip detection, scan completion without IRQ, read/write pseudo-DMA with short, 256-byte, and multi-block transfers, disconnect disabled behavior, and clean removal/reprobe.
