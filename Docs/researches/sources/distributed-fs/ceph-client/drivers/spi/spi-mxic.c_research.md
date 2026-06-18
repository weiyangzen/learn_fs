<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-mxic.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-mxic.c

## Purpose

`spi-mxic.c` is the Macronix MX25F0A SPI controller driver. It supports ordinary SPI transfers, SPI-MEM operations, direct-mapped linear read/write windows, octal/DDR features, swap16 data handling, per-operation frequency changes, and optional pipelined NAND ECC integration through the Macronix ECC engine.

## Important APIs, Types, and Functions

`struct mxic_spi` stores device, clocks, register base, current speed, optional linear mapping, and ECC wrapper state. Clock helpers are `mxic_spi_clk_enable()`, `mxic_spi_clk_disable()`, `mxic_spi_clk_setup()`, and `mxic_spi_set_freq()`. Hardware setup is performed by `mxic_spi_hw_init()`, while operation encoding uses `mxic_spi_prep_hc_cfg()` and `mxic_spi_mem_prep_op_cfg()`.

Manual FIFO exchange is in `mxic_spi_data_xfer()`. SPI-MEM callbacks are `mxic_spi_mem_supports_op()`, `mxic_spi_mem_exec_op()`, `mxic_spi_mem_dirmap_create()`, `mxic_spi_mem_dirmap_read()`, and `mxic_spi_mem_dirmap_write()`. Standard SPI callbacks are `mxic_spi_set_cs()` and `mxic_spi_transfer_one()`. ECC wrappers register a pipelined on-host engine using `mxic_spi_mem_ecc_probe()` and delegate NAND ECC operations to `mxic_ecc_get_pipelined_ops()`.

## Control Flow

Probe obtains clocks and MMIO resources, maps an optional direct-map resource, enables runtime PM, fills controller callbacks and mode bits, initializes the hardware, optionally registers the pipelined ECC engine unless probe defers, and registers the SPI controller.

For ordinary transfers, `transfer_one` sets frequency, derives bus width from device mode and transfer direction, programs the slave control register, exchanges bytes through the TX/RX data registers, and finalizes the transfer.

For SPI-MEM `exec_op`, the driver sets per-operation clock, configures host control for manual chip select, enables the controller, programs the operation descriptor for the selected chip, asserts CS, writes command and address bytes, clocks dummy bytes, transfers data in the requested direction, deasserts CS, and disables the controller. Direct-map reads/writes configure linear-read or linear-write registers, map the requested range into the controller's linear aperture, optionally invoke pipelined ECC processing, otherwise copy to/from IO memory, then disable linear mode and wait for disable status.

## State and Persistence Behavior

`cur_speed_hz` caches clock programming to avoid redundant clock-rate changes. The optional `linear` mapping stores IO and bus addresses for direct-map operations. ECC state records whether a pipelined configuration is active and holds the registered engine. Hardware registers retain mode, linear, interrupt, and host-control settings only while the device is active; runtime suspend disables clocks.

No host persistence is used. External flash state is modified by upper-layer SPI-MEM operations.

## Dependencies and Integration Points

The driver integrates with SPI, SPI-MEM, runtime PM, platform resources named `regs` and optional `dirmap`, clocks `ps_clk`, `send_clk`, and `send_dly_clk`, MTD NAND ECC APIs, and Macronix ECC helpers. It advertises DTR, ECC, swap16, per-op frequency, dual/quad/octal modes, and one chip select.

## Risks and Edge Cases

Direct-map read/write clamps `len` to the linear aperture after programming the requested address and range; callers must handle short returns correctly. `mxic_spi_data_xfer()` polls FIFO bits for every 1-4 byte chunk, so timeout behavior is central. The ordinary transfer path has limited full-duplex support and rejects certain asymmetric dual/quad combinations. ECC registration ignores non-deferral errors and continues without ECC, which is acceptable only if upper layers can operate without it.

Runtime PM enables `auto_runtime_pm`, but hardware initialization is done before registration and clocks must be valid when registers are accessed.

## Test Signals

Tests should include STR and DTR SPI-MEM commands, single/dual/quad/octal widths, command/address/dummy/data combinations, manual CS behavior, direct-map read and write with short aperture clamping, per-op frequency changes, runtime suspend/resume, ECC-pipelined NAND read/write requests, operation timeout injection, and probe paths with absent direct-map resource and deferred ECC engine.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-mxic.c -->
