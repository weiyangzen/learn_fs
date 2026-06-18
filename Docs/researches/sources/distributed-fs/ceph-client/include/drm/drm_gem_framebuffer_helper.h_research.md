# sources/distributed-fs/ceph-client/include/drm/drm_gem_framebuffer_helper.h

Purpose: Declares helper functions for creating and managing DRM framebuffers backed by GEM objects, including handle creation, destruction, CPU access, vmap/vunmap, dirty-enabled creation, and AFBC metadata initialization.

Important APIs, types, and functions: Defines `AFBC_VENDOR_AND_TYPE_MASK`, `drm_gem_fb_get_obj()`, `drm_gem_fb_destroy()`, `drm_gem_fb_create_handle()`, `drm_gem_fb_init_with_funcs()`, `drm_gem_fb_create_with_funcs()`, `drm_gem_fb_create()`, `drm_gem_fb_create_with_dirty()`, `drm_gem_fb_vmap()`, `drm_gem_fb_vunmap()`, `drm_gem_fb_begin_cpu_access()`, `drm_gem_fb_end_cpu_access()`, `drm_is_afbc()`, and `drm_gem_fb_afbc_init()`.

Control flow: Framebuffer creation looks up GEM handles from a mode command, validates format and plane metadata, stores object references in the framebuffer, and installs framebuffer funcs. Handle creation exports a GEM handle for GETFB-like paths. Vmap and CPU access helpers iterate backing objects for all planes. AFBC initialization validates modifier-derived block geometry, alignment, offsets, and minimum buffer size for AFBC framebuffers.

State and persistence: The helper manages framebuffer references to GEM backing objects and temporary CPU mappings. State persists as long as the framebuffer object exists; mappings persist only between vmap/vunmap calls.

Dependencies and integration points: Depends on GEM, DRM framebuffer core, FourCC/modifier metadata, dma-buf CPU access directions, `iosys_map`, mode commands, and AFBC modifiers. Integrated by most GEM-based KMS drivers' `fb_create` callbacks.

Risks and test signals: Risks include plane handle/object mismatch, missing references on shared objects, invalid offsets/pitches accepted, vmap partial failure unwinds, CPU access not propagated to all planes, dirty callback mismatch, and AFBC size/alignment underestimation. Test addfb2 with one and multi-plane formats, duplicate handles, invalid pitches/offsets, vmap failure injection, CPU begin/end on imported buffers, dirtyfb helper creation, and AFBC modifiers.
