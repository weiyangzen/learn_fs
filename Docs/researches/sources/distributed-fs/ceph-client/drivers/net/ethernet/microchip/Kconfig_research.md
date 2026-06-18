# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/Kconfig

## Purpose

This Kconfig file defines the top-level configuration menu for Microchip Ethernet drivers under `drivers/net/ethernet/microchip`. It gates the vendor menu with `NET_VENDOR_MICROCHIP` and exposes selectable driver symbols for SPI Ethernet controllers, PCI Ethernet devices, and several switch/VCAP/FDMA subdirectories.

## Important Symbols

`NET_VENDOR_MICROCHIP` is a boolean vendor selector defaulting to `y`; disabling it hides nested Microchip questions. `ENC28J60` is a tristate SPI Ethernet controller driver and selects `CRC32`. `ENC28J60_WRITEVERIFY` is a debug bool dependent on `ENC28J60`. `ENCX24J600` is a tristate SPI driver for ENC424J600/624J600 devices. `LAN743X` is a PCI driver symbol that depends on `PCI` and `PTP_1588_CLOCK_OPTIONAL`, selecting `FIXED_PHY`, `CRC16`, `CRC32`, and `PHYLINK`.

## Control Flow, State, And Dependencies

Kconfig selection is declarative and persists in `.config`. Enabled symbols feed the local Makefile through `CONFIG_*` values. Dependencies include `SPI`, `PCI`, optional PTP clock support, CRC helpers, fixed PHY, phylink, and nested Kconfig files for `lan865x`, `lan966x`, `sparx5`, `vcap`, and `fdma`.

## Risks And Test Signals

The main risk is drift between Kconfig symbols and Makefile object rules. `ENC28J60_WRITEVERIFY` changes compiled driver behavior by adding writeback checks. Test signals are `make olddefconfig`, menu visibility checks, allmodconfig, and targeted builds for each symbol and sourced subdirectory.
