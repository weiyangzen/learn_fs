# sources/distributed-fs/ceph-client/drivers/hwmon/occ/Makefile

Purpose: object composition for OCC hwmon modules.

Important entries: `occ-hwmon-common-objs := common.o sysfs.o`, `occ-p8-hwmon-objs := p8_i2c.o`, and `occ-p9-hwmon-objs := p9_sbe.o`. Object inclusion follows `CONFIG_SENSORS_OCC`, `CONFIG_SENSORS_OCC_P8_I2C`, and `CONFIG_SENSORS_OCC_P9_SBE`.

Control flow: the Kconfig-selected common module links shared polling, parsing, dynamic sysfs, and status sysfs code, while each transport module links only its bus-specific command sender.

State and persistence: no runtime state; it controls link structure.

Dependencies and integration: ties the hidden common symbol to shared implementation files and the public frontend symbols to their transport objects.

Risks: if a frontend references common exported symbols without `SENSORS_OCC`, link errors occur; current Kconfig selects avoid that.

Test signals: build with common plus P8, common plus P9, both frontends, and all disabled.
