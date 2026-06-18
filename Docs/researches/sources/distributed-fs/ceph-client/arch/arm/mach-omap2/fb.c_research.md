<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/fb.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/fb.c

## Purpose
`fb.c` registers legacy OMAP framebuffer and VRFB platform devices. It provides static physical resource definitions for OMAP2/3 VRFB register and remap windows and an `omapfb` platform device with DMA configuration.

## Important APIs, Types, and Functions
Public init helpers are `omap_init_vrfb()` and `omap_init_fb()`, with stubs when config options are disabled. Internal data includes `omap2_vrfb_resources[]`, `omap3_vrfb_resources[]`, `omap_fb_dma_mask`, `omapfb_config`, and `omap_fb_device`.

## Control Flow
`omap_init_vrfb()` selects OMAP24xx or OMAP34xx VRFB resources based on SoC detection and calls `platform_device_register_resndata()`. `omap_init_fb()` registers the static `omapfb` device. Both are called from `display.c` during fbdev display initialization.

## State and Persistence Behavior
State is platform-device registration and associated resource descriptors. No persistent storage is used. The framebuffer driver later owns display buffers and runtime state.

## Dependencies and Integration Points
It depends on platform-device, memblock/MM/DMA headers, `linux/omapfb.h`, SoC detection, and `display.h`. It integrates with legacy DSS/fbdev setup in `display.c` and VRFB/omapfb drivers.

## Risks
Hard-coded VRFB physical windows are SoC-specific and must match memory maps. Wrong resource selection can overlap real memory or make VRFB unusable. DMA mask changes affect framebuffer allocation capability.

## Test Signals
Build with `CONFIG_OMAP2_VRFB` and `CONFIG_FB_OMAP2`. On OMAP2/3 hardware, verify `omapvrfb` and `omapfb` devices register, resources appear correctly, framebuffer opens, rotation/VRFB paths work, and no resource conflict warnings occur.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/fb.c -->
