# sources/distributed-fs/ceph-client/drivers/spi/spi-cs42l43.c

## Purpose

`spi-cs42l43.c` is the SPI controller driver for the Cirrus Logic CS42L43 MFD. It exposes an internal register-controlled SPI master, supports half-duplex transfers through regmap FIFOs, and can create sidecar CS35L56 amplifier devices based on ACPI/firmware-node information.

## Important APIs, Types, and Functions

`struct cs42l43_spi` holds device, regmap, and SPI controller pointers. Data movement uses `cs42l43_spi_tx()` and `cs42l43_spi_rx()` to write/read 16-byte FIFO blocks through regmap and handshake status bits. `cs42l43_transfer_one()` sets clock divider, configures read/write length, starts transfer, and calls the relevant FIFO helper. `cs42l43_prepare_message()`, `cs42l43_set_cs()`, `cs42l43_prepare_transfer_hardware()`, and `cs42l43_unprepare_transfer_hardware()` configure mode, CS, and block enable. Probe handles controller allocation, PM, FIFO thresholds, firmware-node selection, sidecar GPIO/software-node setup, registration, and optional child amp creation.

## Control Flow

Probe obtains parent `struct cs42l43`, allocates driver state and a host, wires regmap and callbacks, sets half-duplex mode and 8/16/32-bit word caps, enables runtime PM, programs FIFO sizes and stall/watchdog settings, chooses an OF `spi` child node or ACPI function-expansion node, clears the controller fwnode, optionally creates a software node with CS GPIO references and speaker-id property, registers the controller, and, for sidecars, creates left/right `cs35l56` SPI devices.

A transfer chooses the first divider whose root/divided frequency is not above `tfr->speed_hz`, programs read or write mode and length-minus-one register, starts the transaction, then streams FIFO blocks. TX writes packed little-endian words and signals TX done per block. RX polls for RX request, reads words, unpacks bytes, then signals RX done.

## State and Persistence Behavior

The driver persists controller regmap settings, runtime PM enablement, firmware/software-node associations, and optional child SPI devices while probed. Transfer state is local. Persistent side effects are register changes in the parent MFD and creation of child devices; attached amplifier/device state changes happen through SPI clients.

## Dependencies and Integration Points

It integrates with the CS42L43 MFD/regmap, runtime PM, GPIO descriptors, GPIO software nodes, ACPI and OF firmware nodes, property APIs, and the SPI core. It imports the `GPIO_SWNODE` namespace. Sidecar support uses `cs35l56` board info and speaker-id properties from ACPI or GPIOs.

## Risks and Edge Cases

Probe allocates the host with `sizeof(*priv->ctlr)` rather than zero/private data size and then separately calls `spi_controller_set_devdata()`, which wastes memory and should be reviewed. `cs42l43_transfer_one()` returns `-EINVAL` for full-duplex transfers and for speeds below the slowest divider, but only implicitly through missing TX/RX handling or divider loop. Regmap write return values are often ignored in setup paths. Firmware-node lifetime and software-node references are subtle, especially when `nsidecars` is nonzero and the controller node is cleared.

## Test Signals

Tests should cover OF and ACPI probe paths, no-sidecar and sidecar configurations, speaker-id from ACPI and GPIOs, software-node creation failure, controller registration failure, 8/16/32-bit TX and RX, unsupported full-duplex transfer rejection, clock divider boundary speeds, FIFO block lengths including 16-byte multiples and remainders, runtime PM enable/idle, and child amplifier creation failure handling.
