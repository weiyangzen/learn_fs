# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp/Kconfig

## Purpose
This Kconfig entry exposes the legacy MediaTek MT8173 MDP V4L2 mem2mem driver.

## Important APIs, Types, and Functions
The key symbol is `VIDEO_MEDIATEK_MDP`, a tristate option that selects `VIDEOBUF2_DMA_CONTIG`, `V4L2_MEM2MEM_DEV`, and `VIDEO_MEDIATEK_VPU`. It depends on V4L mem2mem drivers, media video device support, MediaTek IOMMU/SMI conditions, and MediaTek architecture or compile-test builds.

## Control Flow
When enabled, Kbuild descends into the `mdp` Makefile and links `mtk-mdp.o`. Runtime control flow is implemented in the C files.

## State and Persistence
The selected value persists in the kernel `.config`, controlling whether the driver is built in, modular, or omitted.

## Dependencies and Integration Points
The symbol couples this driver to V4L2, vb2 DMA-contig, the MediaTek VPU firmware interface, IOMMU, and SMI. It is platform-specific to MT8173-era MDP.

## Risks and Edge Cases
Dependency relaxation for `COMPILE_TEST && MTK_SMI=n` must continue to cover non-MediaTek build testing without exposing impossible runtime configurations. Selecting VPU support means builds must keep the VPU include path and symbols available.

## Test Signals
Run `olddefconfig`, `allmodconfig`, MediaTek ARM64 builds, and compile-test builds with and without `MTK_SMI`.
