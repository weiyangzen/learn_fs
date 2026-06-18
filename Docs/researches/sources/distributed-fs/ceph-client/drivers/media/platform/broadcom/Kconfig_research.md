# sources/distributed-fs/ceph-client/drivers/media/platform/broadcom/Kconfig

## Purpose
This Kconfig entry declares `VIDEO_BCM2835_UNICAM`, the Broadcom BCM283x/BCM271x Unicam CSI-2/CCP2 capture driver.

## Important APIs, Types, and Functions
`VIDEO_BCM2835_UNICAM` is a tristate depending on `ARCH_BCM2835 || COMPILE_TEST`, `COMMON_CLK`, `PM`, and `VIDEO_DEV`. It selects `MEDIA_CONTROLLER`, `V4L2_FWNODE`, `VIDEO_V4L2_SUBDEV_API`, and `VIDEOBUF2_DMA_CONTIG`.

## Control Flow
Enabling the symbol makes the Makefile build `bcm2835-unicam.o`. The selected media-controller and subdev APIs are required because the driver exposes an internal bridge subdev plus image and metadata video nodes.

## State and Persistence
Only kernel configuration state is persisted. Runtime receiver, media graph, and DMA state live in `bcm2835-unicam.c`.

## Dependencies and Integration Points
The symbol integrates Broadcom SoC camera hardware with V4L2, media controller, OF/fwnode graph parsing, runtime PM, common clocks, and vb2 DMA-contig.

## Risks and Edge Cases
Dropping media-controller or subdev selections would break builds or runtime graph registration. Missing PM/common-clock dependencies would expose code that cannot manage the Unicam power and clock requirements.

## Test Signals
Build for Raspberry Pi/BCM2835 and `COMPILE_TEST`; confirm `bcm2835-unicam.ko` is produced and media-controller dependencies are enabled.
