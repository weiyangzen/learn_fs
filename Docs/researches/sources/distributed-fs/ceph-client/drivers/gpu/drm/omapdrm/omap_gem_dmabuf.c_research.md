# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/omap_gem_dmabuf.c

Purpose: Implements OMAPDRM PRIME/dma-buf export and import glue around the GEM memory manager.

Important APIs/types/functions: `omap_dmabuf_ops` supplies `map_dma_buf`, `unmap_dma_buf`, `release`, `begin_cpu_access`, `end_cpu_access`, and `mmap`. Public entry points are `omap_gem_prime_export` and `omap_gem_prime_import`.

Control flow: Export fills `DEFINE_DMA_BUF_EXPORT_INFO` using `omap_gem_mmap_size`, object reservation, OMAP dma-buf ops, and `drm_gem_dmabuf_export`. Attachment mapping calls `omap_gem_get_sg`; unmapping calls `omap_gem_put_sg`. CPU access rejects tiled buffers, then ensures backing pages exist. Import short-circuits self-import from the same device by taking a GEM reference; external imports attach to the dma-buf, map the attachment for `DMA_TO_DEVICE`, create an OMAP dmabuf-backed GEM object, and store the import attachment.

State and persistence: Exported dma-bufs hold the GEM object in `priv`; imported objects retain the attachment and SG table until GEM destruction via `drm_prime_gem_destroy`.

Dependencies and integration: Depends on DMA-BUF namespace, DRM PRIME helpers, `omap_gem_get_sg`, `omap_gem_new_dmabuf`, and GEM mmap helpers. The object funcs in `omap_gem.c` point `.export` here.

Risks: CPU access to tiled buffers is not implemented and returns `-ENOMEM`, which may surprise generic dma-buf users. Import maps attachments `DMA_TO_DEVICE`; bidirectional users depend on subsequent cache sync behavior. Error paths must balance `dma_buf_attach`, `get_dma_buf`, map, detach, and put operations.

Test signals: PRIME self-import should return the same GEM object with increased refcount; external import should reject non-contiguous buffers when DMM is unavailable; dma-buf mmap should use the OMAP GEM fault path; begin/end CPU access should fail for tiled buffers and succeed for linear shmem buffers.
