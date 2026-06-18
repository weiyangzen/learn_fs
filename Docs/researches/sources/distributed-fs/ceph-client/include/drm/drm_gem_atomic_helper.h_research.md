# sources/distributed-fs/ceph-client/include/drm/drm_gem_atomic_helper.h

Purpose: Declares GEM-aware atomic plane helpers, especially for preparing framebuffers and managing shadow-buffered plane state with CPU mappings and format-conversion state.

Important APIs, types, and functions: Declares `drm_gem_plane_helper_prepare_fb()`, shadow plane maximum size constants, `struct drm_shadow_plane_state`, `to_drm_shadow_plane_state()`, low-level and public reset/duplicate/destroy helpers, `DRM_GEM_SHADOW_PLANE_FUNCS`, begin/end framebuffer access helpers, `DRM_GEM_SHADOW_PLANE_HELPER_FUNCS`, simple-display-pipe shadow helpers, and `DRM_GEM_SIMPLE_DISPLAY_PIPE_SHADOW_PLANE_FUNCS`.

Control flow: Atomic plane `prepare_fb` pins or prepares GEM-backed framebuffers. Shadow-buffered planes use a subclassed plane state that stores mappings for framebuffer BOs and data pointers adjusted for offsets. Reset, duplicate, and destroy hooks initialize/copy/release conversion state. Begin/end access hooks establish and release CPU access/mappings around shadow updates, and simple display pipe macros wire the same flow into simple KMS drivers.

State and persistence: Shadow plane state is per-plane atomic state and persists across commits until replaced. Its mappings are transitional and should be established in prepare/begin paths and removed in cleanup/end paths. Format-conversion temporary storage is copied or destroyed with plane state.

Dependencies and integration points: Depends on GEM objects, plane state, `iosys_map`, DRM format conversion, FourCC info, and simple display pipes. Integrates with atomic plane funcs/helper funcs and drivers that upload from shadow buffers to hardware memory.

Risks and test signals: Risks include leaking CPU mappings, duplicating transitional map state incorrectly, stale data pointers after framebuffer offsets change, prepare/cleanup imbalance, shadow buffer size limits inconsistent with mode config, and missing CPU access synchronization for imported dma-bufs. Test atomic plane enable/disable, framebuffer replacement, duplicate/destroy under check-only commits, mmap/vmap failures, imported buffers, format conversion reuse, and simple-pipe helper macros.
