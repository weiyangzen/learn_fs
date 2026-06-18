# sources/distributed-fs/ceph-client/drivers/hid/hid-holtekff.c

Adds rumble support for Holtek On Line Grip based gamepads using a device-specific seven-byte output-report protocol.

`struct holtekff_device` stores the output `hid_field`. `holtekff_send()` copies command bytes into the field and sends `HID_REQ_SET_REPORT`. `holtekff_play()` maps strong/weak rumble into left/right enable bits and a four-bit combined magnitude, sends effect parameters, then sends a start command; zero magnitudes send stop-all. `holtekff_init()` validates output report layout, sends initialization stop commands, sets `FF_RUMBLE`, and registers memless FF. `holtek_probe()` starts HID with default FF disabled and initializes custom FF.

State is only the allocated field pointer passed to input FF. Hardware effect state is live and reset by stop commands. Dependencies include HID core, input FF, optional `CONFIG_HOLTEK_FF`, and Holtek IDs from `hid-ids.h`.

Risks include partially understood protocol fields, exact seven-value report expectations, and ignored FF init errors in probe. Test signals include config enabled/disabled behavior, report validation, zero stop, left/right bits, magnitude saturation, and initialization command sequence.
