# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_gem_prime.c

## Purpose
Implements MSM GEM PRIME/dma-buf import, export, pin, unpin, and vmap support.

## Important APIs, types, and functions
- `msm_gem_prime_get_sg_table()` exports pinned backing pages as an SG table.
- `msm_gem_prime_vmap()` and `msm_gem_prime_vunmap()` map/unmap GEM objects to kernel virtual addresses.
- `msm_gem_prime_import()` handles same-device self-import specially, otherwise delegates to DRM PRIME import.
- `msm_gem_prime_import_sg_table()` creates an MSM imported GEM object from an attachment SG table.
- `msm_gem_prime_export()` builds a dma-buf with MSM-specific release handling.
- `msm_gem_prime_pin()` and `msm_gem_prime_unpin()` pin owned backing pages for dma-buf access.

## Control flow
Export rejects `MSM_BO_NO_SHARE`, increments the GEM VMA refcount to keep lazy mappings alive, and exports a dma-buf with custom ops whose release drops that VMA ref before the DRM dma-buf release. Import detects dma-bufs exported by the same ops on the same device and returns a GEM object reference directly; external imports use DRM helpers and `msm_gem_import()`. Pin skips already imported objects, rejects NO_SHARE, and pins backing pages under the caller-held object lock.

## State and persistence
Exported dma-bufs hold a GEM reference through DRM core and an extra VMA ref until release. Imported objects store external SG table/page arrays in `msm_gem_object` and are treated as imported by GEM core.

## Dependencies and integration points
Depends on DRM PRIME/dma-buf helpers, GEM page/vmap helpers, and `msm_gem_import()`. Integrated through `drm_gem_object_funcs` and `drm_driver` PRIME hooks.

## Risks
`get_sg_table()` assumes pages were already pinned; otherwise it returns an error. NO_SHARE objects must never be exported/imported through PRIME. Vmap helpers assume the object lock context expected by GEM PRIME callbacks.

## Test signals
Same-device self-import, external dma-buf import/export, NO_SHARE rejection, pin/unpin balance, vmap/vunmap, and release dropping VMA refs are key tests.
