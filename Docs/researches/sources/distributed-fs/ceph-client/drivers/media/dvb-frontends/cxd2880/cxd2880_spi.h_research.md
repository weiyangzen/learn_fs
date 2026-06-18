# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_spi.h

## Purpose
Defines a small SPI transport abstraction for the CXD2880 driver.

## Important APIs, Types, and Functions
`enum cxd2880_spi_mode` maps modes 0 through 3. `struct cxd2880_spi` contains optional `read`, required write/write-read callbacks for this driver, `flags`, and a transport-owned `user` pointer.

## Control Flow
No executable flow. Bus-specific code fills callbacks and higher layers invoke them through `cxd2880_devio_spi.c`.

## State and Persistence
`flags` and `user` persist per transport object. The header does not define flag bits.

## Dependencies and Integration Points
Implemented by `cxd2880_spi_device.c` using Linux SPI APIs and consumed by the register I/O SPI adapter.

## Risks and Edge Cases
The `read` callback is present but not used by the current register protocol. Callers must validate callback availability before use or rely on constructor invariants.

## Test Signals
Create transport objects for each SPI mode and verify write/write-read callback invocation through register I/O commands.
