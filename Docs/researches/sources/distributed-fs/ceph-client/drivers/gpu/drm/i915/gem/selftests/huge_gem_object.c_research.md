# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/selftests/huge_gem_object.c

## Purpose
This selftest helper creates synthetic very large GEM objects without allocating all unique physical pages. It lets tests exercise address-space, SG iteration, GTT binding, and object-size paths with a large DMA size and a smaller real physical footprint.

## Important APIs, Types, and Functions
The public constructor is `huge_gem_object`. Backend object ops are `huge_get_pages` and `huge_put_pages`, with `huge_free_pages` freeing only the real allocated pages. The object stores its real physical size in `obj->scratch`.

## Control Flow
Creation validates nonzero and aligned `phys_size`, `phys_size <= dma_size`, and DMA-size fit in GEM object size, allocates a GEM object, initializes a private GEM object with `dma_size`, sets struct-page memory, CPU read/write domains, cache coherency, and records `phys_size`. Page get allocates an SG table with one entry per DMA page, allocates real highmem pages for the first `phys_size / PAGE_SIZE` entries, then repeats references to those pages through the remaining SG entries to simulate a huge object. It prepares pages for GTT DMA and installs them. Page put finishes GTT pages, frees only the real pages, and clears dirty state.

## State and Persistence Behavior
Persistent test-object state is the synthetic GEM size (`base.size`) and real backing size (`scratch`). SG entries beyond the real page count alias earlier pages, so contents are not a faithful full-size backing store.

## Dependencies and Integration Points
It depends on GEM object initialization, cache coherency helpers, SG iterators, GTT prepare/finish, and selftest-only consumers that need large object behavior.

## Risks
This is not a production object model: aliasing pages can hide data-integrity bugs but is appropriate for address-space stress. Freeing must stop at the real page count to avoid double-free. `sg_alloc_table` page counts are limited by unsigned int.

## Test Signals
Huge-object selftests should validate size reporting, SG iteration beyond real backing, GTT binding/unbinding, error cleanup on allocation or DMA preparation failure, and no double-free on repeated alias pages.
