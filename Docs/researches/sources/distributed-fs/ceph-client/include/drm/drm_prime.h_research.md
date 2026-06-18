# sources/distributed-fs/ceph-client/include/drm/drm_prime.h

## Purpose
`drm_prime.h` declares DRM PRIME helpers for exporting and importing GEM buffer objects through dma-buf file descriptors. It provides per-file caches, dma-buf operations, scatter-gather conversion, mmap/vmap helpers, and handle/fd translation.

## Important APIs, types, and functions
`struct drm_prime_file_private` contains private rb-tree caches for dma-bufs and handles protected by a mutex. Core APIs include `drm_gem_prime_fd_to_handle`, `drm_gem_prime_handle_to_dmabuf`, `drm_gem_prime_handle_to_fd`, `drm_gem_dmabuf_export`, and `drm_gem_dmabuf_release`. Export helpers include `drm_gem_map_attach`, `drm_gem_map_detach`, `drm_gem_map_dma_buf`, `drm_gem_unmap_dma_buf`, `drm_gem_dmabuf_vmap`, `drm_gem_dmabuf_vunmap`, `drm_gem_prime_mmap`, `drm_gem_dmabuf_mmap`, `drm_prime_pages_to_sg`, and `drm_gem_prime_export`. Import helpers include `drm_gem_is_prime_exported_dma_buf`, `drm_gem_prime_import_dev`, `drm_gem_prime_import`, `drm_prime_gem_destroy`, and SG extraction helpers.

## Control flow
Export converts a GEM handle to a dma-buf and then to an fd while caching associations per file. Import converts a PRIME fd to a dma-buf, attaches/maps as needed, and returns a GEM handle or object. DMA mappings use sg-tables and direction-specific map/unmap operations. Mmap/vmap helpers bridge GEM memory into userspace or kernel mappings.

## State and persistence
State is per-open-file cache data plus dma-buf/GEM reference counts and attachment mappings. The data is runtime-only and ends when file handles and objects are closed/released.

## Dependencies and integration points
This header integrates GEM, dma-buf, scatterlist/sg_table, devices, iosys maps, vm areas, and DRM file-private handle namespaces. It is the main cross-driver buffer sharing interface.

## Risks and test signals
Risks include fd/handle cache races, reference leaks, mapping direction mismatches, importing one's own exported dma-buf incorrectly, SG table size assumptions, mmap permission issues, and stale attachments after device removal. Test signals include PRIME export/import round trips, self-import, cross-device sharing, mmap/vmap, SG conversion, fd close and handle close ordering, and IGT PRIME tests.
