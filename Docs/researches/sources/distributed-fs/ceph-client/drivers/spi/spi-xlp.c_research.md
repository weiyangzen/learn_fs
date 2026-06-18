<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-xlp.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-xlp.c

## Purpose

`spi-xlp.c` is a platform SPI controller driver for Broadcom/Netlogic XLP-family hardware, matched through ACPI IDs. It registers a four-chip-select SPI host using interrupt-completed FIFO transfers and splits each SPI transfer into hardware-safe chunks of at most 28 bytes.

The driver supports CPOL, CPHA, CS high, per-device speed divisor programming, and basic TX, RX, and full-duplex operation.

## Important APIs, Types, and Functions

`struct xlp_spi_priv` contains MMIO base, current TX/RX pointers and lengths, TX underflow/RX overflow counters, selected chip select, clock rate, command-continuation flag, device copy for logging, and a completion.

Register definitions cover per-chip-select config, frequency divisor, command, status, interrupt enable, FIFO threshold/count, TX/RX FIFOs, and global system control. Important limits are `XLP_SPI_FIFO_SIZE`, `XLP_SPI_MAX_CS`, divisor min/max, and `XLP_SPI_XFER_SIZE` of 28 bytes.

Hardware helpers are `xlp_spi_reg_read()`, `xlp_spi_reg_write()`, `xlp_spi_sysctl_write()`, and `xlp_spi_sysctl_setup()`. SPI setup is `xlp_spi_setup()`, FIFO access is `xlp_spi_fill_txfifo()` and `xlp_spi_read_rxfifo()`, and interrupt handling is `xlp_spi_interrupt()`.

Transfer orchestration uses `xlp_spi_send_cmd()`, `xlp_spi_xfer_block()`, `xlp_spi_txrx_bufs()`, and `xlp_spi_transfer_one()`. Probe maps resources, requests IRQ, reads the SPI clock, allocates/registers the controller, and initializes system control.

## Control Flow

Probe allocates private memory, maps the controller registers, requests the platform IRQ, obtains the SPI clock, allocates a SPI host, assigns four chip selects, setup and transfer callbacks, initializes the completion, attaches private data, resets/enables all SPI channels through `XLP_SPI_SYSCTRL`, and registers the controller.

`xlp_spi_setup()` computes a divisor from controller clock and requested device speed, clamps it to hardware limits, writes FIFO thresholds, and updates config bits for CPHA, CPOL, CS polarity, LSB-first, MOSI/MISO enable, and RX capture for minimum divisor.

`transfer_one()` records the chip select and device, sets `cmd_cont` depending on whether this transfer is the last in the current SPI message, calls `xlp_spi_txrx_bufs()`, finalizes the current transfer, and returns an error if any chunk failed.

`xlp_spi_txrx_bufs()` loops over the transfer length in 28-byte blocks. Each block sets TX/RX pointers and lengths, preloads TX FIFO, writes a command word with TX/RX mode, continuation bit, and bit count, enables RX/TX/done/error interrupts, and waits up to one second for completion. The ISR refills TX FIFO, drains RX FIFO, counts underflow/overflow, clears interrupt status, and completes the wait on transfer-done.

## State and Persistence Behavior

All state is volatile. Per-device persistent hardware programming includes divisor and mode bits in each chip-select register after setup. Per-transfer state lives in private TX/RX pointers, lengths, error counters, selected CS, and completion.

The driver does not store data durably. SPI target devices can persist writes performed through the controller.

## Dependencies and Integration Points

The driver depends on platform devices, ACPI matching (`BRCM900D`, `CAV900D`), clocks, MMIO, IRQs, completions, and SPI controller APIs. It does not use device tree matching in this file.

SPI integration uses controller `setup` and `transfer_one`, `spi_transfer_is_last()` for chip-select continuation, and `spi_finalize_current_transfer()` after synchronous completion.

## Risks and Edge Cases

`struct xlp_spi_priv` contains a full `struct device dev` and `transfer_one()` assigns `xspi->dev = spi->dev`. Copying `struct device` by value is unusual and can be unsafe because devices contain embedded state, locks, and references. Logging should normally use a `struct device *`.

`xlp_spi_txrx_bufs()` returns `bytesleft`, which is zero on success. `transfer_one()` treats any nonzero return as error, so success works, but the helper does not return the transferred byte count like many SPI helpers. Future changes could misinterpret this contract.

The driver waits for completion with a one-second timeout per 28-byte chunk; large transfers can take many seconds if hardware repeatedly times out. Underflow/overflow errors are logged but do not make `xlp_spi_xfer_block()` fail if transfer-done arrived.

FIFO packing/unpacking reverses byte order within each 32-bit FIFO word. This may be hardware-required, but tests must verify byte order for non-multiple-of-four transfers.

## Test Signals

Tests should cover ACPI probe, clock absence, IRQ request failure, divisor clamp at min/max, all supported mode bits, four chip selects, TX-only/RX-only/full-duplex transfers, sizes 1..32 bytes, exact 28-byte split, multi-chunk messages with continuation, timeout handling, underflow/overflow status, and byte ordering for 1/2/3/4-byte chunks.

Static review should flag the by-value `struct device` copy and verify error-counter semantics. Runtime stress should queue multiple transfers to different chip selects and speeds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-xlp.c -->
