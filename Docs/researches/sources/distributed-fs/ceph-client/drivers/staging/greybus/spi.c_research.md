# sources/distributed-fs/ceph-client/drivers/staging/greybus/spi.c

## Purpose
Provides the small Greybus PHY wrapper for the SPI protocol. It binds `GREYBUS_PROTOCOL_SPI` devices, creates a Greybus connection, and delegates Linux SPI controller registration to the shared Greybus SPI library in `spilib.c`.

## Important APIs, Types, and Functions
`gb_spi_probe()` creates and enables the CPort connection, calls `gb_spilib_master_init(connection, &gbphy_dev->dev, spilib_ops)`, stores the connection in gbphy driver data, and drops runtime PM autosuspend. `gb_spi_remove()` resumes the gbphy if needed, calls `gb_spilib_master_exit()`, disables the connection, and destroys it. `spi_driver` is a `gbphy_driver` registered by `module_gbphy_driver()`.

## Control Flow, State, and Integration
This file keeps no per-device state beyond the `gb_connection *` stored with `gb_gbphy_set_data()`. All protocol translation, controller config, device enumeration, and transfers live in `spilib.c`. The optional `spilib_ops` pointer is currently NULL, so no board-specific prepare/unprepare hooks are installed.

## Risks and Test Signals
The wrapper is simple, so main risks are cleanup ordering and runtime PM balance when `gb_spilib_master_init()` fails after connection enable. Test by probing a Greybus SPI interface, verifying controller/device creation from `spilib.c`, then removing and ensuring the connection and registered SPI controller disappear cleanly.
