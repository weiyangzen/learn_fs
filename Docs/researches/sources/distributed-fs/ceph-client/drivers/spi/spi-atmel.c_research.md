# sources/distributed-fs/ceph-client/drivers/spi/spi-atmel.c

## Purpose
Atmel AT32/AT91 SPI controller driver supporting older PDC engines, newer DMAengine transfers, FIFO and non-FIFO PIO, native and GPIO chip selects, runtime PM, and controller-version capability detection.

## Important APIs, Types, and Functions
`struct atmel_spi` holds locks, registers, clocks, current transfer, DMA bounce buffers, completion, capability flags, backend selection, FIFO size, and chip-select bookkeeping. `struct atmel_spi_device` stores per-device CSR. Major paths include `atmel_spi_setup()`, `atmel_spi_set_cs()`, `atmel_spi_one_transfer()`, DMA/PDC/PIO submission helpers, IRQ handlers `atmel_spi_pio_interrupt()` and `atmel_spi_pdc_interrupt()`, and PM/probe/remove routines.

## Control Flow
Probe selects pinctrl default state, gets IRQ and clocks, allocates the controller, maps registers, detects capabilities from `SPI_VERSION`, configures DMA or PDC, requests the appropriate IRQ handler, enables clocks, reads optional FIFO size, initializes hardware, enables runtime PM, and registers the controller. Per-device setup builds a CSR with bits-per-word, polarity, phase, chip-select-active-after-transfer, and word delay. Transfers reject bits-per-word changes not matching the saved CSR, set speed, initialize completion state, then loop until all bytes are moved. Backend selection is PDC if old hardware, DMA for large transfers when channels are available, or PIO. Completion is interrupt-driven, with timeout based on SPI core transfer timeout.

## State and Persistence
Per-device CSR persists in `spi->controller_state`. Runtime state includes `current_transfer`, remaining byte count, `done_status`, `keep_cs`, FIFO size, last polarity, and native CS allocation for GPIO CS. Hardware is reset on init, error cleanup, remove, and resume. Runtime PM gates both peripheral and optional generated clocks.

## Dependencies and Integration Points
It integrates with platform MMIO/IRQ, clk, optional `spi_gclk`, GPIO descriptors, pinctrl, DMAengine, PM runtime, SPI tracepoints, and OF compatible `atmel,at91rm9200-spi`.

## Risks
Chip-select behavior has many hardware erratum workarounds, including dummy transfers for polarity changes with GPIO CS. The native-CS-for-GPIO check appears inverted: it errors when `native_cs_free` is nonzero. PDC and DMA cleanup paths are complex and sensitive to overrun. Resume manually initializes hardware with clocks temporarily enabled before returning to runtime PM state. FIFO thresholds and byte counts must match bits-per-word exactly.

## Test Signals
Test PIO FIFO and non-FIFO, DMA, and PDC hardware where available; CS GPIO and native CS polarity; bits-per-word 8 to 16; word delays; transfer timeouts and overruns; suspend/resume/runtime autosuspend; vmalloc DMA bounce paths on SAM V4/V5; and multi-transfer messages with `cs_change`.
