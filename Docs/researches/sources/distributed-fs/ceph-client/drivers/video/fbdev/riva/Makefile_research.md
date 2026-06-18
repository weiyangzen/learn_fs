# sources/distributed-fs/ceph-client/drivers/video/fbdev/riva/Makefile

Purpose: describes the Kbuild composition of the Riva framebuffer driver module/object.

Important APIs/types/functions: `obj-$(CONFIG_FB_RIVA) += rivafb.o` builds the driver when `CONFIG_FB_RIVA` is enabled. `rivafb-objs := fbdev.o riva_hw.o nv_driver.o` composes the main object from fbdev glue, Riva hardware support, and NV driver code. When `CONFIG_FB_RIVA_I2C` is enabled, `rivafb-i2c.o` is appended to `rivafb-objs`.

Control flow: Kbuild evaluates the config symbols at build time. With Riva framebuffer disabled, no object is built from this directory entry. With it enabled, the listed objects are linked into `rivafb.o`; optional I2C support is included only under its config symbol.

State and persistence: no runtime state exists in the Makefile. Its persistent effect is the build graph and the resulting linked object composition.

Dependencies and integration: integrates with Linux Kbuild, fbdev Riva source files in the same directory, and Kconfig symbols `CONFIG_FB_RIVA` and `CONFIG_FB_RIVA_I2C`. The SPDX tag declares GPL-2.0.

Risks: object ordering can matter if initialization or unresolved symbol dependencies rely on link order. New source files must be added to `rivafb-objs` under the correct config guard. If Kconfig changes symbol names, this Makefile must be updated or the driver silently stops building optional pieces.

Test signals: run kernel builds with `CONFIG_FB_RIVA=n`, `m`, or `y`, and with `CONFIG_FB_RIVA_I2C` toggled. Confirm `rivafb.o` includes `rivafb-i2c.o` only when expected and that all listed source objects are present in the directory.
