# sources/distributed-fs/ceph-client/drivers/spi/spi-sh.c

## Purpose

`spi-sh.c` is an older SuperH SPI controller driver using FIFO registers, one IRQ, waitqueues, and whole-message transfer callbacks. It supports two chip selects, 8-bit or 32-bit register access depending on resource flags, TX and RX transfers, and simple setup/cleanup.

## Important APIs, Types, and Functions

`struct spi_sh_data` stores MMIO base, IRQ, SPI host, cached CR1 interrupt/status bits, waitqueue, and register width. Register helpers abstract 8-bit resources using shifted offsets versus 32-bit resources. Core helpers are bit set/clear, `clear_fifo()`, `spi_sh_wait_receive_buffer()`, `spi_sh_wait_write_buffer_empty()`, `spi_sh_send()`, `spi_sh_receive()`, `spi_sh_transfer_one_message()`, setup/cleanup, IRQ handler, probe, and remove.

## Control Flow

Probe validates memory resource and IRQ, allocates a devm SPI host, determines 8-bit or 32-bit MMIO access from resource flags, maps registers, initializes the waitqueue, requests the IRQ, sets two chip selects, installs setup/transfer/cleanup hooks, and registers the controller. Setup stops the cycle, clears CR1/CR3, resets FIFO, and programs a fixed 1/8 clock setting.

Message transfer clears SSA, then for each transfer calls `spi_sh_send()` when TX data exists and `spi_sh_receive()` when RX data exists. TX asserts SSA, fills up to 32 FIFO bytes, waits for TX buffer empty IRQ when more remains, handles write-protect abort, and on final transfer waits for TX completion before deasserting. RX programs byte count, asserts receive mode, waits for TX empty, waits for RX FIFO-full interrupts for large chunks, reads FIFO bytes, and resets CR3/FIFO for long transfers. The IRQ handler mirrors CR1 status bits into `ss->cr1`, clears enabled interrupt bits in CR4, and wakes the waitqueue.

## State and Persistence Behavior

State is volatile: MMIO register values, waitqueue status bits, FIFO contents, IRQ registration, and fixed setup clock bits. There is no persistence. Attached devices own any nonvolatile side effects.

## Dependencies and Integration Points

The driver depends on platform resources with `IORESOURCE_MEM_8BIT` or `IORESOURCE_MEM_32BIT`, IRQs, MMIO, waitqueues, and SPI core legacy `transfer_one_message`. It does not use DMA, runtime PM, OF match data, or clock framework.

## Risks and Edge Cases

The error path in `spi_sh_transfer_one_message()` calls `spi_finalize_current_message()` and then calls `mesg->complete` manually if present, which risks double completion depending on SPI core behavior. TX final wait checks `if (ret == 0 && (ss->cr1 & SPI_SH_TBE))`, which appears inverted relative to the earlier timeout pattern and may miss timeout reporting. `msg->actual_length` is incremented by full transfer length after send/receive success but partial progress inside helpers is not reported. Fixed clock setup ignores requested transfer speed and mode beyond the hard-coded divisor. Remove unregisters the controller then frees the manually requested IRQ.

## Test Signals

Test 8-bit and 32-bit resource widths, TX-only/RX-only/sequential TX+RX messages, long transfers above FIFO size and `SPI_SH_MAX_BYTE`, write-protect abort, timeout paths for TX and RX waits, final-transfer CS deassertion, cleanup state, double-completion behavior under injected errors, and registration failure cleanup.
