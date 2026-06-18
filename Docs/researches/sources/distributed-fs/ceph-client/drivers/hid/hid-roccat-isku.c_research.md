# sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-isku.c

## Purpose

`hid-roccat-isku.c` supports Roccat Isku and Isku FX keyboards. It exposes keyboard configuration and macro storage through sysfs binary attributes, tracks the active profile, and forwards button/profile reports to the Roccat char device.

## Important APIs, Types, and Functions

- `isku_get_actual_profile()` and `isku_set_actual_profile()`: feature-report accessors for the active zero-based profile.
- `isku_sysfs_read()` and `isku_sysfs_write()`: Isku-specific binary sysfs helpers allowing reads/writes up to each attribute's real size.
- `ISKU_BIN_ATTR_*` macro uses: generate ABI files for macro, key groups, light, key mask, last set, talk, talkfx, control, reset, and info.
- `isku_init_specials()` and `isku_remove_specials()`: allocate state and connect char device only on `ISKU_USB_INTERFACE_PROTOCOL`.
- `isku_raw_event()`, `isku_keep_values_up_to_date()`, and `isku_report_to_chrdev()`: update cached profile and emit char-device reports.

## Control Flow

Probe parses and starts HID, then initializes only the interface with protocol 0. Initialization reads the active profile and tries to register a class-backed Roccat char device. Text sysfs profile writes validate profile <= 4, send the profile report with status polling, update the cached profile, and synthesize a profile event with one-based profile data for userspace. Binary sysfs reads/writes lock `isku_lock` and send exactly `count` bytes, rejecting nonzero offsets and counts larger than the declared maximum.

Raw events are ignored on non-Isku interfaces or before state allocation. Button reports with event `ISKU_REPORT_BUTTON_EVENT_PROFILE` update the cached zero-based profile from one-based report data. All button reports are forwarded with the cached profile converted to one-based numbering.

## State and Persistence Behavior

`struct isku_device` stores char-device state, a mutex, and cached `actual_profile`. Most configuration is persisted in device firmware and read/written on demand through sysfs. The cached profile is updated from both sysfs writes and interrupt reports.

## Dependencies and Integration Points

The driver depends on Roccat common feature-report helpers, Isku layout constants from `hid-roccat-isku.h`, class-backed sysfs groups, and `linux/hid-roccat.h` for event forwarding.

## Risks and Edge Cases

- Binary sysfs helpers permit short writes/reads up to the declared size, which differs from the stricter common helper pattern and may allow partial firmware payloads.
- `roccat_report_event()` is called after sysfs profile writes without checking `roccat_claimed`; if char-device registration failed, the stored minor may be invalid.
- Raw-event data is cast without checking the report size.
- Profile numbering mixes zero-based firmware state with one-based userspace/event data.

## Test Signals

Tests should cover profile set/get, char-device registration failure, partial binary payload behavior, protocol-interface gating, profile-change interrupt reports, and event payload numbering. Hardware tests should verify large macro payload transfers and light/key group writes.
