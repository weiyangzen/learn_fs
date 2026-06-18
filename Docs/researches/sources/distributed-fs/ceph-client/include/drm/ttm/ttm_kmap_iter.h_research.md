# sources/distributed-fs/ceph-client/include/drm/ttm/ttm_kmap_iter.h

Purpose: defines a generic iterator interface for page-sized local kernel mappings of TTM resources.

Important APIs/types/functions: `struct ttm_kmap_iter_ops` provides `map_local()`, `unmap_local()`, and `maps_tt`. `struct ttm_kmap_iter` holds the ops pointer and is embedded by TT/resource-specific iterators.

Control flow: copy/move code initializes a specialized iterator, maps a page index into an `iosys_map`, copies or clears data, and unmaps it before moving to the next page. `maps_tt` distinguishes direct TT pages from aperture-backed TT resources.

State and persistence: iterator state is transient and specialization-specific. No backing memory is owned by this base header.

Dependencies and integration: depends on Linux types and `iosys_map`. Implemented by TT and resource IO mapping helpers, consumed by TTM memcpy move and CPU copy paths.

Risks and test signals: local mapping lifetime must be short and paired. Test page-by-page moves across TT, IO memory, and linear resources, highmem/local mapping correctness, and cleanup on copy errors.
