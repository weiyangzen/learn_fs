<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_dma_buf.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_dma_buf.h

## Purpose
`xe_dma_buf.h` declares the Xe PRIME dma-buf entry points used by DRM GEM callbacks.

## Important APIs, types, and functions
The header includes `drm_gem.h` and declares `struct dma_buf *xe_gem_prime_export(struct drm_gem_object *obj, int flags);` and `struct drm_gem_object *xe_gem_prime_import(struct drm_device *dev, struct dma_buf *dma_buf);`.

## Control flow and integration points
There is no control flow in the header. DRM driver ops wire these functions into PRIME export/import paths. The implementation handles BO placement, dma-buf attachment, mapping, CPU access, and imported object construction.

## State and persistence behavior
The header owns no state. The declared functions manipulate GEM/BO references, dma-buf attachments, runtime PM references, and imported-object attachment state in the implementation.

## Dependencies, risks, and test signals
Dependencies are DRM GEM and dma-buf type visibility. Risks are signature drift with DRM PRIME callbacks or missing include coverage for users. Test signals are successful build of driver ops, PRIME ioctl export/import tests, and KUnit dma-buf scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_dma_buf.h -->
