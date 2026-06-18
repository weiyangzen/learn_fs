# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/Makefile

Purpose: builds the Renesas VSP1/VSP2 driver as a single composite kernel object `vsp1.o` when `CONFIG_VIDEO_RENESAS_VSP1` is enabled. It declares the full object list for core, V4L2 media-controller, DRM/DU, display-list, video-node, read/write pixel formatter, and processing entities.

Important APIs and functions: no C APIs are defined here. The key build contract is `vsp1-y := ...` plus `obj-$(CONFIG_VIDEO_RENESAS_VSP1) += vsp1.o`. Included object files are `vsp1_drv.o`, `vsp1_entity.o`, `vsp1_pipe.o`, `vsp1_dl.o`, `vsp1_drm.o`, `vsp1_video.o`, RPF/WPF/RWPF support, CLU/HSIT/LUT/BRX/SRU/UDS/HGO/HGT/HISTO, IIF/LIF/UIF, and VSPX support.

Control flow role: link order makes all subsystem objects part of one module or built-in driver. `vsp1_drv.o` provides platform probe/remove and module registration, while the other objects provide helpers and entity constructors called from probe-time entity creation or runtime pipeline configuration.

State and persistence: no runtime state. Its persistence concern is build composition: omitting an object silently breaks constructor references or feature support for hardware variants declared in `vsp1_drv.c`.

Dependencies and integration: integrates with Kbuild and the Renesas media-platform Kconfig entry. It assumes all listed sources compile under the same configuration and share private headers in this directory.

Risks and test signals: risks are stale object lists when adding/removing entity files, missing feature support for new hardware blocks, and unresolved symbols from conditional edits. Test with `make drivers/media/platform/renesas/vsp1/` or a kernel `allyesconfig`/target defconfig build with `CONFIG_VIDEO_RENESAS_VSP1`.
