# sources/distributed-fs/ceph-client/drivers/media/platform/via/Kconfig

## Purpose
Adds Kconfig selection for the VIA Chrome9 framebuffer-backed camera controller driver.

## Important APIs, Types, And Functions
- Defines `VIDEO_VIA_CAMERA` as a tristate option named "VIAFB camera controller support".
- Depends on `V4L_PLATFORM_DRIVERS`, `FB_VIA`, and `VIDEO_DEV`.
- Selects `VIDEOBUF2_DMA_SG` and conditionally selects `VIDEO_OV7670` when `VIDEO_CAMERA_SENSOR` is enabled.

## Control Flow
There is no runtime control flow. Enabling this symbol builds the VIA camera platform driver and ensures its VB2 DMA-SG and OV7670 sensor dependencies are available.

## State And Persistence
No state is stored. The symbol controls build configuration.

## Dependencies And Integration Points
Integrated by the media platform drivers Kconfig hierarchy and paired with `drivers/media/platform/via/Makefile`. The help text documents the tested OLPC XO-1.5/OV7670 target.

## Risks And Edge Cases
The driver is tightly coupled to VIA framebuffer infrastructure, so missing `FB_VIA` blocks it. The conditional sensor selection may not cover non-OV7670 sensors if the driver were generalized.

## Test Signals
Configuration tests should verify module and built-in builds with `FB_VIA`, dependency rejection without framebuffer/V4L2 support, and expected autoselection of VB2 DMA-SG and OV7670 support.
