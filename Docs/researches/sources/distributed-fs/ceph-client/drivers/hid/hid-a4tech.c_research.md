# sources/distributed-fs/ceph-client/drivers/hid/hid-a4tech.c

## Purpose

`hid-a4tech.c` is a small HID quirk driver for A4Tech mice whose second wheel or horizontal wheel is not described in a standard HID-compatible way. It intercepts HID input mapping and event delivery so these devices expose normal Linux input events for vertical and horizontal high-resolution wheel movement.

The driver handles two quirk families. `A4_2WHEEL_MOUSE_HACK_7` treats usage `0x00090007` as an orientation selector for a later wheel event. `A4_2WHEEL_MOUSE_HACK_B8` treats the vendor-like Generic Desktop usage `0x000000b8` as a wheel-orientation report that follows a delayed wheel value.

## Important APIs, Types, and Functions

- `struct a4tech_sc` stores per-device quirk bits, current horizontal-wheel selector state, and a delayed wheel value for devices whose orientation arrives in a separate report.
- `a4_input_mapping()` suppresses direct mapping of the nonstandard `A4_WHEEL_ORIENTATION` usage for B8 devices.
- `a4_input_mapped()` adds `REL_HWHEEL` and `REL_HWHEEL_HI_RES` capabilities whenever the generic HID layer mapped `REL_WHEEL_HI_RES`, and suppresses the `0x00090007` selector usage for hack-7 devices.
- `a4_event()` is the main event translator. It consumes selector reports, delays or redirects wheel events, and emits horizontal or vertical wheel events through `input_event()`.
- `a4_probe()` allocates devres-backed state, stores `id->driver_data` quirks, parses the HID descriptor, and starts HID hardware with `HID_CONNECT_DEFAULT`.
- `a4_devices[]` maps four A4Tech USB product IDs to the two quirk modes.

## Control Flow

Probe is conventional: allocate `struct a4tech_sc`, copy quirk flags from the match table, attach it with `hid_set_drvdata()`, call `hid_parse()`, and call `hid_hw_start()`.

During input setup, `a4_input_mapping()` prevents the B8 orientation usage from becoming an input event of its own. After standard mapping, `a4_input_mapped()` makes sure the input device advertises horizontal wheel event bits if it has a high-resolution wheel and hides the hack-7 selector usage.

Runtime event control depends on the quirk. For B8 devices, a `REL_WHEEL_HI_RES` event is stored in `delayed_value` and consumed. When the subsequent `A4_WHEEL_ORIENTATION` event arrives, the driver emits either vertical `REL_WHEEL` and `REL_WHEEL_HI_RES` or horizontal `REL_HWHEEL` and `REL_HWHEEL_HI_RES` depending on the selector value. For hack-7 devices, the `0x00090007` usage sets `hw_wheel`; later `REL_WHEEL_HI_RES` events are rerouted to horizontal wheel events while that flag is set.

## State and Persistence Behavior

All state is per HID device and devm-owned for the device lifetime. `quirks` is fixed after probe. `hw_wheel` and `delayed_value` are mutable event-stream state used to correlate separate HID reports. There is no persistent storage, no sysfs configuration, and no cross-device state.

## Dependencies and Integration Points

- Uses the HID driver hooks `input_mapping`, `input_mapped`, `event`, and `probe`.
- Uses Linux input relative axes `REL_WHEEL`, `REL_WHEEL_HI_RES`, `REL_HWHEEL`, and `REL_HWHEEL_HI_RES`.
- Relies on vendor/product constants from `hid-ids.h`.
- Integrates with the generic HID input path by returning `1` for consumed events, `-1` for usages that should not be mapped, and `0` for default handling.

## Risks and Edge Cases

- B8 event pairing assumes the wheel delta arrives before the orientation usage. Reordered, dropped, or duplicated reports could cause stale `delayed_value` to be applied to the wrong orientation.
- `delayed_value * 120` assumes the delayed value is a low-resolution wheel unit. If the underlying value is already high-resolution on a future device, scaling would be wrong.
- Hack-7 `hw_wheel` is set from a selector value and not automatically cleared except by later selector events, so malformed streams can leave wheel events in horizontal mode.
- The driver adds horizontal capability bits whenever a high-resolution wheel is mapped, even if a future matched device does not actually report horizontal movement.
- There is no explicit locking around `a4tech_sc` event state. This relies on HID input event delivery ordering for a device.

## Test Signals

- Descriptor/input tests should confirm the nonstandard selector usages do not appear as user-visible input events.
- Event tests should feed B8 report sequences and verify vertical versus horizontal wheel output, including high-resolution scaling.
- Hack-7 tests should toggle usage `0x00090007` and confirm subsequent wheel deltas are rerouted only while selected.
- `evtest` or kernel HID selftests on matched device IDs should show `REL_HWHEEL` and `REL_HWHEEL_HI_RES` capabilities.
- Regression tests should verify unmatched HID usages still pass through default mapping and event handling.
