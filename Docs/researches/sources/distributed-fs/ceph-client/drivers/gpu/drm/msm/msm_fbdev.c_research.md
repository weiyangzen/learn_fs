# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_fbdev.c

## Purpose
Implements the optional legacy fbdev compatibility layer for MSM DRM.

## Important APIs, types, and functions
- Module parameter `fbdev` enables/disables fbdev compatibility.
- `msm_fbdev_driver_fbdev_probe()` allocates framebuffer backing BO, pins it for scanout, maps it to CPU, and fills `fb_info`.
- `msm_fbdev_mmap()` maps the backing GEM object through PRIME mmap.
- `msm_fbdev_fb_destroy()` tears down helper, CPU vmap, framebuffer, and DRM client.
- `msm_fbdev_fb_dirty()` forwards fbdev damage to framebuffer dirty handling.

## Control flow
Probe selects a legacy DRM format, aligns pitch with `align_pitch()`, allocates a stolen or regular scanout framebuffer, pins its BO into KMS VM for physical/start address reporting, assigns helper funcs and fb ops, fills fb info, gets a CPU vaddr, and sets `screen_buffer`, `screen_size`, `smem_start`, and `smem_len`. Dirty ignores empty clips and forwards real damage through fb dirty callbacks.

## State and persistence
State is held by the DRM fb helper, fb_info, framebuffer, pinned BO IOVA, and CPU vmap while fbdev is active. Destroy releases those resources.

## Dependencies and integration points
Depends on DRM fb helper, GEM PRIME mmap, MSM framebuffer and GEM helpers, KMS VM, and deferred sysmem fb ops.

## Risks
The failure path after pinning/vmap setup removes the framebuffer but does not explicitly unpin the IOVA in this file; correctness depends on framebuffer/GEM teardown. The global `fbdev` parameter is declared here but higher-level DRM fbdev behavior must respect driver ops. Panic-console assumptions rely on the BO being pinned and CPU-mapped.

## Test signals
Boot fbcon, mmap from fbdev, deferred damage propagation, probe failure unwinds, suspend/resume, and module parameter behavior.
