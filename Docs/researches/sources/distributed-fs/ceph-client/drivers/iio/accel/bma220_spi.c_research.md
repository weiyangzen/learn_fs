# sources/distributed-fs/ceph-client/drivers/iio/accel/bma220_spi.c

## Purpose

`bma220_spi.c` is the SPI wrapper for the BMA220 core. It creates a SPI regmap and delegates all sensor behavior to `bma220_common_probe()`.

## Important APIs, Types, and Functions

`bma220_spi_probe()` initializes the SPI regmap with `bma220_spi_regmap_config` and calls the common core with `spi->irq`. The file also declares SPI ID, ACPI ID `BMA0220`, and OF compatible tables.

## Control Flow

Probe is linear: create regmap, return a dev_err_probe failure if regmap init fails, otherwise call the common probe. The common core handles regulators, reset, triggers, PM, and IIO registration.

## State and Persistence Behavior

No wrapper-private state or hardware policy is stored in this file.

## Dependencies and Integration Points

It depends on SPI, regmap, module tables, ACPI/OF matching, shared PM ops, and `IIO_BOSCH_BMA220` namespace import.

## Risks

The SPI regmap config's read flag and writable-register constraints are owned by the core; wrapper regressions are mostly matching or regmap-init related. Formatting oddities in `.probe` and `.id_table` assignments are cosmetic.

## Test Signals

Tests should bind by SPI ID, OF, and ACPI IDs, verify common-probe invocation, direct register reads with SPI read flag bit 7, IRQ-triggered buffering, and PM suspend/resume.
