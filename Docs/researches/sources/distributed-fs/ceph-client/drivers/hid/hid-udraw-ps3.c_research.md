# sources/distributed-fs/ceph-client/drivers/hid/hid-udraw-ps3.c

Purpose: implements a custom input driver for the THQ PS3 uDraw tablet, splitting one 27-byte raw HID report into four Linux input devices: joypad, touchpad, pen tablet, and accelerometer.

Important APIs, types, and functions: `struct udraw` stores four `input_dev` pointers, the HID device, and touch-position history for two-finger smoothing. `udraw_raw_event()` decodes button bits, d-pad direction, touch type, coordinates, pen pressure, and accelerometer axes. `allocate_and_setup()` creates common input devices with open/close callbacks. `udraw_setup_touch()`, `_pen()`, `_accel()`, and `_joypad()` define capabilities and ranges. `udraw_probe()` allocates state, parses HID, creates/registers input devices, and starts HID with HIDRAW plus driver connection.

Control flow: probe sets up all input nodes before `hid_hw_start()`. Each raw report of length 27 updates and syncs all four input devices, then returns `0` to leave HIDRAW/HIDDEV handling available. Open/close proxy to `hid_hw_open()` and `hid_hw_close()`.

State and persistence: state is devm-managed for device lifetime. Last one-finger and two-finger coordinates smooth unreliable two-finger reports. No persistent storage.

Dependencies and integration: depends on HID raw-event callbacks and input core. The ID table matches the THQ PS3 uDraw USB device.

Risks: `clamp_accel()` appears to divide by `(range * 0xFF)`, producing a very small normalized value; this may be intentional legacy behavior or a scaling bug. Input registration combines calls with `||`, so later registration errors collapse to boolean `1`. Report parsing is hard-coded to byte offsets and ignores other lengths.

Test signals: no automated tests. Validate with hardware by monitoring four input devices, checking pen pressure offset, touch transitions, d-pad/buttons, accelerometer motion, and HIDRAW availability.
