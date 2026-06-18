# sources/distributed-fs/ceph-client/drivers/spi/spi-cavium-thunderx.c

## Purpose

`spi-cavium-thunderx.c` is the PCI front-end for Cavium ThunderX SPI controllers. It adapts the shared OCTEON-style Cavium SPI transfer core to a PCI BAR register layout and clock source.

## Important APIs, Types, and Functions

`thunderx_spi_probe()` allocates a host, enables the PCI device with managed helpers, requests BAR regions, maps BAR 0, fills ThunderX register offsets, gets/enables an optional unnamed clock, computes `sys_freq` with fallback to 700 MHz, configures controller capabilities, and registers the controller. `thunderx_spi_remove()` unregisters and clears the hardware config register. The PCI ID table matches Cavium vendor ID device `0xa00b`.

## Control Flow

Probe initializes the shared `struct octeon_spi` but with offsets `0x1000`, `0x1008`, `0x1010`, and `0x1080`. It sets `SPI_CONTROLLER_HALF_DUPLEX`, four chip selects, CPHA/CPOL/CS-high/LSB-first/3-wire mode bits, 8-bit words, 16 MHz maximum speed, and `octeon_spi_transfer_one_message()` as the message engine. On any failure before registration it releases the host; managed PCI resources handle device cleanup.

## State and Persistence Behavior

Per-controller state consists of BAR mapping, clock pointer, system frequency, register offsets, and shared-core transfer cache such as `last_cfg` and `cs_enax`. Remove writes zero to the configuration register to leave hardware disabled. There is no file-backed persistence or runtime PM.

## Dependencies and Integration Points

The file integrates with Linux PCI, managed PCI resource APIs, clocks, the SPI controller core, and the shared `spi-cavium` transfer implementation. Hardware integration is through BAR 0 and the ThunderX register offset convention.

## Risks and Edge Cases

If the clock provider returns a zero rate, the driver silently falls back to 700 MHz; incorrect fallback frequency affects baud divisor calculation in the shared core. The controller is marked half-duplex, but the shared core can fill both TX and RX buffers in a transfer cycle, so integration expectations should be checked. Like the OCTEON front-end, there is no interrupt, runtime PM, or dynamic CS count discovery.

## Test Signals

Tests should cover PCI enable/request/map failures, missing or zero-rate clock, registration failure cleanup, supported mode advertisement, half-duplex behavior through SPI core validation, and remove-time hardware disable. Shared Cavium transfer tests should run against the ThunderX register offsets.
