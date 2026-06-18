# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun6i-mipi-csi2/Makefile

Purpose: maps `VIDEO_SUN6I_MIPI_CSI2` to the A31 MIPI CSI-2 receiver object.

Important APIs and entries: `sun6i-mipi-csi2-y` contains `sun6i_mipi_csi2.o`; `obj-$(CONFIG_VIDEO_SUN6I_MIPI_CSI2)` builds the module.

Control flow: kbuild emits one module or built-in object from one source file.

State and persistence: no runtime state.

Dependencies and integration points: consumed by the sunxi parent Makefile and the child Kconfig symbol.

Risks: minimal; future file splits require updating `sun6i-mipi-csi2-y`.

Test signals: targeted module build with the config enabled.
