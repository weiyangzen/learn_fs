<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/si4713/radio-platform-si4713.c -->
# sources/distributed-fs/ceph-client/drivers/media/radio/si4713/radio-platform-si4713.c

Purpose: platform-device V4L2 radio wrapper for an Si4713 I2C subdevice. It registers a `/dev/radio*` transmitter node and forwards user-facing V4L2 modulator/frequency/private ioctl operations to the Si4713 subdevice.

Important APIs and functions: module parameter `radio_nr` selects the radio minor. `struct radio_si4713_device` owns `v4l2_device`, `video_device`, and a mutex. File ops use `v4l2_fh_open`, `v4l2_fh_release`, `v4l2_ctrl_poll`, and `video_ioctl2`. Ioctl callbacks include `radio_si4713_querycap`, `g/s_modulator`, `g/s_frequency`, `vidioc_default`, event subscription, and control log status. Platform lifecycle is `radio_si4713_pdriver_probe` and `radio_si4713_pdriver_remove`.

Control flow: probe requires `struct radio_si4713_platform_data` containing the I2C client. It allocates wrapper state, registers a V4L2 device, obtains the subdevice via `i2c_get_clientdata`, registers the subdev with the wrapper V4L2 device, initializes a `video_device` from a template, attaches the subdev control handler, sets TX/RDS capabilities, and registers a radio node. Ioctls use `v4l2_device_call_until_err` to dispatch to subdevice tuner/core ops. Remove unregisters the video node and V4L2 device.

State and persistence: wrapper state is transient and devm-managed. Persistent hardware state remains in the I2C subdevice and Si4713 chip. The wrapper mutex serializes video-device access while the core driver maintains chip/control state.

Dependencies and integration points: depends on platform devices, I2C client data, V4L2 device/video/fh/control/event APIs, and `si4713.h`. It is instantiated either by board/platform data or by the core I2C driver allocating a `radio-si4713` platform device.

Risks: probe cannot proceed without platform data, so device-tree or board flows must create the expected handoff. `platform_get_drvdata` relies on `v4l2_device_register` setting drvdata through the device model; unexpected changes in V4L2 registration behavior would break remove. The wrapper has no direct hardware recovery path; subdevice errors propagate to userspace.

Test signals: platform probe/remove, `/dev/radio*` creation, `VIDIOC_QUERYCAP`, frequency/modulator get/set propagation, RDS control event polling, and teardown with the underlying I2C client removed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/radio/si4713/radio-platform-si4713.c -->
