# sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_gem_prime.c

## Purpose
Implements etnaviv PRIME/dma-buf sharing hooks for sg-table export/import, vmap, pin/unpin, mmap, and imported object release.

## Important APIs, Types, and Functions
Exports `etnaviv_gem_prime_get_sg_table`, `etnaviv_gem_prime_vmap`, `etnaviv_gem_prime_pin`, `etnaviv_gem_prime_unpin`, and `etnaviv_gem_prime_import_sg_table`. Internal ops include `etnaviv_gem_prime_release`, `etnaviv_gem_prime_vmap_impl`, `etnaviv_gem_prime_mmap_obj`, and the imported-object `etnaviv_gem_prime_ops`. Imports the `DMA_BUF` namespace.

## Control Flow
Export sg-table requires local pages already pinned. PRIME pin pins local pages for non-imported objects; unpin currently delegates to the placeholder put-pages path. Import creates a private WC GEM object with PRIME ops, stores the provided sg table, allocates a page array, fills it from the sg table, lockdep-tags the object, and adds it to the GEM list. Vmap maps imported dma-bufs through `dma_buf_vmap`; mmap delegates to `dma_buf_mmap` and drops the reference acquired by generic GEM mmap.

## State and Persistence
Imported objects own a page pointer array but not the pages themselves; release frees the array, unmaps any dma-buf vmap, and calls `drm_prime_gem_destroy` with the sg table.

## Dependencies and Integration Points
Integrated through `drm_driver.gem_prime_import_sg_table` and GEM object funcs in `etnaviv_gem.c`. Depends on DRM PRIME helpers, dma-buf vmap/mmap APIs, and etnaviv GEM private allocation.

## Risks
`get_sg_table` assumes pinning has already happened. Imported pages are borrowed, so release must not unpin them. Vmap lifetime must pair with dma-buf vunmap. Mmap reference dropping must match DRM GEM mmap behavior.

## Test Signals
DMA-buf import/export tests, PRIME mmap/vmap tests, cross-device sharing workloads, object release leak checks, and lockdep class separation for imported GEM locks.
