# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos-gsc/Makefile

Purpose: defines the object composition for the Exynos G-Scaler driver.

Important APIs and entries: `exynos-gsc-objs := gsc-core.o gsc-m2m.o gsc-regs.o`; `obj-$(CONFIG_VIDEO_SAMSUNG_EXYNOS_GSC) += exynos-gsc.o`.

Control flow: kbuild links the core/probe logic, mem2mem operations, and register programming helpers into one module or built-in object according to the Kconfig symbol.

State and persistence: no runtime state; it controls compilation and link composition.

Dependencies and integration points: depends on declarations shared through `gsc-core.h` and Kconfig dependencies selecting V4L2/vb2 support.

Risks: object list drift can cause unresolved symbols or missing functionality. Because all components link into one object, internal symbol visibility is simple but every added compilation unit must be listed here.

Test signals: module/built-in builds with `CONFIG_VIDEO_SAMSUNG_EXYNOS_GSC=y/m`.
