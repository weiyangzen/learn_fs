# Research: sources/distributed-fs/ceph-client/drivers/media/radio/radio-ma901.c

Purpose: USB V4L2 radio receiver driver for the Masterkit MA901 FM radio. It controls frequency, volume, and mono/stereo mode for a V-USB HID-class device with analog audio output.

Important types/APIs: `struct ma901radio_device` stores USB/interface, video/V4L2/control objects, report buffer, mutex, current frequency, volume, stereo mode, and muted flag. Core routines are `ma901radio_set_freq`, `ma901radio_set_volume`, `ma901_set_stereo`, tuner/frequency/control ioctls, USB probe/disconnect, no-op suspend/resume, and release.

Control flow: probe filters a generic VID/PID by product/manufacturer strings, allocates state/buffer, registers V4L2 and a volume control, initializes video_device, stores V4L2 device in USB interface data, defaults current frequency to about 95.21 MHz, and registers the radio node without querying hardware. Setting frequency/volume/stereo fills an 8-byte command report and sends USB control request 9 with type 0x21 and value 0x0300.

State and persistence: driver caches frequency, volume, and stereo mode; comments note the radio has device memory and continues playing if USB power remains. No persistent software state.

Dependencies and integration: USB HID-class matching, V4L2 tuner/radio APIs, volume controls. Risks include generic V-USB ID collisions, unimplemented mute/statistics, no real suspend/resume restoration, and `g_frequency` not setting `f->type`. Test signals include product/manufacturer filtering, frequency clamp, volume control, mono/stereo ioctl behavior, unplug while open, and `v4l2-compliance`.
