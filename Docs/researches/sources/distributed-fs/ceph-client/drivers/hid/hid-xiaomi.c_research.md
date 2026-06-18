# sources/distributed-fs/ceph-client/drivers/hid/hid-xiaomi.c

## Purpose

`hid-xiaomi.c` fixes the Bluetooth Xiaomi Mi Silent Mouse report descriptor so side buttons are exposed. The original descriptor advertises only three buttons; the fixed descriptor raises button usage/count to five.

## Important APIs, Types, and Functions

- `MI_SILENT_MOUSE_ORIG_RDESC_LENGTH`: guards descriptor replacement for the known 87-byte descriptor.
- `mi_silent_mouse_rdesc_fixed`: replacement mouse descriptor with five button bits plus relative X/Y/wheel and a vendor feature report.
- `xiaomi_report_fixup`: replaces the descriptor for `USB_DEVICE_ID_MI_SILENT_MOUSE` when size matches.
- `xiaomi_devices[]` and `xiaomi_driver`: bind the Bluetooth Xiaomi device and install `.report_fixup`.

## Control Flow

On HID parse, the report-fixup hook checks product ID and descriptor length. If both match, it logs the fixup, returns the static descriptor, and updates `*rsize`; otherwise the original descriptor continues through HID core.

## State and Persistence Behavior

The driver has no per-device state. Behavior is entirely static descriptor replacement during probe-time parsing.

## Dependencies and Integration Points

It depends on HID Bluetooth matching, `hid-ids.h` Xiaomi constants, and HID input descriptor parsing. User-space integration is via normal evdev mouse button events after descriptor correction.

## Risks and Edge Cases

- Descriptor replacement will not apply to changed firmware descriptor lengths.
- The fixed descriptor assumes the raw packet already contains five button bits.
- No probe/remove hooks means all behavior must be expressible as descriptor fixup.

## Test Signals

- Pair the mouse and verify BTN_SIDE/BTN_EXTRA or equivalent fourth/fifth button events appear.
- Confirm three primary buttons, X/Y, and wheel still behave normally.
- Verify nonmatching descriptor sizes are left untouched.
