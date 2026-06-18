# sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-arvo.c

## Purpose

`hid-roccat-arvo.c` is the Roccat Arvo keyboard driver. It exposes Arvo mode-key, key-mask, profile, button, and info feature reports through a class-backed sysfs ABI and forwards three-byte special key reports to the Roccat character device.

## Important APIs, Types, and Functions

- `arvo_sysfs_show/set_mode_key()`, `arvo_sysfs_show/set_key_mask()`, and `arvo_sysfs_show/set_actual_profile()`: text sysfs attributes backed by Roccat feature reports.
- `arvo_sysfs_read()` and `arvo_sysfs_write()`: binary sysfs helpers enforcing full-size, offset-zero transfers.
- `bin_attr_button` and `bin_attr_info`: binary ABI endpoints for write-only button data and read-only info data.
- `arvo_init_specials()` and `arvo_remove_specials()`: allocate/free `struct arvo_device` and connect/disconnect the Roccat char device on the non-keyboard interface.
- `arvo_raw_event()` and `arvo_report_to_chrdev()`: convert special reports into `struct arvo_roccat_report`.

## Control Flow

Probe requires USB, parses HID, starts hardware, then calls `arvo_init_specials()`. The keyboard protocol interface is left to generic HID with no driver data; the other interface allocates state, reads the current profile, and attempts `roccat_connect()`. Sysfs operations retrieve the underlying USB interface through the class-device parent chain, lock `arvo_lock`, and use `roccat_common2_receive()` or `roccat_common2_send()`. Profile writes validate a 1-5 profile range and update the cached profile only after the feature-report write succeeds.

Raw events with size 3 are interpreted as `struct arvo_special_report`. The lower nibble becomes the macro button, the upper nibble selects press/release, and the cached profile is attached before the report is sent to the char device.

## State and Persistence Behavior

Persistent per-device state is `struct arvo_device`: char-device claim/minor, `arvo_lock`, and cached `actual_profile`. The selected profile is persistent in device firmware according to the header. Mode-key and key-mask state are read on demand rather than cached.

## Dependencies and Integration Points

The driver depends on HID/USB, the Roccat common feature-report helpers, `linux/hid-roccat.h` char-device APIs, and Arvo wire structs from `hid-roccat-arvo.h`. It registers a class named `arvo` to provide per-device sysfs files.

## Risks and Edge Cases

- Sysfs binary access requires exact full-size transfers; partial userspace reads/writes fail except EOF.
- `arvo_raw_event()` checks only size, not report ID or fixed marker bytes, before converting special reports.
- Char-device setup failure is tolerated, but code paths must continue to check `roccat_claimed`.
- Text writes convert `unsigned long` to one-byte fields without rejecting values beyond byte range for mode/key-mask.

## Test Signals

Test profile set/get, mode-key and key-mask report round trips, full-size binary ABI behavior, keyboard-interface bypass, non-keyboard char-device creation, special-report press/release translation, and remove paths with and without successful `roccat_connect()`.
