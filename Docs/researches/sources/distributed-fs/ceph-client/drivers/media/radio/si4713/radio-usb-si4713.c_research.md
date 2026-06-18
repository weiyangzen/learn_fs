<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/si4713/radio-usb-si4713.c -->
# sources/distributed-fs/ceph-client/drivers/media/radio/si4713/radio-usb-si4713.c

Purpose: USB wrapper for Silicon Labs Si4713 FM transmitter development boards. It reverse-engineers the board's HID control protocol into an emulated I2C adapter, instantiates the common Si4713 I2C subdevice, and exposes a V4L2 radio transmitter node.

Important APIs and functions: `struct si4713_usb_device` owns USB interface/device pointers, V4L2 video/device state, a subdevice pointer, mutex, I2C adapter, and a shared 64-byte buffer. USB setup uses `si4713_start_seq`, `si4713_send_startup_command`, `start_seq`, `command_table`, `send_command`, `si4713_i2c_read`, `si4713_i2c_write`, `si4713_transfer`, and `si4713_register_i2c_adapter`. V4L2 ioctls forward querycap, modulator, frequency, log status, and control events. USB lifecycle is `usb_si4713_probe` and `usb_si4713_disconnect`.

Control flow: probe validates the USB ID/interface, allocates state and buffer, stores V4L2 data in the USB interface, sends the required startup command sequence, registers a V4L2 device, registers the synthetic I2C adapter, creates the Si4713 I2C subdevice with board info at `SI4713_I2C_ADDR_BUSEN_HIGH`, binds the subdevice control handler into the video device, and registers a radio transmitter node. I2C writes map the first command byte to USB framing metadata, while reads poll USB control responses until status is valid or a long USB timeout expires. Disconnect unregisters the video device, marks the V4L2 device disconnected, and drops the final reference so the release callback removes the I2C adapter and frees memory.

State and persistence: runtime state is in `si4713_usb_device` and the shared control buffer. The emulated I2C adapter is persistent only for the USB device lifetime. The startup sequence changes board firmware/device state so later Si4713 power-up commands succeed; no settings survive driver unload except device firmware state.

Dependencies and integration points: depends on USB core, V4L2 device/video/control/event APIs, I2C adapter emulation, and the common `si4713` I2C subdevice. It binds `10c4:8244` HID-class devices and exposes `V4L2_CAP_MODULATOR | V4L2_CAP_RDS_OUTPUT`.

Risks: the command/startup protocol is reverse-engineered and order-sensitive. The shared buffer is reused for send and receive and is protected only by the video-device mutex in normal userspace paths. `si4713_i2c_read` returns success with `data[0] = 0` on timeout so the core driver sees CTS missing rather than a transport error. `si4713_start_seq` continues through the entire sequence and returns only the final command status, so earlier startup failures can be overwritten by later success.

Test signals: USB probe on `10c4:8244`, startup command trace matching expected Windows-derived sequence, synthetic I2C subdevice creation, V4L2 frequency/modulator/RDS controls, disconnect while open, and USB timeout/error injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/si4713/radio-usb-si4713.c -->
