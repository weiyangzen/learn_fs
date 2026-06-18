# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_gem_atomic_helper.c

## Purpose
`drm_gem_atomic_helper.c` provides generic atomic modeset helpers for GEM-backed framebuffers. It primarily solves two problems: implicit synchronization for GEM framebuffer planes and safe kernel mappings for shadow-buffered planes whose commit-tail update functions need CPU access to framebuffer data.

## Important APIs, Types, And Functions
The main synchronization entry point is `drm_gem_plane_helper_prepare_fb()`, which extracts reservation fences from every GEM object backing a framebuffer plane. Shadow-plane state helpers include `__drm_gem_duplicate_shadow_plane_state()`, `drm_gem_duplicate_shadow_plane_state()`, `__drm_gem_destroy_shadow_plane_state()`, `drm_gem_destroy_shadow_plane_state()`, `__drm_gem_reset_shadow_plane()`, and `drm_gem_reset_shadow_plane()`. Mapping helpers are `drm_gem_begin_shadow_fb_access()` and `drm_gem_end_shadow_fb_access()`, with `drm_gem_simple_kms_*` wrappers for `struct drm_simple_display_pipe`.

## Control Flow
`prepare_fb` starts with any explicit fence already attached to the plane state. If an explicit fence exists, it requests kernel fences from each GEM reservation object; otherwise it requests write fences. For each framebuffer plane, it obtains the GEM object through `drm_gem_fb_get_obj()`, calls `dma_resv_get_singleton()`, and either installs that fence directly or chains it with the existing fence using `dma_fence_chain`. Shadow state reset allocates a `drm_shadow_plane_state`, initializes base atomic state and format-conversion state, and attaches it to the plane. Duplication copies the base atomic state and format conversion state but intentionally does not copy mappings. `begin_shadow_fb_access` maps all framebuffer BOs through `drm_gem_fb_vmap()` and records both base mappings and offset-adjusted data pointers; `end_shadow_fb_access` unmaps in reverse through `drm_gem_fb_vunmap()`.

## State And Persistence Behavior
The helper stores per-commit shadow mappings in `struct drm_shadow_plane_state`, not in the plane or framebuffer itself. Mapping lifetime is bounded by atomic access callbacks and must not leak into duplicated state. Fence state is persisted in `state->fence` for the atomic helper machinery to wait on. Format conversion state is copied and released with the shadow plane state.

## Dependencies And Integration Points
This file depends on dma-resv and dma-fence-chain for implicit synchronization, DRM atomic state helpers for plane-state lifecycle, `drm_gem_framebuffer_helper.c` for framebuffer BO lookup and vmap/vunmap, and `drm_simple_kms_helper` for simple display pipe wrappers. Drivers commonly wire these helpers through `DRM_GEM_SHADOW_PLANE_FUNCS`, `DRM_GEM_SHADOW_PLANE_HELPER_FUNCS`, or plane helper `prepare_fb`.

## Risks
Fence merging is subtle: explicit fences are intentionally allowed to override normal implicit write-fence behavior, and adding both in the wrong way would regress explicit synchronization use cases such as different refresh rates sharing one buffer. Shadow mappings must be created outside commit-tail paths that cannot legally call `dma_buf_vmap()`. State duplication must not retain stale `iosys_map` pointers. Error paths in `prepare_fb` must drop the currently accumulated fence chain.

## Test Signals
Coverage should include atomic plane updates with imported dma-buf framebuffers, explicit fence versus implicit fence behavior, multi-plane framebuffer fence chaining, shadow-plane reset/duplicate/destroy cycles, begin/end mapping balance under failure injection, and simple-KMS users of the wrapper callbacks. Lockdep and dma-fence selftests are relevant supporting signals.
