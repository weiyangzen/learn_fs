# sources/distributed-fs/ceph-client/drivers/media/platform/raspberrypi/rp1-cfe/Makefile

Purpose: kbuild object composition for the RP1 CFE driver.

Important APIs/types/functions: `rp1-cfe-objs := cfe.o csi2.o pisp-fe.o dphy.o` and `obj-$(CONFIG_VIDEO_RP1_CFE) += rp1-cfe.o`.

Control flow: kbuild links the core capture driver, CSI-2 receiver, PiSP front-end, and DPHY helper into one module/built-in object.

State and persistence: build graph only.

Dependencies and integration: object ordering is conventional; symbols exported between these local objects are declared in `cfe.h`, `csi2.h`, `pisp-fe.h`, and `dphy.h`.

Risks: missing a new source file from `rp1-cfe-objs` would cause unresolved symbols. Renaming any component must update this file and Kconfig module naming expectations.

Test signals: `make M=drivers/media/platform/raspberrypi/rp1-cfe`, allmodconfig link checks, and modinfo for `rp1-cfe`.
