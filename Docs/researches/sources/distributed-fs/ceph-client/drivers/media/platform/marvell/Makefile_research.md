# sources/distributed-fs/ceph-client/drivers/media/platform/marvell/Makefile

## Purpose
This Makefile builds the two Marvell camera controller modules and links both against the shared `mcam-core.o` implementation.

## Important APIs, Types, And Functions
There are no runtime APIs. `obj-$(CONFIG_VIDEO_CAFE_CCIC) += cafe_ccic.o mcam-core.o` builds the Cafe module support, with `cafe_ccic-y := cafe-driver.o`. `obj-$(CONFIG_VIDEO_MMP_CAMERA) += mmp_camera.o mcam-core.o` builds the MMP module support, with `mmp_camera-y := mmp-driver.o`.

## Control Flow And State
Build state follows the two Kconfig symbols. Both configurations compile `mcam-core.o`; if both are enabled, the build system must avoid duplicate symbol problems through normal kernel object/module handling.

## Dependencies And Integration Points
The Makefile is the bridge between Kconfig and `cafe-driver.c`, `mmp-driver.c`, and `mcam-core.c`. It reflects the architectural split: platform glue lives in the wrapper objects, while V4L2/vb2/register/IRQ frame logic lives in `mcam-core.o`.

## Risks
`mcam-core.c` exports `mccic_*` symbols and also contains module metadata, so incorrect object grouping can produce duplicate or missing symbol behavior. If the core is refactored into a library-like object, this Makefile must preserve the intended link ownership for both modules.

## Test Signals
Build Cafe only, MMP only, and both enabled. Verify that modules contain the expected driver aliases and that no duplicate `mccic_*` symbol or module metadata warnings appear.
