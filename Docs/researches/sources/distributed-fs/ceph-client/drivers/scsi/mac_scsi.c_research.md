# sources/distributed-fs/ceph-client/drivers/scsi/mac_scsi.c

## Purpose
`mac_scsi.c` is the generic Macintosh NCR5380 SCSI platform driver. It binds Macintosh NCR5380-compatible hardware to the shared `NCR5380.c` core by defining register access macros, pseudo-DMA setup/residual callbacks, interrupt/queue/reset aliases, module/boot parameters, and Macintosh-specific PDMA transfer routines with m68k bus-error recovery.

## Important APIs, Types, And Functions
The file configures the core with macros such as `NCR5380_read`, `NCR5380_write`, `NCR5380_dma_xfer_len`, `NCR5380_dma_recv_setup`, `NCR5380_dma_send_setup`, `NCR5380_dma_residual`, and aliases for interrupt, queue, abort, reset, and info functions. Module parameters include queue depth, commands per LUN, SG table size, PDMA threshold, host ID, and Toshiba delay. Boot-time `mac5380=` parsing sets the same values for built-in kernels.

Transfer primitives are `mac_pdma_recv()`, `mac_pdma_send()`, `write_ctrl_reg()`, `macscsi_wait_for_drq()`, `macscsi_pread()`, `macscsi_pwrite()`, `macscsi_dma_xfer_len()`, and `macscsi_dma_residual()`. The platform integration is `mac_scsi_probe()`, `mac_scsi_remove()`, `mac_scsi_template`, and `module_platform_driver_probe()`.

## Control Flow
Probe obtains PIO, optional PDMA, and optional IRQ resources, checks hardware presence, applies module parameter overrides, forces IIfx SG table size to 1, allocates a SCSI host plus `NCR5380_hostdata`, fills register bases and PDMA flags, calls `NCR5380_init()` with late DMA setup, requests a shared IRQ when present, possibly resets the bus, adds the host, stores platform driver data, and scans. Remove unregisters the host, frees IRQ, exits the NCR5380 core, and drops the SCSI host reference.

Pseudo-DMA receive/write waits for DRQ while phase matches and no IRQ is pending, optionally toggles IIfx handshake mode, transfers up to 512 bytes per chunk with bus-error-aware assembly loops, updates `pdma_residual`, logs bus errors, and marks the connected command `DID_ERROR` if the target stops delivering data in a way that cannot be retried. `macscsi_dma_xfer_len()` enables PDMA only when pseudo-DMA is available and the residual exceeds the configured threshold.

## State And Persistence
State is volatile in `NCR5380_hostdata`, including register base, PDMA I/O address, flags, connected command, and `pdma_residual`. Module parameters persist only as module/kernel command-line configuration for the current boot. No device data is persisted.

## Dependencies And Integration Points
The file depends on m68k Macintosh platform data, `hwreg_present()`, Mac IRQs, I/O accessors, the generic NCR5380 core/header, Linux platform driver APIs, and SCSI mid-layer APIs. It includes `NCR5380.c` directly after defining implementation macros, making it a compile-time specialization of the generic core.

## Risks And Edge Cases
Inline assembly and exception-table recovery are architecture-specific and must preserve residual accounting exactly. Send-side bus errors may leave target-visible ACK uncertainty, so commands are retried as errors. Busy waits in `macscsi_wait_for_drq()` rely on polite polling and can still delay progress. Parameter overrides can set queue/SG sizes beyond what old hardware handles unless bounded by core behavior. The driver uses physical platform resource addresses directly as I/O pointers, reflecting legacy m68k address mapping assumptions.

## Test Signals
Signals include boot parameter parsing, probe with and without IRQ/PDMA resources, IIfx single-SG and handshake behavior, PDMA threshold fallback to PIO, receive/send bus-error injection, DRQ timeout handling, NCR5380 queue/abort/reset behavior, SCSI scan on supported Macs, module unload cleanup, and stress transfers across odd/even buffer alignment and residual lengths.
