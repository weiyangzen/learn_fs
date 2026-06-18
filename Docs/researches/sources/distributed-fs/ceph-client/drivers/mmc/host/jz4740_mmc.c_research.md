# sources/distributed-fs/ceph-client/drivers/mmc/host/jz4740_mmc.c

## Purpose

`jz4740_mmc.c` implements a platform MMC host driver for Ingenic JZ4740-family SD/MMC controllers, covering JZ4740, JZ4725B, JZ4760, JZ4780/JZ4775, and X1000 variants. It supports PIO and optional DMAEngine transfers, SDIO interrupts, regulators, GPIO card-detect/write-protect, signal voltage switching, and simple suspend/resume pinctrl handling.

## Important APIs, Types, And Functions

- Register and bit macros define the Ingenic MSC register map: start/stop/clock, status, clock divider, command attributes, block length/count, IRQ mask/status, command/argument/response FIFO, RX/TX FIFO, low-power mode, and JZ4780 DMA control.
- `enum jz4740_mmc_version` selects register width behavior and SoC quirks.
- `enum jz4740_mmc_state` drives threaded IRQ handling: read response, transfer data, send stop, done.
- `enum jz4780_cookie` tracks DMA mapping state for `pre_req`/`post_req` and in-flight IRQ mapping.
- `struct jz4740_mmc_host` stores the host, platform device, clock, variant, IRQ, MMIO base/resource, current request/command, vqmmc state, wait bit, cached `cmdat`, IRQ mask, timeout timer, scatterlist iterator, state, DMA channels, and DMA mode flag.
- `jz4740_mmc_acquire_dma_channels()` supports either a unified `"tx-rx"` channel or separate `"tx"` and `"rx"` channels and tightens `mmc->max_seg_size` to DMA limits.
- `jz4740_mmc_prepare_dma_data()`, `jz4740_mmc_start_dma_transfer()`, `jz4740_mmc_pre_request()`, and `jz4740_mmc_post_request()` implement DMA mapping, descriptor submission, and cleanup.
- `jz4740_mmc_write_data()` and `jz4740_mmc_read_data()` implement PIO FIFO transfers using `sg_mapping_iter` and FIFO request interrupts.
- `jz_mmc_irq()` is the hard IRQ handler; `jz_mmc_irq_worker()` is the threaded state-machine worker.
- `jz4740_mmc_set_ios()`, `jz4740_mmc_set_clock_rate()`, `jz4740_voltage_switch()`, and `jz4740_mmc_enable_sdio_irq()` implement the `mmc_host_ops` control plane.
- `jz4740_mmc_probe()` allocates/configures the host, resources, IRQ, DMA, limits, regulators, and registers with the MMC core.

## Control Flow And State

Requests start in `jz4740_mmc_request()`: the driver stores `host->req`, clears IRQ status, enables `END_CMD_RES`, sets state to `READ_RESPONSE`, arms a 5-second timer, and writes command registers through `jz4740_mmc_send_command()`. The hard IRQ reads status and IRQ flags, handles SDIO IRQs immediately, and when a waited command/data event arrives disables the IRQ source, clears the wait bit/timer, records command/data errors, and wakes the threaded handler.

The threaded handler reads the command response, prepares data iteration, then transfers data through DMA or PIO. DMA mode submits the transfer after mapping and optimistically sets `bytes_xfered`; PIO loops over FIFO request events. After data transfer it polls for `DATA_TRAN_DONE`, optionally sends a stop command and waits for program-done for busy stops, then calls `jz4740_mmc_request_done()`.

Timeout state is persisted in `host->waiting` bit 0 and `timeout_timer`. If a polled IRQ does not arrive quickly, `jz4740_mmc_poll_irq()` enables the hardware IRQ and arms the timer; the timeout handler disables command-end IRQ, marks the command timed out, and completes the request.

Power and bus state are cached in `host->cmdat` and `host->vqmmc_enabled`. `set_ios` resets on power-up, enables/disables regulators and clocks, sets the initialization bit for the next command, and updates bus-width bits.

## Dependencies And Integration Points

The driver integrates with Linux platform devices, OF match data, MMC core (`mmc_of_parse`, `mmc_add_host`, `mmc_request_done`), GPIO slot helpers, regulator supply helpers, DMAEngine, clocks, pinctrl PM states, threaded IRQs, timers, and scatterlist mapping. It includes `asm/cacheflush.h`, but the visible code path mostly relies on DMA/SG and FIFO access helpers. Device tree compatibles map directly to `enum jz4740_mmc_version`.

## Risks And Edge Cases

- DMA and PIO completion differ: DMA marks all bytes transferred immediately after submission, so data error paths must be caught by controller status and DMA termination.
- `jz4740_mmc_post_request()` assumes `data` is valid in the error branch; callers normally provide data for pre/post paths, but null handling is partial.
- Poll-to-IRQ fallback depends on `host->waiting` and timer ordering. Races could double-complete if an IRQ and timer cross, though the bit test mitigates this.
- Fixed `max_busy_timeout` is 5 seconds and the code comments call out that it does not honor per-command busy timeout yet.
- Version-specific IRQ register width and DMA control location are critical for older versus JZ4780+ SoCs.
- The JZ4760 maximum clock is clamped to 24 MHz due to known reliability issues.

## Test Signals

Validation should cover all compatible variants, 1/4/8-bit bus modes where advertised, PIO fallback when DMA channels are unavailable, unified and split DMA channel configurations, DMA pre_req/post_req paths, SDIO IRQ signaling, command/data CRC and timeout handling, stop commands after multi-block transfers, card-detect/write-protect GPIOs, vmmc/vqmmc regulator transitions, and suspend/resume pinctrl state selection.
