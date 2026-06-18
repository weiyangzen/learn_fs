# sources/distributed-fs/ceph-client/drivers/media/usb/em28xx/Makefile

## Purpose
This Makefile maps EM28xx Kconfig symbols to kernel module object lists and include paths.

## Important APIs, types, and functions
`em28xx-y` defines the core module objects: `em28xx-core.o`, `em28xx-i2c.o`, `em28xx-cards.o`, and `em28xx-camera.o`. Composite object groups include `em28xx-v4l-objs`, `em28xx-alsa-objs`, and `em28xx-rc-objs`. `obj-$(CONFIG_VIDEO_EM28XX*)` lines build core, V4L2, ALSA, DVB, and RC modules. `ccflags-y` adds tuner and DVB frontend include directories.

## Control flow and state
There is no runtime state. Build control is driven by Kconfig expansion: selected symbols decide which modules are linked and which objects form each module.

## Dependencies and integration
The Makefile integrates the EM28xx source directory with the kernel media build, tuner headers, and DVB frontend headers.

## Risks and test signals
Risks include object list drift when files are renamed, missing include paths for new frontend headers, and Kconfig/Makefile symbol mismatches. Test with `make M=drivers/media/usb/em28xx`, module builds for each symbol combination, and clean builds after adding or removing EM28xx source files.
