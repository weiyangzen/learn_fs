# sources/distributed-fs/ceph-client/drivers/spi/spi-sh-msiof.c

## Purpose

`spi-sh-msiof.c` is the SuperH/R-Car MSIOF SPI controller driver. It supports host and target modes, native and GPIO chip selects, 3-wire, LSB-first, many bits-per-word combinations, PIO and DMA, SoC-specific FIFO sizes and controller flags, optional DTDL/SYNCDL timing properties, and detection of MSIOF instances used for I2S rather than SPI.

## Important APIs, Types, and Functions

`struct sh_msiof_chipdata` carries bits-per-word masks, FIFO sizes, controller flags, minimum divider power, and quirks. `struct sh_msiof_spi_priv` stores controller, MMIO base, clock, platform device, parsed info, completions, FIFO sizes, DMA bounce pages and addresses, native CS state, and target-abort state.

Important functions include register read/write and CTR polling, IRQ handler, reset, clock and pin-mode register setup, DTDL/SYNCDL encoding, mode-register programming, FIFO read/write variants for aligned/unaligned and swapped 8/16/32-bit data, native-CS setup, message prepare, hardware start/stop, target abort, completion wait, PIO chunk transfer, DMA transfer, byte/word swap copy helpers, `sh_msiof_transfer_one()`, DT parsing, DMA channel allocation/release, probe/remove, and PM.

## Control Flow

Probe rejects nodes with graph ports because they represent MSIOF-I2S usage, selects chipdata and platform/DT info, applies fixed DTDL for R8A7795, allocates host or target controller, gets clock/IRQ/MMIO, requests IRQ, enables runtime PM, applies FIFO overrides, sets SPI capabilities and hooks, optionally allocates DMA channels plus one-page TX/RX DMA bounce buffers, and registers the controller.

Message prepare configures pin and CS polarity before assertion. Each transfer resets registers, sets the clock in host mode, limits word count by FIFO size, attempts DMA for chunks over 15 bytes when DMA exists, packing 8/16-bit data into 32-bit DMA words with byte/halfword swaps, and falls back to PIO on `-EAGAIN`. PIO chooses width-specific FIFO functions, programs mode registers and watermarks, fills TX FIFO, starts hardware, waits for interrupt completion or target abort, drains RX FIFO, clears status, stops hardware, and repeats for remaining words including odd trailing bytes.

## State and Persistence Behavior

State is runtime-only: completions, target-abort flag, FIFO sizing, native CS polarity cache, DMA bounce pages, and controller registers. There is no persistent storage. Timing properties from DT/platform data are parsed at probe and then used for each pin-mode setup.

## Dependencies and Integration Points

The driver integrates with platform/OF, OF graph, clock framework, PM runtime, interrupts, DMAengine plus SH DMA compatibility filters, SPI core host/target APIs, and `linux/spi/sh_msiof.h` register definitions/platform data. Match data covers SH Mobile and R-Car generations 2 through 4.

## Risks and Edge Cases

DMA uses single-page bounce buffers and chunks capped by mode-register word-length fields; large transfers rely on repeated packing/unpacking. Both source and destination cannot be unaligned for copy helpers, as noted in comments. Target abort completes both normal and TX-DMA completions, so abort races with real completions require careful testing. DTDL/SYNCDL values outside limited encodings are ignored with warnings. If DMA setup partially fails, release paths must unmap/free pages and channels exactly once. Clock setup reports too-low requested rates but still programs maximum divisor.

## Test Signals

Test SH/R-Car generation match data, host and target mode, native and GPIO CS, active-high CS, 3-wire TX high-Z, DTDL/SYNCDL DT values, 8/16/24/32-bit transfers, unaligned buffers, odd trailing bytes, DMA and PIO paths, DMA fallback, target abort during PIO and DMA, low-speed requests, suspend/resume, and probe rejection for I2S graph nodes.
