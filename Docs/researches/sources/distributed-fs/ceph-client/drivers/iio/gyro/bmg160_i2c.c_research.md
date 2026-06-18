# sources/distributed-fs/ceph-client/drivers/iio/gyro/bmg160_i2c.c

## Purpose
I2C transport shim for BMG160-compatible gyroscopes.

## Important APIs, Types, And Functions
Defines an 8-bit regmap config, `bmg160_i2c_probe`, `bmg160_i2c_remove`, ACPI/I2C/OF match tables, and an `i2c_driver` using shared `bmg160_pm_ops`.

## Control Flow
Probe initializes an I2C regmap, chooses the IIO name from I2C ID or ACPI name, and delegates to `bmg160_core_probe` with client IRQ. Remove delegates to `bmg160_core_remove`.

## State And Persistence
No local device state beyond devm regmap allocation and driver data set by the core.

## Dependencies And Integration Points
Depends on I2C, REGMAP_I2C, BMG160 core exports, ACPI ID `BMG0160`, I2C IDs, and OF compatibles for BMG160/BMI055/BMI088.

## Risks
If neither I2C ID nor ACPI name is available, the core name can be NULL. Bus-specific regmap max register must stay aligned with core register use.

## Test Signals
Build as module, probe via I2C/ACPI/OF names, verify regmap init failure path, IRQ forwarding, PM ops attachment, and clean remove.
