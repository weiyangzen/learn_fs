# sources/distributed-fs/ceph-client/drivers/hid/hid-elecom.c

## Purpose
`hid-elecom.c` fixes report descriptors for several ELECOM mice and trackballs whose descriptors advertise the wrong button count or a nonexistent horizontal wheel. The goal is to let Linux expose all real extra buttons without relying on vendor software.

## Important APIs, Types, And Functions
`mouse_button_fixup()` is the reusable descriptor patch helper. It validates expected descriptor item offsets, clamps the requested number of buttons to `MOUSE_BUTTONS_MAX`, updates the report count, usage maximum, and padding size, and logs the fix. `elecom_report_fixup()` switches on product ID and either clears the BM084 bogus consumer-page horizontal wheel marker or calls `mouse_button_fixup()` with product-specific byte offsets and expected button count. `elecom_devices[]` lists supported Bluetooth and USB ELECOM devices.

## Control Flow
There is no custom probe; `module_hid_driver()` registers a HID driver with `report_fixup` only. When a matching device is parsed, HID core calls `elecom_report_fixup()` with the raw descriptor. The switch selects the known descriptor layout for each product family. `mouse_button_fixup()` first checks descriptor length and sentinel item bytes at the supplied offsets; if any check fails, the descriptor is left untouched. When checks pass, the button count and padding are rewritten in place before generic HID parsing proceeds.

## State And Persistence
The driver keeps no per-device runtime state and writes no persistent settings. All behavior is descriptor mutation during parse.

## Dependencies And Integration Points
The file depends on HID descriptor fixup, `hid-ids.h` ELECOM product IDs, and normal HID input parsing after the descriptor is corrected. User-visible output is standard mouse/trackball input events with corrected button capability.

## Risks
Every fix is offset-based. If ELECOM ships a firmware descriptor variant for the same product ID, the sentinel checks may prevent the fix, leaving buttons unavailable, or a coincidentally matching layout could be patched incorrectly. The helper clamps at eight buttons, so devices with more physical buttons would need code changes. Because there is no probe or runtime logging beyond fixup messages, failures are visible mainly through missing input capabilities.

## Test Signals
Testing should compare `hid-recorder`/debugfs descriptors before and after fixup, confirm `evtest` exposes six or eight buttons as appropriate for each listed device, verify BM084 no longer exposes the bogus horizontal wheel, and check that unsupported descriptor variants remain unmodified rather than corrupted.
