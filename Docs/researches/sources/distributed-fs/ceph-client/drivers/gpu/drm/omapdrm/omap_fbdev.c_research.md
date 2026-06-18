# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_fbdev.c

Purpose: Provides legacy fbdev emulation for OMAP DRM, including fb helper probe, deferred I/O, write-combine mmap, damage forwarding, and optional DMM y-wrap scrolling.

Important APIs/functions: `omap_fbdev_driver_fbdev_probe()` creates a 32bpp XRGB fbdev surface, allocates an OMAP GEM scanout/WC BO, initializes an OMAP framebuffer, pins it for `fix.smem_start`, fills `fb_info`, sets up deferred I/O, and enables y-wrap when DMM is present and module parameter `ywrap` is true. `omap_fbdev_pan_display()` uses DMM roll through `pan_worker()` for y-wrap or falls back to DRM helper pan. `omap_fbdev_dirty()` forwards fbdev damage to framebuffer dirty. `omap_fbdev_setup()` allocates managed fbdev state and calls `drm_client_setup()`.

Control flow: Main DRM registration calls `omap_fbdev_setup()`. DRM client/fb helper invokes fbdev probe, which allocates the backing BO and framebuffer. Deferred writes trigger damage, and panning either rolls TILER page mappings immediately or queues work if atomic context.

State and persistence: `struct omap_fbdev` stores DRM device, ywrap flag, and work item. The fbdev BO remains pinned for the fb_info lifetime and is cleaned in `omap_fbdev_fb_destroy()`.

Dependencies/integration: Depends on DRM fb helper/client setup, OMAP GEM allocation/pin/vaddr/roll, OMAP framebuffer init/dirty, DMM availability, and the driver ordered workqueue.

Risks and test signals: Permanent pinning is intentional for fb_mmap but increases memory pressure. y-wrap requires DMM and page-aligned pitch. Destroy must unpin and remove framebuffer exactly once. Test fbcon boot, mmap writes, deferred damage, pan/ywrap on DMM and non-DMM systems, module parameter disabling, and cleanup on fbdev removal.
