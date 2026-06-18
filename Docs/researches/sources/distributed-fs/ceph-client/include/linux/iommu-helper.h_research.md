# sources/distributed-fs/ceph-client/include/linux/iommu-helper.h

Purpose: This header provides small generic helpers for IOMMU bitmap allocation and DMA boundary calculations.

Important APIs, types, and functions: `iommu_device_max_index` clamps an allocation size against a DMA mask and offset. `iommu_is_span_boundary` detects whether an indexed range crosses a power-of-two boundary. `iommu_area_alloc` allocates from a bitmap subject to start, length, shift, boundary, and alignment constraints. `iommu_num_pages` computes covered I/O pages for an address/length pair.

Control flow: Allocation users compute page counts and boundary constraints, then call `iommu_area_alloc` to find a suitable bitmap span. Boundary detection BUGs if the boundary size is not power-of-two.

State and persistence: The helpers operate on caller-owned bitmaps and have no internal state.

Dependencies and integration points: Depends on `bug.h`, `log2.h`, `math.h`, and generic types. Used by IOMMU/DMA implementations that maintain bitmap-based aperture allocators.

Risks: Invalid boundary sizes crash via `BUG_ON`. Offsets and masks must be in compatible units. Integer overflow in size+offset or address+length calculations must be considered by callers.

Test signals: Test DMA mask clamping, boundary-crossing at exact edges, non-crossing spans, page count rounding for unaligned starts, alignment masks, and failure when no bitmap span is available.
