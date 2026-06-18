# sources/distributed-fs/ceph-client/drivers/spi/spi-armada-3700.c

## Purpose
Marvell Armada 3700 SPI host driver for FIFO and full-duplex non-FIFO transfers. It supports multiple native chip selects from DT, mode 3, 8/32 bpw, and single, dual, or quad transfer lane flags.

## Important APIs, Types, and Functions
`struct a3700_spi` stores controller, MMIO base, clock, IRQ, buffer cursors, byte length, wait mask, and completion. Register helpers are `spireg_read()` and `spireg_write()`. Setup helpers program CS, pin mode, FIFO mode, CPOL/CPHA, clock prescaler, byte length, FIFO thresholds, and headers. Core callbacks are `a3700_spi_prepare_message()`, `a3700_spi_transfer_one()`, `a3700_spi_unprepare_message()`, and `a3700_spi_set_cs()`.

## Control Flow
Probe reads `num-cs`, maps resources, obtains a prepared clock, computes min/max speed, initializes hardware, requests IRQ, and registers the controller. Message preparation enables the clock, flushes FIFOs, and sets SPI mode. A transfer is initialized into `tx_buf`, `rx_buf`, and `buf_len`. Full-duplex uses non-FIFO mode and busy-waits on `XFER_DONE` for each 4-byte or final 1-byte chunk. Half-duplex FIFO mode configures lane width, thresholds, headers for unaligned leading TX bytes, starts read or write mode, then waits on `WFIFO_RDY`, `RFIFO_RDY`, `WFIFO_EMPTY`, and `XFER_RDY` through completion-backed IRQ handling.

## State and Persistence
State is primarily MMIO state plus current buffer cursors. `wait_mask` links the active waiter to the IRQ handler. The clock is enabled only during prepared messages. CS state is held in hardware enable bits and deactivated explicitly.

## Dependencies and Integration Points
It integrates with OF compatible `marvell,armada-3700-spi`, platform IRQ/MMIO, clk, completions, and SPI core transfer callbacks. Lane mode values come from SPI core transfer fields.

## Risks
The wait path clears `wait_mask` before its second status recheck, making that fallback ineffective as written and increasing timeout sensitivity for edge-triggered IRQ races. Full-duplex uses unbounded `cpu_relax()` polling on `XFER_DONE`. Several timeout constants are only 10 ms or 10 loop iterations, so slow hardware may fail. Header-mode unaligned TX handling mutates `buf_len` and `tx_buf`, which must remain tightly coupled to FIFO writes.

## Test Signals
Use IRQ-driven FIFO read/write tests, full-duplex loopback, unaligned transfer lengths, 8 and 32 bpw, dual and quad paths, clock gating through prepare/unprepare, timeout injection, and CS behavior across multi-transfer messages.
