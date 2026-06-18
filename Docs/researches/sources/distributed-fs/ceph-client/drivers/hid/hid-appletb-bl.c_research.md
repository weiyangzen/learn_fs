# sources/distributed-fs/ceph-client/drivers/hid/hid-appletb-bl.c

## Purpose

`hid-appletb-bl.c` is a backlight driver for the Touch Bar backlight endpoint on T2-era MacBook Pro systems. It binds to the Apple Touch Bar backlight HID device, locates the required HID feature report fields, and exposes brightness control through the Linux backlight subsystem.

## Important APIs, Types, and Functions

- Module parameter `brightness` sets default startup brightness: off, dim, or full. Values above 2 are clamped to full brightness during probe.
- `struct appletb_bl` stores the auxiliary field, brightness field, registered `backlight_device`, and whether the HID device is currently powered full-on.
- `appletb_bl_brightness_map[]` maps backlight core levels `0..2` to device protocol values `APPLETB_BL_OFF`, `APPLETB_BL_DIM`, and `APPLETB_BL_ON`.
- `appletb_bl_set_brightness()` sets the auxiliary field to `1`, writes the brightness field, powers the HID device to `PM_HINT_FULLON` when needed, sends the feature report, and drops back to `PM_HINT_NORMAL` when brightness is off.
- `appletb_bl_update_status()` translates backlight blanking and brightness into device protocol values.
- `appletb_bl_probe()` parses the HID descriptor, finds the required feature fields, starts and opens HID hardware, sets default brightness, and registers a raw backlight device.
- `appletb_bl_remove()` turns the Touch Bar backlight off, closes hardware, and stops HID hardware.

## Control Flow

Probe starts by parsing the HID descriptor. It searches feature reports on vendor page `0xff120001` for usages `0xff120020` and `0xff120021`, corresponding to the auxiliary and brightness controls. Both fields must exist and belong to the same report. After allocating state, the driver starts HID hardware in `HID_CONNECT_DRIVER` mode, opens it, writes the default brightness through `appletb_bl_set_brightness()`, and registers `appletb_backlight` with `BACKLIGHT_RAW` type and maximum brightness `2`.

Backlight core calls `appletb_bl_update_status()` whenever brightness or blanking changes. Blanking forces the device brightness protocol value to off; otherwise the core brightness index selects off, dim, or full from the map. Report transmission is synchronous enough to return errors from field setting and power-on, but `hid_hw_request()` itself is fire-and-forget in this code path.

Remove turns brightness off using the same report path, then closes and stops HID hardware.

## State and Persistence Behavior

The private state is devm-managed for the HID device lifetime. `full_on` tracks whether the driver has requested full power; it avoids redundant `PM_HINT_FULLON` calls and is cleared after setting brightness off and requesting normal power. The backlight device persists until devres cleanup. There is no persistent brightness storage in this file; startup brightness comes from the read-only module parameter.

## Dependencies and Integration Points

- Uses HID descriptor parsing, `hid_find_field()`, `hid_set_field()`, `hid_hw_power()`, `hid_hw_request()`, `hid_hw_start()`, `hid_hw_open()`, close, and stop.
- Integrates with the Linux backlight subsystem through `devm_backlight_device_register()` and `backlight_ops`.
- Uses power-management hints to keep the HID endpoint awake while nonzero brightness is active.
- Matches `USB_DEVICE_ID_APPLE_TOUCHBAR_BACKLIGHT` from `hid-ids.h`.
- Provides `BL_CORE_SUSPENDRESUME` so the backlight core calls update paths across suspend/resume.

## Risks and Edge Cases

- The module parameter is an `int`; negative values are not clamped before indexing `appletb_bl_brightness_map`, so a negative `brightness` parameter could index before the array during probe.
- The driver validates that both fields share a report but does not validate field logical ranges. Unexpected descriptors could accept `hid_set_field()` but not behave as intended.
- `hid_hw_request()` has no return value here, so transport failures after field staging are not reported to the backlight core.
- Remove calls `appletb_bl_set_brightness()` and ignores errors, which is reasonable for teardown but can leave hardware lit if the device stops responding.
- Power-state tracking relies on this driver being the only actor controlling the endpoint power hint.

## Test Signals

- Probe tests should verify missing fields, split reports, HID start/open failures, default brightness writes, and backlight registration.
- Parameter tests should cover brightness values 0, 1, 2, values greater than 2, and negative values to expose the lower-bound indexing risk.
- Backlight tests should verify blanking maps to off and normal updates map indices to off/dim/on protocol values.
- Power-management tests should confirm nonzero brightness requests `PM_HINT_FULLON`, off requests `PM_HINT_NORMAL`, and suspend/resume invokes update status.
- Device tests on supported MacBook Pro hardware should observe `/sys/class/backlight/appletb_backlight` brightness changes reflected on the Touch Bar backlight.
