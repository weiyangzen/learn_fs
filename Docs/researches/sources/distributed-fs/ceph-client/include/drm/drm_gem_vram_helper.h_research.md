# sources/distributed-fs/ceph-client/include/drm/drm_gem_vram_helper.h

Purpose: Defines GEM/TTM helper types and APIs for devices with dedicated VRAM, including VRAM-backed GEM objects, default driver and plane helper macros, VRAM memory-manager integration, and mode validation against VRAM capacity.

Important APIs, types, and functions: Defines placement flags, `struct drm_gem_vram_object`, container helpers `drm_gem_vram_of_bo()` and `drm_gem_vram_of_gem()`, object creation/put/offset/vmap/vunmap helpers, dumb create sizing/fill helpers, `drm_gem_vram_driver_dumb_create()`, plane prepare/cleanup helpers, `DRM_GEM_VRAM_PLANE_HELPER_FUNCS`, `DRM_GEM_VRAM_DRIVER`, `struct drm_vram_mm`, `drm_vram_mm_of_bdev()`, `drm_vram_mm_debugfs_init()`, `drmm_vram_helper_init()`, and `drm_vram_helper_mode_valid()`.

Control flow: Drivers initialize a managed VRAM MM with base and size, create VRAM GEM objects backed by TTM BOs, use dumb-create helpers for scanout buffers, and wire plane helper funcs so framebuffer BOs are pinned/prepared for scanout and unpinned on cleanup. Objects can be placed in VRAM or system memory and evicted when VRAM is scarce; vmap helpers manage reference-counted CPU mappings. Mode validation rejects display modes whose framebuffer requirements exceed available VRAM.

State and persistence: Runtime state includes each VRAM object's TTM BO, cached map, vmap use count, placement policy, and the device's `drm_vram_mm` with VRAM base/size and TTM device. It persists for the DRM device and object lifetimes but has no disk persistence.

Dependencies and integration points: Depends on DRM GEM/file/ioctl/modes, TTM BO and placement APIs, TTM-backed GEM helpers, plane helper callbacks, VRAM debugfs, and mode validation. Integrated by simple PCI/display drivers with fixed aperture VRAM.

Risks and test signals: Risks include incorrect VRAM base/size setup, placement flags that allow scanout from evicted system memory, vmap count imbalance, BO pin/unpin leaks in plane helpers, dumb pitch/size overflow, mode validation not accounting for bpp/pitch, and debugfs lifetime issues. Test VRAM MM init failure, dumb create/map, page flips under VRAM pressure, eviction to system memory, plane prepare/cleanup balance, vmap/vunmap nesting, mode validation near memory limits, and debugfs VRAM reporting.
