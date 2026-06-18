# sources/distributed-fs/ceph-client/drivers/spi/spi-ti-qspi.c

## Purpose
`spi-ti-qspi.c` implements the Texas Instruments DRA7xx/AM4372 QSPI controller driver. It supports ordinary half-duplex SPI transfers, dual/quad read commands, runtime PM with clock-context restore, optional memory-mapped read acceleration through `spi-mem`, and optional DMA memcpy from the memory-mapped QSPI window into client buffers or a bounce buffer.

## Important APIs, Types, And Functions
`struct ti_qspi` holds controller state: completions, transfer mutex, host, base and mmap MMIO windows, syscon chip-select regmap, functional clock, saved clock context, DMA channel/bounce buffer, command/device-control shadows, and memory-map state. `struct ti_qspi_regs` currently stores only the clock-control register for resume restore.

SPI callbacks include `ti_qspi_setup()` and `ti_qspi_start_transfer_one()`. SPI memory operations are implemented by `ti_qspi_exec_mem_op()` and `ti_qspi_adjust_op_size()` through `ti_qspi_mem_ops`. Regular transfer helpers are `qspi_write_msg()`, `qspi_read_msg()`, and `qspi_transfer_msg()`. Memory-map helpers include `ti_qspi_enable_memory_map()`, `ti_qspi_disable_memory_map()`, `ti_qspi_setup_mmap_read()`, `ti_qspi_dma_xfer_sg()`, and `ti_qspi_dma_bounce_buffer()`.

## Control Flow
Probe allocates a SPI host, configures CPOL/CPHA and dual/quad RX support, sets half-duplex flags, maps the controller and optional memory-map resources, optionally resolves a syscon chip-select register, gets `fck`, enables autosuspend runtime PM, reads max frequency and chip-select count, tries to obtain a DMA_MEMCPY channel and bounce buffer, maps the memory window for PIO fallback when DMA is unavailable, initializes memory-map state, and registers the controller.

Ordinary SPI messages program device-control polarity/phase, compute a frame length capped at 4096 words, write command and device-control registers, disable mmap mode if active, then process transfers under `list_lock`. Writes poll for not-busy, load one, two, four, or optimized 16 bytes into data registers, issue a write command, and poll write-complete. Reads choose single/dual/quad command mode, optimize 8-bit reads up to 16 bytes using the data register bank, issue commands, poll completion, and copy data out. After message transfers, the driver invalidates the command register and finalizes the message.

For `spi-mem` reads, `adjust_op_size` keeps reads inside the mmap window or caps fallback transfers to frame size. `exec_op` accepts only address-bearing reads within the mmap window, enables memory-map mode for the current CS when needed, programs opcode/address/dummy/bus-width setup, and copies from the mapped window. With DMA, it either maps the caller's buffer as an SG table when possible or DMA-copies into a coherent bounce buffer and then `memcpy()`s to the caller.

## State And Persistence
The driver caches `ctx_reg.clkctrl` and restores it in runtime resume. It tracks whether memory-map mode is enabled and which chip select owns it, disabling mmap before ordinary SPI transfers. `cmd` and `dc` are per-message shadows. There is no durable storage beyond hardware registers and driver memory.

## Dependencies And Integration Points
Dependencies include SPI core, `spi-mem`, platform resources, OF, clk, runtime PM, regmap/syscon, pinctrl headers, DMAengine, OMAP DMA headers, MMIO, and Linux scatterlist/DMA mapping helpers. OF compatibles are `ti,dra7xxx-qspi` and `ti,am4372-qspi`. The driver can integrate with SoC-level chip-select mapping through a `syscon-chipselects` property.

## Risks
Only read operations are optimized through `spi-mem`; writes and out-of-window reads fall back to ordinary transfer mode. Polling loops rely on status bits and can timeout or warn if the controller stays busy. DMA timeout is scaled to `msecs_to_jiffies(len)`, so very small or very large copies have unusual timeout behavior. Memory-map mode is shared mutable state protected by `list_lock`; failing to disable it before normal transfers would misroute commands. The driver requests an IRQ but does not use interrupt-driven transfer completion in this source, so IRQ resource presence is more platform-contract than runtime mechanism.

## Test Signals
Test ordinary 8/16/32-bit reads and writes, 16-byte optimized register reads/writes, dual and quad reads, frame-length truncation at 4096 words, mmap reads inside and outside the mapped window, DMA SG and bounce-buffer paths, absence of DMA fallback to `memcpy_fromio`, syscon chip-select switching, runtime resume clock restore, and timeout handling. Watch for `write timed out`, `read timed out`, DMA timeout, and `qspi busy` warnings.
