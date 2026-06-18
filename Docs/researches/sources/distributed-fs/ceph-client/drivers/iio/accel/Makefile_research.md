# sources/distributed-fs/ceph-client/drivers/iio/accel/Makefile

Purpose: Kbuild object list for IIO accelerometer drivers.

Important entries: this subset maps `CONFIG_ADIS16201` to `adis16201.o`, `CONFIG_ADIS16209` to `adis16209.o`, `CONFIG_ADXL313` to `adxl313_core.o`, `CONFIG_ADXL313_I2C/SPI` to bus glue objects, `CONFIG_ADXL345` to `adxl345_core.o`, `CONFIG_ADXL345_I2C/SPI`, `CONFIG_ADXL355` to `adxl355_core.o`, and `CONFIG_ADXL355_I2C/SPI`. It also lists the remaining accelerometer drivers alphabetically and composes `st_accel-y` from ST core/buffer pieces.

Control flow: Kconfig symbols directly control object inclusion. Shared core objects are built when hidden core symbols are selected by a frontend.

State and persistence: no runtime state; the file is build metadata.

Dependencies and integration: pairs with `drivers/iio/accel/Kconfig`, Linux Kbuild, regmap-based frontend/core splits, and IIO sensor modules.

Risks: Makefile/Kconfig drift can produce selected symbols with no object, or objects with no reachable symbol. Alphabetical ordering is the local maintenance convention and helps avoid duplicate entries.

Test signals: module builds for each accelerometer symbol, link checks for namespace imports/exports, and allmodconfig coverage of core plus transport object combinations.
