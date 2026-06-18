# sources/distributed-fs/ceph-client/drivers/spi/spi-sun6i.c

## Purpose
`spi-sun6i.c` is the Linux SPI controller driver for Allwinner sun6i/sun8i/sun50i style SPI host blocks. It registers a `spi_controller` for device-tree matched SoCs, programs the controller registers for chip select, mode, clocking, FIFO thresholds, burst counters, and optional dual/quad transfer widths, and supports both interrupt-driven FIFO transfers and DMA transfers for messages larger than the controller FIFO.

## Important APIs, Types, And Functions
The central state type is `struct sun6i_spi`, which holds the `spi_controller`, MMIO base, DMA FIFO addresses, AHB/module clocks, reset control, completions, active tx/rx pointers, remaining length, and SoC config. `struct sun6i_spi_cfg` captures FIFO depth, whether the block has the older clock divider register, and extra `mode_bits`.

Key SPI callbacks are `sun6i_spi_set_cs()`, `sun6i_spi_transfer_one()`, `sun6i_spi_can_dma()`, and `sun6i_spi_max_transfer_size()`. Probe and lifecycle entry points are `sun6i_spi_probe()`, `sun6i_spi_remove()`, `sun6i_spi_runtime_resume()`, and `sun6i_spi_runtime_suspend()`. Low-level helpers `sun6i_spi_read()`, `sun6i_spi_write()`, `sun6i_spi_drain_fifo()`, and `sun6i_spi_fill_fifo()` encapsulate MMIO and FIFO movement.

## Control Flow
Probe allocates a controller, maps the register resource, requests the IRQ, reads match data, wires SPI callbacks, obtains clocks and reset, optionally requests `tx` and `rx` DMA channels, resumes the hardware, enables runtime PM autosuspend, and registers the controller. Transfer setup clears interrupts, resets FIFOs, chooses interrupt or DMA thresholds, programs SPI mode bits, manual chip select, RX discard for TX-only transfers, clock divisors or sample mode, transfer counters, and single/dual/quad burst control. For PIO it primes the TX FIFO and then uses transfer-complete, RX-ready, and TX-empty interrupts. For DMA it prepares scatter-gather DMA descriptors and waits for both controller completion and RX DMA completion when needed.

`sun6i_spi_handler()` first handles transfer complete and completes `done`; otherwise it drains RX FIFO on `RF_RDY` or fills TX FIFO on `TF_ERQ`, disabling TX-empty interrupts once no TX bytes remain. Timeout handling disables interrupts and terminates DMA channels on failed DMA transfers.

## State And Persistence
The driver keeps only runtime hardware state. Active transfer pointers and lengths live in `struct sun6i_spi` and are reinitialized per transfer. Hardware state is reset through FIFO reset bits, interrupt status writes, clock/divider configuration, and reset-controller/runtime-PM transitions. There is no persistent on-disk state.

## Dependencies And Integration Points
The file integrates with the SPI core, platform bus, OF matching, Linux clk/reset frameworks, runtime PM, IRQ handling, and DMAengine. It exposes device-tree compatible strings for Allwinner A31, H3, R329, and A523-like controllers. GPIO chip selects are supported through `use_gpio_descriptors`; native chip select is programmed in the transfer-control register.

## Risks
DMA is enabled only when both channels are present; partial DMA availability falls back to PIO but still needs careful cleanup on probe deferral. Clock programming differs by `has_clk_ctl`, so wrong match data can produce invalid sampling. Dual/quad support is limited to configs that advertise those mode bits. Timeout paths terminate DMA but do not fully reset the controller beyond disabling interrupts, so persistent hardware wedging would depend on later transfer setup and runtime PM recovery. FIFO count assumptions are explicitly noted for A523-compatible hardware.

## Test Signals
Useful tests include small transfers at and below FIFO depth, large DMA transfers, RX-only/TX-only/full-duplex transfers, timeout/error injection, runtime suspend/resume across transfers, chip-select polarity and GPIO CS tests, and dual/quad SPI transfers on `sun50i-r329`-style match data. Kernel logs from timeout warnings, DMA preparation warnings, and missing DMA channel warnings are the primary runtime diagnostics.
