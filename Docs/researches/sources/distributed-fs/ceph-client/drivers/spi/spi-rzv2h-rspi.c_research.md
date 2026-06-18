# sources/distributed-fs/ceph-client/drivers/spi/spi-rzv2h-rspi.c

## Purpose

`spi-rzv2h-rspi.c` is a newer Renesas RSPI controller driver for RZ/V2H(P), RZ/G3L/G3E, RZ/T2H, and RZ/N2H-style hardware. It supports host-mode SPI with 4 to 32 bits per word, PIO and DMA, multiple clock-source selection algorithms, hardware resets, and four chip selects.

## Important APIs, Types, and Functions

`struct rzv2h_rspi_info` describes SoC-specific clock search functions, TCLK name, FIFO size, and clock count. `struct rzv2h_rspi_priv` stores the SPI controller, matched info, MMIO base, TCLK/PCLK, waitqueue, bytes-per-word, RX IRQ, cached requested/effective frequency, selected SPR/BRDV divisors, PCLK use flag, and DMA completion flag.

Important functions include register RMW helpers, FIFO clear and IRQ clear helpers, `rzv2h_rx_irq_handler()`, PIO send/receive helpers, `rzv2h_rspi_transfer_dma()`, `rzv2h_rspi_transfer_one()`, clock calculators `rzv2h_rspi_find_rate_fixed()` and `rzv2h_rspi_find_rate_variable()`, `rzv2h_rspi_setup_clock()`, message prepare/unprepare, and probe.

## Control Flow

Probe allocates a host controller, maps registers, gets all clocks and identifies TCLK plus optional PCLK by name, deasserts `presetn` and `tresetn`, requests the RX IRQ, declares mode and bits-per-word capabilities, computes minimum speed from the rounded TCLK, optionally requests DMA channels, and registers the controller.

`prepare_message()` disables SPE before changing configuration, scans message transfers for the minimum speed and bits-per-word, computes `bytes_per_word`, recalculates divisors only when requested speed changes, writes SPBR, SPCR, SPPCR, SPCMD, SSLP, and FIFO thresholds, clears FIFOs, then enables SPE. `transfer_one()` sets the effective speed, computes word count, uses DMA when the SPI core mapped the transfer for DMA, otherwise loops through PIO send/receive with IRQ waits, clears IRQ state, and requests a PIO retry when DMA setup returns `-EAGAIN`. `unprepare_message()` disables SPE.

## State and Persistence Behavior

State is volatile: selected clock source/rate/divisors, cached last requested speed, interrupt status, DMA completion, and bytes-per-word. The reset lines and clocks are device resources. There is no persistent host-side storage; persistent effects belong to attached SPI devices.

## Dependencies and Integration Points

The driver integrates with OF match data, clock bulk APIs, reset controls, DMAengine, waitqueues, interrupts, and SPI core DMA mapping. SoC-specific match data selects fixed or variable TCLK/PCLK search behavior and FIFO thresholds.

## Risks and Edge Cases

`prepare_message()` derives `bits_per_word` from the last transfer examined; mixed bits-per-word messages may not be represented correctly. The generated `rzv2h_rspi_rx_u8()` helper uses `readl` for an 8-bit destination, which is suspicious even if the register tolerates 32-bit reads. DMA requires both TX and RX channels and always prepares both directions, matching the controller's `MUST_RX|MUST_TX` flags. PIO waits rely on RX IRQ setting `rspi->status`; stale status is cleared around transfers but IRQ loss produces HZ timeouts. Fixed-rate search rejects SPR=0/BRDV=0 due to hardware restrictions.

## Test Signals

Test all matched SoCs, fixed and variable clock selection, PCLK fallback, speed-boundary requests around 50 MHz and prohibited divisors, 4/8/16/24/32-bit words, mixed transfer messages, PIO vs DMA fallback, missing one DMA channel, RX IRQ timeout, reset acquisition failures, active-high CS, loopback, and transfer after repeated prepare/unprepare cycles.
