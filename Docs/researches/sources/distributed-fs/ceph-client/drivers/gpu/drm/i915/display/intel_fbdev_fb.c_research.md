# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fbdev_fb.c

Purpose: provides fbdev backing-object allocation and fb_info mapping helpers shared by i915 fbdev setup.

Important APIs/types/functions: `intel_fbdev_fb_pitch_align()` aligns pitches to 64 bytes. `intel_fbdev_fb_prefer_stolen()` decides whether stolen memory is acceptable, skipping Meteor Lake and requiring at least twice the requested size. `intel_fbdev_fb_bo_create()` allocates lmem, stolen, or shmem GEM backing. `intel_fbdev_fb_bo_destroy()` drops the GEM object. `intel_fbdev_fb_fill_info()` fills fb_info physical aperture fields and pins an iomap for `screen_base`.

Control flow: allocation prefers contiguous user lmem on discrete GPUs; otherwise it tries stolen memory only when policy allows and falls back to shmem. Fill-info computes `fix.smem_start` from lmem IO aperture or GGTT gmadr+VMA offset, locks the object with a ww context, pins an iomap, and stores screen base/size.

State and persistence: the GEM object persists through fbdev lifetime. `info->fix.smem_*`, `info->screen_base`, and `info->screen_size` persist in fb_info until fbdev teardown. The iomap pin persists until the VMA/object cleanup path unpins it.

Dependencies and integration: depends on GEM lmem/stolen/shmem allocation, GGTT offsets, memory-region IO ranges, VMA iomap pinning, ww locking, and DRM fbdev code in `intel_fbdev.c`.

Risks: wrong smem_start calculation breaks fbdev mmap/console access. Stolen preference competes with features such as FBC. Mapping failures must propagate cleanly. Meteor Lake stolen avoidance is a workaround-sensitive policy.

Test signals: allocate fbdev on integrated, discrete/lmem, and low-stolen systems; validate fb_info mmap/write behavior, fallback from stolen to shmem, iomap pin failures, and object cleanup without leaked pins.
