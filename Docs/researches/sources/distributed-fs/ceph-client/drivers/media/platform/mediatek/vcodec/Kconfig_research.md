# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/Kconfig

## Purpose
This Kconfig file defines the MediaTek video codec driver option and internal booleans for SCP and VPU firmware backends.

## Important APIs, Types, And Functions
`VIDEO_MEDIATEK_VCODEC` is a tristate option for the combined MediaTek encoder/decoder driver. It depends on V4L2 mem2mem, IOMMU or compile-test support, video devices, MediaTek architecture or compile-test, either legacy VPU or SCP firmware, and MTK SMI. It selects videobuf2 DMA-contig, V4L2 mem2mem, backend booleans, H.264/VP9 helpers, and media controller support.

## Control Flow
Kconfig selection controls which Makefile objects are compiled and which firmware backend initializers are available. The dependency lines keep module/built-in linkage aligned with VPU and SCP dependencies.

## State, Persistence, And Dependencies
No runtime state. Build-time dependencies determine whether VPU/SCP backend code and debug/media support are compiled.

## Integration Points
`common/Makefile` uses `VIDEO_MEDIATEK_VCODEC_VPU` and `VIDEO_MEDIATEK_VCODEC_SCP` to include firmware backend implementations. Decoder and encoder Makefiles build modules under `VIDEO_MEDIATEK_VCODEC`.

## Risks
Incorrect dependency states can create unresolved symbols when a backend is built as a different linkage type. Compile-test depends on MTK_SMI being disabled unless available.

## Test Signals
Build matrix coverage for built-in/module/compile-test, VPU-only, SCP-only, and both-backend configurations is the main signal.
