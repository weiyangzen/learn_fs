# sources/distributed-fs/ceph-client/include/drm/drm_fbdev_dma.h

Purpose: Provides the fbdev-emulation probe hook macro for drivers whose framebuffer memory is backed by DMA GEM helpers.

Important APIs, types, and functions: With `CONFIG_DRM_FBDEV_EMULATION`, declares `drm_fbdev_dma_driver_fbdev_probe()` and defines `DRM_FBDEV_DMA_DRIVER_OPS` to set `.fbdev_probe` to that helper. Without fbdev emulation, the macro sets `.fbdev_probe = NULL`.

Control flow: DMA GEM drivers include the macro in `struct drm_driver` initialization. When fbdev emulation starts, the DRM core calls the probe helper to allocate and initialize fbdev state using DMA-backed scanout storage.

State and persistence: The header stores no state. Runtime fbdev state is held in `struct drm_fb_helper` and the allocated DMA GEM framebuffer.

Dependencies and integration points: Integrates with `drm_fb_helper`, `drm_gem_dma_helper`, `struct drm_driver.fbdev_probe`, and Kconfig-controlled fbdev emulation.

Risks and test signals: Risks include silently disabling fbdev when Kconfig is off, using the macro in a driver that does not use DMA-compatible GEM objects, and mismatched surface sizing. Test builds with fbdev emulation on and off, boot console creation, DMA dumb-buffer allocation, and fbdev teardown.
