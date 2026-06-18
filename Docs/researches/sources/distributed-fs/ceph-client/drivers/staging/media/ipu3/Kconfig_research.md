# sources/distributed-fs/ceph-client/drivers/staging/media/ipu3/Kconfig

## Purpose

`drivers/staging/media/ipu3/Kconfig` declares the build-time configuration symbol for the Intel IPU3 ImgU staging driver.

## Important APIs, Types, and Functions

The only symbol is `VIDEO_IPU3_IMGU`, a tristate option labeled "Intel ipu3-imgu driver". It depends on `PCI`, `VIDEO_DEV`, and `X86`, and selects `MEDIA_CONTROLLER`, `VIDEO_V4L2_SUBDEV_API`, `IOMMU_IOVA`, and `VIDEOBUF2_DMA_SG`.

## Control Flow

Kconfig has no runtime control flow. During kernel configuration, selecting this option enables the corresponding Makefile object aggregation and eventually builds the `ipu3-imgu` module or built-in driver.

## State and Persistence Behavior

The selected value persists only in the kernel build configuration, such as `.config`. It creates no runtime state by itself.

## Dependencies and Integration Points

This config integrates the IPU3 staging media driver with the kernel media, V4L2, PCI, x86, IOMMU IOVA, and scatter-gather vb2 subsystems. The help text identifies Skylake/Kaby Lake SoCs with MIPI cameras and names the module `ipu3-imgu`.

## Risks and Edge Cases

The x86 and PCI dependencies prevent accidental builds on unsupported architectures. Because this is a staging driver, API churn and incomplete hardware coverage are plausible. Missing selected dependencies would surface as build failures in IPU3 objects.

## Test Signals

Test `allyesconfig`/`allmodconfig` style builds on x86, dependency exclusion on non-x86 or no-PCI configs, module build as `M`, built-in build as `Y`, and presence of the expected `ipu3-imgu` module.
