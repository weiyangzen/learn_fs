# sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-helper-spi.c

## Purpose
Connects generic packet helper initialization to SPI4 interfaces and optional SPI4000 devices.

## Important APIs, Types, And Functions
Functions are `__cvmx_helper_spi_enumerate()`, `__cvmx_helper_spi_probe()`, `__cvmx_helper_spi_enable()`, `__cvmx_helper_spi_link_get()`, and `__cvmx_helper_spi_link_set()`.

## Control Flow
Enumerate/probe return ten ports for SPI4000 and sixteen otherwise. Generic SPI enables PKO CRC insertion. Enable turns on IPD CRC checking for each port, starts the SPI interface in duplex mode, initializes SPI4000 if present, and enables SPI/GMX interrupts. Link get returns simulated/generic 10 Gbps or decodes SPI4000 in-band speed.

## State, Persistence, And Dependencies
State is in PKO CRC, PIP, SPI, and GMX CSRs. It depends on SPI4000 detection and the lower-level `cvmx-spi.c` training pipeline.

## Integration Points
Called by `cvmx-helper.c` for SPI mode after common IPD/PKO setup.

## Risks
Generic SPI assumes link up with no external status. Misdetecting SPI4000 changes CRC behavior. Lower-level start failures are not deeply surfaced here.

## Test Signals
Verify port count, CRC behavior, SPI training success, SPI4000 speed decode, and SPX/STX interrupt responses.
