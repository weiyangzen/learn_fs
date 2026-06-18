# sources/distributed-fs/ceph-client/drivers/iio/Kconfig

Purpose: top-level Industrial I/O configuration menu. It exposes the `IIO` subsystem, optional core features such as buffers, triggers, configfs, software devices/triggers, triggered events, generic time-scale helper, backend framework, and then sources all IIO device-class submenus.

Important symbols: `IIO`, `IIO_BUFFER`, `IIO_CONFIGFS`, `IIO_GTS_HELPER`, `IIO_TRIGGER`, `IIO_CONSUMERS_PER_TRIGGER`, `IIO_SW_DEVICE`, `IIO_SW_TRIGGER`, `IIO_TRIGGERED_EVENT`, and `IIO_BACKEND`. It sources `drivers/iio/accel/Kconfig` plus ADC, DAC, IMU, gyro, light, pressure, trigger, and other sensor/actuator families.

Control flow: when `IIO` is disabled, all nested menus are hidden. Enabling `IIO_BUFFER` exposes buffer implementations. Enabling `IIO_TRIGGER` exposes trigger support and the trigger submenu. Driver Kconfigs under each source file select or depend on these core options, so this file is the root of the build-time dependency graph for IIO.

State and persistence: no runtime state. It persists only through generated kernel configuration and controls which objects are built into the kernel or modules.

Dependencies and integration: selects `DMA_SHARED_BUFFER` for buffer support and `CONFIGFS_FS` for configfs-backed software devices/triggers. It integrates the IIO core with Kbuild via `drivers/iio/Makefile` and with all child sensor driver menus.

Risks: hidden helper symbols must remain selected by their consumers; otherwise drivers may compile without required core support. Menu ordering and source paths are part of discoverability. Incorrect dependencies can expose impossible configurations or hide valid drivers.

Test signals: `make olddefconfig`, `make menuconfig`, allmodconfig/allnoconfig coverage, and representative module builds for buffered, triggered, configfs, and backend users.
