# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_prime.c

## Purpose

`radeon_prime.c` implements the Radeon KMS driver's PRIME/DMA-BUF GEM sharing hooks. It converts exported Radeon BO pages into scatter-gather tables, imports external DMA-BUF attachments as GTT-backed Radeon BOs, pins/unpins shared BOs for PRIME access, and blocks export of unsafe userptr-backed buffers.

## Important APIs, Functions, And Types

- `radeon_gem_prime_get_sg_table(struct drm_gem_object *obj)` converts a Radeon GEM object's TTM pages (`bo->tbo.ttm->pages`, `num_pages`) to an `sg_table` with `drm_prime_pages_to_sg()`.
- `radeon_gem_prime_import_sg_table(struct drm_device *dev, struct dma_buf_attachment *attach, struct sg_table *sg)` creates a Radeon BO backed by an imported SG table and the DMA-BUF reservation object.
- `radeon_gem_prime_pin(struct drm_gem_object *obj)` pins the BO into `RADEON_GEM_DOMAIN_GTT` and increments `prime_shared_count` on success.
- `radeon_gem_prime_unpin(struct drm_gem_object *obj)` unpins and decrements `prime_shared_count` when nonzero.
- `radeon_gem_prime_export(struct drm_gem_object *gobj, int flags)` rejects userptr-backed BOs with `-EPERM`, otherwise delegates to `drm_gem_prime_export()`.
- Key types are `struct drm_gem_object`, `struct radeon_bo`, `struct dma_buf_attachment`, `struct dma_resv`, and `struct sg_table`.

## Control Flow

Export-side SG table creation assumes the BO has a populated TTM translation table and passes its page array to DRM PRIME helpers. Full export goes through `radeon_gem_prime_export()`, which first calls `radeon_ttm_tt_has_userptr()` to prevent exporting memory owned by userspace userptr mappings, then returns the generic DRM GEM PRIME DMA-BUF.

Import starts with the attachment's `dma_buf->resv`. The function locks the reservation object, calls `radeon_bo_create()` with size `attach->dmabuf->size`, page alignment, non-kernel placement, GTT domain, the supplied SG table, and the shared reservation object, then unlocks regardless of success. On success it sets the GEM object function table to `radeon_gem_object_funcs`, adds the BO to `rdev->gem.objects` under `rdev->gem.mutex`, initializes `prime_shared_count` to one, and returns the GEM base object.

Pinning is deliberately simple: the BO is pinned into GTT with `radeon_bo_pin()`, and the shared count is incremented only when the pin succeeds. Unpin always calls `radeon_bo_unpin()` and then decrements the count defensively only if it is nonzero.

## State And Persistence Behavior

The file persists no disk state. Runtime state changes are on BOs and device lists:

- Imported BOs are created in GTT placement and tied to the DMA-BUF reservation object, enabling cross-driver fencing/reservation synchronization.
- `bo->tbo.base.funcs` is set so the imported object uses Radeon GEM object operations.
- Imported BOs are linked into `rdev->gem.objects` for normal Radeon GEM lifetime tracking.
- `prime_shared_count` tracks active PRIME sharing/pin references at the BO level.

## Dependencies And Integration Points

The implementation depends on Linux DMA-BUF reservation locking, DRM PRIME helpers, TTM TT page arrays, Radeon BO creation/pinning APIs, GEM object conversion helpers, and the Radeon DRM driver table. In this source tree, `radeon_drv.c` wires `.gem_prime_import_sg_table = radeon_gem_prime_import_sg_table`; other PRIME hooks may be inherited from DRM GEM helpers or wired elsewhere depending on kernel API shape.

## Risks And Edge Cases

- `radeon_gem_prime_get_sg_table()` assumes `bo->tbo.ttm` and its page array are valid. Calling it for an object without populated TTM pages would be unsafe.
- Import correctness depends on holding the DMA-BUF reservation lock while creating the BO with the shared reservation object. Changes to locking order could deadlock with exporter/importer paths.
- `prime_shared_count` is local bookkeeping, not a full lifetime mechanism by itself. Mismatched pin/unpin calls can underrepresent actual sharing, though the decrement is guarded against going below zero.
- Userptr export is explicitly forbidden. Removing that check could expose process-owned pages through DMA-BUF in ways the driver cannot safely migrate, pin, or revoke.
- Imported BOs are added to the global GEM object list; failure paths before that point must not leave partially linked objects.

## Test Signals

Useful validation includes PRIME import/export smoke tests with another DRM device, DMA-BUF fence synchronization tests, import failure injection around `radeon_bo_create()`, userptr GEM export returning `-EPERM`, repeated pin/unpin balance tests observing `prime_shared_count`, and device unload after imported DMA-BUF objects to confirm list/lifetime cleanup does not leak or double-free BOs.
