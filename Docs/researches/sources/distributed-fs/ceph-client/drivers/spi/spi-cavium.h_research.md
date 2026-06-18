# sources/distributed-fs/ceph-client/drivers/spi/spi-cavium.h

## Purpose

`spi-cavium.h` is the shared private header for Cavium OCTEON and ThunderX SPI drivers. It defines common driver state, controller limits, register-offset access macros, the shared transfer callback prototype, and 64-bit MPI register bitfield layouts used by the shared core.

## Important APIs, Types, and Functions

`struct octeon_spi_regs` stores offsets for config, status, TX, and data registers. `struct octeon_spi` stores the mapped register base, cached configuration, accumulated CS enable bits, system frequency, offsets, and optional clock pointer. Macros `OCTEON_SPI_CFG()`, `OCTEON_SPI_STS()`, `OCTEON_SPI_TX()`, and `OCTEON_SPI_DAT0()` access those offsets. Constants include `OCTEON_SPI_MAX_BYTES` and `OCTEON_SPI_MAX_CLOCK_HZ`.

The header declares `octeon_spi_transfer_one_message()`. It also defines legacy OCTEON physical MPI register addresses and unions `cvmx_mpi_cfg`, `cvmx_mpi_datx`, `cvmx_mpi_sts`, and `cvmx_mpi_tx` with endian-specific bitfields and SoC-family variants.

## Control Flow

The header is not executable by itself. Front-ends fill `struct octeon_spi` with a register base, register offsets, and frequency, then install `octeon_spi_transfer_one_message()` as the controller callback. The shared core uses the bitfield unions to build hardware config and TX command words, poll status, and move byte data through DAT registers.

## State and Persistence Behavior

The state described here lives for the lifetime of a probed controller. `last_cfg` and `cs_enax` persist across transfers and influence whether the core rewrites config registers and which CS enable bits stay active. The union definitions model hardware register state but do not persist data outside the controller.

## Dependencies and Integration Points

The header depends on kernel clock types and SPI controller declarations from inclusion context. It integrates front-end drivers with the shared Cavium transfer core and exposes OCTEON MPI register fields for big-endian and little-endian bitfield layouts.

## Risks and Edge Cases

The union register layouts rely on compiler bitfield ordering and `__BIG_ENDIAN_BITFIELD`; mismatches would corrupt hardware programming. Several SoC-family variants are present but the shared core mostly uses the generic `.s` views, so variant-specific missing fields may matter on older OCTEON parts. The legacy `CVMX_ADD_IO_SEG` addresses assume OCTEON architecture definitions when used.

## Test Signals

Compile tests should include relevant endianness and architecture configurations. Layout-sensitive changes should be checked against hardware manuals or register-unit tests where possible. Runtime tests should validate that platform and PCI front-ends fill offsets correctly and that shared-core config bits map to expected CPOL/CPHA/CS/clock behavior.
