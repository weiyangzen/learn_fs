# sources/distributed-fs/ceph-client/drivers/hid/hid-lg2ff.c

## Purpose

`hid-lg2ff.c` provides memless rumble support for Logitech RumblePad/RumblePad 2 style devices selected by `LG_FF2` in `hid-lg.c`.

## Important APIs, Types, And Functions

`struct lg2ff_device` holds the output `hid_report` used for rumble commands. `lg2ff_init()` validates the first input device and output report 0 field 0 with at least seven values, allocates the private object, sets `FF_RUMBLE`, creates a memless FF device, initializes the report to a stop command, and sends it. `play_effect()` translates Linux `FF_RUMBLE` magnitudes into Logitech report bytes.

## Control Flow

`lg_probe()` starts HID hardware with generic FF disabled, then calls `lg2ff_init()`. Initialization uses the first HID input device as the FF device and stores `lg2ff_device` as memless callback data. On each rumble effect, strong and weak magnitudes are scaled from 16-bit input FF units to 8-bit device units. Nonzero rumble sends command `0x51` with weak in value index 2 and strong in index 4; zero rumble sends command `0xf3` with both magnitudes cleared. Each effect is sent with `hid_hw_request(..., HID_REQ_SET_REPORT)`.

## State And Persistence Behavior

The only private state is the allocated `lg2ff_device` referenced by input FF core. The output report object belongs to HID core. Hardware rumble state persists until another effect command or stop command is sent; initialization explicitly sends a stopped state.

## Dependencies And Integration Points

This file depends on Linux input force-feedback memless support, HID output reports, and the shared Logitech header. It is not a HID driver by itself; it is called by `hid-lg.c` for devices marked `LG_FF2`.

## Risks And Test Signals

Risks include assuming the first HID input is the desired gamepad, accepting only one fixed output report layout, and no explicit cleanup callback beyond input core lifetime. Test by probing RumblePad variants, verifying `FF_RUMBLE` appears in `ffbit`, playing weak/strong/combined effects through `fftest`, stopping effects, and checking malformed descriptors fail cleanly with `-ENODEV`.
