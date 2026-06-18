# sources/distributed-fs/ceph-client/drivers/staging/iio/addac/adt7316-spi.c

## Purpose
Provides SPI transport glue for the ADT7316/7/8 and ADT7516/7/9 shared IIO core.

## Important APIs, Types, and Functions
Defines SPI command bytes `ADT7316_SPI_CMD_READ` and `ADT7316_SPI_CMD_WRITE`, a 5 MHz maximum clock, multi-read/write helpers, single-byte wrappers, and `adt7316_spi_probe()`. Probe validates `spi_dev->max_speed_hz`, sends three dummy writes to switch the chip from default I2C protocol to SPI protocol, builds a `struct adt7316_bus`, and calls shared `adt7316_probe()`.

## Control Flow and State
The transport keeps no private state. Multi-read first selects the starting register with a write command, then sends a read command and reads `count` bytes. Multi-write builds a command buffer containing write command, register, and data bytes. Count is clamped to `ADT7316_REG_MAX_ADDR`.

## Dependencies and Integration Points
Depends on Linux SPI APIs, OF/SPI ID tables for all six supported chip names, and shared `adt7316_pm_ops`. The shared core receives `spi_dev->irq` and `spi_dev->modalias` as the name used to infer chip family.

## Risks and Test Signals
Risks include rejecting boards configured above 5 MHz, ignoring errors from the three protocol-switch writes, and relying on modalias string positions in the shared core. Test signals include bus transactions with logic analyzer traces, max clock validation, probe for all IDs, PM suspend/resume, and register read/write failures.
