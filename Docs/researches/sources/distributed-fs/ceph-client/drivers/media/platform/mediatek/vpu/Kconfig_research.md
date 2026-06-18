## sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vpu/Kconfig

Purpose: declares the build configuration option for the MediaTek Video Processor Unit driver.

Important APIs/types/functions: `config VIDEO_MEDIATEK_VPU` is a tristate option named "Mediatek Video Processor Unit". It depends on mem2mem V4L2 drivers, video device support, and either MediaTek architecture or compile testing.

Control flow: selecting the option builds the `mtk-vpu` module/built-in driver from the Makefile. The help text describes firmware downloading and VPU communication for MT8173 video codec hardware.

State and persistence behavior: build-time configuration only, no runtime state.

Dependencies and integration points: controls compilation of `drivers/media/platform/mediatek/vpu/mtk_vpu.c`, which exports symbols used by older MediaTek vcodec firmware integration paths.

Risks: dependency coverage must stay aligned with driver includes and exported API users. The help text is MT8173-specific even though surrounding vcodec code may support newer SCP-based paths elsewhere.

Test signals: Kconfig build matrix with option disabled, module, and built-in; COMPILE_TEST on non-MediaTek architectures.
