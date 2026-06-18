<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sun3x_esp.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/sun3x_esp.c

## Purpose
`sun3x_esp.c` is the Sun3x platform front-end for the generic ESP SCSI core. It maps Sun3x ESP and DMA registers, implements `esp_driver_ops` for big-endian m68k DMA register access, and registers a platform SCSI host named `sun3x_esp`.

## Important APIs, Types, And Functions
The key integration object is `sun3x_esp_ops`, which supplies `esp_write8`, `esp_read8`, `irq_pending`, `reset_dma`, `dma_drain`, `dma_invalidate`, `send_dma_cmd`, and `dma_error` to `esp_scsi.c`. Probe/remove are `esp_sun3x_probe()` and `esp_sun3x_remove()`. DMA helper functions are `sun3x_esp_reset_dma()`, `sun3x_esp_dma_drain()`, `sun3x_esp_dma_invalidate()`, `sun3x_esp_send_dma_cmd()`, and `sun3x_esp_dma_error()`.

## Control Flow
Probe allocates a SCSI host with `scsi_esp_template`, sets `host->max_id`, initializes the embedded `struct esp`, maps ESP registers from memory resource 0 and DMA registers from resource 1, allocates a coherent 16-byte command block, requests the platform IRQ with `scsi_esp_intr`, sets initiator ID 7, configures the ESP clock to 20 MHz, stores driver data, and calls `scsi_esp_register()`. Remove unregisters the ESP core, disables DMA interrupts, frees IRQ and command-block DMA memory, and releases the SCSI host.

During I/O, the ESP core calls the ops. Register accesses use `reg * 4` spacing. DMA reset toggles `DMA_RST_SCSI` and enables interrupts. Drain waits for `DMA_FIFO_ISDRAIN` to clear after requesting standard drain. Invalidate waits for `DMA_PEND_READ`, disables DMA/write/count, toggles `DMA_FIFO_INV`, and clears it. `send_dma_cmd()` loads ESP transfer count bytes, enables DMA, sets write direction, writes the DMA address, and starts the ESP command.

## State And Persistence Behavior
State is the generic `struct esp` plus mapped MMIO pointers, command-block DMA address, IRQ number, configured SCSI ID/mask, and clock frequency. No persistent state is stored. DMA controller state is reset or invalidated around transfers.

## Dependencies And Integration Points
The driver depends on Sun3x platform resources, m68k DMA/DVMA headers, coherent DMA allocation, platform IRQs, and the generic `esp_scsi` core. It intentionally bypasses normal `readl()`/`writel()` in favor of volatile 32-bit accesses because the m68k helpers assume little-endian MMIO semantics that are wrong for Sun3x.

## Risks
Risks include endian-sensitive DMA register access, missing cleanup of mapped MMIO in remove, drain/invalidate timeouts that only log, IRQ sharing interactions, and hard-coded SCSI ID/clock assumptions. Probe error unwinding unmaps resources, but normal remove frees only IRQ/command block/host and disables interrupts.

## Test Signals
Test probe/remove on Sun3x platform resources, endian-correct DMA CSR reads/writes, DMA interrupt pending and error bits, FIFO drain timeout, pending-read invalidate timeout, read/write DMA command setup, command-block allocation failure, IRQ request failure, `scsi_esp_register()` failure unwinding, and generic ESP command completion through `scsi_esp_intr`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sun3x_esp.c -->
