# sources/distributed-fs/ceph-client/drivers/hid/hid-accutouch.c

## Purpose

`hid-accutouch.c` is a minimal HID driver for Elo Accutouch touchscreens. Its only behavior is to remap any HID Button-page usage to `BTN_TOUCH`, making the touchscreen contact state visible through the Linux input touchscreen button convention.

## Important APIs, Types, and Functions

- `accutouch_input_mapping()` checks `usage->hid & HID_USAGE_PAGE` and maps all Button-page usages to `EV_KEY/BTN_TOUCH` with `hid_map_usage()`.
- `accutouch_devices[]` matches the Elo Accutouch 2216 USB device ID.
- `accutouch_driver` installs only the `input_mapping` hook; parsing, hardware start, input registration, and event handling are left to the HID core.

## Control Flow

When a matching device is bound, the generic HID core performs standard driver setup because this driver has no custom probe. During HID input mapping, each usage is passed to `accutouch_input_mapping()`. Button-page usages are consumed and mapped to `BTN_TOUCH`; all other usages return `0` so the generic HID mapping path handles them normally.

At runtime, events follow the standard HID input path. Since button usages were mapped to `BTN_TOUCH`, presses and releases are reported as touchscreen contact changes instead of generic mouse or button events.

## State and Persistence Behavior

The file defines no private state and stores no persistent data. All runtime state is maintained by the HID core and input subsystem. The behavior is entirely static based on the device ID and usage page.

## Dependencies and Integration Points

- Depends on Linux HID and module infrastructure.
- Uses `hid_map_usage()` and input event constants `EV_KEY` and `BTN_TOUCH`.
- Uses Elo vendor and product IDs from `hid-ids.h`.
- Integrates with generic HID through the `input_mapping` callback and `module_hid_driver()`.

## Risks and Edge Cases

- Mapping every Button-page usage to `BTN_TOUCH` is intentionally broad. If a future Accutouch descriptor exposes more than one button with distinct meanings, they will all collapse to the same key.
- The driver assumes the generic HID core already maps axes and other touch metadata adequately.
- There is no custom validation of report shape, so unusual firmware descriptors rely entirely on HID core behavior.
- The `MODULE_AUTHOR` string is missing a closing angle bracket in the email text; this is cosmetic but visible in module metadata.

## Test Signals

- A descriptor-level test should verify Button-page usages become `BTN_TOUCH`.
- Runtime testing with an Accutouch 2216 should show contact press/release events on `BTN_TOUCH` with expected absolute position events from generic HID.
- Regression tests should confirm non-button usages still use generic HID mappings.
- Build/module tests should confirm the device ID table exports through `MODULE_DEVICE_TABLE(hid, ...)`.
