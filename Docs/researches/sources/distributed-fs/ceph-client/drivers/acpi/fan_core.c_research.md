# sources/distributed-fs/ceph-client/drivers/acpi/fan_core.c

Purpose: `fan_core.c` is the ACPI fan platform driver. It supports both legacy fans controlled through ACPI power states and ACPI 4.0 fans controlled through `_FST`, `_FIF`, `_FPS`, and `_FSL`, registers thermal cooling devices, optionally exposes hwmon data, and supports Microsoft fan DSM trip-point extensions.

Important APIs, types, and functions: the externally used function is `acpi_fan_get_fst()`. Cooling callbacks are `fan_get_max_state()`, `fan_get_cur_state()`, and `fan_set_cur_state()`. ACPI parsers include `acpi_fan_get_fif()` and `acpi_fan_get_fps()`. DSM helpers include `acpi_fan_dsm_init()`, `acpi_fan_dsm_start()`, `acpi_fan_dsm_set_trip_points()`, and `acpi_fan_dsm_update_trips_points()`. Lifecycle functions are `acpi_fan_probe()`, `acpi_fan_remove()`, and PM callbacks.

Control flow: probe allocates `struct acpi_fan`, detects `_FST`, and decides ACPI 4.0 support by checking `_FIF`, `_FPS`, and `_FSL`. ACPI 4.0 fans parse capabilities, parse and sort performance states by speed, initialize Microsoft DSM support if present, register hwmon, install an ACPI notify handler, prime DSM trip notifications, and create extra sysfs attributes. Legacy fans update initial ACPI power state. All fans register a thermal cooling device and create reciprocal sysfs links. Runtime cooling callbacks map thermal states to either ACPI power state or `_FSL` control values. Notify event `0x80` evaluates `_FST`, updates DSM trip points, notifies hwmon, and generates a netlink ACPI event.

State and persistence: per-device state includes parsed `_FIF`, sorted `_FPS`, current hwmon and cooling device pointers, DSM trip granularity, and sysfs attributes. Firmware remains the source of current control and speed through `_FST`. The only tunable is `min_trip_distance`, controlling DSM trip-point spacing.

Dependencies and integration: integrates with ACPI method evaluation and `_DSD` notifications, thermal framework cooling devices, optional hwmon via `fan_hwmon.c`, sysfs attributes via `fan_attr.c`, ACPI netlink events from `event.c`, and platform-driver ACPI HID matching from `fan.h`.

Risks: firmware data validation is critical. `_FIF` step size is clamped to 1-9, but `_FPS` values can still contain sentinel or extreme numbers. `acpi_fan_speed_cmp()` subtracts speeds as `int`, so unusually large firmware speed deltas can overflow comparison semantics. DSM notification priming relies on firmware behavior outside the base ACPI fan spec. Probe error paths must remove attributes only after they have been created.

Test signals: test legacy power-state fans, ACPI 4.0 discrete and fine-grain fans, `_FST` parse errors, `_FPS` invalid packages, thermal cooling state mapping, `_FSL` failures, ACPI notify event `0x80`, DSM-capable systems, resume reinitialization, sysfs link cleanup, and hwmon registration failure unwind.
