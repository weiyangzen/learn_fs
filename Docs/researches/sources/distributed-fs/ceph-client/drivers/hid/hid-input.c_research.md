# sources/distributed-fs/ceph-client/drivers/hid/hid-input.c

## Purpose

`hid-input.c` is the generic HID-to-Linux-input bridge. It walks parsed HID reports, maps HID usages into `input_dev` event capabilities, creates one or more input devices for a HID device, dispatches incoming HID values into input events, manages output-report LEDs, exposes keymap get/set callbacks, negotiates resolution multipliers, and optionally registers HID battery usages as `power_supply` devices.

## Important APIs, Types, and Functions

- `hidinput_connect(struct hid_device *hid, unsigned int force)`: top-level input registration path. It initializes `hid->inputs` and LED work, runs feature/battery mapping, configures input/output report usages, adjusts resolution multipliers, and registers populated `input_dev` instances.
- `hidinput_disconnect(struct hid_device *hid)`: unregisters/free input devices and cancels pending LED work.
- `hidinput_hid_event(...)`: value-level dispatch from HID core to input core. It handles power-supply updates, hat switches, digitizer tool state, high-resolution wheels, relative volume emulation, absolute inversion quirks, MSC scan events, and relative-key release synthesis.
- `hidinput_report_event(...)`: emits `input_sync()` for each input device unless `HID_QUIRK_NO_INPUT_SYNC` is set.
- `hidinput_configure_usage(...)`: central usage-to-event mapper. It covers keyboard, button, simulation, generic desktop, LED, digitizer, telephony, consumer, battery, camera, HP vendor, PID, and fallback pages, while giving HID drivers `input_mapping` and `input_mapped` hooks.
- `hidinput_calc_abs_res(...)`: exported helper that derives input-axis resolution from HID logical/physical extents and units, including cm/inch, radians/degrees, and gram/newton conversion.
- LED helpers: `hidinput_get_led_field`, `hidinput_count_leds`, `hidinput_find_field`, `hidinput_led_worker`, and `hidinput_input_event`.
- Battery helpers under `CONFIG_HID_BATTERY_STRENGTH`: `hidinput_setup_battery`, `hidinput_update_battery`, query/scaling helpers, quirk table, and `hidinput_get_battery_property`.
- Device construction helpers: `hidinput_allocate`, `hidinput_match`, `hidinput_match_application`, `hidinput_configure_usages`, and cleanup helpers.

## Control Flow

Connection starts by rejecting non-input devices unless forced. Feature reports are scanned first so feature-backed battery strength and driver-specific feature mappings are available. Input and output reports are then walked; depending on quirks, reports are grouped by report id, by application, or into a default input device. Each field is tagged with a multi-touch slot index when a collection contains `HID_DG_CONTACTID`, then every usage is configured.

Generic mapping first lets the specific HID driver override or suppress a usage. Otherwise it maps by usage page and usage id, sets event bits, resolves duplicate codes, sets absolute parameters/resolution, creates hat-switch paired axes, and records `EV_MSC/MSC_SCAN` support for keys. Populated inputs are passed through the driver's `input_configured` hook and registered; empty ones are discarded.

Runtime events arrive through `hidinput_hid_event`. Power usages update `struct hid_battery`; normal usages are clamped or ignored according to HID null-state rules, transformed for digitizer tool state and scroll handling, filtered when unchanged, and sent via `input_event`. Report completion calls `hidinput_report_event`, which synchronizes all input devices for the HID device.

Output events from input userspace enter `hidinput_input_event`. Force-feedback events are delegated to `input_ff_event`; LED events update the matching HID output field and schedule `hidinput_led_worker`, which sends a HID output or set-report request.

## State and Persistence Behavior

Persistent state is attached to `struct hid_device`: the `hid->inputs` list, `hid->batteries`, `led_work`, quirk bits, report field mappings, and resolution multiplier state. Each `struct hid_input` owns one `input_dev`, optional generated name, application id, registration flag, and associated report list. Each `struct hid_usage` is mutated with input `type`, `code`, priority, hat metadata, wheel accumulator, and resolution multiplier.

Battery state persists in `struct hid_battery` instances allocated with devres: min/max, report id/type, capacity, status, presence, charge status, avoid-query flag, and rate-limit timestamp. LED state persists in HID output field values and is sent asynchronously through workqueue context. No file-backed persistence exists; all state is rebuilt on device re-probe or reset-resume.

## Dependencies and Integration Points

This file depends on HID core report parsing, HID driver hooks (`input_mapping`, `input_mapped`, `feature_mapping`, `input_configured`), input core APIs, power-supply APIs when enabled, workqueues, low-level HID request/output callbacks, KUnit test inclusion under `CONFIG_HID_KUNIT_TEST`, and constants from `linux/hid.h`, `linux/input.h`, and `hid-ids.h`. It exports several helpers for other HID code, including LED-field lookup/counting and report synchronization.

## Risks and Edge Cases

- Usage mapping is intentionally broad and highly compatibility-sensitive; changes can alter userspace-visible event codes for many devices.
- Duplicate-code suppression can silently ignore usages unless `HID_QUIRK_INCREMENT_USAGE_ON_DUPLICATE` is set.
- Descriptor-derived logical/physical ranges and units are trusted after limited sanity checks; malformed descriptors can yield missing resolution, ignored axes, or bad input ranges.
- Battery querying assumes small raw reports and may block in property reads unless the device is marked avoid-query.
- LED output work reads report fields without the HID core lock by design; it relies on later queued workers to converge if userspace races LED updates.
- Digitizer tool ordering depends on usage priorities and report ordering. Regressions can leave stale `BTN_TOOL_*` or `BTN_TOUCH` state.
- `hidinput_connect` has a broad unwind path; newly added allocation or registration work must be covered by `hidinput_disconnect` or explicit cleanup.

## Test Signals

Useful signals include `CONFIG_HID_KUNIT_TEST` coverage for mapping and resolution helpers, hid-tools replay tests for keyboards, mice, tablets, remotes, multi-touch devices, and high-resolution wheels, power-supply tests for report and feature battery devices, lockdep/workqueue checks around LED updates and disconnect, reset-resume tests for resolution multipliers, and userspace-visible event regression tests for duplicate usages, keymap remapping, digitizer eraser/in-range behavior, hat switches, and relative volume controls.
