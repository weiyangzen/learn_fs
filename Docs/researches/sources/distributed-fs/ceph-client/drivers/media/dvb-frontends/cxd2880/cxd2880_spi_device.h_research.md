# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_spi_device.h

## Purpose
Declares the Linux SPI-device transport wrapper for CXD2880.

## Important APIs, Types, and Functions
`struct cxd2880_spi_device` stores `struct spi_device *spi`. Declares `cxd2880_spi_device_initialize()` and `cxd2880_spi_device_create_spi()`.

## Control Flow
No executable flow. Users initialize the Linux SPI device settings and then create the generic SPI callback wrapper.

## State and Persistence
The wrapper stores the external SPI device pointer; it does not own the SPI device.

## Dependencies and Integration Points
Includes the generic CXD2880 SPI header. Used by frontend attach/probe code to bridge kernel SPI to the demod register layer.

## Risks and Edge Cases
Prototype parameter `speedHz` differs in style from the implementation's `speed_hz`, but type/order match. Lifetime of the wrapped SPI device is external.

## Test Signals
Compile-time prototype matching and runtime attach/remove tests proving no stale `spi_device` pointer remains after frontend teardown.
