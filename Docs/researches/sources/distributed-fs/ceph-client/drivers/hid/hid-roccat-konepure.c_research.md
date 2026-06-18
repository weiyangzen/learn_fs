# sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-konepure.c

## Purpose

`hid-roccat-konepure.c` is a simplified common-helper driver for Roccat KonePure and KonePure Optical mice. It exposes common feature-report sysfs files and forwards special button reports directly to the Roccat char device.

## Important APIs, Types, and Functions

- `struct konepure_mouse_report_button`: eight-byte report 3 payload layout.
- `ROCCAT_COMMON2_BIN_ATTRIBUTE_*` declarations: generate sysfs ABI for actual profile, control, info, talk, macro, sensor, TCU, TCU image, profile settings, and profile buttons.
- `konepure_init_specials()` and `konepure_remove_specials()`: allocate a `roccat_common2_device` and connect/disconnect char device on mouse interfaces.
- `konepure_raw_event()`: forwards report-number-3 data to userspace without further translation.

## Control Flow

Probe parses and starts HID, then initializes only USB mouse protocol interfaces. The class `konepure` supplies bin attributes through the Roccat char-device class device. Common sysfs callbacks perform exact-size USB feature transfers and status polling for writes. Raw events on the mouse interface are ignored unless `data[0] == 3`; claimed char-device instances receive the raw report bytes.

## State and Persistence Behavior

The driver stores only `struct roccat_common2_device` state: char-device claim/minor and a lock. All profile, macro, sensor, and TCU state remains in firmware and is accessed on demand.

## Dependencies and Integration Points

It depends on `hid-roccat-common.h` macros and common helpers, HID/USB mouse-interface selection, and Roccat char-device APIs.

## Risks and Edge Cases

- `konepure_raw_event()` does not check report size before forwarding.
- The driver forwards raw report bytes in the firmware layout, so userspace must know the report format.
- Common-helper exact-size sysfs limitations and receive short-copy risk apply.

## Test Signals

Tests should verify each bin attribute mode/size, exact-size access behavior, char-device connection, report-3 forwarding, non-mouse-interface bypass, and removal with failed char-device registration.
