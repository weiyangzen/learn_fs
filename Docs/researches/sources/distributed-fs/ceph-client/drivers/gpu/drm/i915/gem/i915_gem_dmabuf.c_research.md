## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_dmabuf.c

### Purpose

`i915_gem_dmabuf.c` implements PRIME/dma-buf export and import for i915 GEM objects, including attachment mapping, CPU access synchronization, mmap/vmap support, imported-object page acquisition, and local object fast-path import.

### Important APIs, types, and functions

Public entry points are `i915_gem_prime_export()` and `i915_gem_prime_import()`. The `dma_buf_ops` implementation provides attach/detach, map/unmap, mmap, vmap/vunmap, begin/end CPU access, and release. Imported dma-buf objects use `i915_gem_object_dmabuf_ops` with `i915_gem_object_get_pages_dmabuf()` and `i915_gem_object_put_pages_dmabuf()`.

### Control flow

Export fills `DEFINE_DMA_BUF_EXPORT_INFO`, lets object ops veto or prepare dmabuf export, and calls `drm_gem_dmabuf_export()` with the GEM reservation object. Attach requires the object to be migratable to system memory, migrates it there under a ww context, waits for migration, and pins pages. Mapping copies the object's sg table and maps it for the attachment device with `DMA_ATTR_SKIP_CPU_SYNC`. CPU access locks the object, pins pages, transitions to CPU or GTT domain, and retries ww deadlocks. Import returns the original object if the dma-buf came from the same i915 device; otherwise it attaches, refs the dma-buf, allocates a private GEM object, points it at the dma-buf reservation object, and sets GTT read domain.

### State and persistence behavior

Exports share the GEM object's reservation object with the dma-buf. Attach pins pages until detach. Imports persist `obj->base.import_attach`, reuse the external `dma_buf->resv`, and map/unmap pages through dma-buf attachment callbacks. CPU access transitions alter GEM cache/domain state. For some non-coherent cases, imported pages trigger a global `wbinvd_on_all_cpus()`.

### Dependencies

It depends on Linux dma-buf/highmem/dma-resv APIs, DRM GEM PRIME helpers, i915 object/domain/migration/scatterlist helpers, ww locking, and module namespace import for DMA_BUF.

### Integration points

Driver hooks in `i915_driver.c` use `i915_gem_prime_import()`. GEM object ops expose export through `i915_gem_prime_export()`, and GVT uses export for virtual GPU dma-buf sharing. Imported objects integrate with normal i915 object lifetime through custom get/put-pages ops.

### Risks

Migration-to-system-memory failure prevents attach/export use by devices that cannot access LMEM. Cache synchronization is subtle: skipped CPU sync, GTT-domain transitions, and heavy `wbinvd_on_all_cpus()` are platform-dependent. Same-device import intentionally refs the GEM object rather than the dma-buf file, so lifetime assumptions differ from foreign imports. sg-table copying must preserve original entries accurately.

### Test signals

PRIME export/import igt tests, cross-device dma-buf sharing, mmap/vmap CPU access tests, LMEM migration tests, ww-deadlock retry coverage, same-device import fast path, and selftests included under `CONFIG_DRM_I915_SELFTEST`.
