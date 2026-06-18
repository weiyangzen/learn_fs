# sources/distributed-fs/ceph-client/drivers/gpu/drm/xlnx/Kconfig

## Purpose

This Kconfig file defines the Xilinx ZynqMP DisplayPort Subsystem DRM/KMS driver and optional DisplayPort audio support.

## Important APIs, Types, And Functions

It defines `DRM_ZYNQMP_DPSUB` and `DRM_ZYNQMP_DPSUB_AUDIO`. The display driver selects DRM bridge connector, DP helpers, GEM DMA helpers, KMS helpers, client selection, generic PHY, and DMA engine support. Audio depends on ASoC and the display driver.

## Control Flow

No runtime control flow. Kconfig resolves platform, clock, OF, DMA, PHY, DPDMA, DRM, and sound dependencies.

## State And Persistence Behavior

No runtime state. Selected symbols control built objects and optional audio integration.

## Dependencies And Integration Points

The driver depends on `ARCH_ZYNQMP || COMPILE_TEST`, common clocks, OF, DMADEVICES, `PHY_XILINX_ZYNQMP`, and `XILINX_ZYNQMP_DPDMA`. Audio selects generic DMAengine PCM.

## Risks And Test Signals

Risks include invalid modular ASoC combinations and missing DMA/PHY dependencies. Test with built-in and module configurations, with and without `DRM_ZYNQMP_DPSUB_AUDIO`.
