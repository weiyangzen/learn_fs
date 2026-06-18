
# sources/distributed-fs/ceph-client/drivers/media/pci/tw5864/Makefile

## Purpose
This Makefile declares the TW5864 module composition. It builds a single `tw5864` driver object when `CONFIG_VIDEO_TW5864` is enabled.

## Important APIs, Types, And Functions
`tw5864-objs` is composed from `tw5864-core.o`, `tw5864-video.o`, `tw5864-h264.o`, and `tw5864-util.o`. `obj-$(CONFIG_VIDEO_TW5864) += tw5864.o` connects the composite object to Kbuild.

## Control Flow
There is no runtime control flow. At build time, Kbuild compiles the listed objects and links them into either a built-in object or `tw5864.ko`.

## State And Persistence
The file contributes only build metadata. It does not define runtime state.

## Dependencies And Integration Points
The object list corresponds to the PCI probe/IRQ implementation, V4L2/vb2 video implementation, H.264 header generation, and indirect register helpers. Any new source file with referenced symbols must be added here.

## Risks
The linked objects must stay consistent with exported prototypes in `tw5864.h`. Adding audio or MJPEG support without updating this list would create unresolved symbols or missing functionality.

## Test Signals
Build `CONFIG_VIDEO_TW5864=m` and confirm the resulting module contains the PCI driver and all helper symbols referenced across the four objects.
