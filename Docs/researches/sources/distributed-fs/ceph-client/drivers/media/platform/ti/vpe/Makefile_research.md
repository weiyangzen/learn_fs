# sources/distributed-fs/ceph-client/drivers/media/platform/ti/vpe/Makefile

## Purpose
Maps TI VPE/VPDMA/scaler/CSC/VIP media Kconfig symbols to kbuild objects and enables debug compiler flags.

## Important APIs, Types, and Functions
The important interfaces are `obj-$(CONFIG_VIDEO_TI_VPE)`, `obj-$(CONFIG_VIDEO_TI_VPDMA)`, `obj-$(CONFIG_VIDEO_TI_SC)`, `obj-$(CONFIG_VIDEO_TI_CSC)`, and `obj-$(CONFIG_VIDEO_TI_VIP)`, plus composite object assignments `ti-vpe-y`, `ti-vpdma-y`, `ti-sc-y`, `ti-csc-y`, and `ti-vip-y`.

## Control Flow
Kbuild evaluates selected `CONFIG_VIDEO_TI_*` symbols and builds the corresponding module or built-in object. `ccflags-$(CONFIG_VIDEO_TI_VPE_DEBUG) += -DDEBUG` enables debug logging compilation when requested.

## State and Persistence
No runtime state exists. Persistent effect is build composition and module naming.

## Dependencies and Integration Points
The Makefile is coupled to Kconfig symbols in the media platform tree and to source filenames `vpe.c`, `vpdma.c`, `sc.c`, `csc.c`, and `vip.c`.

## Risks and Edge Cases
Renaming objects without updating this file breaks builds. Selecting helper modules separately from full VPE/VIP users can expose missing exported-symbol dependencies.

## Test Signals
Run `make M=drivers/media/platform/ti/vpe` under module and built-in configs, with and without `VIDEO_TI_VPE_DEBUG`, and confirm expected `ti-*.ko` artifacts.
