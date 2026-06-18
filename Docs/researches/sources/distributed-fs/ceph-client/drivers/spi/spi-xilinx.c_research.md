<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-xilinx.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-xilinx.c

## Purpose

`spi-xilinx.c` is a host-mode driver for older Xilinx OPB/AXI SPI IP blocks. It uses the Linux `spi_bitbang` framework with custom chip-select, setup, and buffer transfer routines that drive the controller FIFO directly, optionally using the controller's TX-empty interrupt for long transfers.

The driver supports platform data and device-tree configuration, up to 32 chip selects, selectable endian register access, CPOL/CPHA, LSB-first, loopback, and fixed hardware-configured SPI clock.

## Important APIs, Types, and Functions

`struct xilinx_spi` embeds `struct spi_bitbang` first, then stores completion, register base, IRQ, force-IRQ flag, TX/RX pointers, bytes per word, detected FIFO size, inactive chip-select mask, and endian-specific register access functions.

Register definitions cover the SPI control/status/TX/RX/slave-select registers and IPIF global interrupt, interrupt status/enable, and reset registers. Interrupt masks include TX empty and several errors that should not occur in host-only operation.

Endian helpers are `xspi_read32()`, `xspi_write32()`, `xspi_read32_be()`, and `xspi_write32_be()`. Data helpers are `xilinx_spi_tx()` and `xilinx_spi_rx()`. Hardware setup and discovery are `xspi_init_hw()` and `xilinx_spi_find_buffer_size()`.

SPI bitbang hooks are `xilinx_spi_chipselect()`, `xilinx_spi_setup_transfer()`, and `xilinx_spi_txrx_bufs()`. `xilinx_spi_irq()` completes long interrupt-assisted transfers. Probe and remove are `xilinx_spi_probe()` and `xilinx_spi_remove()`.

## Control Flow

Probe reads platform data or device properties for chip-select count, bits per word, and optional forced IRQ mode. It validates chip-select count, allocates a SPI host, initializes bitbang hooks, maps registers, detects register endianness by writing and reading the loopback control bit, sets `bytes_per_word`, detects FIFO size by resetting and writing until TX full, optionally requests an IRQ, initializes hardware, and starts the bitbang controller.

Chip select updates the control register mode bits from the SPI device and writes the slave-select register. The inactive CS mask is updated during setup based on `SPI_CS_HIGH`, and activation toggles the target bit from that inactive mask.

Transfers begin with the transmitter inhibited. The driver sets TX/RX pointers and computes remaining words. If an IRQ exists and either forced or the transfer exceeds FIFO size, it inhibits transmission, clears stale IPIF interrupts, enables global interrupt, and waits on a completion for TX empty. Otherwise it polls status.

For each chunk, it fills the TX FIFO up to detected FIFO capacity, releases inhibit to start transfer, waits for completion or polls status, inhibits again in IRQ mode, then drains RX FIFO for the same number of words. A stall detector resets hardware and fails if TX does not empty and RX remains empty for repeated reads at the start of a chunk.

Remove stops the bitbang controller and disables IPIF interrupts.

## State and Persistence Behavior

The driver stores volatile controller state only: detected endian accessors, FIFO capacity, inactive chip-select mask, transfer pointers, completion state, and IRQ mode. Hardware registers are reset and initialized at probe and after detected stalls.

No file-backed state is used. SPI target devices may persist changes made by transfers. The SPI clock is not programmable by this driver because it is fixed by IP block design parameters.

## Dependencies and Integration Points

The driver depends on platform bus, optional platform data (`struct xspi_platform_data`), device tree compatibles for Xilinx AXI/XPS SPI, MMIO, IRQs, completions, and `spi_bitbang`.

It integrates with legacy board files by instantiating platform-data `spi_board_info` devices after controller start, and with device tree through `xlnx,num-ss-bits` and `xlnx,num-transfer-bits`.

## Risks and Edge Cases

TX/RX word access casts user buffers to `u16 *` or `u32 *` without unaligned helpers, so unaligned buffers on strict-alignment architectures may fault for 16-bit or 32-bit word sizes.

FIFO size detection writes zeros until TX full after reset. If status behavior is unexpected, the detected size can be wrong and later chunking can overrun hardware assumptions.

Interrupt mode waits without a timeout. If TX-empty interrupt is lost, a transfer can hang. Poll mode has a stall detector, but IRQ wait lacks an equivalent timeout.

The driver assumes host-only mode and does not handle mode fault, underrun, or overrun interrupts beyond ignoring them. Hardware or wiring faults may be hard to diagnose.

## Test Signals

Tests should cover little- and big-endian register access, device-tree and platform-data probe, valid and invalid chip-select counts, bits-per-word values 8/16/32 as configured, all mode bits, CS high/low inactive masks, FIFO-size detection, short poll transfers, long IRQ transfers, forced IRQ mode, TX-only/RX-only/full-duplex, and stall recovery.

Static analysis should inspect unaligned access risks and no-timeout IRQ waits. Fault injection should cover missing IRQ, stale IPIF interrupt status, register mapping failure, and `spi_bitbang_start()` failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-xilinx.c -->
