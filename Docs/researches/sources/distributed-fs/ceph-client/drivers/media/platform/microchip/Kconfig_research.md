# sources/distributed-fs/ceph-client/drivers/media/platform/microchip/Kconfig

## Purpose
This Kconfig file defines the Microchip media platform driver menu and build switches for the ISC, XISC, shared ISC base, and CSI2DC bridge drivers.

## Important APIs, Types, and Functions
`VIDEO_MICROCHIP_ISC` enables the SAMA5D2 Image Sensor Controller module. `VIDEO_MICROCHIP_XISC` enables the SAMA7G5 eXtended ISC module. `VIDEO_MICROCHIP_ISC_BASE` is an internal tristate selected by both ISC variants. `VIDEO_MICROCHIP_CSI2DC` enables the CSI2 Demux Controller. The options select V4L2 media-controller, subdevice, fwnode, vb2 DMA-contig, and regmap-mmio support as needed.

## Control Flow
The user-visible ISC and XISC choices pull in the common base automatically, while CSI2DC builds independently as a bridge subdevice. All user-visible options are guarded by `V4L_PLATFORM_DRIVERS`, `VIDEO_DEV`, relevant clock/OF dependencies, and `ARCH_AT91 || COMPILE_TEST`.

## State and Persistence
Kconfig state is persisted in the kernel build configuration. It does not create runtime state but determines which modules and symbols are compiled.

## Dependencies and Integration Points
The file integrates these drivers into the Linux media platform menu. It gates compilation against V4L2, media-controller, COMMON_CLK, OF for CSI2DC, and AT91 architecture support.

## Risks and Edge Cases
Because `VIDEO_MICROCHIP_ISC_BASE` is non-user-visible and defaults to `n`, direct builds of common code rely on the ISC/XISC selects. Missing `MEDIA_CONTROLLER` or `VIDEO_V4L2_SUBDEV_API` would break the graph-based probe paths, so the selects are part of the ABI contract for these drivers.

## Test Signals
Build tests should cover built-in and module configurations for ISC, XISC, CSI2DC, `COMPILE_TEST`, and disabled `V4L_PLATFORM_DRIVERS`. Expected module names are `microchip-isc`, `microchip-xisc`, and `microchip-csi2dc`.
