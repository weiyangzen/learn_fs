<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sun3_scsi.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/sun3_scsi.c

## Purpose
`sun3_scsi.c` is the Sun3 NCR5380 SCSI controller front-end. It wires the generic `NCR5380.c` core to Sun3 on-board or VME DMA hardware, provides platform probe/remove glue, and implements Sun3-specific DVMA setup, FIFO handling, interrupt dispatch, and residual reporting.

## Important APIs, Types, And Functions
The file defines `NCR5380_read()`, `NCR5380_write()`, and NCR5380 callback aliases before including `NCR5380.h` and later `NCR5380.c`. Hardware layouts are `struct sun3_dma_regs` and, for non-VME on-board controllers, `struct sun3_udc_regs`. Important functions are `scsi_sun3_intr()`, `sun3scsi_dma_setup()`, `sun3scsi_dma_count()`, `sun3scsi_dma_residual()`, `sun3scsi_dma_xfer_len()`, `sun3scsi_dma_start()`, `sun3scsi_dma_finish()`, `sun3_scsi_probe()`, and `sun3_scsi_remove()`.

## Control Flow
At build time, the file becomes either `sun3_scsi` or a VME variant depending on `SUN3_SCSI_VME`. Probe applies module-parameter overrides for queue depth, commands per LUN, SG table size, and host ID. Non-VME probe maps one memory resource and allocates DVMA memory for UDC descriptors. VME probe scans up to two IRQ/MMIO resource pairs, maps VME16 space, and tests whether the DMA CSR looks like a present board. Probe then allocates a SCSI host with `NCR5380_hostdata`, initializes the generic NCR5380 core, requests the IRQ, initializes the Sun3 DMA registers, optionally resets the SCSI bus, registers the host, and scans.

For data transfer, `sun3scsi_dma_xfer_len()` requests DMA only for non-passthrough transfers of at least `DMA_MIN_SIZE`. `sun3scsi_dma_setup()` maps the buffer into DVMA space, resets FIFO/UDC state, programs direction and count/address registers, and returns the accepted byte count. The generic NCR5380 core calls `sun3scsi_dma_start()` to launch the UDC or VME DMA count and later `sun3scsi_dma_finish()` to disable DMA, drain/read FIFO leftovers, compute `last_residual`, copy residual packed bytes back into memory for reads, unmap DVMA, and reset controller state. The IRQ handler checks DMA error bits and forwards SCSI/DMA interrupts to `NCR5380_intr()`.

## State And Persistence Behavior
The driver uses file-static state for the single supported controller: `dregs`, `udc_regs`, `sun3_dma_orig_addr`, `sun3_dma_orig_count`, `sun3_dma_active`, `sun3_dma_setup_done`, and `last_residual`. There is no persistent state; all state is MMIO, DVMA mappings, and NCR5380 host state. The TODO notes lack of support for multiple Sun3 SCSI VME boards, and the globals enforce that limitation.

## Dependencies And Integration Points
It depends on m68k Sun3 IO/DVMA helpers, the platform bus, SCSI host APIs, the generic NCR5380 core, and platform-provided IRQ/MMIO resources. VME builds additionally use `sun3_ioremap()`, VME page types, `dvma_map_vme()`, and `sun3_map_test()`.

## Risks
The main risks are single-controller global state, FIFO residual edge cases on odd read/write counts, UDC timeout paths, VME board detection false positives, DVMA mapping lifetime, and error unwinding across partially initialized NCR5380/DVMA resources. The code returns DMA length zero for small/passthrough commands, so performance and correctness depend on the NCR5380 PIO fallback.

## Test Signals
Test non-VME and VME builds, module-parameter overrides, missing resources, IRQ request failure, DVMA allocation failure, DMA transfers below and above `DMA_MIN_SIZE`, odd-length reads/writes, FIFO empty timeout, DMA bus error/conflict IRQ reporting, VME board probing, residual reporting through the NCR5380 core, remove cleanup, and `NCR5380_maybe_reset_bus()` behavior during probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sun3_scsi.c -->
