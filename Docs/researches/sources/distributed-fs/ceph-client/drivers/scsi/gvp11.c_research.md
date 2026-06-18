# sources/distributed-fs/ceph-client/drivers/scsi/gvp11.c

## Purpose

`gvp11.c` is the Amiga Zorro driver for GVP Series II SCSI boards using a WD33C93 SCSI controller and GVP DMA engine. It probes compatible Zorro products, validates the WD33C93, initializes DMA and WD33C93 core glue, and registers a SCSI host.

## Important APIs, types, and functions

- `struct gvp11_hostdata` embeds `struct WD33C93_hostdata` and stores GVP registers plus the device pointer.
- `gvp11_intr()` handles shared Amiga port interrupts and dispatches to `wd33c93_intr()` when the GVP DMA interrupt bit is pending.
- `dma_setup()` maps SCSI data, allocates bounce buffers when addresses violate the DMA mask, programs CNTR/ACR/BANK, and starts DMA.
- `dma_stop()` stops DMA, unmaps/free bounce buffers, and copies read data back when needed.
- `check_wd33c93()` probes indirect WD33C93 registers to distinguish real SCSI boards from same-product-code RAM boards.
- `gvp11_probe()` claims Zorro memory, validates board size and chip, allocates a SCSI host, initializes registers, configures DMA mask, initializes WD33C93 core, requests IRQ, and scans.
- `gvp11_remove()` disables interrupts, removes the SCSI host, frees IRQ, releases host and memory.

## Control flow

Zorro probe first checks DMA mask and board size, reserves the first 256 bytes, maps registers through `ZTWO_VADDR()`, and runs the WD33C93 detection sequence. It then allocates `Scsi_Host`, initializes GVP DMA secret registers and control state, prepares WD33C93 register pointers, selects DMA mask from module override or product data, initializes the WD33C93 core with callbacks, requests the shared Amiga port IRQ, enables DMA interrupts, registers the host, and scans.

DMA setup first tries direct `dma_map_single()`. If the mapped address violates the controller mask, it unmaps and uses a kernel or chip-RAM bounce buffer, copying write data into the bounce buffer as needed. It programs direction, DMA address, bank register, and starts DMA. Stop reverses this and copies from bounce buffer for successful reads.

## State and persistence behavior

Per-host state is in `gvp11_hostdata` and embedded WD33C93 state, including bounce-buffer pointers, DMA direction, and DMA mask. Hardware state persists in GVP registers (`CNTR`, `BANK`, `ACR`, start/stop DMA) and WD33C93 indirect registers.

## Dependencies and integration points

The driver depends on Amiga/Zorro bus APIs, Amiga chip RAM allocation, DMA mapping, WD33C93 core callbacks, and the SCSI midlayer. The Zorro ID table maps board products to default DMA masks.

## Risks and edge cases

- Bounce-buffer handling is complex; a failed remap path calls `dma_unmap_single()` even after the original mapping was cleared, so error handling deserves scrutiny.
- A static `scsi_alloc_out_of_range` changes future allocation strategy globally after one out-of-range allocation.
- The interrupt handler reads `CNTR` directly and assumes the pending bit is stable.
- Busy-waiting on `GVP11_DMAC_BUSY` during probe has no timeout.
- Chip RAM bounce buffers bypass cache maintenance by using physical addresses directly.

## Test signals

Hardware tests should cover direct DMA, kernel bounce buffer DMA, chip RAM bounce fallback, read/write transfers, shared IRQ handling, WD33C93 detection failure, board-size rejection, and remove cleanup. Static checks should inspect DMA unmap/free paths.
