# sources/distributed-fs/ceph-client/drivers/media/usb/go7007/go7007-usb.c

Purpose: runtime USB transport for GO7007 boards. It contains board descriptors, USB ID matching, HPI operations, optional EZ-USB I2C support, URB allocation, stream start/stop, firmware download transport, and disconnect cleanup.

Important APIs and functions: `go7007_usb_probe()` allocates `struct go7007` and `struct go7007_usb`, selects a board descriptor, prepares interrupt/video/audio URBs, boots the encoder, creates optional I2C adapters, probes board variants, and registers the encoder. HPI callbacks include `go7007_usb_interface_reset()`, `go7007_usb_ezusb_write_interrupt()`, `go7007_usb_onboard_write_interrupt()`, `go7007_usb_read_interrupt()`, `go7007_usb_stream_start()`, `go7007_usb_stream_stop()`, `go7007_usb_send_firmware()`, and `go7007_usb_release()`.

Control flow: probe selects static board metadata from `driver_info`, boots the device, detects special XMen/Pelco/Adlink and TV402U tuner variants, checks USB speed, allocates bulk/interrupt endpoints, then hands off to core registration. Streaming submits eight video URBs and, when enabled, eight audio URBs. Completion callbacks parse video into V4L2 buffers or deliver audio to ALSA, then resubmit while VB2 streaming remains active.

State and persistence: `go->hpi_context` stores USB state and URBs. Device status gates callbacks and control paths. Module parameter `assume_endura` affects ambiguous hardware detection.

Dependencies and integration points: integrates USB core, I2C core, V4L2 subdevices, tuner and codec metadata, ALSA via the core `audio_deliver` callback, and board data consumed by firmware/V4L2 code.

Risks and test signals: risks include probe cleanup returning `-ENOMEM` for non-memory failures, URB partial allocation cleanup, endpoint assumptions, callback/disconnect races, USB 1.1 corruption, and I2C coalescing limits. Test hotplug, stream while disconnecting, all board IDs, EZ-USB and onboard HPI paths, audio-enabled and audio-disabled boards, firmware download failures, and suspend/resume via USB core.
