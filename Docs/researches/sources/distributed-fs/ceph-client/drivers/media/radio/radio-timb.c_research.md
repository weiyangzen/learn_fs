# sources/distributed-fs/ceph-client/drivers/media/radio/radio-timb.c

Purpose: implements a platform V4L2 radio wrapper for Timberdale FPGA designs. It delegates actual tuner and DSP behavior to I2C V4L2 subdevices described by platform data.

Important APIs and functions: platform lifecycle is `timbradio_probe` and `timbradio_remove`. V4L2 ioctl wrappers are `timbradio_vidioc_querycap`, tuner get/set, and frequency get/set, all forwarding to `sd_tuner` except querycap. File operations use standard V4L2 fh open/release/poll/ioctl paths.

Control flow: probe requires `timb_radio_platform_data`, allocates managed `struct timbradio`, copies platform data, initializes a mutex and video device, registers a standalone V4L2 device, creates tuner and DSP I2C subdevices on the configured adapter, assigns the DSP control handler to the parent V4L2 device, registers the radio video node, and stores driver data. Ioctls route tuner/frequency calls to the tuner subdevice via `v4l2_subdev_call`.

State and persistence: state is device-managed memory containing copied platform data, tuner/DSP subdevice pointers, video/V4L2 objects, and mutex. Persistence depends on child devices; this wrapper does not cache frequency or tuner state.

Dependencies and integration points: depends on platform data from `linux/platform_data/media/timb_radio.h`, I2C adapters, V4L2 subdevice registration helpers, and child tuner/DSP drivers. It integrates the DSP controls into the parent radio node by reusing `sd_dsp->ctrl_handler`.

Risks: `i2c_get_adapter` return values are not checked or released, which can leak adapter references or fail unclearly. Probe registers the V4L2 device with NULL parent rather than `&pdev->dev`. There is no explicit cleanup of child subdevices beyond `v4l2_device_unregister`. Missing platform data is fatal.

Test signals: platform-device instantiation with valid/invalid platform data, missing I2C adapter behavior, tuner/DSP subdevice creation, forwarded tuner/frequency ioctls, DSP controls on the parent node, remove cleanup, and `v4l2-compliance` with the actual subdevices.
