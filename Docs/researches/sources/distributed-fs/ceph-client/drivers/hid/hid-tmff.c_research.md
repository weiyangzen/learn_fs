# sources/distributed-fs/ceph-client/drivers/hid/hid-tmff.c

Purpose: adds force feedback support for older ThrustMaster HID devices, mainly rumble gamepads and force-feedback wheels, by finding a vendor output field and registering memless input FF playback.

Important APIs, types, and functions: `ff_rumble[]` and `ff_joystick[]` are per-device FF capability lists stored in `id->driver_data`. Under `CONFIG_THRUSTMASTER_FF`, `struct tmff_device` keeps the output report and force field. `tmff_scale_u16()` and `tmff_scale_s8()` map input effect ranges to the HID field logical range. `tmff_play()` handles `FF_CONSTANT` and `FF_RUMBLE`, writes two values into the output field, and sends `HID_REQ_SET_REPORT`. `tmff_init()` locates the output field with usage `HID_UP_GENDESK | 0xbb`, sets input FF bits, and calls `input_ff_create_memless()`.

Control flow: `tm_probe()` parses and starts HID with normal FF connection masked out, then calls `tmff_init()` with the matched effect list. If FF support is not compiled, `tmff_init()` is an inline no-op and the device remains a normal HID input device.

State and persistence: the only allocated runtime object is `tmff_device`, owned by the input FF subsystem as memless callback data after successful setup. No persistent storage exists. Device-specific behavior is captured by static ID table entries and the special motor swap for product `0xb320`.

Dependencies and integration: depends on HID report enumeration, input force-feedback APIs, HID output requests, and `hid-ids.h`. It registers a `hid_driver` named `thrustmaster`.

Risks: `tm_probe()` ignores the return value from `tmff_init()`, so FF setup failures do not fail device probing. Output report parsing is strict about duplicate fields and field size but logs unknown output usages. Range conversion assumes two field values and correct descriptor logical min/max.

Test signals: no KUnit tests. Validation should inspect input FF capabilities and exercise rumble/constant effects with tools such as `fftest`, while checking report writes on real listed hardware.
