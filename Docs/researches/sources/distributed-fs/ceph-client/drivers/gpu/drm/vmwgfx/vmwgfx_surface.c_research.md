# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_surface.c

Purpose: Implements vmwgfx user/internal surfaces, including legacy and guest-backed creation, PRIME/reference ioctls, backup buffers, coherent dirty tracking, scanout surfaces, and DRM dumb-buffer creation.

Important APIs/types: `struct vmw_user_surface`, `struct vmw_surface_dirty`, legacy/GB `vmw_res_func` tables, `vmw_surface_define_ioctl()`, `vmw_surface_reference_ioctl()`, `vmw_gb_surface_define*_ioctl()`, `vmw_gb_surface_reference*_ioctl()`, `vmw_gb_surface_define()`, and `vmw_dumb_create()`.

Control flow: Legacy define validates mips/formats, copies user sizes, computes offsets, initializes a resource, and optionally creates backup BOs. Legacy validation emits `SURFACE_DEFINE` and DMA upload/download. GB surfaces choose define command version by SM capability, bind/unbind MOBs, read back/invalidate, destroy views/bindings, and expose backup handles. Extended define validates SM4/SM4.1/SM5 fields, creates/adopts backup BOs, and enables coherent dirty tracking.

State/persistence: Metadata stores format/flags/mips/size/array/multisample/scanout. Resources track id, backup BO, guest-memory size/offset, dirty/coherent state, and views. User visibility is via TTM prime objects and file references.

Dependencies/integration: SVGA3D definitions, resource core, BO/GEM/TTM, binding/view cleanup, cursor snooping, surface cache, KMS scanout, and DRM dumb callbacks.

Risks/test signals: User ABI validation, feature gates, dirty range translation, PRIME/security reference rules, dumb-buffer ownership, coherent mmap damage, eviction, and scanout format tests.
