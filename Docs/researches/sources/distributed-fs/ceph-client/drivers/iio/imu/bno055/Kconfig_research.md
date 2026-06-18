## sources/distributed-fs/ceph-client/drivers/iio/imu/bno055/Kconfig

Purpose: Kconfig entries for Bosch BNO055 common, UART/serdev, and I2C drivers.

Important APIs, types, and functions: `BOSCH_BNO055` is a hidden tristate selected by bus drivers and selects `IIO_BUFFER` and `IIO_TRIGGERED_BUFFER`. `BOSCH_BNO055_SERIAL` depends on `SERIAL_DEV_BUS`, selects `REGMAP` and the common driver, and builds module `bno055_sl`. `BOSCH_BNO055_I2C` depends on `I2C`, selects `REGMAP_I2C` and the common driver, and builds `bno055_i2c`.

Control flow: users choose a bus-specific option; the selected common symbol ensures the shared IIO implementation is linked.

State and persistence behavior: no runtime state; this file controls build inclusion and dependency closure.

Dependencies and integration points: integrates the BNO055 folder with IIO buffering, triggered buffering, serdev, I2C, and regmap subsystems.

Risks and edge cases: serial selects only generic `REGMAP`, not `REGMAP_I2C`, because it implements a custom regmap bus. The help text names the serial module `bno055_sl`, while the Makefile builds object `bno055_ser.o`; packaging expectations should match generated module naming.

Test signals: Kconfig build matrix should cover common+I2C, common+serial with tracing on/off, module and built-in configurations, and dependency failures when I2C or serdev are unavailable.
