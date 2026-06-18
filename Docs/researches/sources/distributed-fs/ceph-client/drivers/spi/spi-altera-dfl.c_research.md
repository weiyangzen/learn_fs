# sources/distributed-fs/ceph-client/drivers/spi/spi-altera-dfl.c

## Purpose

`spi-altera-dfl.c` is a Device Feature List bus wrapper for the shared Altera SPI core. It supports FPGA DFL features where an Altera SPI master is accessed through an indirect register window, commonly connected to Intel MAX BMC SPI devices.

## Important APIs, types, and functions

- `indirect_bus_reg_read()` and `indirect_bus_reg_write()` implement regmap callbacks over the DFL indirect-access registers with busy polling and `INDIRECT_TIMEOUT`.
- `indirect_regbus_cfg` describes a 32-bit regmap backed by those callbacks.
- `config_spi_host()` reads `SPI_CORE_PARAMETER` and derives mode bits, chipselect count, and bits-per-word mask.
- `dfl_spi_altera_probe()` allocates the SPI controller, maps DFL MMIO, creates the indirect regmap, initializes the shared core, registers the controller, and instantiates a board-info SPI device (`m10-n5010` or `m10-d5005`).

## Control flow

Probe maps the DFL resource, reads controller parameters, initializes a regmap whose operations issue indirect read/write commands, sets `hw->irq = -EINVAL` for polling mode, calls `altera_spi_init_host()`, and registers the controller. After controller registration it creates a MAX10 SPI device on chip select 0 with a 12.5 MHz max speed.

## State and persistence behavior

Software state is device-managed and tied to the DFL device. Hardware state persists in the indirect SPI registers and DFL feature MMIO. The wrapper does not implement remove-specific cleanup beyond devm and module DFL driver teardown.

## Dependencies and integration points

The file depends on the FPGA DFL bus, regmap, SPI framework, `linux/spi/altera.h`, and the exported core functions from `spi-altera-core.c`. It matches DFL feature ID `0xe` under `FME_ID`.

## Risks and edge cases

- Indirect read/write loops use `cpu_relax()` with a fixed loop count rather than time-based polling.
- The wrapper forces polling mode by setting a negative IRQ.
- `board_info.bus_num = 0` is hard-coded even though the controller uses `host->bus_num = -1`; this deserves validation on systems with multiple SPI buses.
- Failure to create the child SPI device is logged but does not fail probe.

## Test signals

Build with `CONFIG_FPGA_DFL` and `CONFIG_SPI_ALTERA_DFL`. Runtime tests on DFL hardware should verify indirect read/write timeouts, parameter-derived chipselect and bit-width limits, creation of the expected MAX10 device name by revision, and polling transfers through the shared core.
