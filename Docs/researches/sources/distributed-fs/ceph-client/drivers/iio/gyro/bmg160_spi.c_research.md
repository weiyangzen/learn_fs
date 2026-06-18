# sources/distributed-fs/ceph-client/drivers/iio/gyro/bmg160_spi.c

## Purpose
SPI transport shim for BMG160-compatible gyroscopes.

## Important APIs, Types, And Functions
Defines SPI regmap config, `bmg160_spi_probe`, `bmg160_spi_remove`, SPI/OF match tables, and a `spi_driver` with shared PM ops.

## Control Flow
Probe obtains SPI ID, initializes a SPI regmap, and delegates to `bmg160_core_probe` with SPI IRQ and ID name. Remove calls `bmg160_core_remove`.

## State And Persistence
No transport-owned runtime state aside from the devm regmap.

## Dependencies And Integration Points
Depends on SPI, REGMAP_SPI, BMG160 core exports, and OF/SPI IDs for BMG160/BMI055/BMI088.

## Risks
Probe assumes `spi_get_device_id` returns non-NULL and dereferences `id->name`. Regmap access flags are generic; any SPI read/write flag requirements must be represented by regmap defaults or future config updates.

## Test Signals
Build/probe via SPI IDs and OF compatibles, verify IRQ propagation to the core, exercise core sysfs and buffered paths over SPI, and test remove.
