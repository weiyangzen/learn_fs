# sources/distributed-fs/ceph-client/drivers/media/usb/uvc/Kconfig

Purpose: declares the kernel configuration switches for the USB Video Class driver and its optional input-event support.

Important symbols: `USB_VIDEO_CLASS` is a tristate named "USB Video Class (UVC)", depends on `VIDEO_DEV`, and selects `VIDEOBUF2_VMALLOC` and `UVC_COMMON`. `USB_VIDEO_CLASS_INPUT_EVDEV` is a bool for UVC input events device support, defaults to yes, depends on `USB_VIDEO_CLASS`, and requires either built-in input support or matching modular input support.

Control flow: these Kconfig symbols determine whether `uvcvideo.o` is built by the sibling Makefile and whether button/event support is compiled in elsewhere in the UVC driver. The help text describes webcam-style video input support and event reporting for device buttons.

State and persistence: no runtime state is stored here. The selected values are persisted only in the kernel build configuration and affect compile-time object inclusion and dependencies.

Dependencies and integration points: integrates with the media subsystem through `VIDEO_DEV`, videobuf2 vmalloc allocation, common UVC code, and input core constraints. The Makefile consumes `CONFIG_USB_VIDEO_CLASS` to build the module.

Risks: selecting vmalloc-backed vb2 constrains the queue implementation choice in `uvc_queue.c`. The input-event option has a compound dependency that must keep modular/built-in combinations link-safe. Help text still references the historical linux-uvc site and may not reflect current documentation.

Test signals: run Kconfig dependency checks for built-in and module combinations, build with UVC disabled/enabled, build with input event support enabled and disabled, and verify `uvcvideo` links when `INPUT` is modular or built in.
