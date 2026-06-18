# sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-koneplus.c

## Purpose

`hid-roccat-koneplus.c` supports Roccat Kone[+] and Kone XTD mice. It exposes feature-report configuration through sysfs, controls profile selection for profile-specific reads, tracks the active profile, and forwards button reports to the Roccat char device.

## Important APIs, Types, and Functions

- `koneplus_send_control()`: sends common control requests for profile settings/buttons with range validation and status polling.
- `koneplus_get_actual_profile()` and `koneplus_set_actual_profile()`: read/write the zero-based active profile.
- `koneplus_sysfs_read()` and `koneplus_sysfs_write()`: exact-size binary sysfs helpers using `roccat_common2_*`.
- Generated attributes for control, talk, macro, tcu image, info, sensor, tcu, profile settings, and profile buttons.
- `koneplus_sysfs_read_profilex_settings/buttons()`: select a profile through control then read the current profile payload.
- `koneplus_raw_event()`, `koneplus_keep_values_up_to_date()`, and `koneplus_report_to_chrdev()`: update active profile and forward report 3 events.

## Control Flow

Probe initializes only the USB mouse interface. It reads the current active profile, stores it, and connects the char device. Sysfs fixed attributes directly read or write their command payloads. Profile-specific read-only attributes first send a control request selecting profile 0-4 for settings or buttons, then read the shared profile payload command. Text profile writes validate profile <= 4, send the active-profile command with status polling, update cached state, and synthesize a one-based profile event.

Raw events on the mouse interface inspect button report number 3. Profile event type `0x20` updates cached `actual_profile` from one-based report data. Quicklaunch and timer release events are filtered out; other button report fields are copied into `struct koneplus_roccat_report` with the cached profile converted to one-based numbering.

## State and Persistence Behavior

Per-device state is minimal: zero-based `actual_profile`, char-device state, and a mutex. The driver does not cache full profile settings or button payloads; it reads them from firmware on demand. Active profile persists in device firmware when set.

## Dependencies and Integration Points

The driver depends on Roccat common feature-report helpers, `hid-roccat-koneplus.h` layouts, HID/USB mouse-interface selection, class-backed sysfs, and Roccat char-device event delivery.

## Risks and Edge Cases

- Firmware info reads ignore the return value of `roccat_common2_receive()` and may print uninitialized stack data on failure.
- `koneplus_sysfs_set_actual_profile()` reports to the char device without checking `roccat_claimed`.
- Raw-event size is not checked before casting to the button report struct.
- Profile selection is a two-step control/read sequence; concurrent sysfs accesses outside the same lock can select the wrong profile if not serialized. The profilex helpers call `koneplus_send_control()` before entering `koneplus_sysfs_read()`'s lock, so there is a race window.

## Test Signals

Tests should cover profile range validation, profile-specific read serialization, firmware-info failure handling, raw report translation/filtering, char-device unavailable paths, and exact-size sysfs behavior for large macro and TCU image transfers.
