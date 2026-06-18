# sources/distributed-fs/ceph-client/drivers/iio/common/cros_ec_sensors/Kconfig

Purpose: Kconfig definitions for ChromeOS EC IIO sensor support. It exposes the shared core and three client drivers for contiguous 3-axis sensors, lid angle, and activity events.

Important symbols: `IIO_CROS_EC_SENSORS_CORE` depends on `SYSFS` and `CROS_EC_SENSORHUB`, and selects `IIO_BUFFER` plus `IIO_TRIGGERED_BUFFER`. `IIO_CROS_EC_SENSORS`, `IIO_CROS_EC_SENSORS_LID_ANGLE`, and `IIO_CROS_EC_ACTIVITY` all depend on the core.

Control flow: users select the core directly or indirectly through feature drivers. Build selection then maps to objects in the local Makefile.

State and persistence: no runtime state; it controls configuration availability and selected build dependencies.

Dependencies and integration: integrates ChromeOS EC sensorhub support with IIO buffering/trigger infrastructure. Help text describes physical 3D sensors, convertible lid-angle reporting, and virtual activity/proximity events.

Risks and test signals: dependency mistakes would allow building without EC sensorhub or buffer support. Test signals include Kconfig dependency resolution, module build for each symbol, and ensuring feature drivers cannot be enabled without `IIO_CROS_EC_SENSORS_CORE`.
