
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_prime.c

## Purpose
Implements PRIME/dma-buf import and export helpers for Nouveau GEM objects, allowing buffer sharing with other DRM devices while enforcing Nouveau placement and no-share policy.

## Important APIs, Types, and Functions
External functions are `nouveau_gem_prime_get_sg_table()`, `nouveau_gem_prime_import_sg_table()`, `nouveau_gem_prime_pin()`, `nouveau_gem_prime_unpin()`, and `nouveau_gem_prime_export()`.

## Control Flow
Export sg-table creation converts the TTM page array to an sg table with `drm_prime_pages_to_sg()`. Import locks the dma-buf reservation object, allocates a Nouveau BO in GART domain using the supplied sg table and shared reservation object, initializes the embedded GEM object, initializes BO/TTM state, and returns the GEM object. PRIME pin pins the BO in GART; unpin releases it. Export rejects `nvbo->no_share`, prepares the BO for export with a non-blocking TTM operation context, then delegates to `drm_gem_prime_export()`.

## State and Persistence
Imported objects persist as Nouveau BO/GEM objects backed by the dma-buf reservation object and sg table. Export does not create new persistent Nouveau state beyond dma-buf bookkeeping in DRM/TTM core.

## Dependencies and Integration Points
Depends on Linux dma-buf, DRM PRIME helpers, TTM TT pages, Nouveau BO/GEM allocation, and the GEM object function table installed in `nouveau_gem.c`. Registered through the DRM driver and GEM object funcs.

## Risks and Test Signals
Risks include exporting private no-share BOs, pinning failures mapped to `-EINVAL`, reservation locking/lifetime with imported dma-bufs, and assumptions that TTM pages exist for sg export. Test signals include PRIME import/export with another DRM driver, no-share export denial, GART pin/unpin under eviction pressure, mmap/rendering of imported BOs, and dma-buf lifetime after file close.
