# sources/distributed-fs/ceph-client/drivers/spi/spi-ep93xx.c

## Purpose
Implements a SPI controller driver for Cirrus Logic EP93xx SSP hardware. It supports GPIO-described chip selects, 4- to 16-bit words, interrupt-driven PIO, optional DMA for larger transfers, and controller clock prepare/unprepare hooks.

## Important APIs, Types, And Functions
`struct ep93xx_spi` stores clock, MMIO base, SSPDR physical address, byte counters, FIFO occupancy, DMA channels, scatter tables, and a zero page for dummy TX/RX. Setup and data functions include `ep93xx_spi_calc_divisors()`, `ep93xx_spi_chip_setup()`, `ep93xx_do_write()`, `ep93xx_do_read()`, and `ep93xx_spi_read_write()`. DMA is handled by `ep93xx_spi_dma_prepare()`, `ep93xx_spi_dma_finish()`, `ep93xx_spi_dma_callback()`, and `ep93xx_spi_dma_transfer()`. Lifecycle functions are `ep93xx_spi_probe()` and `ep93xx_spi_remove()`.

## Control Flow
Probe allocates a SPI host, configures callbacks and mode/word masks, gets the clock, maps registers, requests IRQ, attempts DMA setup, disables hardware, and registers the controller. Each transfer configures divisors/mode, resets counters, and selects DMA when RX DMA exists and length exceeds FIFO depth. PIO primes TX FIFO and enables RX/TX/overrun interrupts. The ISR handles overrun as `-EIO`, otherwise drains RX and fills TX until complete, then disables interrupts and finalizes the transfer. DMA maps page-sized scatter chunks for both directions, uses a zero page when one side has no buffer, starts RX and TX DMA, and finalizes when RX completes.

## State And Persistence
Transfer state lives in `host->cur_msg->state`, `tx`, `rx`, and `fifo_level`. DMA scatter tables are reused between transfers and freed on remove. Hardware is enabled only during prepared transfer hardware. No persistent storage is used.

## Dependencies And Integration Points
Depends on platform resources, clk, IRQ, DMAengine, scatterlists, SPI core, and OF compatible `cirrus,ep9301-spi`. It relies on SPI core transfer finalization and GPIO descriptor chip-select support.

## Risks
PIO FIFO accounting must remain exact to avoid RX overruns. DMA uses `virt_to_page()` over client buffers, so assumptions about buffer mapping are important. The DMA callback finalizes on RX completion and assumes TX completion has also become harmless. Timeout while flushing stale RX FIFO blocks message preparation.

## Test Signals
PIO transfers at 4/8/16 bits, DMA and PIO fallback, TX-only/RX-only dummy-buffer paths, RX overrun injection, divisor boundary rates, DMA probe defer, remove after DMA allocation, and FIFO flush timeout are useful tests.
