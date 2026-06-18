# sources/distributed-fs/ceph-client/include/drm/drm_gem_shmem_helper.h

Purpose: Defines the shmem-backed GEM object subtype and helper APIs/macros for drivers whose buffer objects are pageable shmem files with optional pinning, vmap, madvise/purge, PRIME import, and dumb-buffer creation.

Important APIs, types, and functions: Defines `struct drm_gem_shmem_object`, `to_drm_gem_shmem_obj()`, init/create/release/free helpers, page put/pin/unpin/vmap/vunmap/mmap helpers, locked pin/unpin and madvise helpers, `drm_gem_shmem_is_purgeable()`, purge, sg-table helpers, print-info helper, `drm_gem_shmem_vm_ops`, object-func wrapper inlines, PRIME import helpers, `drm_gem_shmem_dumb_create()`, `DRM_GEM_SHMEM_DRIVER_OPS`, and KUnit-only direct wrappers.

Control flow: Drivers create shmem GEM objects, pin pages for scanout or dma-buf access, optionally vmap them for CPU access, and unpin/unmap when no longer needed. Madvise marks objects as purgeable or active; purge can drop unpinned, non-imported, non-exported backing pages with positive madv and an sg table. Object funcs wrap the helpers under GEM reservation locking. Driver op macros install shmem PRIME and dumb-create defaults.

State and persistence: Per-object state includes the base GEM object, page array, page use and pin counts, madv state/list, imported sg table, virtual address and vmap count, dirty/accessed-on-put flags, and write-combine mapping policy. The shmem file backing persists while the GEM object exists, but pages can be evicted or purged if unpinned and marked purgeable.

Dependencies and integration points: Depends on Linux shmem/mm, GEM, PRIME, dma-buf attachments, sg tables, VM operations, DRM file/ioctl, shrinker/madvise patterns, and KUnit test hooks. Used by many virtual/simple GPU and display drivers.

Risks and test signals: Risks include page pin/use count imbalance, purging exported or imported buffers, stale sg tables after purge, vmap count leaks, dirty/accessed flags not applied on put, mmap attribute mismatch, and madvise races under reservation locks. Test create/free, pin/unpin nesting, vmap/vunmap nesting, mmap faults, PRIME import/export, madvise active/purge transitions, shrinker purge under memory pressure, KUnit helper paths, and write-combined mapping behavior.
