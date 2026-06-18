# sources/distributed-fs/ceph-client/drivers/iio/humidity/Kconfig

Purpose: Kconfig menu for IIO humidity sensor drivers. It declares user-visible sensor options and hidden transport helpers for humidity devices under `drivers/iio/humidity`.

Important APIs/types/functions: User-visible configs include `AM2315`, `DHT11`, `ENS210`, `HDC100X`, `HDC2010`, `HDC3020`, `HID_SENSOR_HUMIDITY`, `HTS221`, `HTU21`, `SI7005`, and `SI7020`. Hidden helper configs `HTS221_I2C` and `HTS221_SPI` select regmap buses and depend on `HTS221`. Several entries select IIO buffer helpers, triggered buffers, CRC libraries, HID sensor common code, or measurement-specialties common I2C support.

Control flow: The menu has no runtime control flow. Its selections drive which objects the Makefile builds and ensure dependent common frameworks are available when a driver is enabled.

State and persistence: Kconfig choices persist in kernel `.config` and module build output. There is no runtime state.

Dependencies and integration points: Integrates humidity sensor support with I2C, GPIOLIB, HID sensor hub, SPI through HTS221 suboptions, CRC7/CRC8, and IIO buffer/trigger infrastructure. `HTS221` selects both transport helpers conditionally, depending on available I2C or SPI master support.

Risks: Incorrect `select` usage can force helper code without all runtime requirements. `DHT11` allows `COMPILE_TEST` without `GPIOLIB`, useful for build coverage but not runtime. HTS221 depends on `(I2C || SPI)` but selects `HTS221_SPI if (SPI_MASTER)`, so SPI-only configurations require SPI master symbols to align.

Test signals: Run `olddefconfig`/`allmodconfig`/`allyesconfig` build checks, verify module names match help text, and confirm selected helpers are built for each enabled driver.
