
# sources/distributed-fs/ceph-client/drivers/media/usb/stk1160/Makefile

## Purpose
The Makefile defines the composite STK1160 module.

## Important APIs, Types, and Functions
`stk1160-y` includes `stk1160-core.o`, `stk1160-v4l.o`, `stk1160-video.o`, `stk1160-i2c.o`, and `stk1160-ac97.o`; `obj-$(CONFIG_VIDEO_STK1160) += stk1160.o`.

## Control Flow
Kbuild links the five implementation objects into one `stk1160` built-in object or module according to `CONFIG_VIDEO_STK1160`.

## State and Persistence
No runtime state exists. The file defines build composition.

## Dependencies and Integration Points
The object split mirrors the driver's internal module boundaries: USB core/probe, V4L2/vb2 policy, isochronous video transfer, I2C bridge, and AC97 setup.

## Risks and Edge Cases
Removing any object breaks cross-file prototypes declared in `stk1160.h`. Adding new split files requires updating the composite list.

## Test Signals
Build `CONFIG_VIDEO_STK1160=m` and confirm all five objects are linked into `stk1160.ko`.
