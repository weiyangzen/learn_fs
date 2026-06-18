# sources/distributed-fs/ceph-client/drivers/spi/spi-sun4i.c

## Purpose

`spi-sun4i.c` is the Allwinner A10/A20 SPI host controller driver. It implements interrupt-driven PIO transfers for 8-bit words with manual chip select, CPOL/CPHA, CS-high, LSB-first, runtime PM clock gating, and a 64-byte FIFO.

## Important APIs, Types, and Functions

`struct sun4i_spi` stores the SPI controller, MMIO base, AHB/module clocks, completion, and current TX/RX buffer state. Register helpers wrap `readl()`/`writel()`. FIFO helpers `sun4i_spi_fill_fifo()` and `sun4i_spi_drain_fifo()` move bytes to/from hardware. SPI hooks are `sun4i_spi_set_cs()`, `sun4i_spi_transfer_one()`, and `sun4i_spi_max_transfer_size()`. `sun4i_spi_handler()` handles transfer complete, RX FIFO 3/4 full, and TX FIFO 3/4 empty interrupts. Probe maps resources, requests IRQ, gets clocks, initializes runtime PM, and registers the host.

## Control Flow

Runtime resume enables AHB and module clocks and sets master/TX-pause defaults. `set_cs` selects the chip, enables manual CS, sets the requested level, and updates inactive polarity. A transfer rejects lengths beyond the 24-bit hardware counter, clears interrupts, resets FIFOs, programs mode bits, enables/disables discard-hash-burst for TX-only, enables the controller, adjusts the module clock if necessary, chooses CDR2 or CDR1 divider, programs burst/transmit counts, preloads up to FIFO depth minus one, enables TC and RX FIFO interrupts plus TX FIFO interrupt when needed, starts exchange, and waits with a computed timeout. The IRQ drains/fills FIFO and completes on TC.

## State and Persistence Behavior

State is volatile and per-controller. Runtime PM gates clocks while idle. Transfer-specific buffer pointers and remaining length live in `struct sun4i_spi`. Hardware registers are reprogrammed on each transfer and clocks are disabled during runtime suspend.

## Dependencies and Integration Points

The driver depends on platform/OF matching (`allwinner,sun4i-a10-spi`), clocks named `ahb` and `mod`, MMIO, IRQs, completions, runtime PM, GPIO descriptors, and the SPI core. It advertises four chip selects and max transfer size one less than the 24-bit counter maximum.

## Risks and Edge Cases

The timeout calculation divides by `tfr->speed_hz / 1000`; speeds below 1000 Hz would divide by zero, though the controller advertises a 3 kHz minimum. `platform_get_irq()` errors are collapsed to `-ENXIO`, losing deferral details. `clk_set_rate()` return value is ignored when trying to raise module clock. On timeout, interrupts are disabled but the exchange bit or FIFO state is not explicitly reset until a later transfer. RX-only transfers use zero-filled TX bytes from `sun4i_spi_fill_fifo()`, which is expected for SPI but should be tested.

## Test Signals

Test all mode bits, manual CS levels and inactive polarity, RX-only/TX-only/full-duplex transfers, lengths around FIFO depth and maximum counter, low/high speed divisor selection, module clock rate adjustment failure, timeout handling, runtime suspend/resume, missing clocks/IRQ, and interrupt sequencing where RX FIFO and TC arrive close together.
