# sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-kovaplus.c

## Purpose

`hid-roccat-kovaplus.c` supports Roccat Kova[+] mice. It caches profile settings/buttons for five profiles, exposes feature-report sysfs files, tracks active profile/CPI/sensitivity, and forwards translated button reports to the Roccat char device.

## Important APIs, Types, and Functions

- `kovaplus_send_control()` and `kovaplus_select_profile()`: select firmware profile payloads for subsequent reads.
- `kovaplus_get_profile_settings/buttons()` and `kovaplus_get_actual_profile()`: initialize cached state.
- `kovaplus_set_actual_profile()`: write the active zero-based profile with status polling.
- Generated sysfs attributes for control, info, profile settings/buttons, and per-profile read-only profile payloads.
- Text attributes for active profile, CPI, X/Y sensitivity, and firmware version.
- `kovaplus_keep_values_up_to_date()` and `kovaplus_report_to_chrdev()`: update cached runtime values and publish userspace events.

## Control Flow

Initialization on the mouse interface reads each profile's settings and buttons with a 70 ms delay between operations because shorter delays can freeze the device, then reads the current active profile and derives runtime CPI/sensitivity from the cached profile settings. Sysfs profile-specific reads select a profile through control and then read the shared payload. Active-profile writes validate `< 5`, send the firmware command, update cached state, and synthesize a profile event.

Raw event handling processes report number 3. Profile type `0x20` updates active profile and derived values, CPI type converts firmware CPI values with `kovaplus_convert_event_cpi()`, and sensitivity type updates X/Y sensitivity. Userspace reports skip profile type `0x30`, attach cached one-based profile, include a button number only for macro/shortcut/quicklaunch/timer events, and normalize CPI values.

## State and Persistence Behavior

`struct kovaplus_device` caches active profile, active CPI, active X/Y sensitivity, char-device state, mutex, and arrays of five profile settings and button payloads. Firmware remains authoritative for writes through sysfs; cached initialization data is used for runtime state derivation.

## Dependencies and Integration Points

The driver uses Roccat common feature-report helpers, `hid-roccat-kovaplus.h` layouts, class-backed sysfs, USB mouse-interface filtering, and Roccat char-device events.

## Risks and Edge Cases

- `kovaplus_send_control()` uses `roccat_common2_send()` without status polling, unlike some sibling drivers.
- Profile-specific read helpers select the profile before entering the common read lock, leaving a possible race with other sysfs operations.
- Firmware-version reads ignore receive errors and may print uninitialized data.
- Raw-event casts do not check size.
- The fixed 70 ms wait is hardware-sensitive and may be insufficient for some devices or unnecessarily slow for others.

## Test Signals

Tests should cover initialization timing, all five profile cache loads, active profile changes, CPI conversion values `4` and `7`, sensitivity updates, firmware-info failure handling, profile-read concurrency, exact-size sysfs behavior, and event filtering for profile type `0x30`.
