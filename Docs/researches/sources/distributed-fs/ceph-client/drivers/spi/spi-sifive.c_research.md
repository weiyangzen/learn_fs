# sources/distributed-fs/ceph-client/drivers/spi/spi-sifive.c

## Purpose

`spi-sifive.c` is the Linux SPI host controller driver for the SiFive SPI IP block in host mode. It exposes the memory-mapped controller through the SPI core, supports up to 32 chip selects, 8-bit words, CPOL/CPHA, active-high chip select, LSB-first ordering, and dual/quad transfer width flags, but it explicitly does not implement sub-8-bit word handling or DMA.

## Important APIs, Types, and Functions

`struct sifive_spi` stores MMIO registers, the bus clock, discovered FIFO depth, inactive CS polarity bitmap, and a completion used by interrupt-driven waits. Register helpers `sifive_spi_read()` and `sifive_spi_write()` wrap `ioread32()`/`iowrite32()`. `sifive_spi_init()` disables watermark interrupts, configures TX/RX watermarks and default delays, and exits flash-specialized mode.

SPI core hooks are `sifive_spi_prepare_message()`, `sifive_spi_set_cs()`, and `sifive_spi_transfer_one()`. `sifive_spi_prep_transfer()` calculates `SCKDIV`, programs frame format/protocol/endianness/direction, and chooses polling versus interrupt wait. `sifive_spi_irq()` handles TX/RX watermark interrupts, disables further interrupts, and completes the waiter. Probe allocates a host, maps registers, enables the clock, reads optional `sifive,fifo-depth` and `sifive,max-bits-per-word`, probes CS lines through `CSDEF`, requests the IRQ, and registers the controller.

## Control Flow

For each message, `prepare_message` updates CS polarity/defaults, selected chip select, and SCK mode. `set_cs` switches hardware CS mode between automatic and hold, with active-high correction. `transfer_one` sets transfer format, then sends data in FIFO-sized chunks. It always requires TX data because the controller is registered with `SPI_CONTROLLER_MUST_TX`; dummy data is supplied by the SPI core when callers provide receive-only transfers. For each chunk it fills TX FIFO, waits for RX watermark when receiving or TX watermark when transmitting only, then drains RX FIFO if applicable.

Probe performs one-time hardware setup and register discovery. Remove unregisters the controller and disables interrupts. System suspend suspends the SPI controller, disables interrupts, and gates the clock; resume re-enables the clock and resumes the SPI controller.

## State and Persistence Behavior

There is no file-backed persistence. Long-lived state is limited to one controller's MMIO base, clock handle, FIFO depth, CS inactive bitmap, and completion. Hardware state persists while powered: programmed delay registers, watermarks, chip select defaults, SCK mode, SCK divisor, and frame format. Suspend disables the clock without fully reinitializing all format registers on resume, relying on future message/transfer setup to rewrite active transfer settings.

## Dependencies and Integration Points

The driver depends on platform devices, device tree matching (`sifive,spi0`), clocks, MMIO accessors, IRQs, completions, and the Linux SPI controller API. It integrates with GPIO chip selects through `SPI_CONTROLLER_GPIO_SS` and disables device DMA by clearing `pdev->dev.dma_mask`.

## Risks and Edge Cases

`sifive_spi_transfer_one()` increments `tx_ptr` unconditionally. Correct operation depends on `SPI_CONTROLLER_MUST_TX` ensuring a valid TX buffer for RX-only transfers. The wait path has no timeout, so lost interrupts or a stuck watermark can hang a transfer. Polling loops are also unbounded. The divisor calculation masks to 12 bits; an unsupported low speed can silently wrap to an unintended faster speed. The dual/quad mode selection uses the max of TX/RX nbits, so mixed-width phases inside a single transfer are not represented.

## Test Signals

Useful tests include probe with explicit and missing FIFO-depth properties, CS line auto-probe, all CPOL/CPHA modes, active-high and GPIO CS, LSB-first transfers, RX-only dummy TX, TX-only, dual/quad advertised transfers, long transfers spanning multiple FIFO chunks, suspend/resume around active devices, and fault injection for missing IRQ, zero clock, and stuck TX/RX watermark conditions.
