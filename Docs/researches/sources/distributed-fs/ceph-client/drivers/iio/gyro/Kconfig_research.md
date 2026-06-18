# sources/distributed-fs/ceph-client/drivers/iio/gyro/Kconfig

## Purpose
Kconfig menu for IIO digital gyroscope drivers. It defines user-visible driver choices and hidden bus helper symbols for SPI, I2C, HID sensor hub, Samsung SSP, ST, ADIS, Bosch, NXP, InvenSense, and Analog Devices gyroscopes.

## Important APIs, Types, And Functions
Important symbols include `ADIS16080`, `ADIS16130`, `ADIS16136`, `ADIS16260`, `ADXRS290`, `ADXRS450`, `BMG160`, `BMG160_I2C`, `BMG160_SPI`, `FXAS21002C`, `FXAS21002C_I2C`, `FXAS21002C_SPI`, `HID_SENSOR_GYRO_3D`, `MPU3050`, `MPU3050_I2C`, `IIO_ST_GYRO_3AXIS`, `IIO_ST_GYRO_I2C_3AXIS`, `IIO_ST_GYRO_SPI_3AXIS`, and `ITG3200`.

## Control Flow
The menu gates compilation by bus and subsystem dependencies. Composite drivers select hidden transport symbols when the relevant bus is available, while ADIS, HID, and triggered-buffer-capable drivers select their helper libraries.

## State And Persistence
Kconfig selections persist in kernel build configuration and determine which objects and modules are built. No runtime state is stored here.

## Dependencies And Integration Points
Integrates with SPI, SPI_MASTER, I2C, I2C_MUX, SYSFS, HID_SENSOR_HUB, REGMAP, REGMAP_I2C, REGMAP_SPI, IIO_BUFFER, IIO_TRIGGERED_BUFFER, IIO_ADIS_LIB, IIO_ADIS_LIB_BUFFER, IIO_ST_SENSORS_CORE/I2C/SPI, and HID sensor common trigger support.

## Risks
Hidden bus helper symbols are selected from parent choices, so dependency mistakes can silently omit transport modules. The `BMG160` and `FXAS21002C` parent symbols select both bus shims when both buses are enabled, increasing module surface. `MPU3050` is hidden and depends on `MPU3050_I2C` for user selection.

## Test Signals
Run Kconfig dependency checks with common allmodconfig/allnoconfig fragments, verify expected modules are emitted from matching Makefile rules, and test that enabling each visible option pulls in its required regmap, buffer, and transport support.
