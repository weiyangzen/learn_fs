# sources/distributed-fs/ceph-client/drivers/hid/hid-razer.c

## Purpose

`hid-razer.c` supports Razer BlackWidow gaming keyboard macro keys. It optionally remaps keyboard usages `0x68` through `0x6c` to Linux `KEY_MACRO1` through `KEY_MACRO5` and sends a feature report to the mouse-typed interface to enable those macro key reports.

## Important APIs, Types, and Functions

- `macro_key_remapping`: module parameter controlling whether the usage remapping is active.
- `blackwidow_init[]`: 91-byte feature-report payload used to enable macro key reporting.
- `razer_input_mapping()`: maps selected keyboard-page usages with `hid_map_usage_clear()`.
- `razer_probe()`: parses the report descriptor, sends `blackwidow_init` via `hid_hw_raw_request()` when `hdev->type == HID_TYPE_USBMOUSE`, then starts hardware.
- `razer_devices[]`: matches BlackWidow, BlackWidow Classic, and BlackWidow Ultimate USB IDs.

## Control Flow

During probe the driver parses HID first. If the current interface is the BlackWidow interface identified as `HID_TYPE_USBMOUSE`, it duplicates the static initialization payload and sends it as feature report ID 0 with `HID_REQ_SET_REPORT`. A short or failed transfer is logged, but probe continues to `hid_hw_start()` so the device remains usable. During input mapping, when `macro_key_remapping` is enabled, only keyboard usage-page entries in the `0x68`-`0x6c` range are consumed and remapped; all other usages return 0 for normal HID mapping.

## State and Persistence Behavior

The module parameter is global mutable state. No per-device allocation persists after probe. The device-level macro enablement is pushed into keyboard firmware state through the feature report and is not retried after resume in this file.

## Dependencies and Integration Points

This driver uses HID input mapping, raw feature requests, USB-facing HID report semantics, and Linux input macro keycodes. It depends on Razer VID/PID constants from `hid-ids.h`.

## Risks and Edge Cases

- The feature report is only sent on probe for `HID_TYPE_USBMOUSE`; suspend/resume or firmware reset paths may require reinitialization but no PM hooks are present.
- A short successful transfer is logged but does not fail probe; this favors usability but can hide disabled macro keys.
- The usage-page test uses a bitwise expression; future usage encodings should be checked against HID helper idioms before extending it.
- Disabling `macro_key_remapping` leaves any enabled macro reports to generic mapping, which may or may not be meaningful.

## Test Signals

Tests should verify that the macro keys generate `KEY_MACRO1`-`KEY_MACRO5` when remapping is enabled, fall back to generic handling when disabled, and that the 91-byte feature report is sent only to the intended interface. Resume testing should confirm whether macro keys remain enabled after power management transitions.
