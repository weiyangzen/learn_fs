
# sources/distributed-fs/ceph-client/drivers/media/usb/usbtv/Makefile

## Purpose
The Makefile defines the composite USBTV007 module.

## Important APIs, Types, and Functions
`usbtv-y` includes `usbtv-core.o`, `usbtv-video.o`, and `usbtv-audio.o`; `obj-$(CONFIG_VIDEO_USBTV) += usbtv.o`.

## Control Flow
Kbuild links the three implementation objects into one built-in object or module when `CONFIG_VIDEO_USBTV` is enabled.

## State and Persistence
No runtime state exists here; this file only defines build composition.

## Dependencies and Integration Points
The object list maps the driver's main subsystems: USB/core probe, V4L2 video capture, and ALSA audio capture.

## Risks and Edge Cases
All three objects are needed for the advertised Kconfig support. Adding feature splits requires updating `usbtv-y`.

## Test Signals
Build with `CONFIG_VIDEO_USBTV=m` and confirm the final `usbtv` module includes core, video, and audio objects.
