# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun8i-di/Makefile

Purpose: maps the deinterlace Kconfig symbol to its single implementation object.

Important APIs and entries: `obj-$(CONFIG_VIDEO_SUN8I_DEINTERLACE) += sun8i-di.o`.

Control flow: kbuild compiles and links `sun8i-di.c` when the option is enabled.

State and persistence: no runtime state.

Dependencies and integration points: consumed by the sunxi parent Makefile.

Risks: minimal unless the driver is split into multiple source files.

Test signals: targeted build with `CONFIG_VIDEO_SUN8I_DEINTERLACE=m`.
