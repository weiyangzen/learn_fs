# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_fb.c

## Purpose
Implements MSM framebuffer objects, scanout preparation/cleanup, dirtyfb propagation, framebuffer creation/validation, debug descriptions, and stolen/regular fb allocation.

## Important APIs, types, and functions
- `struct msm_framebuffer` extends `drm_framebuffer` with MSM format, dirtyfb refcount, per-plane IOVA, and prepare count.
- `msm_framebuffer_create()` looks up GEM handles and calls the internal initializer.
- `msm_framebuffer_prepare()` pins all plane BOs into the KMS VM and records IOVAs.
- `msm_framebuffer_cleanup()` unpins plane BOs and clears IOVAs when prepare count reaches zero.
- `msm_alloc_stolen_fb()` allocates fbdev-style scanout buffers, preferring stolen memory.

## Control flow
Create validates plane objects, format support via `mdp_get_format()`, plane sizes including offsets/pitches/subsampling, and rejects `MSM_BO_NO_SHARE` because scanout maps into the KMS VM. Prepare increments dirtyfb when needed, uses `prepare_count` to avoid duplicate pinning, gets VMA refs, and pins IOVAs for each plane. Cleanup mirrors this by decrementing dirtyfb, unpinning IOVAs, and dropping VMA refs on the final cleanup.

## State and persistence
Framebuffer state persists in `struct msm_framebuffer` while the DRM framebuffer exists. Per-plane IOVAs are valid only while prepared. Dirtyfb refcount tracks whether users of the fb need pixel flush handling.

## Dependencies and integration points
Depends on DRM framebuffer/GEM helpers, MSM KMS VM, GEM IOVA helpers, MDP format lookup, dirtyfb helper, and fbdev allocation path.

## Risks
If pinning one plane fails after earlier planes are pinned, the function returns without local unwind, relying on callers/error paths to cleanup. `prepare_count` and dirtyfb refcount must stay balanced. Plane size validation must match DRM format subsampling to prevent scanout beyond BO size.

## Test signals
Framebuffer creation with multi-plane formats, invalid pitches/offsets/sizes, NO_SHARE rejection, repeated prepare/cleanup balance, dirtyfb behavior, and stolen-memory fallback are useful tests.
