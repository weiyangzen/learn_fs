# sources/distributed-fs/ceph-client/drivers/scsi/mac_esp.c

## Purpose
`mac_esp.c` is the Macintosh Quadra front-end for the generic ESP SCSI core. It maps fixed Macintosh ESP register addresses, implements byte register access and pseudo-DMA/PIO transfer callbacks, handles the shared edge-triggered Mac SCSI IRQ for up to two ESP chips, and registers/unregisters ESP instances as platform devices.

## Important APIs, Types, And Functions
`struct mac_esp_priv` stores the generic `struct esp *` plus PDMA status and data I/O addresses. Global `esp_chips[2]` and `esp_chips_lock` coordinate the shared interrupt handler. Hardware access callbacks are `mac_esp_write8()`, `mac_esp_read8()`, `mac_esp_reset_dma()`, `mac_esp_dma_drain()`, `mac_esp_dma_invalidate()`, `mac_esp_dma_error()`, `mac_esp_irq_pending()`, and `mac_esp_dma_length_limit()`. Transfer helpers are `mac_esp_wait_for_empty_fifo()`, `mac_esp_wait_for_dreq()`, the inline-assembly `MAC_ESP_PDMA_LOOP`, and `mac_esp_send_pdma_cmd()`.

The integration surface is `struct esp_driver_ops mac_esp_ops`, `esp_mac_probe()`, `esp_mac_remove()`, and `mac_scsi_esp_intr()`. Probe fills the generic ESP fields and calls `scsi_esp_register()`.

## Control Flow
Probe rejects non-Mac systems and device IDs above 1, allocates a SCSI host with generic ESP private data, allocates a 16-byte command block, creates `mac_esp_priv`, chooses register addresses and clock frequency from `macintosh_config->scsi_type`, sets the FIFO register and callbacks, and selects PDMA or PIO. Quadra and Quadra2 use PDMA; Quadra3 logs PIO and disables sync because its PSC DMA is not driven. The first ESP instance normally owns the shared IRQ, and the second shares the global handler through `esp_chips[]`. After registration with the generic ESP core, the SCSI scan is handled by that core.

On transfer, `mac_esp_send_pdma_cmd()` programs transfer counts, issues the ESP command, waits for DREQ, runs the 68k assembly loop in read or write direction, drains FIFO for reads, and repeats until the ESP count reaches zero or an interrupt/error stops the loop. The IRQ handler loops while either chip reports `ESP_STAT_INTR`, calling `scsi_esp_intr()` for each to avoid losing edge-triggered transitions.

## State And Persistence
Runtime state is volatile: `esp_chips[]`, per-device `mac_esp_priv`, generic ESP state, command block memory, send-command error flag, and platform driver data. There is no persistent configuration; machine type and fixed addresses are firmware/platform facts.

## Dependencies And Integration Points
The driver depends on m68k Macintosh platform data (`macintosh_config`), NuBus accessors, VIA DRQ checks, Mac IRQ constants, generic ESP SCSI core (`esp_scsi.h`), Linux platform driver and SCSI host APIs, and low-level inline assembly exception-table fixups for PDMA.

## Risks And Edge Cases
The PDMA wait loops can spin for up to 500000 iterations with microsecond delays, so hung hardware causes long stalls. `mac_esp_ops.send_dma_cmd` is a global ops field mutated to PIO when one device lacks PDMA; mixed-device configurations could be sensitive to that shared mutation. Fixed physical MMIO addresses and machine-type branches limit portability. Transfer loops rely on m68k exception-table recovery and manual count reconstruction. Shared IRQ handling must update `esp_chips[]` atomically enough to avoid calling into a removed chip.

## Test Signals
Signals include probe on Quadra, Quadra2, and Quadra3 paths; PDMA and PIO transfer success; IRQ sharing with one and two ESP devices; FIFO-empty and DREQ timeout logging; transfer length clamping at 0xffff; generic ESP scan and command completion; unregister/free IRQ behavior when removing one of two chips; and error propagation through `esp->send_cmd_error`.
