# sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/Kconfig

## Purpose
`geode/Kconfig` defines AMD Geode framebuffer configuration entries.

## APIs And Control Flow
`FB_GEODE` gates family support on fbdev, PCI, x86/compile-test, and not UML. `FB_GEODE_LX`, `FB_GEODE_GX`, and `FB_GEODE_GX1` are tristate entries depending on `FB_GEODE`, selecting `FB_IOMEM_HELPERS`, and documenting module names `lxfb`, `gxfb`, and `gx1fb`.

## State, Dependencies, Integration, Risks
There is no runtime state. The file integrates with the Geode Makefile and fbdev Kconfig. Risks are dependency drift or missing helper selection. Test signals are x86_32/x86 compile-test builds, module and built-in combinations, and UML exclusion.
