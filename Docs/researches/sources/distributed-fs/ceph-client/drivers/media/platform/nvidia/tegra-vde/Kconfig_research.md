# sources/distributed-fs/ceph-client/drivers/media/platform/nvidia/tegra-vde/Kconfig

## Purpose
This Kconfig file defines the NVIDIA Tegra Video Decoder Engine driver option.

## Important APIs, Types, and Functions
`VIDEO_TEGRA_VDE` is a tristate option depending on `V4L_MEM2MEM_DRIVERS`, `ARCH_TEGRA || COMPILE_TEST`, and `VIDEO_DEV`. It selects DMA shared buffers, IOMMU IOVA support, media-controller, SRAM, vb2 DMA-contig/SG, V4L2 H.264 controls, and V4L2 mem2mem core.

## Control Flow
When enabled, the Tegra VDE module is built and can expose a stateless H.264 mem2mem decoder device. Selected dependencies cover request API controls, media graph support, DMA-buf import, SRAM IRAM allocation, and buffer management.

## State and Persistence
Kconfig selection persists in the kernel build configuration and determines module availability.

## Dependencies and Integration Points
The driver integrates with V4L2 mem2mem, stateless H.264 control UAPI, Tegra SoC power/clock/reset, SRAM, IOMMU, and DMA-buf frameworks.

## Risks and Edge Cases
`COMPILE_TEST` can build the code away from Tegra hardware, but runtime probe still requires named MMIO resources, SRAM, resets, and clocks. Missing IOMMU support changes buffer contiguity requirements.

## Test Signals
Build as module and built-in on Tegra and compile-test configurations, verify selected dependencies are present, and run V4L2 compliance on hardware with stateless H.264 requests.
