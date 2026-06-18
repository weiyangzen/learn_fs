# sources/distributed-fs/ceph-client/drivers/media/usb/uvc/Makefile

Purpose: defines how the UVC driver module is composed from its implementation objects.

Important build entries: `uvcvideo-objs` always includes `uvc_driver.o`, `uvc_queue.o`, `uvc_v4l2.o`, `uvc_video.o`, `uvc_ctrl.o`, `uvc_status.o`, `uvc_isight.o`, `uvc_debugfs.o`, and `uvc_metadata.o`. When `CONFIG_MEDIA_CONTROLLER=y`, it also includes `uvc_entity.o`. `obj-$(CONFIG_USB_VIDEO_CLASS) += uvcvideo.o` ties the aggregate object to the Kconfig symbol.

Control flow: no runtime execution occurs, but this file controls link composition. The main driver, V4L2 ioctl layer, streaming engine, controls, status endpoint handling, Apple iSight decoder, debugfs, metadata capture, and optional media-controller graph support are linked into one `uvcvideo` module or built-in object.

State and persistence: build state only. The selected object list affects which symbols exist at runtime, especially media-controller entity registration and cleanup.

Dependencies and integration points: consumes `CONFIG_USB_VIDEO_CLASS` from Kconfig and `CONFIG_MEDIA_CONTROLLER` from the media core. It must remain consistent with prototypes and conditional stubs in `uvcvideo.h`.

Risks: adding a new UVC feature requires updating this object list or it will compile in isolation but fail to link. `uvc_entity.o` is only built for built-in media-controller support, so references to its functions must stay guarded by `CONFIG_MEDIA_CONTROLLER`.

Test signals: build UVC as a module and built in, with and without `CONFIG_MEDIA_CONTROLLER`, and run modpost/link checks for missing UVC symbols.
