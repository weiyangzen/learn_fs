# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/Kconfig

## Purpose

This Kconfig entry exposes the Intel IPU7 staging driver as `VIDEO_INTEL_IPU7`, covering the base `intel_ipu7` module and the `intel_ipu7_isys` module used for camera sensor capture.

## Important APIs, Types, and Functions

The config is a tristate and selects required infrastructure: `AUXILIARY_BUS`, `IOMMU_IOVA`, `VIDEO_V4L2_SUBDEV_API`, `MEDIA_CONTROLLER`, `VIDEOBUF2_DMA_SG`, and `V4L2_FWNODE`.

## Control Flow

There is no runtime control flow. At build configuration time it gates compilation of IPU7 modules.

## State and Persistence Behavior

No runtime state is defined. The selected symbol determines whether objects are built-in, modular, or omitted.

## Dependencies and Integration Points

Dependencies require ACPI or compile-test, video device support, x86 with DMA, PCI, and the IPU bridge compatibility expression. The selected symbols line up with the auxiliary-bus split between base and ISYS drivers.

## Risks and Edge Cases

Dependency drift can make the module buildable without a subsystem it assumes at runtime, especially media-controller, fwnode, vb2, auxiliary bus, or IOVA support.

## Test Signals

Build-test with `m`, `y`, and disabled configurations, plus `COMPILE_TEST` where supported, verifies that the Kconfig dependencies match source includes.
