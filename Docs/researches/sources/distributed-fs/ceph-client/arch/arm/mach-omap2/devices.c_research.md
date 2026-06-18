<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/devices.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/devices.c

## Purpose
`devices.c` contains legacy OMAP2 platform-device setup that remains in this slice only for video-output registration. It registers an `omap_vout` platform device when OMAP2 VOUT support is enabled.

## Important APIs, Types, and Functions
The public function is `omap_init_vout()`. Internals include `omap_vout_resource[]`, `omap_vout_dma_mask`, and `omap_vout_device`. When `CONFIG_VIDEO_OMAP2_VOUT` is disabled, `omap_init_vout()` is a stub returning zero.

## Control Flow
If enabled, `omap_init_vout()` calls `platform_device_register(&omap_vout_device)`. The resource array length depends on `CONFIG_FB_OMAP2` and `CONFIG_FB_OMAP2_NUM_FBS`, matching legacy framebuffer/V4L2 display-device coexistence. The function is called by display initialization after DSS and framebuffer setup.

## State and Persistence Behavior
State is the registered platform device and its 32-bit DMA mask. No persistent data is written. Once registered, driver binding and lifetime are managed by the platform bus.

## Dependencies and Integration Points
It depends on platform-device core, DMA masks, OMAP DMA headers, `display.h`, `control.h`, and OMAP device/hwmod infrastructure. Its main integration point is `display.c` through `omap_init_vout()`.

## Risks
This is legacy platform-data plumbing. Resource-count conditionals can mismatch VOUT/framebuffer expectations. Incorrect DMA masks or registration ordering can break `omap_vout` probe or video overlay buffer allocation.

## Test Signals
Compile with and without `CONFIG_VIDEO_OMAP2_VOUT` and `CONFIG_FB_OMAP2`. On supported OMAP display systems, confirm `omap_vout` platform device appears, binds to the V4L2 output driver, and can allocate/display DMA-backed buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/devices.c -->
