# sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-kone.c

## Purpose

`hid-roccat-kone.c` supports the original Roccat Kone mouse. It mirrors all five profile payloads and settings in memory, exposes them through sysfs, handles firmware write confirmation and checksum updates, manages TCU calibration and startup profile changes, and forwards special mouse events through the Roccat char device.

## Important APIs, Types, and Functions

- `kone_receive()` and `kone_send()`: Kone-specific USB control transfer wrappers using 16-bit command values rather than the common `0x300 | report_id` helper.
- `kone_get_profile()`, `kone_set_profile()`, `kone_get_settings()`, `kone_set_settings()`, `kone_get_weight()`, and `kone_get_firmware_version()`: device data accessors.
- `kone_check_write()`: polls `kone_command_confirm_write` until success or error after writes.
- `kone_set_settings_checksum()`: recomputes the settings byte-sum checksum.
- Sysfs callbacks for `settings`, `profile1`-`profile5`, `actual_profile`, `actual_dpi`, `weight`, `firmware_version`, `tcu`, and `startup_profile`.
- `kone_init_kone_device_struct()`: reads all profiles, settings, and firmware version during initialization.
- `kone_raw_event()`, `kone_keep_values_up_to_date()`, and `kone_report_to_chrdev()`: filter repeated firmware events, update cached DPI/profile, and emit userspace reports.

## Control Flow

Probe requires USB, parses HID, starts hardware, and initializes only the mouse protocol interface. Initialization reads the five profiles, settings, firmware version, computes the active profile/DPI from the startup profile, and attempts char-device registration.

Sysfs profile and settings reads serve from the cached mirror and allow partial reads. Writes require full object payloads at offset zero. Settings writes validate startup profile, write to the device, replace the cached settings, activate the new startup profile, and emit a profile switch event if it changed. Profile writes avoid device I/O when the payload matches the cached profile. `startup_profile` text writes update the cached settings, recompute checksum, write settings, activate the profile, and emit a report. `tcu` writes run a multi-step calibration sequence with sleeps, reread settings, optionally update the TCU state and checksum, and reactivate the startup profile.

Raw event handling processes 12-byte `struct kone_mouse_event` reports. It suppresses repeated tilt/special-button data introduced by firmware 1.38 by comparing the `wipe` group with the last event. Profile and DPI switch/OSD events update cached state. Relevant profile, DPI, macro, and multimedia events are forwarded to the Roccat char device.

## State and Persistence Behavior

`struct kone_device` caches active profile/DPI, the last mouse event, all five profiles, settings, firmware version, char-device state, and a mutex. Firmware stores profiles/settings persistently; the driver assumes cached values remain valid unless a write or TCU calibration changes them. Weight is read on demand because hardware can change without notification.

## Dependencies and Integration Points

The driver uses HID/USB control transfers, Roccat char-device APIs, class-backed sysfs groups, Kone wire structs from `hid-roccat-kone.h`, and Linux sleep/allocation helpers. It differs from newer Roccat drivers by not using `roccat_common2_*` for core Kone commands.

## Risks and Edge Cases

- `kone_get_profile()` and `kone_set_profile()` use unusual USB requests (`USB_REQ_CLEAR_FEATURE` and `USB_REQ_SET_CONFIGURATION`) for class/interface transfers; this is device-specific but fragile.
- The TCU path logs "couldn't read settings" on the normal success path after setting `retval = size`, because the label is reached unconditionally.
- `kone_tcu_command()` treats the positive byte count returned by `kone_send()` as success/failure directly; a full one-byte write returns 0 from `kone_send()`, but this relies on wrapper behavior.
- Cached profile indexing assumes event values are in range; malformed event values can index outside `profiles`.
- Char-device failure is tolerated, but manual profile-report calls need `roccat_claimed` checks in all paths.
- Full-object writes cast userspace buffers directly to packed structs, so validation is limited.

## Test Signals

Tests should cover initial mirror loading, full and partial sysfs reads, profile/settings no-op writes, checksum recomputation, startup profile switching, TCU activation/deactivation timing, write-confirm status values, raw-event duplicate suppression, out-of-range event handling, and char-device failure tolerance.
