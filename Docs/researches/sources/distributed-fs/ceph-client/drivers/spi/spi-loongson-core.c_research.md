# sources/distributed-fs/ceph-client/drivers/spi/spi-loongson-core.c

## Purpose

`spi-loongson-core.c` implements the shared Loongson SPI controller logic used by both PCI and platform frontends. It registers the SPI controller, performs byte-at-a-time FIFO transfers, manages chip-selects, mode, clock dividers, and suspend/resume state.

## Important APIs, Types, And Functions

The shared state is `struct loongson_spi` from `spi-loongson.h`. Core helpers are `loongson_spi_write_reg()`, `loongson_spi_read_reg()`, `loongson_spi_set_cs()`, `loongson_spi_set_clk()`, `loongson_spi_set_mode()`, `loongson_spi_update_state()`, `loongson_spi_write_read_8bit()`, `loongson_spi_write_read()`, and `loongson_spi_reginit()`. Exported entry points are `loongson_spi_init_controller()` and `loongson_spi_dev_pm_ops`.

## Control Flow, State, And Persistence

Frontends pass a mapped register base to `loongson_spi_init_controller()`. The core allocates a devm SPI host, sets mode/setup/prepare/transfer/unprepare/set_cs hooks, reads an optional clock, initializes the hardware, and registers the controller. Message preparation saves and clears `PARA.MEM_EN`; unprepare restores it, keeping SPI transfers from colliding with memory-style controller mode. Transfers update speed/mode if cached values differ, then loop one byte at a time by writing FIFO, polling `SPSR.RFEMPTY` with a 1 ms timeout, and reading FIFO.

Suspend stores SPCR/SPER/SPSR/PARA/SFCS/TIMI and resumes by restoring them before resuming the controller. This is volatile hardware state only.

## Dependencies And Integration Points

The core depends on SPI core, clocks, MMIO byte access, and polling helpers. It exports symbols in namespace `SPI_LOONGSON_CORE` for `spi-loongson-pci.c` and `spi-loongson-plat.c`.

## Risks And Test Signals

Risks include byte-at-a-time polling latency, `mode` cache accumulation via OR instead of exact assignment, divider table assumptions, and timeout behavior when RFEMPTY never clears. Test with all SPI modes, CS polarity, multiple chipselects, suspend/resume register restoration, and transfer timeout injection.
