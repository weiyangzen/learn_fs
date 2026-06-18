# sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-pyra.c

## Purpose

`hid-roccat-pyra.c` supports Roccat Pyra wired and wireless mice. It exposes settings/profile/info reports through sysfs, caches profile settings for runtime CPI/profile tracking, and forwards selected button reports to the Roccat char device.

## Important APIs, Types, and Functions

- `pyra_send_control()`: selects profile settings/buttons with range validation.
- `pyra_get_settings()`, `pyra_set_settings()`, and `pyra_get_profile_settings()`: firmware accessors.
- `pyra_sysfs_read()` and `pyra_sysfs_write()`: exact-size binary sysfs helpers.
- Generated attributes for control, info, profile settings/buttons, and per-profile read-only settings/buttons.
- `pyra_sysfs_write_settings()`: custom settings writer that updates active profile and emits a profile event.
- `pyra_init_pyra_device_struct()`: reads settings and all five profile settings, then derives cached runtime state.
- `pyra_raw_event()`, `pyra_keep_values_up_to_date()`, and `pyra_report_to_chrdev()`: runtime event handling.

## Control Flow

Probe initializes only mouse protocol interfaces. Initialization reads the three-byte settings report, then each profile's settings, and calls `profile_activated()` using the startup profile. Sysfs profile-specific reads select the profile through a control report before reading the shared payload. Settings writes require exactly `PYRA_SIZE_SETTINGS`, validate the startup profile, send with status polling, update the cached active profile/CPI, and synthesize a profile event.

Raw events process button report number 3. Profile type `PROFILE_2` updates the active zero-based profile from one-based data; CPI type updates the cached CPI. Char-device forwarding emits profile/CPI changes immediately and forwards macro/shortcut/quicklaunch press events with the current one-based profile value.

## State and Persistence Behavior

`struct pyra_device` stores active profile, active CPI, char-device state, mutex, and cached settings for five profiles. Firmware stores the startup profile and profile settings; the driver mirrors enough data to report runtime values without rereading on every interrupt.

## Dependencies and Integration Points

The driver depends on Roccat common helpers, Pyra wire definitions from `hid-roccat-pyra.h`, HID/USB mouse-interface filtering, class-backed sysfs, and Roccat char-device APIs.

## Risks and Edge Cases

- The `PYRA_BIN_ATTRIBUTE_R` macro uses `.size_new`, which is unusual compared with `struct bin_attribute`'s `.size` and may rely on local kernel compatibility or be a typo.
- Profile-specific read helpers select the profile before acquiring the sysfs transfer lock, creating a race with other profile-selection operations.
- `pyra_sysfs_show_actual_profile()` ignores read errors and returns `settings.startup_profile` from an uninitialized stack struct on failure.
- `pyra_sysfs_write_settings()` emits a char-device report without checking `roccat_claimed`.
- Raw-event casts do not check size.

## Test Signals

Tests should cover wired and wireless IDs, initialization cache load, settings writes, startup profile validation, profile/CPI event updates, profile-specific read races, firmware-info/settings read failure paths, bin attribute structure compatibility, and exact-size sysfs behavior.
