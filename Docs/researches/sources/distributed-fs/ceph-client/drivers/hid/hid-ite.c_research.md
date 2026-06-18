# sources/distributed-fs/ceph-client/drivers/hid/hid-ite.c

## Purpose

`hid-ite.c` handles ITE and ITE-like keyboard-controller HID devices that need small descriptor or event corrections. It fixes Acer/Synaptics keyboard-dock touchpad toggle descriptors, maps vendor-page touchpad on/off usages to the function keys expected by userspace, and synthesizes rfkill button press/release events for devices that only report a zero-valued release-like packet.

## Important APIs, Types, and Functions

- `QUIRK_TOUCHPAD_ON_OFF_REPORT`: per-device driver-data bit enabling Acer keyboard-dock descriptor and mapping fixes.
- `ite_report_fixup(...)`: checks exact descriptor sizes and byte offsets, then changes specific input items from absolute/variable to relative for touchpad on/off reports.
- `ite_input_mapping(...)`: maps vendor page `0x00880078` to `KEY_F22` and `0x00880079` to `KEY_F23`; suppresses other usages on that page for the quirked devices.
- `ite_event(...)`: intercepts `HID_GD_RFKILL_BTN` and emits a complete `KEY_RFKILL` press/release sequence.
- `ite_probe(...)`: stores `id->driver_data`, opens/parses the report descriptor with `hid_open_report`, and starts the hardware with default HID connections.
- `ite_devices` and `ite_driver`: match ITE, 258A, and specific Synaptics/Acer USB HID devices and register the fixup/mapping/event hooks.

## Control Flow

During probe the driver stores the quirk mask in HID drvdata before parsing. Descriptor parsing calls `ite_report_fixup`; quirked Acer dock descriptors are recognized by size and byte signatures, then a single item flag byte is patched. Input mapping later sees the corrected usages and remaps the two touchpad state events to F22/F23. Runtime rfkill reports are intercepted after input claiming; the driver obtains the report's `field->hidinput->input` device and sends press, sync, release, sync.

## State and Persistence Behavior

The only persistent state is the quirk bit stored via `hid_set_drvdata`. Descriptor mutation is in-memory for the current parsed HID device. The rfkill path stores no state and always treats a received rfkill usage as an instantaneous button press.

## Dependencies and Integration Points

This driver integrates with HID core report fixup, input mapping, and event hooks. It depends on HID/input constants, `hid-ids.h` IDs, and the generic HID input path for all normal events. Userspace compatibility is explicit: Acer touchpad toggles are mapped to `KEY_F22` and `KEY_F23`.

## Risks and Edge Cases

- Descriptor fixes are exact offset patches; firmware revisions with shifted descriptors will bypass the fix or could be mispatched if they match accidentally.
- `ite_event` assumes the rfkill report semantics are unique enough that any report means a press, regardless of value.
- Quirk storage casts integer driver data through `void *`; adding larger state would require a real allocation.
- The input mapping suppresses all other vendor page `0x00880000` usages on quirked devices.

## Test Signals

Test with affected Acer Switch/One docks should show F22/F23 events for touchpad toggles, no spurious axes from the toggle descriptor, and complete rfkill press/release events despite zero values. Descriptor regression tests should include the three known size/offset layouts and a nonmatching descriptor that remains unchanged.
