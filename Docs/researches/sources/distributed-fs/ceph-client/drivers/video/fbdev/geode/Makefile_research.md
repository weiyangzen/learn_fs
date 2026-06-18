# sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/Makefile

## Purpose
`geode/Makefile` maps Geode framebuffer Kconfig symbols to composite driver objects.

## APIs And Control Flow
It builds `gx1fb.o`, `gxfb.o`, and `lxfb.o` from the corresponding `CONFIG_FB_GEODE_*` symbols. Object lists show `gx1fb_core.o display_gx1.o video_cs5530.o`, `gxfb_core.o display_gx.o video_gx.o suspend_gx.o`, and `lxfb_core.o lxfb_ops.o`.

## State, Dependencies, Integration, Risks
There is no runtime state. It integrates display-controller code with chip core and video-output files. Risks are missing objects or unresolved symbols after refactors. Test signals are allmodconfig/allyesconfig and individual module builds.
