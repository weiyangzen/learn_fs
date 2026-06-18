<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-zynq-qspi.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-zynq-qspi.c

## Purpose

`spi-zynq-qspi.c` is a SPI memory controller driver for the Xilinx Zynq QSPI controller. It exposes the controller through `spi-mem` operations, supports up to two chip selects, dual/quad mode bits, per-operation frequency, and interrupt-driven FIFO transfer of command, address, dummy, and data phases.

The driver disables linear mode, uses manual chip select, and performs all SPI memory operations through programmed FIFO writes and RX draining.

## Important APIs, Types, and Functions

`struct zynq_qspi` stores device, MMIO base, reference and APB clocks, IRQ, active TX/RX pointers, remaining byte counters, and a completion.

Register definitions cover QSPI config, status/interrupt registers, enable, delay, TX data registers for 1/2/3/4-byte writes, RX data, thresholds, GPIO, linear config, and module ID. Important masks control manual start/select, baud divisor, FIFO width, master mode, RX/TX interrupt bits, linear two-memory mode, upper page, and FIFO thresholds.

Hardware and SPI MEM helpers include `zynq_qspi_init_hw()`, `zynq_qspi_supports_op()`, `zynq_qspi_chipselect()`, `zynq_qspi_config_op()`, `zynq_qspi_setup_op()`, `zynq_qspi_txfifo_op()`, `zynq_qspi_rxfifo_op()`, `zynq_qspi_write_op()`, `zynq_qspi_read_op()`, `zynq_qspi_irq()`, and `zynq_qspi_exec_mem_op()`.

Probe and remove are `zynq_qspi_probe()` and `zynq_qspi_remove()`.

## Control Flow

Probe allocates a SPI host, maps registers, enables `pclk` and `ref_clk`, initializes the completion, requests IRQ, reads optional `num-cs`, validates the two-CS limit, sets SPI MEM callbacks and per-operation-frequency capability, sets max speed to `refclk / 2`, initializes hardware, and registers the controller.

Hardware initialization disables the controller and interrupts, disables linear mode while enabling two-memory mode if more than one chip select exists, drains RX FIFO, clears status, configures master/manual-CS/flash-interface/FIFO-width bits, sets thresholds, and enables the controller.

`supports_op` accepts SPI MEM operations supported by the default helper and rejects address phases longer than three bytes. `exec_mem_op` asserts chip select, configures mode and baud divisor from the SPI device and operation max frequency, then executes command, address, dummy, and data phases sequentially. Each phase sets TX/RX pointers and byte counts, primes TX FIFO, enables RX/TX interrupts, and waits up to one second for completion. Data-in uses dummy zero TX bytes to clock RX data.

The IRQ handler acknowledges status, drains RX when RX-not-empty is set, writes more TX data when TX-not-full indicates room, disables RX/TX interrupts when both counters reach zero, and completes the phase.

Remove unregisters the controller and disables QSPI.

## State and Persistence Behavior

Driver state is volatile: clock handles, MMIO mapping, active buffers/counters, completion, and controller configuration. The hardware retains mode, baud, chip-select page, threshold, and enable bits until changed or disabled.

SPI memory operations can change attached flash contents for program/erase commands, but the driver itself stores no durable state or cache. Two-chip-select systems use the linear config upper-page bit to select lower or upper memory.

## Dependencies and Integration Points

The driver depends on platform/OF resources, clocks named `"pclk"` and `"ref_clk"`, IRQs, MMIO, completions, and SPI MEM. It matches `"xlnx,zynq-qspi-1.0"`.

Integration with SPI NOR occurs through `spi_controller_mem_ops` and `spi_controller_mem_caps.per_op_freq`. Controller setup refuses changes while the SPI core marks the controller busy.

## Risks and Edge Cases

`zynq_qspi_exec_mem_op()` uses `xqspi->txbuf` as scratch storage for address bytes after the command phase, but `xqspi->txbuf` still points at `op->cmd.opcode`, a one-byte field. Writing `op->addr.nbytes` bytes through it is a strong memory corruption risk. It should use a local address buffer.

If an earlier phase times out and sets `err`, later phases still run because the code does not stop after every timeout. This can leave chip select asserted longer and issue partial operations.

The driver allocates a dummy buffer for dummy cycles and returns `-ENOMEM` without deasserting chip select if allocation fails. Similar early returns should be audited for chip-select cleanup.

Only three-byte addresses are supported, so large flashes requiring four-byte address opcodes must use different command forms or fail. Interrupt waits use fixed one-second timeouts per phase rather than transfer-size-derived timeouts.

## Test Signals

Tests should cover probe with one and two chip selects, missing clocks, invalid `num-cs`, all supported SPI MEM phase combinations, address lengths 0..4, command-only operations, read and write data, dummy cycles, dual/quad mode advertisement, per-operation frequency divisors, timeout per phase, and remove disabling hardware.

Static and fault tests should target the address scratch-buffer bug, chip-select cleanup on allocation failure, phase-timeout short-circuiting, RX/TX counter underflow, and interrupt status handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-zynq-qspi.c -->
