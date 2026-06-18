# sources/distributed-fs/ceph-client/drivers/spi/spi-cavium-octeon.c

## Purpose

`spi-cavium-octeon.c` is the platform front-end for Cavium OCTEON MPI SPI controllers. It binds OF platform devices, maps OCTEON register space, supplies OCTEON-specific register offsets and clock rate, and delegates actual transfer execution to the shared Cavium core in `spi-cavium.c`.

## Important APIs, Types, and Functions

The driver uses shared `struct octeon_spi` from `spi-cavium.h`. `octeon_spi_probe()` allocates a SPI host, maps the first platform memory resource, sets `sys_freq` from `octeon_get_io_clock_rate()`, installs MPI register offsets, configures controller capabilities, and registers the host. `octeon_spi_remove()` unregisters the controller and writes zero to the configuration register to clear CS enable bits.

## Control Flow

On probe, the driver allocates host-private `struct octeon_spi`, stores the platform drvdata, maps MMIO, initializes offsets for config/status/tx/data, advertises four chip selects and mode support for CPHA, CPOL, CS-high, LSB-first, and 3-wire, sets 8-bit-only transfers and 16 MHz maximum speed, points `transfer_one_message` at `octeon_spi_transfer_one_message()`, and registers the controller. Remove unregisters, then leaves hardware in a disabled state.

## State and Persistence Behavior

The file owns no complex persistent state. It initializes `register_base`, `sys_freq`, and offset values that persist for the life of the host. Hardware configuration is reset to zero on remove. SPI device-visible state is created by the shared core during transfers.

## Dependencies and Integration Points

It depends on platform devices, OF matching, OCTEON architecture support for `octeon_get_io_clock_rate()`, MMIO accessors, and the shared `spi-cavium` core. The compatible string is `cavium,octeon-3010-spi`.

## Risks and Edge Cases

This front-end assumes the OCTEON architecture helper is available and that the register layout starts at offsets 0, 0x08, 0x10, and 0x80. It has no runtime PM, clock gating, or IRQ support. Registering fixed four chip selects may mismatch unusual hardware descriptions. Cleanup uses a controller reference get/put pattern around unregister, so lifetime expectations should remain aligned with SPI core behavior.

## Test Signals

Probe tests should validate MMIO mapping failure, host allocation failure, controller registration failure, OF matching, and the reported mode/bits/speed caps. Runtime tests should use the shared Cavium transfer tests for CS handling, chunking, and polling, then confirm remove writes zero to the config register.
