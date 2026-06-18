# sources/distributed-fs/ceph-client/drivers/media/radio/radio-mr800.c

Purpose: implements a V4L2 USB radio driver for the AverMedia MR 800. The hardware provides tuning/control over USB while analog audio is handled outside this driver by a sound input path.

Important APIs and functions: USB entry points are `usb_amradio_probe`, `usb_amradio_disconnect`, suspend/resume callbacks, and the `module_usb_driver` registration. Device commands go through `amradio_send_cmd`; helpers include `amradio_set_mute`, `amradio_set_freq`, `amradio_set_stereo`, `amradio_get_stat`, `vidioc_s_hw_freq_seek`, and `usb_amradio_init`. V4L2 controls expose `V4L2_CID_AUDIO_MUTE`.

Control flow: probe allocates `struct amradio_device` and an 8-byte command buffer, registers a `v4l2_device`, creates the mute control, initializes mutex and video device metadata, stores USB interface data, sets a default frequency, initializes mute/stereo/frequency state, then registers `/dev/radioX`. V4L2 ioctls call command helpers under the video-device lock. Hardware seek programs search level, restarts from the cached current frequency, issues up/down search, polls the ready flag for up to 30 seconds, reads the found frequency, stops search, and reprograms the cached frequency.

State and persistence: per-device state tracks USB device/interface, V4L2 device/video device/control handler, shared transfer buffer, cached frequency, stereo preference, mute flag, and a mutex. State is volatile and freed by the V4L2 release callback after disconnect and last reference.

Dependencies and integration points: depends on USB bulk endpoints, HID-class USB ID matching, V4L2 radio ioctls, V4L2 controls/events, and analog audio routing outside the driver. Userspace sees hardware frequency seek support and a mute control.

Risks: endpoint numbers are hard-coded (`sndintpipe` 2 and receive pipe `0x81`) and not validated during probe. `vidioc_g_frequency` rejects calls unless `f->type` is already `V4L2_TUNER_RADIO`, which is stricter than many drivers. Seek uses a static 8-byte buffer and blocking polling; nonblocking callers are rejected. Suspend stores "was unmuted" by temporarily setting `muted` false after muting, which is subtle. Frequency conversion comments note occasional out-of-range search results.

Test signals: USB probe/disconnect while file handles are open, `v4l2-compliance`, mute/stereo/frequency command tracing, hardware seek success/timeout/interruption, suspend/resume restoring frequency and mute state, and fault injection for partial bulk transfers.
