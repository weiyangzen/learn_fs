<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/hdpvr/hdpvr-core.c -->
# sources/distributed-fs/ceph-client/drivers/media/usb/hdpvr/hdpvr-core.c

Purpose: USB probe/disconnect and device initialization for the Hauppauge HD PVR driver. It owns module parameters, USB ID matching, firmware authorization, endpoint discovery, initial option programming, buffer allocation, optional I2C/IR setup, and video-node registration.

Important APIs/types/functions: `hdpvr_probe()` is the main USB bind path. `hdpvr_disconnect()` tears down active I/O and registered interfaces. `hdpvr_device_init()` performs firmware authorization and initial hardware setup. `device_authorization()` reads status/firmware data and sends the challenge response. `challenge()` mutates the firmware challenge bytes. `hdpvr_delete()` releases stream buffers and the USB device reference. Module parameters include `video_nr`, `hdpvr_debug`, `default_video_input`, `default_audio_input`, and `boost_audio`.

Control flow: probe allocates `struct hdpvr_device`, registers a V4L2 device early for logging, initializes locks/waitqueues/control-transfer buffer/default options, discovers the bulk-in endpoint, authorizes the device, sends default options/filter/fan/audio-boost requests, allocates 64 USB transfer buffers, registers I2C and IR when enabled, assigns a device number, then calls `hdpvr_register_videodev()`. Disconnect marks status disconnected under `io_mutex`, wakes readers and buffer submitter, calls `v4l2_device_disconnect()`, flushes work, cancels queued URBs, unregisters I2C and video device, and decrements the device count.

State and persistence: persistent runtime state is `struct hdpvr_device`: USB handle, V4L2/video structures, options, firmware version/capability flags, bulk endpoint geometry, status, queue lists, waitqueues, I2C adapter, and shared control buffer. Firmware programming persists on the hardware until reset or reconfigured. No on-disk state exists.

Dependencies and integration: uses USB core, V4L2 device/common helpers, Linux I2C when enabled, and the HD-PVR control/video/I2C functions. It binds Hauppauge USB IDs `2040:4900/4901/4902/4903/4982` and registers through `module_usb_driver()`.

Risks: the `dev_nr` atomic is a monotonically incremented slot counter decremented on disconnect, so device-number reuse under out-of-order disconnects is coarse. `device_authorization()` uses `dev->usbc_buf[46]` after allocating 64 bytes, which is safe but depends on the fixed allocation. Probe error paths must stay aligned with whether I2C adapter/client registration succeeded; video release also unregisters I2C, so double-delete risks require path review. Firmware challenge behavior is opaque and hardware-version sensitive.

Test signals: probe each supported USB ID; run with default input/audio module parameters; check firmware version/capability logging; test no-bulk-endpoint and authorization failure paths with fault injection; plug/unplug during read streaming; verify no URB or I2C adapter leaks under repeated bind/unbind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/hdpvr/hdpvr-core.c -->
