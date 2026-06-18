# sources/distributed-fs/ceph-client/drivers/hid/wacom_wac.h

## Purpose
`wacom_wac.h` defines the shared constants, packet/report IDs, Wacom vendor HID usage values, device type taxonomy, quirk flags, feature records, and runtime state structures used by the Wacom HID driver. It is the contract between the Wacom-specific decoder in `wacom_wac.c` and the broader driver in `wacom.h` / other Wacom implementation files.

## Important APIs, Types, and Fields
- Packet length defines such as `WACOM_PKGLEN_BBFUN`, `WACOM_PKGLEN_BBTOUCH3`, `WACOM_PKGLEN_WIRELESS`, and `WACOM_BYTES_PER_MT_PACKET` are used by raw IRQ routing.
- Device/report IDs include stylus/touch/cursor/eraser/pad IDs and report numbers like `WACOM_REPORT_PENABLED`, `WACOM_REPORT_INTUOSPAD`, `WACOM_REPORT_REMOTE`, `WACOM_REPORT_DEVICE_LIST`, and `WACOM_REPORT_USB`.
- Command report IDs include LED, icon transfer, pairing, and wireless Intuos commands.
- Quirk flags include low-resolution Bamboo touch, `SENSE`, AES pen, battery, tool serial, and inferred third pen button behavior.
- Vendor HID usage constants cover Wacom digitizer, touch, G9/G11 pages, serial high bits, tool type, distance, touch strips/rings, mute/touch switches, battery, accelerometer, offsets, mode changes, and ExpressKeys.
- Field-class macros `WACOM_BATTERY_USAGE()`, `WACOM_PAD_FIELD()`, `WACOM_PEN_FIELD()`, `WACOM_FINGER_FIELD()`, and `WACOM_DIRECT_DEVICE()` categorize HID fields for mapping/event dispatch.
- The enum assigns integer device families from `PENPARTNER` through `HID_GENERIC`, `BOOTLOADER`, and `MAX_TYPE`.
- `struct wacom_features` stores static/probed capabilities: name, axis maxima/resolution/fuzz, pressure/distance, type, button count, offsets, device type bitmask, physical units, quirks, touch max, paired product IDs, packet length, and HID-type filters.
- `struct wacom_shared` stores cross-interface pen/touch/wireless state.
- `struct hid_data` stores per-report and persistent HID-generic decode state.
- `struct wacom_wac` is the central per-interface runtime object containing names, data buffer, tool IDs, serials, feature state, input devices, FIFOs, Bluetooth flags, ring counters, mode state, and `hid_data`.

## Control Flow Role
The header does not execute control flow itself, but it shapes all Wacom dispatch. Raw packet handlers branch on enum `features.type` and packet length constants. HID-generic mapping and event paths rely on the usage classification macros and Wacom usage constants. Probe/setup code uses `struct wacom_features` to decide which input devices to allocate and which capabilities to expose; report handlers update `struct wacom_wac` and `struct wacom_shared` fields across callbacks.

## State and Persistence
All structures defined here are volatile kernel runtime state. `struct wacom_features` begins from static table data but is modified during probe by HID descriptors and quirks. `struct hid_data` is intentionally mutable across report callbacks. `struct wacom_shared` enables multiple HSI/HID interfaces or paired pen/touch devices to share arbitration and device references. No disk persistence is defined.

## Dependencies and Integration Points
The header depends on `linux/types.h`, `linux/hid.h`, and `linux/kfifo.h`. Its constants map directly to HID usages, Linux input event codes, HSI-independent Wacom command reports, and local Wacom driver work. It is included by `wacom_wac.c` and other Wacom driver files that need feature and state definitions.

## Risks and Edge Cases
- The device enum order is semantically significant because source code uses range comparisons such as `type >= INTUOS5S && type <= INTUOSPL`; inserting new values in the wrong place can break family checks.
- Usage-classification macros are broad and order-sensitive; `wacom_wac_usage_mapping()` checks battery, pad, pen, then finger.
- Struct fields such as `offset_*`, `oVid/oPid`, `pktlen`, and `check_for_hid_type` drive probe-time pairing and filtering; incorrect defaults can expose the wrong input device.
- `WACOM_MAX_REMOTES`, packet lengths, and `touch_max` values need to align with buffer sizes and multitouch slot allocation in the C implementation.

## Test Signals
- Compile tests should catch missing constants and struct layout users.
- Runtime descriptor tests should verify field classifiers put vendor usages in the expected battery/pad/pen/finger paths.
- Device table additions should be checked for enum range assumptions, `touch_max`, paired product IDs, and packet length compatibility.
