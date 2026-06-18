# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_prime.h

## Purpose

`radeon_prime.h` declares the private Radeon PRIME/DMA-BUF hook functions used by the Radeon DRM driver and related GEM code. It is a narrow interface around exporting, importing, pinning, unpinning, and CPU mapping PRIME-shared GEM objects.

## Important APIs, Types, And Functions

- `radeon_gem_prime_export(struct drm_gem_object *gobj, int flags)`
- `radeon_gem_prime_get_sg_table(struct drm_gem_object *obj)`
- `radeon_gem_prime_pin(struct drm_gem_object *obj)`
- `radeon_gem_prime_unpin(struct drm_gem_object *obj)`
- `radeon_gem_prime_vmap(struct drm_gem_object *obj)`
- `radeon_gem_prime_vunmap(struct drm_gem_object *obj, void *vaddr)`
- `radeon_gem_prime_import_sg_table(struct drm_device *dev, struct dma_buf_attachment *, struct sg_table *sg)`

The declarations rely on DRM and DMA-BUF types being visible from including files; the header does not add its own forward declarations.

## Control Flow

There is no runtime control flow in the header. It provides compile-time declarations for PRIME operations. `radeon_prime.c` implements export, SG-table creation, import, pin, and unpin in this source set. The header also declares vmap/vunmap functions; they are not implemented in the paired `radeon_prime.c` file reviewed here, so either they are obsolete declarations, implemented conditionally outside this subset in other kernel versions, or unused in this tree.

## State And Persistence Behavior

The header owns no state. The declared functions operate on GEM objects, BO pinning state, DMA-BUF reservation objects, and imported BO list membership, but all such state is managed in implementation files.

## Dependencies And Integration Points

The header connects the Radeon driver table and GEM/PRIME code to `radeon_prime.c`. `radeon_drv.c` uses at least the SG-table import declaration for `.gem_prime_import_sg_table`. The API depends on DRM core types, DMA-BUF attachment and SG-table types, and Radeon GEM object conventions.

## Risks And Edge Cases

- The vmap/vunmap declarations are not matched by implementations in `radeon_prime.c` in this tree. If a caller starts using them without adding definitions, the build will fail at link time.
- Because the header does not include or forward-declare its parameter types, include-order mistakes can create compile failures.
- Signature drift against DRM core PRIME hooks is a recurring maintenance risk when kernel DRM APIs change.

## Test Signals

Compile/link coverage is the primary header signal, especially with all PRIME hooks enabled. Additional runtime signals come from the implementation: successful DMA-BUF import, userptr export rejection, GTT pin/unpin balancing, and clean unload with imported/exported objects.
