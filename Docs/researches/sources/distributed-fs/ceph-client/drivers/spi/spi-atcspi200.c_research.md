# sources/distributed-fs/ceph-client/drivers/spi/spi-atcspi200.c

## Purpose
Andes ATCSPI200 SPI controller driver focused on `spi-mem` operations for Qilai and AE350 compatibles. It supports command/address/data transactions, single to quad data widths, optional DMA for large aligned data phases, and suspend/resume.

## Important APIs, Types, and Functions
`struct atcspi_dev` stores controller, mutex, DMA completion, regmap, clock, data register DMA address, FIFO sizes, target clock, data-merge flag, and DMA availability. `atcspi_exec_mem_op()` is the central `spi_mem` path. Helpers program transfer format/control, poll FIFO readiness, transfer data in PIO, configure DMA, map `spi_mem` data buffers for DMA, and wait for controller idle. `atcspi_setup()` resets hardware, configures 8-bit data length, reads FIFO sizes, and programs SCLK divider.

## Control Flow
Probe allocates the controller, initializes mutex and regmap-backed MMIO, enables the clock, fills controller properties, resets/configures the hardware, registers the controller, then tries to acquire RX/TX DMA channels. Each memory op is serialized by `mutex_lock()`, programs format/control/address/opcode, chooses DMA when enabled and length is at least 256 bytes, otherwise uses FIFO polling. After data movement, it polls `ATCSPI_ACTIVE` clear before unlocking. `adjust_op_size` caps data to 512 bytes and aligns DMA-sized operations down to four bytes.

## State and Persistence
Controller state includes cached clock rate, selected SCLK rate, FIFO sizes, and transient `data_merge` mode. DMA channels live in `host->dma_rx` and `host->dma_tx`. Registers are not cached by regmap. Suspend disables the clock after SPI core suspend; resume re-enables the clock, reruns setup, then resumes the controller.

## Dependencies and Integration Points
It integrates with platform MMIO, regmap, clk, DMAengine, SPI core, and `spi_mem`. It uses `spi_controller_dma_map_mem_op_data()` and related unmap helpers for DMA-safe `spi_mem` buffers.

## Risks
The driver is `spi-mem` only and does not implement generic `transfer_one`. `atcspi_init_controller()` sets max speed to a fixed target rather than reading per-device speeds. DMA enable bits are set but not explicitly cleared after DMA transfers. Data merge assumes 4-byte aligned lengths and pointer access; `adjust_op_size` helps only for DMA-sized ops.

## Test Signals
Run SPI NOR read-id, read, page program, quad read, operation splitting at 512 bytes, DMA and PIO length thresholds, unaligned small transfers, suspend/resume, clock divider boundary tests, and forced DMA timeout/error tests.
