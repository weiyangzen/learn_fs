# sources/distributed-fs/ceph-client/drivers/media/platform/nxp/Makefile

Purpose: Top-level build glue for NXP media platform drivers.

Important APIs, types, and functions: Adds subdirectories `dw100/`, `imx-jpeg/`, and `imx8-isi/` unconditionally to `obj-y`, allowing their own Makefiles to decide object inclusion. Maps top-level Kconfig symbols to objects: `imx7-media-csi.o`, `imx8mq-mipi-csi2.o`, `imx-mipi-csis.o`, `imx-pxp.o`, and `mx2_emmaprp.o`.

Control flow: Kbuild evaluates this file after Kconfig selection. `obj-y += subdir/` descends into subdirectories, while `obj-$(CONFIG_...) += file.o` includes selected objects.

State and persistence behavior: No runtime state; it persists build composition based on `.config`.

Dependencies and integration points: Must remain synchronized with `Kconfig` symbols and actual source filenames. Subdirectories `dw100` and `imx-jpeg` have their own Makefiles mapping local config symbols to module objects.

Risks: Unconditional subdirectory descent is normal but relies on child Makefiles guarding objects correctly. A symbol/object mismatch causes missing driver builds or stale object references.

Test signals: Kbuild with each `CONFIG_VIDEO_*` option as built-in and module should produce the expected object or module name. `make drivers/media/platform/nxp/` catches path and symbol drift.
