# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_devio_spi.c

## Purpose
Adapts the generic CXD2880 register I/O abstraction to the chip's SPI command protocol.

## Important APIs, Types, and Functions
`cxd2880_io_spi_create()` installs SPI-backed `read_regs`, `write_regs`, and `write_reg` callbacks into `struct cxd2880_io`. Static helpers `cxd2880_io_spi_read_reg()` and `cxd2880_io_spi_write_reg()` encode commands. `BURST_WRITE_MAX` limits writes to 128 payload bytes.

## Control Flow
Read validates arguments and 8-bit address range, chooses command `0x0b` for SYS or `0x0a` for DMD, then loops in chunks up to 255 bytes through `spi->write_read()`. Write validates size and address range, chooses `0x0f` for SYS or `0x0e` for DMD, appends an extra dummy byte for SYS writes, and calls `spi->write()`.

## State and Persistence
`cxd2880_io_spi_create()` stores the SPI backend pointer, slave select, and zeroes unused I2C address fields. Runtime register state is in hardware.

## Dependencies and Integration Points
Depends on `struct cxd2880_spi` callbacks and generic `cxd2880_io` users in tuner/demod code. It bridges bus-level SPI access to register-bank operations.

## Risks and Edge Cases
Write rejects sizes above 128 despite loop code supporting chunking; callers must split larger sequences. `sub_address + size > 0x100` protects only 8-bit register windows. Missing `spi->write_read` or `spi->write` callback would crash because the helper only checks `io->if_object`.

## Test Signals
SPI trace should show the expected command bytes for SYS/DMD reads and writes, address wrap rejection, 255-byte read chunking, 128-byte write limit, and correct propagation of transport errors.
