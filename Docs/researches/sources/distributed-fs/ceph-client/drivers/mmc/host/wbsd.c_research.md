# sources/distributed-fs/ceph-client/drivers/mmc/host/wbsd.c

## Purpose
This file implements the Winbond W83L51xD SD/MMC host driver. It supports both PnP-discovered and manually configured platform instances, exposes the chip through the MMC core, and handles legacy I/O-port, IRQ, and optional ISA DMA resources.

## Important APIs, types, and functions
- `wbsd_ops` provides MMC `.request`, `.set_ios`, and `.get_ro`.
- Low-level helpers `wbsd_unlock_config()`, `wbsd_write_config()`, `wbsd_read_config()`, `wbsd_write_index()`, and `wbsd_read_index()` access Super I/O config and indexed SD registers.
- `wbsd_init_device()` resets the SD function/FIFO, sets card-detect mode, powers down the port, configures max timeout and interrupts, and records card-present state.
- `wbsd_prepare_data()`, `wbsd_finish_data()`, `wbsd_empty_fifo()`, and `wbsd_fill_fifo()` implement data transfer through ISA DMA or programmed FIFO.
- `wbsd_irq()` accumulates interrupt status and schedules bottom-half work for card, FIFO, CRC, timeout, and transfer-complete events.
- Resource setup is split across `wbsd_scan()`, `wbsd_request_resources()`, `wbsd_chip_config()`, `wbsd_chip_validate()`, `wbsd_init()`, and `wbsd_shutdown()`.

## Control flow
Requests enter `wbsd_request()` under `spin_lock_bh()`. The driver rejects missing-card requests, validates data commands against the controller-supported command set, prepares data when present, sends the command, and either finishes immediately or leaves completion to IRQ/work handling. `wbsd_send_command()` writes opcode and argument bytes to the command register, waits until card traffic clears, then checks accumulated ISR bits for card removal, timeout, and CRC errors before reading short or long responses.

For data transfers, `wbsd_prepare_data()` programs timeout registers, block size including CRC bytes, bus width, and resets the FIFO. If DMA is available, it copies write data into a 64 KiB DMA buffer, programs the ISA DMA controller, and enables host DMA. Without DMA, it initializes scatter-gather traversal, configures FIFO thresholds, and pre-fills FIFO for writes. IRQ bottom halves drain/fill FIFO, mark CRC/timeout errors, or call `wbsd_finish_data()`. Finish logic optionally sends a stop command, waits until block read/write state clears, disables DMA, computes `bytes_xfered`, copies read DMA data back to SG, adjusts bytes on error, and completes the MMC request.

Card detection is interrupt and timer mediated. `wbsd_card_bh_work()` updates `WBSD_FCARD_PRESENT`, aborts active transfers on removal, and calls `mmc_detect_change()`. DAT3 chip-select initialization temporarily sets `WBSD_FIGNORE_DETECT`; `ignore_timer` later re-enables detection and schedules a card check.

## State and persistence
Driver state resides in `struct wbsd_host`: current request, accumulated ISR, SG cursor, DMA buffer/address, clock, bus width, config port/unlock code, chip ID, base/IRQ/DMA resources, flags, work items, and ignore timer. There is no persistent storage. Module parameters `nopnp`, `io`, `irq`, and `dma` configure non-PnP probing.

## Dependencies and integration points
The driver depends on legacy port I/O, ISA DMA APIs, PnP, platform devices, MMC core, workqueues, timers, and scatterlist helpers. It uses `devm_mmc_alloc_host()` but manually manages I/O regions, IRQ, DMA buffer, and PnP/platform registration.

## Risks and edge cases
- The source comments document broken FIFO size and threshold behavior; FIFO mode uses proactive workqueue polling to compensate.
- ISA DMA requires a 64 KiB-aligned buffer below 16 MB; failures fall back to FIFO, while unexpected alignment bugs call `BUG_ON(1)`.
- Several paths busy-wait on hardware status under lock.
- Data command support is explicitly limited; unsupported commands with data return `-EINVAL`.
- Request completion unlocks around `mmc_request_done()` and then relocks, so caller assumptions around `host->lock` must remain consistent.

## Test signals
Key tests include PnP and non-PnP probe, configured I/O/IRQ/DMA combinations, FIFO fallback, read/write single and multi-block transfers, card removal during transfer, CRC and timeout interrupt handling, write-protect reporting, suspend/resume for both platform and PnP modes, and DAT3/MMC chip-select detection blackout behavior.
