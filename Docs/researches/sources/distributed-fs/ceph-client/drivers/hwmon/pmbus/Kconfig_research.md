# sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/Kconfig

Purpose: PMBus hwmon configuration menu. It enables the PMBus core, generic PMBus support, and a large list of chip-specific drivers including every PMBus source in this work item.

Important symbols: `PMBUS` is the menuconfig and core module gate depending on `I2C`. Relevant entries here include `SENSORS_ACBEL_FSG032`, `SENSORS_ADM1266`, `SENSORS_ADM1275`, `SENSORS_ADP1050`, `SENSORS_ADP1050_REGULATOR`, `SENSORS_APS_379`, `SENSORS_BEL_PFE`, `SENSORS_BPA_RS600`, `SENSORS_CRPS`, `SENSORS_DELTA_AHE50DC_FAN`, `SENSORS_FSP_3Y`, `SENSORS_HAC300S`, `SENSORS_IBM_CFFPS`, `SENSORS_DPS920AB`, and `SENSORS_INA233`. `SENSORS_ADM1266` selects `CRC8` and depends on `GPIOLIB`; `SENSORS_IBM_CFFPS` depends on `LEDS_CLASS`.

Control flow: when `PMBUS` is enabled, the nested symbols determine which chip drivers build. Optional regulator integration for ADP1050/LTP8800 depends on both the sensor driver and `REGULATOR`.

State and persistence: no runtime state. This file controls compile-time inclusion, module availability, and dependency closure.

Dependencies and integration: integrates hwmon PMBus drivers with I2C, GPIO, LED, CRC, and regulator subsystems where needed. Help text documents module names consumed by users and packaging.

Risks: dependency mistakes cause build or probe failures only for selected configurations, especially optional GPIO/LED/regulator features. The menu is long, so Makefile/Kconfig drift is a common maintenance risk.

Test signals: `olddefconfig`, randconfig/allmodconfig builds, module names matching help text, and targeted builds for drivers with extra dependencies such as ADM1266 and IBM CFFPS.
