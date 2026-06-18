# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_gem.h

Purpose: Declares the OMAPDRM GEM object management interface used by the driver core, framebuffer, plane, fbdev, PRIME, PM, and debugfs code.

Important APIs/types/functions: Forward-declares DRM, dma-buf, page, seq_file, and VM types, plus `union omap_gem_size`. Exports init/deinit, optional PM resume, debugfs describe helpers, object constructors, dumb buffer callbacks, mmap size/offset helpers, PRIME import/export, roll, CPU/DMA synchronization, pin/unpin, page get/put, flag and tiled address helpers, and SG table get/put.

Control flow: This header is the contract between `omap_gem.c`, `omap_gem_dmabuf.c`, and other OMAPDRM units. Callers create GEM handles, pin buffers before scanout/DMA, query tiled geometry, and release pins/SG references through the paired APIs.

State and persistence: No storage is defined here, but the API exposes operations that mutate per-object pin/page/cache/TILER state and driver-wide DMM user-GART state.

Dependencies and integration: Included through `omap_drv.h` users and implemented by `omap_gem.c` and `omap_gem_dmabuf.c`; visible to DRM driver callbacks for dumb buffers and PRIME.

Risks: Many functions assume the passed `drm_gem_object` is an OMAP GEM object. Callers must balance `omap_gem_pin`/`omap_gem_unpin` and `omap_gem_get_sg`/`omap_gem_put_sg`, and tiled helper use is valid only for tiled pinned objects.

Test signals: Build coverage with and without `CONFIG_PM`, `CONFIG_DEBUG_FS`, and `CONFIG_DRM_FBDEV_EMULATION`; runtime tests should verify every declared paired API has balanced use in framebuffer, PRIME, and fbdev paths.
