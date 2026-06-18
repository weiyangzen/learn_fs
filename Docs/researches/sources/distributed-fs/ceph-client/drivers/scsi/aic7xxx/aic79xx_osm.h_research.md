# sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic79xx_osm.h

## Purpose

`aic79xx_osm.h` is the Linux platform contract for the portable AIC79xx/AHD core. It imports Linux kernel, PCI, and SCSI headers; defines BSD-style bus/DMA typedefs expected by the core; declares Linux OSM entry points; defines per-device/per-adapter platform state; and provides inline wrappers for status, residual, sense, locking, PCI identity, and queue-freeze behavior.

## Important APIs, Types, and Functions

- Platform typedefs include `ahd_dev_softc_t` as `struct pci_dev *`, `ahd_io_ctx_t` as `struct scsi_cmnd *`, `bus_space_tag_t`, `bus_space_handle_t`, `bus_dma_segment_t`, `bus_dma_tag_t`, and `bus_dmamap_t`.
- `struct ahd_linux_dma_tag` stores the simplified Linux DMA allocation constraints used by the core shims.
- `enum ahd_linux_dev_flags` and `struct ahd_linux_device` track per-LUN queue state, active/opening counts, queue freeze, tag-depth adaptation, and periodic ordered tag behavior.
- `struct scb_platform_data` stores Linux-specific SCB state: device pointer, buffer bus address, transfer length, and autosense residual.
- `struct ahd_platform_data` stores interrupt-safe adapter state: target pointers, spinlock, error-handler completion, `Scsi_Host`, IRQ, BIOS address, and memory BAR bus address.
- Inline locking wrappers `ahd_lockinit()`, `ahd_lock()`, and `ahd_unlock()` use `spin_lock_irqsave()` around core critical sections.
- Transaction wrappers manipulate Linux `scsi_cmnd->result` with CAM status in the upper word and SCSI status in the lower word; residual wrappers use `scsi_set_resid()` and `scsi_get_resid()`.
- PCI helpers expose config register constants, PCI-X status masks, bus/slot/function accessors, and `ahd_flush_device_writes()`.

## Control Flow and State

This header does not implement a standalone flow, but it shapes every Linux AHD path. The SCSI queue path stores CAM state in `cmd->result`, uses `struct scb_platform_data` for per-command transfer metadata, and updates `struct ahd_linux_device` counters. The PCI attach path fills `struct ahd_platform_data`, maps registers using the bus-space fields in `struct ahd_softc`, and stores the IRQ/host for later removal.

## Dependencies and Integration Points

The header depends on Linux SCSI mid-layer, SPI transport, PCI, interrupt, module, byteorder, and I/O APIs. It includes `cam.h`, `queue.h`, `scsi_message.h`, `scsi_iu.h`, `aiclib.h`, and finally the portable `aic79xx.h`, making it the bridge between Linux and the OS-neutral AHD core. It declares functions implemented by `aic79xx_osm.c`, `aic79xx_osm_pci.c`, and `aic79xx_proc.c`.

## Risks

- The `scsi_cmnd->result` encoding must remain consistent with `ahd_linux_queue_cmd_complete()`; any mid-layer API change around result bytes can break status mapping.
- `ahd_dmamap_sync()` is intentionally a no-op for coherent memory, with a comment noting possible architecture uncertainty.
- `ahd_flush_device_writes()` relies on an `INTSTAT` read to flush writes, which may be insufficient on some architectures if I/O ordering assumptions change.
- Per-target indexing assumes channel B, when present, is represented by offset `+8`; wrong topology assumptions would corrupt target state lookup.

## Test Signals

- Full driver compile catches platform/core type-contract drift.
- Runtime tests should verify spinlock-protected queueing/completion, status/result mapping, residual updates, procfs info, PCI resource mapping, and target transport attribute visibility.
