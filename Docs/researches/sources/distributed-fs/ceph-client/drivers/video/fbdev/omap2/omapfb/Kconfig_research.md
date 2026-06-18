# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/Kconfig

## Purpose
This Kconfig file defines the OMAP2+ framebuffer driver option, VRFB support symbol, debug support, framebuffer count, and includes DSS/display-driver Kconfig files.

## Important APIs, Types, And Functions
- `OMAP2_VRFB` is a helper bool selected on older OMAP2/OMAP3.
- `menuconfig FB_OMAP2` depends on `FB`, `DRM_OMAP = n`, and `GPIOLIB`; it selects `FB_OMAP2_DSS` and `FB_IOMEM_HELPERS`.
- `FB_OMAP2_DEBUG_SUPPORT` enables debug code controlled at runtime by a module parameter.
- `FB_OMAP2_NUM_FBS` chooses 1-10 fbdev framebuffers, defaulting to 3.
- It sources `dss/Kconfig` and `displays/Kconfig`.

## Control Flow
Nested options are visible only inside `if FB_OMAP2`.

## State And Persistence
No runtime state. The selected symbols determine which objects and code paths build into the kernel.

## Dependencies And Integration Points
This file coordinates fbdev OMAP2 with the DSS core, display subdrivers, GPIOLIB, and DRM mutual exclusion.

## Risks
The `DRM_OMAP = n` dependency prevents coexistence with the newer DRM OMAP driver. Display Kconfig symbols may be hidden if `FB_OMAP2` is disabled even for compile-only testing of individual panels.

## Test Signals
Config tests should verify that enabling `FB_OMAP2` selects DSS, exposes display drivers, and respects `FB_OMAP2_NUM_FBS` bounds.
