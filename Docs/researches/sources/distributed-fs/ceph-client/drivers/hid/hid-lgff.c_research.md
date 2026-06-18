# sources/distributed-fs/ceph-client/drivers/hid/hid-lgff.c

## Purpose

`hid-lgff.c` provides the older generic Logitech force-feedback backend for WingMan Cordless RumblePad, WingMan Force 3D, and related Logitech devices selected by `LG_FF` in the main driver. It supports rumble, constant force, and optional autocenter depending on product id.

## Important APIs, Types, And Functions

`struct dev_type` maps vendor/product ids to an FF capability list. Static capability arrays describe rumble-only, joystick constant-force, and joystick constant-force plus autocenter devices. `lgff_init()` validates input/report layout, selects capabilities from the table, sets input FF bits, creates a memless FF device, and assigns `hid_lgff_set_autocenter()` when supported. `hid_lgff_play()` writes device reports for `FF_CONSTANT` and `FF_RUMBLE`.

## Control Flow

After `hid-lg.c` starts HID hardware with generic FF disabled, it calls `lgff_init()` for `LG_FF` products. Initialization uses the first input device and output report 0 field 0 requiring at least seven values. If the product is not in the table, it defaults to constant-force joystick behavior. Runtime constant-force effects offset X/Y ramp levels by `0x7f`, clamp to 8-bit values, write command `0x51 0x08 x y`, and send the report. Rumble effects scale weak/strong magnitudes to 8-bit left/right values, write command `0x42`, and send the report. Autocenter writes a seven-byte `0xfe 0x0d` command with a 4-bit magnitude.

## State And Persistence Behavior

This backend does not allocate private per-device state. It writes directly into the first output report's value buffer. Hardware force/rumble/autocenter state persists until another report overwrites it or the device resets.

## Dependencies And Integration Points

It depends on Linux input memless FF, HID output reports, and the main Logitech driver for device matching and lifecycle. It is enabled by `CONFIG_LOGITECH_FF` through the declaration in `hid-lg.h`.

## Risks And Test Signals

Risks include defaulting unknown table matches to joystick constant-force, assuming the first input and first output report are correct, shared report buffer mutation without a private lock, and differing sign/centering conventions from FF3/FF4. Test with product-specific FF bit exposure, `fftest` rumble and constant force, autocenter magnitude changes, malformed report validation, and repeated start/stop effects.
