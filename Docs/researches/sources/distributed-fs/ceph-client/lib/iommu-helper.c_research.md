# sources/distributed-fs/ceph-client/lib/iommu-helper.c

Purpose: implements `iommu_area_alloc()`, a bitmap-based allocator for IOMMU aperture ranges with alignment and boundary-span constraints.

Important APIs: `iommu_area_alloc(map, size, start, nr, shift, boundary_size, align_mask)` searches the bitmap for `nr` zero bits starting at `start`, aligned by `align_mask`, rejects candidates that span an IOMMU boundary, sets the selected bits, and returns the index or `-1`.

Control flow: the function subtracts one from `size` to exclude the limit, calls `bitmap_find_next_zero_area()`, checks `iommu_is_span_boundary()`, advances `start` to the next boundary-aligned candidate on conflict, and retries. On success it mutates the bitmap with `bitmap_set()`.

State and persistence: the caller-owned bitmap is the persistent allocation state. There is no internal locking, so synchronization belongs to the caller.

Dependencies and integration: depends on bitmap helpers and the IOMMU helper header. It integrates with IOMMU free-area managers that need boundary-safe DMA/I/O virtual address allocation.

Risks: `size -= 1` assumes nonzero size; callers must serialize concurrent allocation/free; wrong `shift` or `boundary_size` can allow boundary crossings or waste address space; returning `-1` through an unsigned long requires callers to compare appropriately.

Test signals: bitmap allocator unit tests for alignment, exact-boundary, near-limit, full-map, and concurrent caller locking assumptions.
