# sources/distributed-fs/ceph-client/drivers/acpi/fan.h

Purpose: `fan.h` is the shared ACPI fan driver interface. It centralizes ACPI fan device IDs, ACPI 4.0 fan data structures, driver state, validation helpers, and cross-file function declarations used by the core, sysfs-attribute, and hwmon fan files.

Important APIs, types, and functions: `ACPI_FAN_DEVICE_IDS` lists Intel thermal fan HIDs and generic `PNP0C0B`. Data models include `struct acpi_fan_fps` for `_FPS` performance states, `struct acpi_fan_fif` for `_FIF` capabilities, `struct acpi_fan_fst` for `_FST` current state, and `struct acpi_fan` for per-device driver data. Inline helpers `acpi_fan_speed_valid()` and `acpi_fan_power_valid()` reject `U32_MAX` and larger placeholder values. Declared functions include `acpi_fan_get_fst()`, attribute create/delete helpers, and hwmon hooks with stubs when hwmon is unavailable.

Control flow: the header itself has no runtime flow, but it defines the shared contracts followed by `fan_core.c`, `fan_attr.c`, and `fan_hwmon.c`.

State and persistence: `struct acpi_fan` stores per-device ACPI handle, ACPI 4.0 capability flags, `_FIF` data, `_FPS` array, optional Microsoft DSM trip granularity, optional hwmon device, thermal cooling device, and sysfs attributes. All state is in-memory and regenerated on probe.

Dependencies and integration: the header integrates ACPI, thermal cooling, optional hwmon, and device sysfs attribute code. The ID macro is intentionally shared with ACPI power-management code.

Risks: the speed/power validity helpers encode firmware placeholder behavior; callers that bypass them may expose invalid values. `ACPI_FPS_NAME_LEN` bounds generated sysfs names such as `stateN`, so large state counts rely on sane formatting.

Test signals: compile coverage with and without `CONFIG_HWMON`, ACPI 4.0 and legacy fan probe paths, validation of `U32_MAX` placeholder values, and HID matching for new fan IDs.
