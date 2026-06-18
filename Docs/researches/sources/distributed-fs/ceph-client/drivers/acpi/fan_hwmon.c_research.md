# sources/distributed-fs/ceph-client/drivers/acpi/fan_hwmon.c

Purpose: `fan_hwmon.c` exposes ACPI fan telemetry through the Linux hwmon subsystem. It maps current `_FST` values and the current `_FPS` entry to standard fan and power sensor attributes.

Important APIs, types, and functions: public hooks are `devm_acpi_fan_create_hwmon()` and `acpi_fan_notify_hwmon()`. Internal helpers are `acpi_fan_get_current_fps()`, `acpi_fan_hwmon_is_visible()`, and `acpi_fan_hwmon_read()`. The hwmon chip exposes `fan_input`, optional `fan_target`, and optional `power_input`.

Control flow: registration attaches an `acpi_fan` hwmon device using `devm_hwmon_device_register_with_info()`. Visibility always allows current fan RPM, but only exposes target RPM and power for ACPI 4.0 non-fine-grain fans, and only exposes power if at least one `_FPS` state has valid power. Reads evaluate `_FST`, validate current speed, locate the `_FPS` entry whose control matches current control, and return speed or power converted from milliwatts to microwatts. Notify integration emits a hwmon event for `fan_input`.

State and persistence: the hwmon device pointer is stored in `struct acpi_fan`. Sensor values are not cached; reads query firmware through `acpi_fan_get_fst()` and use parsed `_FPS` state data from probe.

Dependencies and integration: depends on the hwmon core, ACPI fan core parser/state, unit conversion constants, and validity helpers in `fan.h`. It is conditionally compiled through the header's `IS_REACHABLE(CONFIG_HWMON)` hooks.

Risks: if `_FST` control does not match any parsed `_FPS` state, target and power reads fail with `-EIO`. Invalid or oversized firmware values become `-ENODEV` or `-EOVERFLOW`. Fine-grain fans hide target and power because not every control value maps to a performance state.

Test signals: verify hwmon file visibility for legacy, ACPI 4.0 discrete, and ACPI 4.0 fine-grain fans; validate unit conversion for power; exercise invalid speed/power sentinels; test no matching current FPS; and confirm notify events reach hwmon listeners.
