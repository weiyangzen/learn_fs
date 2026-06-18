# sources/distributed-fs/ceph-client/drivers/input/misc/ad714x-spi.c

## Purpose

This SPI transport driver connects Analog Devices AD714x capacitive touch controllers to the shared AD714x core. It formats AD714x SPI command words, performs big-endian register transfers, and delegates input/device setup to the common core.

## Important APIs, Types, and Functions

`AD714x_SPI_CMD_PREFIX` and `AD714x_SPI_READ` define the command word format. `ad714x_spi_read()` builds a two-transfer SPI message: command transmit followed by receive of `len` 16-bit words, then converts received data from big-endian. `ad714x_spi_write()` sends command and data words in one `spi_write()`. `ad714x_spi_probe()` sets `bits_per_word = 8`, calls `spi_setup()`, then calls `ad714x_probe()` with `BUS_SPI`, IRQ, and callbacks.

## Control Flow

SPI probe configures the bus word size, then delegates to the shared AD714x core. Core register reads invoke the command+receive message path; writes invoke the two-word write path. Driver registration uses `module_spi_driver()` with driver name `ad714x_captouch`.

## State and Persistence Behavior

The transport layer persists only the shared chip pointer in SPI driver data. Transfers use the common chip transfer buffer, with receive data starting at `xfer_buf[1]` because `xfer_buf[0]` holds the command.

## Dependencies and Integration Points

It depends on the SPI core, AD714x shared core, `ad714x_pm` sleep ops, input bus identity `BUS_SPI`, and the SPI device's IRQ. Unlike the I2C file, no explicit SPI ID or OF table is present here.

## Risks and Edge Cases

`spi_write()` and `spi_sync()` return errors, but the code does not validate actual transferred lengths. Buffer sizing must account for command plus maximum read length. Forcing `bits_per_word = 8` may override board-specified settings. Missing ID/OF tables can limit module autoload depending on how devices are instantiated.

## Test Signals

Test SPI setup failure, command word encoding for read/write, endian conversion, multiword reads, transfer error injection, buffer length limits, IRQ propagation to the shared core, PM suspend/resume, and device autoload paths for board-described SPI devices.
