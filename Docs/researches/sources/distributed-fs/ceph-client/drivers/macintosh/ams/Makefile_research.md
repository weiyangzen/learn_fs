<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/ams/Makefile -->
# sources/distributed-fs/ceph-client/drivers/macintosh/ams/Makefile

Purpose: This Makefile builds the Apple Motion Sensor composite module.

Important mappings: `ams-y` always includes `ams-core.o` and `ams-input.o`. `CONFIG_SENSORS_AMS_PMU` adds `ams-pmu.o`; `CONFIG_SENSORS_AMS_I2C` adds `ams-i2c.o`. `CONFIG_SENSORS_AMS` builds `ams.o`.

Control flow and dependencies: There is no runtime logic. The object composition matches the runtime backend selection in `ams-core.c`, where I2C is tried before PMU if both are enabled.

Risks and test signals: Backend-only build combinations must still provide the symbols referenced by core through Kconfig guards. Build-test PMU-only, I2C-only, and both-backend configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/ams/Makefile -->
