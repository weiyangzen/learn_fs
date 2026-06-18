# sources/distributed-fs/ceph-client/drivers/hid/hid-retrode.c

## Purpose

`hid-retrode.c` improves Retrode 2 controller adapter presentation. It forces multi-input splitting and assigns useful names to the input devices for SNES mouse, SNES/N64 ports, and Mega Drive ports based on HID report IDs.

## Important APIs, Types, and Functions

- `retrode_probe()`: sets `HID_QUIRK_MULTI_INPUT`, parses HID, and starts hardware.
- `retrode_input_configured()`: names each `hid_input` according to `hi->report->field[0]->report->id`.
- `retrode_devices[]`: matches `USB_VENDOR_ID_FUTURE_TECHNOLOGY` / `USB_DEVICE_ID_RETRODE2`.
- `CONTROLLER_NAME_BASE`: base string for generated input names.

## Control Flow

Probe sets the multi-input quirk before parsing so HID creates separate input devices for different report IDs. After input devices are configured, the callback inspects the first field's report ID: 0 becomes `Retrode SNES Mouse`, 1 and 2 become `Retrode SNES / N64 #1/#2`, 3 and 4 become `Retrode Mega Drive #1/#2`, and unknown IDs log an error and receive an `Unknown` suffix. Names are allocated with `devm_kasprintf()` and assigned directly to `hi->input->name`.

## State and Persistence Behavior

No private driver state is kept. The only persistent per-device data is devm-managed input-name memory tied to the HID device lifetime and the quirk bit set on the HID device before parse.

## Dependencies and Integration Points

The driver relies on HID multi-input behavior, input device configuration callbacks, and Retrode USB IDs from `hid-ids.h`.

## Risks and Edge Cases

- `retrode_input_configured()` assumes `hi->report->field[0]` is present; malformed descriptors with no fields could crash.
- Unknown report IDs still create input devices, but their names lose port specificity.
- The quirk must be set before `hid_parse()`; moving it later would break input splitting.

## Test Signals

Tests should verify that report IDs 0-4 produce distinct input devices with the expected names, unknown report IDs log an error but still allocate a name, and the SNES mouse path is unaffected by the multi-input quirk. Descriptor fuzzing should cover absent fields.
