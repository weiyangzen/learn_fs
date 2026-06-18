# sources/distributed-fs/ceph-client/drivers/scsi/arm/cumana_1.c

## Purpose

`cumana_1.c` implements the Cumana 16-bit SCSI-1 expansion-card driver using the generic NCR5380 core. It defines board-specific register access, pseudo-DMA read/write routines, IRQ setup, host-template glue, probe/remove, and module registration.

## Important APIs, Types, and Functions

The file specializes NCR5380 through macros such as `NCR5380_read`, `NCR5380_write`, `NCR5380_dma_xfer_len`, `NCR5380_dma_recv_setup`, `NCR5380_dma_send_setup`, `NCR5380_intr`, `NCR5380_queue_command`, and `NCR5380_info`. Card-specific helpers are `cumanascsi_read()`, `cumanascsi_write()`, `cumanascsi_pread()`, `cumanascsi_pwrite()`, `cumanascsi_dma_xfer_len()`, `cumanascsi1_probe()`, and `cumanascsi1_remove()`.

## Control Flow

Probe claims resources, allocates an NCR5380-sized host, maps slow IOC space for control/registers and MEMC space for pseudo-DMA, initializes the NCR5380 core with DMA fixup and late DMA setup flags, maybe resets the bus, enables card control, requests the IRQ, adds the host, and scans. The included `../NCR5380.c` supplies queueing, interrupt, and error handling under the Cumana-specific macros.

PIO-style pseudo DMA switches card control modes, polls status bits for interrupt or ready, transfers fast 32-byte chunks as split 16-bit writes/reads, handles trailing bytes, and restores the control latch.

## State and Persistence Behavior

State is NCR5380 hostdata plus an added `ctrl` implementation field storing the current control latch. No durable state is written. Runtime state is managed mostly inside the included NCR5380 core and SCSI mid-layer.

## Dependencies and Integration Points

The file depends on ARM ecard APIs, MMIO helpers, Linux SCSI host APIs, and the generic NCR5380 implementation. It integrates with SCSI through `cumanascsi_template`, IRQ registration, `scsi_add_host()`, and `scsi_scan_host()`.

## Risks and Edge Cases

The source includes `../NCR5380.c` directly, so macro definitions must be correct before inclusion. Pseudo-DMA casts buffers to `unsigned long *` and performs word chunking, making alignment and trailing byte handling important. `cumanascsi_dma_xfer_len()` returns `cmd->transfersize`, not total residual length, so behavior depends on mid-layer transfer-size semantics. Cleanup must unmap both IO windows on partial probe failure.

## Test Signals

Useful checks include probe/remove with both MMIO windows, IRQ delivery, NCR5380 bus reset and scan, pseudo-DMA read/write for 0-byte, sub-32-byte, 32-byte, and larger transfers, interrupt-aborted transfer handling, and `/proc` host naming as `CumanaSCSI-1`.
