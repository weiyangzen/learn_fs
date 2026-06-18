# Research: sources/distributed-fs/ceph-client/drivers/media/radio/dsbr100.c

Purpose: USB V4L2 radio receiver driver for D-Link DSB-R100/Gemtek USB Radio 21. It controls only initialization, frequency, mute/on-off, and stereo-status reporting; audio remains analog through a sound card input.

Important types/APIs: `struct dsbr100_device` stores USB device, video/v4l2 devices, control handler, transfer buffer, lock, current frequency, stereo, and muted state. Device operations include `dsbr100_setfreq`, `dsbr100_start`, `dsbr100_stop`, `dsbr100_getstat`, V4L2 tuner/frequency ioctls, mute control, USB probe/disconnect, suspend/resume, and release.

Control flow: probe allocates device/buffer, registers V4L2 device and mute control, initializes video_device, stores `usb_set_intfdata`, defaults to muted at 87.5 MHz, and registers the radio node. Setting frequency clamps to 87.5-108 MHz and sends vendor control request `DSB100_TUNE` only if not muted. Mute toggles `DSB100_ONOFF`; unmute starts and retunes. Tuner status sends vendor GET_STATUS and interprets one bit as stereo. Disconnect mutes, unregisters the video node, marks V4L2 device disconnected, and drops the device reference.

State and persistence: current frequency, muted flag, and stereo flag are runtime memory; the USB device stores radio state while powered. No persistence after unplug.

Dependencies and integration: USB core, V4L2 radio/tuner controls, control events, mutex locking, and compatible USB VID/PID `04b4:1002`.

Risks: a single shared transfer buffer is protected by the video_device lock for file ops, but suspend/resume/disconnect must also take that lock. Signal strength is synthesized from stereo only. Test signals include `v4l2-compliance`, tune/mute suspend/resume cycles, disconnect during open file, and USB control-message error paths.
