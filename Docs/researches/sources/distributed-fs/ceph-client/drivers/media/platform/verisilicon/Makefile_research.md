# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/Makefile

Purpose: object composition rules for the Verisilicon/Hantro VPU media driver. It builds the `hantro-vpu` composite object from common codec/framework files and appends SoC-specific hardware integration files according to Kconfig symbols.

Important entries: `obj-$(CONFIG_VIDEO_HANTRO) += hantro-vpu.o` creates the main module/built-in object. `hantro-vpu-y` always includes common driver, V4L2, postprocessor, JPEG encoder, G1/G2 codec engines, H.264/MPEG2/VP8/HEVC/VP9 helpers, and JPEG helpers. Conditional lists add `imx8m_vpu_hw.o`, `sama5d4_vdec_hw.o`, Rockchip JPEG/H.264/MPEG2/VP8/AV1/filmgrain/entropy/hardware files, `sunxi_vpu_hw.o`, and `stm32mp25_vpu_hw.o`.

Control flow: Kbuild uses the `VIDEO_HANTRO` tristate to decide whether `hantro-vpu.o` is linked. It then folds each `hantro-vpu-y` and `hantro-vpu-$(CONFIG_...)` object into the composite driver for the selected configuration.

State and persistence: no runtime state; it controls build artifacts and link composition.

Dependencies and integration: pairs directly with `verisilicon/Kconfig` and the parent media platform build. The common object list must stay in sync with codec support selected by `VIDEO_HANTRO`; conditional objects must match SoC support symbols.

Risks: missing a new codec/helper object from the common list can cause unresolved symbols or silently absent format support. Rockchip support gathers several generations and AV1 support under one config symbol, so platform-specific code can be compiled on Rockchip builds even when not used by the running SoC. Object ordering is conventional but common files must provide symbols before SoC hooks reference them at link time.

Test signals: `make M=drivers/media/platform/verisilicon` under each config combination; `modinfo hantro-vpu` when modular; link checks for all conditional SoC symbols; and boot probe on each supported platform confirming the expected hardware variant table is present.
