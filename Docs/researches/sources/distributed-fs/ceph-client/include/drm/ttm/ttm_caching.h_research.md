# sources/distributed-fs/ceph-client/include/drm/ttm/ttm_caching.h

Purpose: defines TTM CPU caching policy names and the conversion entry point to page protections.

Important APIs/types/functions: `TTM_NUM_CACHING_TYPES` is 3. `enum ttm_caching` covers `ttm_uncached`, `ttm_write_combined`, and `ttm_cached`. `ttm_prot_from_caching()` converts a caching enum and base `pgprot_t` into the mapping protection to use.

Control flow: allocation, mapping, and fault paths choose an enum based on placement/device requirements and ask `ttm_prot_from_caching()` for CPU PTE attributes.

State and persistence: caching policy is stored in TTM TT/resources and affects mappings while present.

Dependencies and integration: depends on Linux page-table types. Integrated by TTM TT, pool, BO mapping, and resource mapping code.

Risks and test signals: wrong cache policy can cause incoherent GPU/CPU access or slow mappings. Test cached/write-combined/uncached mmap and kmap paths, device snooping assumptions, and architecture-specific pgprot output.
