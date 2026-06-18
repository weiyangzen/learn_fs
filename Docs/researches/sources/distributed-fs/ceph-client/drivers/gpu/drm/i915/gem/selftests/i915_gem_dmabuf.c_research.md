# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/selftests/i915_gem_dmabuf.c

## Purpose
Verifies i915 PRIME dma-buf export/import behavior, including self-import reuse, external mock imports, forced same-driver imports as different devices, LMEM limitations, ownership transfer, and exported-object vmap behavior.

## APIs And Control Flow
Key tests are `igt_dmabuf_export()`, `igt_dmabuf_import_self()`, `igt_dmabuf_import_same_driver_lmem()`, `verify_access()`, `igt_dmabuf_import_same_driver()`, `igt_dmabuf_import()`, `igt_dmabuf_import_ownership()`, and `igt_dmabuf_export_vmap()`. Mock tests export/import shmem and mock dma-bufs; live tests force different-device import paths, verify LMEM-only import failure, and use GPU writes through imported objects to verify native-object visibility.

## State, Dependencies, Integration, Risks, And Tests
State is held in GEM objects, dma-buf refs, reservations/fences, attachments, sg tables, and maps. Dependencies include PRIME hooks, memory-region placement, mock context/dmabuf helpers, `igt_gpu_fill_dw()`, `dma_resv_wait_timeout()`, and `force_different_devices`. Risks include refcount/ownership transfer errors, LMEM migration policy changes, and stale importer fences. Signals include duplicate self-import objects, wrong LMEM error, non-SMEM exports, visibility mismatches, wait timeouts, and nonzero fresh vmaps.
