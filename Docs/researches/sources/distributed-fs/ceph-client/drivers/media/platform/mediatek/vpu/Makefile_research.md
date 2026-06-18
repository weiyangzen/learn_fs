## sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vpu/Makefile

Purpose: Kbuild file for the MediaTek VPU driver.

Important APIs/types/functions: builds `mtk-vpu.o` from `mtk_vpu.o` when `CONFIG_VIDEO_MEDIATEK_VPU` is enabled.

Control flow: no runtime flow; Kbuild links the single implementation object into the module or built-in image.

State and persistence behavior: build-only file with no runtime state.

Dependencies and integration points: paired with `Kconfig` and `mtk_vpu.c`.

Risks: if additional source files are added to the VPU driver, this Makefile must be updated or symbols will be missing. The module object name must remain aligned with Kconfig help text and module aliases.

Test signals: kernel build with `VIDEO_MEDIATEK_VPU=m/y` and module load check for `mtk-vpu`.
