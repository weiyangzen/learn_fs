# sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/bdisp/Makefile

Purpose: maps the BDISP Kconfig symbol to its composite driver object.

Important APIs and entries: `obj-$(CONFIG_VIDEO_STI_BDISP) += bdisp.o` and `bdisp-objs := bdisp-v4l2.o bdisp-hw.o bdisp-debug.o`.

Control flow: when `VIDEO_STI_BDISP` is enabled, kbuild links V4L2 frontend, hardware programming, and debugfs/performance support into one BDISP driver object or module.

State and persistence: no runtime state. It determines build composition.

Dependencies and integration points: depends on the Kconfig symbol defined in the same directory and on the listed implementation files.

Risks: adding new implementation files requires updating `bdisp-objs`. Removing debug support would require handling references from the V4L2/hardware files.

Test signals: enabled/disabled module builds and link checks for all BDISP objects.
