# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_gem.c

## Purpose
`vmwgfx_gem.c` adapts vmwgfx TTM buffer objects to the DRM GEM and PRIME interfaces. It supplies GEM object callbacks, creates GEM handles for vmwgfx BOs, imports dma-buf scatter-gather tables, handles mmap/vmap differences for imported objects, and exposes a debugfs view of per-file GEM objects.

## Important APIs, Types, and Functions
- `vmw_gem_object_funcs` provides GEM operations: free, open/close, info printing, pin/unpin, sg-table export, vmap/vunmap, mmap, and vm ops.
- `vmw_vm_ops` routes GEM faults and write faults through vmwgfx BO VM handlers plus TTM open/close hooks.
- `vmw_gem_object_create_with_handle()` creates a vmwgfx BO with default domain based on MOB support and publishes a GEM handle.
- `vmw_prime_import_sg_table()` creates a `ttm_bo_type_sg` BO backed by an imported dma-buf reservation object and sg table.
- `vmw_gem_object_create_ioctl()` implements dmabuf allocation ABI response fields including map handle and current GMR id.
- `vmw_debugfs_gem_init()` registers `vmwgfx_gem_info`; debugfs helpers walk DRM files and object idrs.

## Control Flow
Object creation builds `vmw_bo_params`, calls `vmw_bo_create()`, then creates a GEM handle that owns the user reference. PRIME import locks the dma-buf reservation, creates an SG-type BO using the imported reservation and sg table, assigns vmwgfx GEM funcs, and unlocks. Mapping imported objects delegates to dma-buf operations and rejects iomem vmaps; local BO mappings use TTM helpers. mmap for imported objects resets VMA hooks before calling dma-buf mmap and drops the `drm_gem_mmap_obj()` reference on success.

## State and Persistence Behavior
Runtime state lives in GEM handle tables, BO refcounts, BO pin counts, TTM resources, imported dma-buf reservation objects, and optional debugfs output. No disk persistence exists. The debugfs walk observes open DRM files under `filelist_mutex` and object idrs under `table_lock`.

## Dependencies and Integration Points
The file depends on `vmwgfx_bo.h`, TTM GEM helpers, DRM PRIME helpers, dma-buf APIs, Linux debugfs, and vmwgfx BO VM fault handlers. KMS framebuffer creation and execbuf BO lookup rely on the GEM handles created here.

## Risks
Imported dma-buf paths have distinct ownership and mapping semantics; failure to reset VMA fields or drop references would cause stale vm_ops or leaks. `vmw_gem_object_get_sg_table()` assumes `bo->ttm` is a `vmw_ttm_tt`. Debugfs walks task names under RCU because stored pids may outlive tasks. Pin/unpin callbacks assume callers already hold the appropriate reservation context.

## Test Signals
Cover dmabuf allocation ioctl, GEM mmap/vmap/vunmap for local and imported objects, PRIME import/export, pin/unpin through framebuffer scanout, debugfs `vmwgfx_gem_info` under multiple DRM clients, and refcount/pin-count stability after handle close.
