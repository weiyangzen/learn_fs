# sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic7xxx_osm.h

Purpose: Linux OS mapping header for the `aic7xxx` core. It defines Linux-facing aliases, DMA/bus-space abstractions, per-device/per-SCB/per-adapter platform storage, locking helpers, PCI/EISA entry points, SCSI result wrappers, and integration declarations used by the core and bus-specific files.

Important APIs, types, and functions: key types are `ahc_dev_softc_t`, `ahc_io_ctx_t`, `bus_space_tag_t`, `bus_space_handle_t`, `bus_dma_segment_t`, `bus_dma_tag_t`, `struct ahc_linux_dma_tag`, `struct ahc_linux_device`, `struct scb_platform_data`, and `struct ahc_platform_data`. It declares DMA functions, low-level I/O functions, `ahc_linux_register_host()`, PCI/EISA mapping functions, proc functions, `ahc_platform_*()` hooks, `ahc_linux_isr()`, `ahc_done()`, `ahc_send_async()`, and `ahc_print_path()`.

Control flow role: this header lets portable code call FreeBSD/CAM-style primitives while Linux-specific implementations live in `aic7xxx_osm.c` and `aic7xxx_osm_pci.c`. Inline helpers translate Linux `scsi_cmnd` fields into CAM-like transaction and SCSI status, transfer length/direction/residual accessors, autosense behavior, and SCB freeze semantics. Lock helpers wrap `spin_lock_irqsave()` around adapter state.

State and persistence: `struct ahc_linux_device` tracks live queue depth, freeze counts, active commands, issued command count, tag throttling, and ordered-tag starvation counters. `struct scb_platform_data` links an SCB to device state and stores DMA transfer length and autosense residual. `struct ahc_platform_data` stores target pointers, lock, controller freeze count, error-handler completion, Linux `Scsi_Host`, IRQ, BIOS address, and MMIO bus address. All are runtime-only.

Dependencies and integration: includes Linux block, PCI, interrupt, module, I/O, and SCSI/SPI transport headers plus local `cam.h`, `queue.h`, `scsi_message.h`, `aiclib.h`, and `aic7xxx.h`. It exposes PCI config register constants used by the portable PCI layer.

Risks: many macros/inline wrappers encode Linux mid-layer assumptions, for example always performing autosense and treating coherent DMA sync as no-op. `ahc_freeze_scb()` modifies command result bits and device freeze counters inline, so misuse affects completion. The header is widely included; ABI or field changes can break multiple bus/core files.

Test signals: compile all AIC7XXX variants with/without PCI/EISA/debug/pretty-print options, validate structure field use across `aic7xxx_osm.c`, `aic7xxx_pci.c`, and `aic7770_osm.c`, run sparse/build checks for address-space annotations, and exercise queue-depth/status/residual wrappers through normal I/O and error completions.
