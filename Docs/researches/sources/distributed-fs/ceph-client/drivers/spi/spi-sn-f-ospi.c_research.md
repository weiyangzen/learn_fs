# sources/distributed-fs/ceph-client/drivers/spi/spi-sn-f-ospi.c

## Purpose

`spi-sn-f-ospi.c` is a SPI memory controller driver for Socionext F_OSPI flash hardware. It implements `spi_mem` indirect operations for single, dual, quad, and octal bus widths, with per-operation frequency support, but it does not implement interrupt-driven or DMA data movement.

## Important APIs, Types, and Functions

`struct f_ospi` holds MMIO base, device, clock, and a mutex protecting configuration and transfers. Configuration helpers include `f_ospi_prepare_config()`, `f_ospi_unprepare_config()`, `f_ospi_config_clk()`, `f_ospi_get_mode()`, and `f_ospi_config_indir_protocol()`. Transfer helpers are `f_ospi_indir_read()`, `f_ospi_indir_write()`, `f_ospi_indir_start_xfer()`, `f_ospi_indir_stop_xfer()`, and `f_ospi_indir_wait_xfer_complete()`.

The `spi_controller_mem_ops` table provides `adjust_op_size`, `supports_op`, and `exec_op`. Probe uses `devm_spi_alloc_host()`, maps registers, enables the clock, initializes hardware via `f_ospi_init()`, and registers the controller.

## Control Flow

Each indirect operation locks the controller, stops the internal clock and waits until AXI is idle/SPI clock stopped, programs the requested clock divisor, chip select, command/address/data bus widths, bit order, sample edge, data unit size, direction, address size, dummy cycles, address, opcode, and relevant IRQ status bits, then restarts the internal clock. Read starts the transfer and polls `READ_BUF_READY` for each byte, reading from `OSPI_DAT`; write polls `WRITE_BUF_READY` and writes one byte at a time. No-data writes start and then wait for transaction completion. Completion is detected by polling `CS_TRANS_COMP`, then the status bit is cleared.

## State and Persistence Behavior

There is no persistent storage. Controller state is hardware register configuration protected by `mlock`. Probe disables boot signal mode and all IRQ status/output bits; transfers program protocol state per operation. The device clock is acquired enabled and is not runtime-managed.

## Dependencies and Integration Points

The driver depends on platform device resources, device tree compatible `socionext,f-ospi`, clocks, MMIO polling, mutexes, and `spi_mem`. It advertises up to four chip selects and per-operation frequency capability.

## Risks and Edge Cases

The timeout constants are named in milliseconds but passed as the timeout argument to `readl_poll_timeout()`, whose timeout is in microseconds; this makes several waits much shorter than the names imply. Data movement is byte-at-a-time despite data-unit programming, which may be correct for the FIFO contract but limits throughput. `FIELD_PREP()` is used with single-bit data-rate masks and zero values, which is harmless but easy to misread. Unsupported directions only warn in lower helpers; `exec_op` returns `-EOPNOTSUPP` for unknown directions. Address sizes over four bytes and dummy cycles over 255 are rejected.

## Test Signals

Validate `spi_mem` opcode/address/dummy/data combinations for 1-1-1, dual, quad, and octal widths; all chip selects; per-operation clock rates; no-data commands; reads/writes at `OSPI_DAT_SIZE_MAX`; address nbytes rejection; dummy-cycle rejection; and poll timeout behavior with hardware stalled in AXI-active, clock-stopped, buffer-ready, and transaction-complete states.
