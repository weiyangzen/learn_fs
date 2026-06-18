# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/Kconfig

## Purpose
This Kconfig entry declares the Intel IPU6 camera driver option `VIDEO_INTEL_IPU6`, covering the 6th generation Intel Image Processing Unit used for camera capture on Intel SoCs.

## Important APIs, types, and functions
The option is a tristate named "Intel IPU6 driver". It depends on ACPI or compile testing, `VIDEO_DEV`, `X86`, DMA support, and compatibility with optional `IPU_BRIDGE`. It selects `AUXILIARY_BUS`, `IOMMU_IOVA`, `VIDEO_V4L2_SUBDEV_API`, `MEDIA_CONTROLLER`, `VIDEOBUF2_DMA_SG`, and `V4L2_FWNODE`.

## Control flow and integration points
Enabling this symbol builds the IPU6 core and ISYS modules through the Makefile. The selected subsystems are required by the source files in this group: auxiliary devices for ISYS/PSYS children, IOVA for IPU6 MMU DMA mapping, media controller and V4L2 subdev APIs for the camera graph, and fwnode parsing for firmware-described sensors.

## State, persistence, and dependencies
Kconfig stores only build-time configuration. Its dependency set determines whether the runtime driver can register PCI, auxiliary, media, V4L2, and DMA paths safely.

## Risks and test signals
Risks are missing selected symbols, enabling the driver on unsupported non-X86 platforms, or compile-test paths that do not cover optional bridge combinations. Test signals include `allyesconfig`, `allmodconfig`, `COMPILE_TEST`, builds with and without `IPU_BRIDGE`, and successful module generation for both `intel_ipu6` and `intel_ipu6_isys`.
