# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fbdev.c

Purpose: implements i915 fbdev emulation setup, including BIOS framebuffer reuse, fallback fb allocation, GGTT pinning, fb_info population, deferred I/O operations, mmap support, suspend handling, and frontbuffer invalidation for fbcon writes.

Important APIs/types/functions: private `struct intel_fbdev` stores the selected `intel_framebuffer`, pinned `i915_vma`, and pin flags. Key functions are `intel_fbdev_setup()`, `intel_fbdev_driver_fbdev_probe()`, `intel_fbdev_framebuffer()`, `intel_fbdev_vma_pointer()`, `intel_fbdev_get_map()`, `intel_fbdev_init_bios()`, `__intel_fbdev_fb_alloc()`, fb_ops wrappers for set_par/blank/pan/mmap/destroy, and helper callbacks `intelfb_dirty()`, `intelfb_restore()`, and `intelfb_set_suspend()`.

Control flow: setup allocates `intel_fbdev`, attempts to reuse the largest active BIOS framebuffer if it can satisfy all active pipes, picks preferred bpp, and calls DRM client setup. Probe validates or allocates the framebuffer, pins it into the GGTT for CPU-visible `screen_base`, fills `fb_info`, clears non-shmem allocations when needed, and records VMA state. fb_ops delegate to DRM fb helper operations then invalidate frontbuffer state so FBC/PSR/DRRS can react. Destroy finalizes fb helper, unpins the VMA, removes the framebuffer, and releases the DRM client.

State and persistence: `display->fbdev.fbdev` persists for device lifetime through drmm allocation. The framebuffer object, VMA pin, `info->screen_base`, and `info->screen_size` persist while fbdev is registered. BIOS fb reuse holds an extra framebuffer reference. Suspend state is propagated to fb_info, and stolen/lmem contents may be cleared on resume/allocation.

Dependencies and integration: integrates with DRM fb helper/client setup, i915 framebuffer creation, GEM object helpers, GGTT pinning, frontbuffer tracking, runtime PM, fbdev deferred I/O, console/sysrq infrastructure, and `intel_fbdev_fb.c` allocation/mapping helpers.

Risks: BIOS framebuffer reuse must verify pitch/size across all active CRTCs or fbcon can draw outside valid memory. Error paths around VMA pinning and `screen_base` mapping are delicate; comments intentionally rely on object-free/unpin cleanup. Stolen memory can contain garbage after hibernation. Missing invalidation after fbdev writes can leave FBC/PSR displaying stale contents.

Test signals: boot with firmware fb takeover, multi-pipe BIOS configurations, forced new fb allocation, fbcon text and pan/blank operations, fbdev mmap writes, suspend/hibernate resume, stolen/lmem/shmem allocations, remove/unbind cleanup, and DRM fbdev emulation disabled builds.
