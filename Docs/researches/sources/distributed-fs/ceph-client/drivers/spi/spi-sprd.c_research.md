# sources/distributed-fs/ceph-client/drivers/spi/spi-sprd.c

## Purpose

`spi-sprd.c` is the Spreadtrum SPI host controller driver for `sprd,sc9860-spi`. It supports PIO and DMA transfers, CPOL/CPHA, 3-wire mode, dual TX line mode, runtime PM, and FIFO-length chunking.

## Important APIs, Types, and Functions

`struct sprd_spi` stores MMIO/physical base, clock, IRQ, source/hardware speed, transfer mode, word delay, current buffers, DMA state, and completion. `struct sprd_spi_dma` tracks RX/TX DMA channels, bus width, fragment length, and RX length. Setup and transfer are split across `sprd_spi_setup_transfer()`, `sprd_spi_init_hw()`, `sprd_spi_txrx_bufs()` for PIO, and `sprd_spi_dma_txrx_bufs()` for DMA. Buffer accessors handle 8-, 16-, and 32-bit words. IRQ handling completes DMA transfers and reads any RX tail not covered by DMA.

## Control Flow

Probe allocates a SPI host, maps registers, initializes clocks, IRQ, and optional DMA, enables runtime PM, resumes the controller, and registers it. `transfer_one` records buffers, configures hardware mode, speed, bits per word, transfer length, RX/TX mode, word delay, FIFO reset, and then chooses DMA when available and transfer length exceeds the 32-byte FIFO. PIO transfers loop in FIFO-sized chunks, set TX or RX length registers, write TX data or trigger receive-only mode, poll TX/RX completion, read RX FIFO, and enter idle. DMA transfers enable interrupts, configure TX and/or RX DMA descriptors, program length registers, enable DMA, wait for completion, then disable DMA/IRQs and enter idle.

## State and Persistence Behavior

State is volatile per-controller runtime state plus hardware registers. Runtime suspend releases DMA channels and disables the enable clock; runtime resume re-enables the clock and reacquires DMA channels when DMA was enabled. There is no file-backed persistence.

## Dependencies and Integration Points

The driver depends on platform resources, OF aliasing, clocks named `spi`, `source`, and `enable`, DMAengine with Spreadtrum DMA flags, IRQs, completions, runtime PM, and the SPI core. It registers `set_cs`, `transfer_one`, and `can_dma`.

## Risks and Edge Cases

`sctlr->max_speed_hz` is set before `sprd_spi_clk_init()` initializes `ss->src_clk`, so the advertised max speed can be based on zero. `sprd_spi_clk_init()` calls `clk_set_parent(clk_spi, clk_parent)` even if optional clock lookups failed and set those pointers to NULL; that relies on clock API tolerance. DMA wait has no timeout. Runtime suspend releases DMA channels while `ss->dma.enable` remains true, then resume reacquires them; error handling for later transfers after failed reacquire depends on runtime PM returning failure. Transfer length conversions for 16/32-bit frames use right shifts, so invalid odd byte lengths are not explicitly rejected.

## Test Signals

Exercise PIO and DMA transfers above/below FIFO size, RX-only, TX-only, full duplex, 3-wire TX/RX, dual TX line mode, 8/16/32-bit frames including unaligned lengths, word-delay units and clamp bounds, DMA tail RX handling, runtime suspend/resume with DMA channel loss, missing optional clocks, and IRQ timeout/hang scenarios.
