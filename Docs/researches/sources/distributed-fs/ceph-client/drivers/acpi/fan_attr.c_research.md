# sources/distributed-fs/ceph-client/drivers/acpi/fan_attr.c

Purpose: `fan_attr.c` creates extra sysfs attributes for ACPI fans with `_FST`, especially ACPI 4.0 fans with `_FIF/_FPS/_FSL`. It exposes current RPM, fine-grain control capability, and one read-only `stateN` file per fan performance state.

Important APIs, types, and functions: the main exported helpers are `acpi_fan_create_attributes()` and `acpi_fan_delete_attributes()`. Attribute show functions are `show_fan_speed()`, `show_fine_grain_control()`, and `show_state()`.

Control flow: creation always adds `fan_speed_rpm` for `_FST` fans. If the fan is not ACPI 4.0, it stops there. For ACPI 4.0, it adds `fine_grain_control`, then iterates `_FPS` entries to create `state0`, `state1`, etc. Each `stateN` line reports control, trip point, speed, noise level scaled by 100, and power, replacing invalid sentinel values with `not-defined`. Error handling unwinds already-created files. Deletion removes the same files in reverse logical scope.

State and persistence: the file stores sysfs `device_attribute` objects inside `struct acpi_fan` and each `struct acpi_fan_fps`. It does not persist values; reads evaluate current `_FST` only for `fan_speed_rpm`, while `stateN` shows cached `_FPS` data parsed during probe.

Dependencies and integration: depends on ACPI device driver data from `fan_core.c`, `acpi_fan_get_fst()`, and sysfs APIs. The attributes are created and removed by fan probe/remove and error paths.

Risks: invalid firmware values are partly normalized for display but `show_fan_speed()` prints `_FST` speed directly, relying on lower layers or users to interpret placeholders. Partial sysfs creation must unwind correctly to avoid dangling attributes. The `stateN` format is ABI-like and should not change casually.

Test signals: verify sysfs files for legacy `_FST` fans and ACPI 4.0 fans, invalid sentinel formatting, creation unwind after injected sysfs failures, removal after probe failure and driver remove, and live `_FST` read error propagation.
