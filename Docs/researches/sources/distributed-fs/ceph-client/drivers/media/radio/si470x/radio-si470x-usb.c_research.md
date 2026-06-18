# sources/distributed-fs/ceph-client/drivers/media/radio/si470x/radio-si470x-usb.c

Purpose: implements the USB HID transport, RDS interrupt URB handling, LED status, and probe/disconnect paths for USB Si470x FM radio receivers.

Important APIs and functions: USB lifecycle is `si470x_usb_driver_probe`, `si470x_usb_driver_disconnect`, suspend/resume callbacks, and `si470x_usb_release`. HID helpers are `si470x_get_report`, `si470x_set_report`, register callbacks, `si470x_get_all_registers`, `si470x_set_led_state`, and `si470x_get_scratch_page_versions`. RDS interrupt processing is `si470x_int_in_callback`. `si470x_start_usb` starts the interrupt URB and common radio configuration.

Control flow: probe allocates state and USB buffers, finds an interrupt IN endpoint, allocates an URB, disambiguates the shared Raremono/Si470x USB ID by reading device ID, registers V4L2 state and controls, reads chip and scratch versions, sets LED connect state, allocates the RDS buffer, starts the interrupt URB and common radio, tunes 87.5 MHz, and registers the video node. HID register access uses class GET_REPORT/SET_REPORT on endpoint 0. The interrupt callback handles STC completion, decodes RDS register reports into 3-byte V4L2 RDS blocks when synchronized, updates the circular buffer, wakes readers, and resubmits while running. Disconnect marks V4L2 disconnected, unregisters video, kills URB, clears interface data, and releases via V4L2 refcount.

State and persistence: `struct si470x_device` includes USB device/interface, HID control buffer, interrupt buffer/endpoint/URB/running flag, version bytes, common register cache, RDS buffer indices, completion, lock, and V4L2 objects. Runtime state is freed in `si470x_usb_release`.

Dependencies and integration points: depends on USB HID class reports, interrupt URBs, V4L2 common Si470x exports, V4L2 controls/events/read, unaligned endian helpers, and USB audio for actual sound on most devices. USB IDs include multiple known products and share one ID with Raremono, handled by runtime detection.

Risks: `int_in_running` is a plain int updated across URB callback, suspend, and disconnect with minimal synchronization. The callback comments question whether mutex locking is needed around shared state. Probe starts the radio before registering the video device. RDS buffer overflow drops oldest data silently. Suspend/resume support is noted as historically problematic but present.

Test signals: HID report read/write failures, shared-ID detection against Raremono, interrupt endpoint validation, URB resubmit behavior under errors, RDS synchronization/error flags, LED reports, suspend/resume with active readers, disconnect races, and V4L2 compliance including read/poll.
