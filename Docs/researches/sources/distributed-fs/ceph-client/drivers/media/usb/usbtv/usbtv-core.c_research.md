# sources/distributed-fs/ceph-client/drivers/media/usb/usbtv/usbtv-core.c

Purpose: provides the USB driver shell for the Fushicai USBTV007 grabber. It matches supported USB IDs, validates the expected interface layout, allocates `struct usbtv`, initializes video and audio subdrivers, and tears them down on disconnect.

Important APIs and functions: `usbtv_set_regs` is the shared vendor-control helper used by audio and video setup paths. `usbtv_probe` and `usbtv_disconnect` are the USB driver callbacks. `usbtv_id_table` matches devices `1b71:3002`, `1f71:3301`, and `1f71:3306`. `module_usb_driver(usbtv_usb_driver)` registers the module.

Control flow: probe rejects interfaces that do not have two alternate settings or whose alternate setting 1 does not expose four endpoints. It derives the isochronous packet size from endpoint 0 of alternate setting 1, allocates the device object, stores the USB device and `iso_size`, and publishes it with `usb_set_intfdata`. Video initialization runs first, then audio initialization. On success the code takes an extra V4L2 device reference so the `struct usbtv` lifetime can extend past USB disconnect while video file handles still exist. Disconnect clears interface data, frees ALSA and V4L2 frontends, nulls `udev`, and drops that V4L2 reference.

State and persistence: no persistent storage exists. Hardware register state is programmed by subdrivers with `usbtv_set_regs`, which loops over index/value pairs and sends vendor requests to endpoint zero. Device state lives in `struct usbtv` and is ultimately released by the V4L2 release callback in `usbtv-video.c`.

Dependencies and integration points: depends on Linux USB core and the USBTV video/audio modules declared in `usbtv.h`. It integrates with V4L2 lifetime management by relying on `v4l2_device_get`/`put` instead of freeing `struct usbtv` immediately when video nodes are still referenced.

Risks: endpoint validation is minimal and assumes endpoint ordering in alternate setting 1. `usbtv_set_regs` stops on the first failing control request but has no per-register diagnostics. The audio failure path deliberately manipulates V4L2 references and depends on `usbtv_video_free` undoing the extra get, so lifetime regressions would be easy if initialization ordering changes.

Test signals: validate probe with all supported product IDs, rejection of malformed descriptors, video-init failure cleanup, audio-init failure cleanup, disconnect with open V4L2 descriptors, and register write error handling through USB fault injection.
