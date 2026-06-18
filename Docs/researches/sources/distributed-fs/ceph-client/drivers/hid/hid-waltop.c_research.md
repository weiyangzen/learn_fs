# sources/distributed-fs/ceph-client/drivers/hid/hid-waltop.c

## Purpose

`hid-waltop.c` is a small HID quirk driver for Waltop pen tablets whose report descriptors do not describe usable digitizer, mouse, wheel, keyboard, consumer-control, pressure, and tilt data correctly. It replaces known broken descriptors for several USB product IDs and normalizes a few raw pen reports before the HID input layer consumes them.

## Important APIs, Types, and Functions

- Fixed descriptor arrays: `slim_tablet_5_8_inch_rdesc_fixed`, `slim_tablet_12_1_inch_rdesc_fixed`, `q_pad_rdesc_fixed`, `pid_0038_rdesc_fixed`, `media_tablet_10_6_inch_rdesc_fixed`, `media_tablet_14_1_inch_rdesc_fixed`, and `sirius_battery_free_tablet_rdesc_fixed`.
- Original descriptor size constants gate replacement so the driver only substitutes the descriptor revision it knows how to fix.
- `waltop_report_fixup(...)`: switches on `hdev->product`, verifies `*rsize`, updates `*rsize`, and returns a static replacement descriptor.
- `waltop_raw_event(...)`: edits report data in place for report ID 16 pen packets, clearing pressure for barrel-button states and converting Sirius tilt values from device units into HID/user-space angle units.
- `waltop_devices[]` and `waltop_driver`: bind the USB Waltop products and register `.report_fixup` plus `.raw_event`.

## Control Flow

When a matching USB HID device is parsed, HID core calls `waltop_report_fixup`. The function only changes the descriptor if both product ID and expected original length match, avoiding accidental replacement of unknown firmware revisions. Runtime input reports then pass through `waltop_raw_event`: generic pen reports with barrel buttons pressed get pressure bytes zeroed, while Sirius Battery Free Tablet 10-byte pen reports additionally have signed tilt bytes normalized through a lookup table and Y tilt sign reversal.

## State and Persistence Behavior

The file keeps no per-device allocation or persistent state. Its state is static read-only descriptor data. The only mutable behavior is in-place mutation of the current raw input report buffer before later HID parsing.

## Dependencies and Integration Points

It depends on HID core report-fixup/raw-event hooks, `hid-ids.h` Waltop vendor/product constants, and normal kernel HID/input descriptor parsing. The replacement descriptors are the integration contract with user-space input consumers because they expose correct digitizer axes, pressure ranges, tilt, wheel, keyboard, and consumer usages.

## Risks and Edge Cases

- Descriptor replacement is size-sensitive; a firmware update with the same product ID but a different descriptor length will silently use the original descriptor.
- Static descriptors must exactly match the raw packet layouts. Any mismatch can create misparsed axes or buttons.
- Pressure is always cleared when low nibble `data[1] > 1`, which intentionally discards pressure for barrel-button states and may hide valid pressure from unusual stylus firmware.
- Sirius tilt conversion clamps to the lookup table range, so values above the expected 60-degree range are saturated.

## Test Signals

- Attach each listed Waltop product and confirm `hid-recorder`/`evtest` show expected X/Y/pressure/buttons, media controls, and wheel events.
- Verify unknown descriptor sizes do not get replaced.
- For Sirius, validate tilt sign and clamp behavior against known positive/negative X/Y tilt reports.
- Exercise barrel-button reports and confirm pressure drops to zero only for the intended pen report ID and size.
