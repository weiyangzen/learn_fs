# sources/distributed-fs/ceph-client/drivers/hid/hid-sjoy.c

Purpose: supports SmartJoy PLUS and related PS2-to-USB adapters, including optional force-feedback rumble support when `CONFIG_SMARTJOYPLUS_FF` is enabled, plus device-specific HID quirks for multi-input and broken output reports.

Important APIs/types/functions: `struct sjoyff_device` stores the output report used for rumble. `hid_sjoyff_play()` maps Linux rumble magnitudes to the adapter's output fields. `sjoyff_init()` locates output reports per input device and creates memless force feedback. `sjoy_probe()` applies table quirks, parses HID, starts hardware without generic FF, and calls `sjoyff_init()`.

Control flow: probe ORs `id->driver_data` into `hdev->quirks`, parses the device, starts HID with `HID_CONNECT_DEFAULT & ~HID_CONNECT_FF`, then initializes driver-specific FF. FF setup walks each HID input and the output report list in tandem, validates at least one field and three values, allocates `sjoyff_device`, seeds output bytes, sends an initial SET_REPORT, sets `FF_RUMBLE`, and registers `input_ff_create_memless()`. A rumble effect scales strong magnitude to 0..255 and converts weak magnitude to an on/off bit, writes fields 1 and 2, and sends SET_REPORT.

State and persistence: when FF is enabled, each input device owns a small heap `sjoyff_device` as memless FF data and references a HID output report. The adapter output state persists in device firmware until overwritten. Without `CONFIG_SMARTJOYPLUS_FF`, no extra state is created.

Dependencies/integration: depends on HID core, Linux input FF, output-report lists, and vendor/product IDs for WiseGroup and Play.com adapters. Uses HID quirk flags `HID_QUIRK_NOGET`, `HID_QUIRK_MULTI_INPUT`, and `HID_QUIRK_SKIP_OUTPUT_REPORTS`.

Risks: FF initialization assumes output reports correspond to input devices by list order; devices with unexpected report ordering fail or rumble the wrong port. Allocated `sjoyff_device` lifetime is tied to input FF cleanup, so failures after allocation must free correctly. Probe ignores `sjoyff_init()` return value, so lack of FF does not prevent basic input. Devices marked skip-output-reports may not expose FF.

Test signals: all listed adapters should create correct numbers of input devices; quirked devices should avoid broken GET/output behavior; with FF enabled, rumble should change strong/weak motors as expected and stop on zero effect; missing output report should log but keep joystick input working.
