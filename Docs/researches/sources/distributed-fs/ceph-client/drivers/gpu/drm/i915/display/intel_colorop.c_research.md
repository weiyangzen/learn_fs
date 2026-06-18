# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_colorop.c

## Purpose
Provides the small i915 wrapper around DRM colorop objects used by the plane color pipeline UAPI.

## Important APIs and control flow
`to_intel_colorop()` converts a `struct drm_colorop` to the embedding `struct intel_colorop`. `intel_colorop_alloc()` zero-allocates the wrapper and returns `ERR_PTR(-ENOMEM)` on failure. `intel_colorop_create()` allocates and records the `enum intel_color_block` id. `intel_colorop_destroy()` calls `drm_colorop_cleanup()` and frees the wrapper.

## State and integration
Persistent state is the allocated `struct intel_colorop`, especially its embedded DRM colorop base and i915 color-block id. The file integrates with `intel_color_pipeline.c`, which creates colorops and passes `intel_colorop_destroy` as the DRM destroy callback.

## Risks and test signals
Risks are mostly lifetime related: destroying before DRM init completion, failing to cleanup DRM object state, or double-freeing through pipeline rollback paths. Tests should cover failed pipeline initialization, plane teardown, and KASAN/KMEMLEAK runs around DRM colorop object lifetime.
