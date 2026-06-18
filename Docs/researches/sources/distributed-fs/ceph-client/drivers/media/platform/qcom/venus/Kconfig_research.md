# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/venus/Kconfig

## Purpose
`Kconfig` exposes `CONFIG_VIDEO_QCOM_VENUS`, the build-time option for the Qualcomm Venus V4L2 mem2mem encoder/decoder driver.

## Important Configuration
- `config VIDEO_QCOM_VENUS` is a tristate option labeled "Qualcomm Venus V4L2 encoder/decoder driver".
- Depends on `V4L_MEM2MEM_DRIVERS`, `VIDEO_DEV`, `QCOM_SMEM`, and either Qualcomm ARM64 with `IOMMU_API` or `COMPILE_TEST`.
- Selects `OF_DYNAMIC` on Qualcomm architectures, `QCOM_MDT_LOADER`, `QCOM_SCM`, `VIDEOBUF2_DMA_CONTIG`, and `V4L2_MEM2MEM_DEV`.

## Control Flow And Integration
The option controls compilation of the Venus core, decoder, and encoder objects listed in the Makefile. The selected dependencies are directly reflected in source code: firmware MDT loading, SCM secure calls, SMEM firmware version publication, dynamic OF child nodes, DMA-contiguous vb2 queues, and V4L2 mem2mem devices.

## State And Persistence
No runtime state. The tristate determines whether the driver is built in, modular, or absent.

## Risks
- Missing `IOMMU_API`, `QCOM_SCM`, or `QCOM_MDT_LOADER` support prevents firmware boot on real hardware.
- `OF_DYNAMIC` is selected only under `ARCH_QCOM`; dynamic child node behavior may differ under compile-test configurations.

## Test Signals
Build matrix should include built-in, module, and `COMPILE_TEST` coverage. Runtime probe requires matching device tree nodes, firmware files, reserved memory, SCM availability when secure boot is used, and V4L2 mem2mem device registration.
