# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_devio_spi.h

## Purpose
Declares the SPI-backed constructor for the CXD2880 generic I/O interface.

## Important APIs, Types, and Functions
Includes common, I/O, SPI, and tuner-demod headers. Declares `cxd2880_io_spi_create(struct cxd2880_io *io, struct cxd2880_spi *spi, u8 slave_select)`.

## Control Flow
No executable flow. Consumers call the constructor before creating or initializing `struct cxd2880_tnrdmd`.

## State and Persistence
No state in the header. The constructor populates caller-owned `struct cxd2880_io`.

## Dependencies and Integration Points
Connects SPI transport setup to all demod register access. `cxd2880_top.c` and initialization glue depend on this constructor to wire hardware access.

## Risks and Edge Cases
The unused `slave_select` field may imply support not present in the SPI command code. Include cycles should be watched because it includes `cxd2880_tnrdmd.h` though only I/O and SPI types are needed for the prototype.

## Test Signals
Compile users that include only this header plus required kernel SPI/DVB headers. Runtime attach should fail cleanly if construction receives null pointers.
