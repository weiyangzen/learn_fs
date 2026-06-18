# sources/distributed-fs/ceph-client/drivers/iio/accel/Kconfig

Purpose: accelerometer driver menu for IIO. It declares build symbols for many accelerometer families and their bus-specific frontends, with hidden core symbols for shared logic.

Important symbols: this subset centers on `ADIS16201`, `ADIS16209`, `ADXL313`, `ADXL313_I2C`, `ADXL313_SPI`, `ADXL345`, `ADXL345_I2C`, `ADXL345_SPI`, `ADXL355`, `ADXL355_I2C`, and `ADXL355_SPI`. The file also defines Bosch, NXP/Freescale, Kionix, ST, HID sensor, ChromeOS EC, Memsic, Murata, and other accelerometer options. Many bus frontends select `REGMAP_I2C` or `REGMAP_SPI`; buffered drivers select `IIO_BUFFER`, `IIO_TRIGGERED_BUFFER`, or `IIO_KFIFO_BUF`.

Control flow: visible bus-specific options select hidden shared core symbols such as `ADXL313`, `ADXL345`, `ADXL355`, `BMA220`, `BMA400`, or `MMA7455`. Dependencies prevent conflicting or impossible configurations, for example ADXL345 excludes `INPUT_ADXL34X` because compatible IDs are shared.

State and persistence: no runtime state. It controls generated `.config` values and module/built-in selection.

Dependencies and integration: consumed by `drivers/iio/accel/Makefile`. It integrates accelerometer drivers with SPI, I2C, ACPI/HID, regmap, IIO buffers, triggered buffers, and vendor common cores.

Risks: hidden core symbols must be selected by every frontend. Optional I2C/SPI selection patterns can accidentally build unwanted transports if dependencies are too broad. Shared-compatible exclusions must remain accurate to avoid driver binding conflicts.

Test signals: `olddefconfig`, `allyesconfig`, `allmodconfig`, single-symbol builds for each bus frontend, and binding/probe tests that verify only one compatible driver claims ADXL345-class devices.
