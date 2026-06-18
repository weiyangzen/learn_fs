# sources/distributed-fs/ceph-client/drivers/gnss/Kconfig

## Purpose
This Kconfig file defines the Linux GNSS receiver subsystem and transport or chipset drivers for serial and USB GNSS devices.

## Important Entries
`GNSS` builds the core `gnss` module. `GNSS_SERIAL` is a hidden helper selected by `GNSS_MTK_SERIAL` and `GNSS_UBX_SERIAL`. Concrete drivers are `GNSS_MTK_SERIAL`, `GNSS_SIRF_SERIAL`, `GNSS_UBX_SERIAL`, and `GNSS_USB`, with dependencies on `SERIAL_DEV_BUS` or `USB`.

## Control Flow and State
There is no runtime control flow. Kconfig controls whether the GNSS char-device core and transport drivers are compiled.

## Dependencies and Integration Points
The serial drivers integrate with serdev and device-tree compatible strings. USB support integrates with the USB core.

## Risks and Test Signals
The SiRF driver depends directly on `SERIAL_DEV_BUS` but does not select `GNSS_SERIAL` because it implements its own serial handling. Configuration tests should build each driver alone and in combinations, including module and built-in variants.
