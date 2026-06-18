# sources/distributed-fs/ceph-client/drivers/hid/hid-saitek.c

Purpose: implements Saitek/Mad Catz HID quirks for the PS1000 gamepad and R.A.T./M.M.O. gaming mice. It fixes a broken PS1000 report descriptor and converts mode-button state changes on several mice into normal press/release input events.

Important APIs/types/functions: `struct saitek_sc` stores `quirks` and previous `mode`. Quirk bits are `SAITEK_FIX_PS1000`, `SAITEK_RELEASE_MODE_RAT7`, and `SAITEK_RELEASE_MODE_MMO7`. Main callbacks are `saitek_probe`, `saitek_report_fixup`, `saitek_raw_event`, and `saitek_event`.

Control flow: probe allocates driver data, records `id->driver_data`, initializes mode to `-1`, parses HID, and starts hardware. Descriptor fixup checks the exact PS1000 descriptor size and byte pattern, converts a spurious axis item into a no-op logical minimum, and clears constant bits for buttons/d-pad. Raw-event handling for R.A.T. devices reads the mode bits from the report, clears those bits so they do not stay permanently pressed, and injects one chosen mode bit only when the mode changes after the initial state. The `.event` callback sees that synthetic press and immediately reports a release to compensate for missing hardware release events.

State and persistence: only per-device `mode` persists across reports. No sysfs, files, or power-supply state is created. Descriptor edits persist only for the parsed in-memory HID descriptor.

Dependencies/integration: depends on HID core parse/start, report-fixup and raw-event hooks, input event reporting, `hid-ids.h` vendor/product IDs, and standard mouse button code offsets relative to `BTN_MOUSE`.

Risks: raw-event logic is size- and bit-position-sensitive (`size == 7` for R.A.T.7-style, `size == 8` for M.M.O.7). New firmware variants with different layouts will bypass or be corrupted by the mapping. The event callback assumes specific button offsets for mode buttons. PS1000 fixup is exact-pattern guarded, which is safe but leaves unknown descriptors untouched.

Test signals: PS1000 descriptor should expose working buttons and d-pad; mode cycling on each listed R.A.T./M.M.O. mouse should generate one button click per mode transition with no stuck buttons; initial mode report should not create a false click; unrelated reports should pass through unchanged.
