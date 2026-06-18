<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/cros_ec_dev.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/cros_ec_dev.c

Purpose: implements the ChromeOS EC platform MFD "device" layer. It creates a stable class device under the `chromeos` class, detects dedicated MCU roles and EC features, and hotplug-adds feature-specific and platform EC child devices such as char device, debugfs, hwmon, sysfs, sensor hub, USB-PD, GPIO, RTC, LED, watchdog, UCSI, charger control, lightbar, peripheral charger, and VBC NVRAM.

Important APIs and functions: module lifecycle is `cros_ec_dev_init`/`cros_ec_dev_exit`; platform lifecycle is `ec_device_probe`/`ec_device_remove`; class release is `cros_ec_class_release`. Detection uses `cros_ec_check_features`, `cros_ec_get_sensor_count`, `cros_ec_cmd` with `EC_CMD_PCHG_COUNT`, DMI match for legacy Link lightbar, and OF property `"google,has-vbc-nvram"`.

Control flow: module init registers the `chromeos` class and platform driver. Probe allocates `struct cros_ec_dev`, links it to parent `ec_dev`, initializes feature cache sentinels, creates a class device named from platform data, detects whether the EC is a fingerprint/ISH/SCP/touchpad MCU and adjusts the exposed EC name, adds sensorhub if sensors exist, iterates feature-to-cell mappings, adds USB-PD charger/logging unless UCSI already supplies power information, adds lightbar by feature or Link DMI quirk, adds OF-only USB-PD notifier, queries peripheral charger count, adds always-present platform children, and adds VBC child if the parent OF node advertises it. Remove removes MFD children and unregisters the class device.

State and persistence: `struct cros_ec_dev` stores parent EC device pointer, command offset, class device, feature cache, and platform device linkage. Child devices are hotplug MFD devices and may persist only while this platform device is bound. EC firmware features and peripheral charger count are queried live from the EC.

Dependencies and integration points: depends on the lower-level ChromeOS EC transport/protocol device as parent driver data, platform data (`struct cros_ec_platform`), DMI, OF, MFD hotplug APIs, ChromeOS EC command definitions, and the child drivers named by the cell tables. The `chromeos` class gives userspace a stable namespace for EC/MCU devices.

Risks: many child-add failures are logged but non-fatal, so partial EC functionality is expected and must be diagnosed from logs. Feature detection requires EC command support; older firmware may rely on quirks like DMI Link lightbar or platform cells. The code assumes platform data is present and contains `cmd_offset`/`ec_name`. USB-PD charger is intentionally skipped when UCSI is present to avoid duplicate power-supply providers. Class device lifetime uses manual `device_initialize`/`device_add`/`put_device` plus kzalloc release, so error paths are sensitive.

Test signals: class registration and `/sys/class/chromeos` device creation, feature-cache queries for each `EC_FEATURE_*`, child enumeration with ECs that support sensors, USB-PD, UCSI, GPIO, RTC, LED, charger, hang detect, lightbar, PCHG, and VBC; old Link DMI lightbar behavior; failure injection for individual `mfd_add_hotplug_devices`; and remove/unload cleanup without leaked class devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/cros_ec_dev.c -->
