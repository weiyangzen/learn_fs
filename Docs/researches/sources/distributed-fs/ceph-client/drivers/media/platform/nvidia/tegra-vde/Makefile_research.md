# sources/distributed-fs/ceph-client/drivers/media/platform/nvidia/tegra-vde/Makefile

## Purpose
This Makefile composes the Tegra VDE driver module.

## Important APIs, Types, and Functions
`tegra-vde-y` includes `vde.o`, `iommu.o`, `dmabuf-cache.o`, `h264.o`, and `v4l2.o`. `obj-$(CONFIG_VIDEO_TEGRA_VDE) += tegra-vde.o` gates the final object.

## Control Flow
When `VIDEO_TEGRA_VDE` is enabled, kbuild links platform probe/power code, IOMMU helpers, DMA-buf cache, H.264 hardware programming, and V4L2 mem2mem glue into one module.

## State and Persistence
The file has build-time state only.

## Dependencies and Integration Points
The object list mirrors the internal module boundaries declared in `vde.h`.

## Risks and Edge Cases
Every object depends on shared `struct tegra_vde` and helper prototypes. Removing one object from the list will break exported-internal calls such as `tegra_vde_h264_decode_run()` or `tegra_vde_iommu_map()`.

## Test Signals
Build the module and inspect link errors, module symbol layout, and tracepoint generation from `vde.o` plus `trace.h`.
