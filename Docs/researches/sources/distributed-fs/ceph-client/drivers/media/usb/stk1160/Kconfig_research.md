
# sources/distributed-fs/ceph-client/drivers/media/usb/stk1160/Kconfig

## Purpose
This Kconfig entry exposes the STK1160 USB video capture driver.

## Important APIs, Types, and Functions
The symbol is `VIDEO_STK1160`, a `tristate` depending on `VIDEO_DEV && I2C`. It selects `VIDEOBUF2_VMALLOC` and `VIDEO_SAA711X`.

## Control Flow
When enabled, the companion Makefile builds the composite `stk1160` driver from core, V4L2, video, I2C, and AC97 source files. Selecting `VIDEO_SAA711X` provides the decoder subdevice used during probe.

## State and Persistence
This file has compile-time configuration state only.

## Dependencies and Integration Points
It integrates with V4L2, I2C, videobuf2 vmalloc, and the SAA711x decoder driver. The help text clarifies that audio capture is expected through `snd-usb-audio`, not this video driver.

## Risks and Edge Cases
The driver contains AC97 setup helpers but does not implement ALSA capture, so users may expect audio from this option alone and not get it. Dropping `I2C` or `VIDEO_SAA711X` would break decoder probing.

## Test Signals
Build with `CONFIG_VIDEO_STK1160=m`, confirm `stk1160.ko` is produced and the SAA711x dependency is selected.
