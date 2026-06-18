# sources/distributed-fs/ceph-client/drivers/hid/hid-cypress.c

## Purpose
`hid-cypress.c` applies targeted quirks for Cypress-based HID devices with broken report descriptors or unusual wheel behavior. It fixes barcode reader usage min/max ordering, corrects a Varmilo VA104M logical minimum, and implements a two-wheel mouse mode where one button-like usage toggles whether vertical wheel events should be reported as horizontal wheel events.

## Important APIs, Types, And Functions
Quirk flags are stored in `id->driver_data` and then in HID driver data: `CP_RDESC_SWAPPED_MIN_MAX`, `CP_2WHEEL_MOUSE_HACK`, `CP_2WHEEL_MOUSE_HACK_ON`, and `VA_INVAL_LOGICAL_BOUNDARY`. `cp_rdesc_fixup()` scans descriptors for swapped Usage Maximum/Minimum items and rewrites the item tags and bounds. `va_logical_boundary_fixup()` recognizes a 25-byte Varmilo consumer-control descriptor and changes Logical Minimum from 572 to zero. `cp_report_fixup()` dispatches descriptor changes by quirk bit. `cp_input_mapped()` adjusts input capabilities for the two-wheel device and suppresses the toggle usage. `cp_event()` tracks the toggle usage and diverts `REL_WHEEL` into `REL_HWHEEL` while active. `cp_probe()` stores quirks, parses, and starts HID.

## Control Flow
On probe, the driver records the quirk bitmask from the matching device ID, parses the HID descriptor, and starts the device normally. HID core invokes `cp_report_fixup()` before parsing; that function applies descriptor-level corrections based on the stored quirk bits. For the two-wheel mouse quirk, input mapping adds `REL_HWHEEL` capability when `REL_WHEEL` is seen and suppresses usage `0x00090005` from becoming a normal button. Runtime events then use that suppressed usage as a mode latch: nonzero values set `CP_2WHEEL_MOUSE_HACK_ON`, zero clears it. While active, vertical wheel events are re-emitted as horizontal wheel events and consumed.

## State And Persistence
The only state is the quirk bitmask kept in `hid_get_drvdata()`. For the two-wheel mouse, this bitmask is mutated at runtime to include or remove `CP_2WHEEL_MOUSE_HACK_ON`. No persistent device configuration is written.

## Dependencies And Integration Points
The file depends on HID descriptor fixup, HID input mapping/event hooks, Linux input relative axes, and Cypress/Varmilo IDs from `hid-ids.h`. It integrates by making broken devices parse as ordinary HID input devices after small descriptor or event-level corrections.

## Risks
Descriptor fixup relies on byte-pattern matching and in-place mutation; overbroad matching could corrupt an unrelated descriptor, while overly narrow matching can miss firmware variants. The barcode reader fixup scans for any `0x29 ... 0x19` pattern and swaps adjacent bounds, so descriptor structure assumptions matter. The two-wheel state is stored as a cast integer pointer in driver data, which is a common quirk pattern but requires all users to treat it as flags, not allocated memory.

## Test Signals
Test barcode readers should parse without usage-range errors. The Varmilo receiver should expose consumer controls with sane logical bounds. The Cypress mouse should advertise both vertical and horizontal wheel capability, suppress the toggle button as a normal key, and emit `REL_HWHEEL` only while the toggle usage is active.
