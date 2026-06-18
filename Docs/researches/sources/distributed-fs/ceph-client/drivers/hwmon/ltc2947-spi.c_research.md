# sources/distributed-fs/ceph-client/drivers/hwmon/ltc2947-spi.c

Purpose: SPI transport wrapper for the LTC2947 core hwmon driver.

Important APIs/types/functions: defines a regmap with 8 bit registers and 8 bit values; `ltc2947_probe()` creates the SPI regmap and calls `ltc2947_core_probe()`; `ltc2947_driver` binds the `ltc2947` SPI id and shared OF match data.

Control flow: `module_spi_driver()` registers the wrapper. Probe uses `devm_regmap_init_spi()`, returns any regmap initialization failure, then delegates common setup, scaling, sysfs registration, and PM callbacks to the core.

State and persistence behavior: no independent runtime state. All programmed thresholds, continuous conversion mode, GPIO configuration, and suspend/resume state are owned by `ltc2947-core.c`.

Dependencies and integration points: integrates Linux SPI, regmap, hwmon through the core, and the shared local header. The driver uses `pm_ptr(&ltc2947_pm_ops)`.

Risks: correctness depends on regmap SPI semantics matching the chip command format; if bus-specific read/write flags are ever required, this simple config will be insufficient. Wrapper/core symbol export mismatches break both build and runtime binding.

Test signals: compile with SPI support, instantiate via SPI id or OF compatible, check regmap initialization and core registration, and run shared LTC2947 hwmon read/write tests over SPI.
