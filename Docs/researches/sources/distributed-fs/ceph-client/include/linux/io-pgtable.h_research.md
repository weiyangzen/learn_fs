# sources/distributed-fs/ceph-client/include/linux/io-pgtable.h

Purpose: This header defines the I/O page-table allocator interface used by IOMMU drivers to create and manipulate hardware-specific translation tables.

Important APIs, types, and functions: Formats are enumerated by `enum io_pgtable_fmt`. `struct io_pgtable_cfg` describes quirks, address sizes, page sizes, coherency, TLB callbacks, optional custom allocators, and backend-private format data. `struct io_pgtable_ops` provides `map_pages`, `unmap_pages`, `iova_to_phys`, optional `pgtable_walk`, and dirty tracking. Allocation is through `alloc_io_pgtable_ops` and `free_io_pgtable_ops`.

Control flow: IOMMU drivers select a format and pass configuration plus a cookie to the allocator. Backends populate format-specific config, return ops, and use `iommu_flush_ops` callbacks for full flushes, walk-cache flushes, and page invalidation batching. Inline helpers call TLB callbacks only when present.

State and persistence: `struct io_pgtable` stores the selected format, cookie, copied config, and operation table. Page-table memory persists until `free_io_pgtable_ops`; TLB dirtiness may remain and must be handled by caller sequencing.

Dependencies and integration points: Depends on `linux/iommu.h` for protection flags, dirty bitmap, and gather state. Integrates with ARM LPAE/v7s, Mali, Apple DART, and AMD backend init functions.

Risks: Wrong quirks or address-size fields can create invalid translations. Custom allocators must return zeroed DMA-mappable memory. TLB callbacks can run in atomic context and must not block. Dirty tracking requires hardware/backend support and correct clear/no-clear flags.

Test signals: Backend tests should cover map/unmap granularity, TLB callback ordering, custom allocator acceptance, unsupported quirks, dirty bit read/clear, `pgtable_walk` output, and allocation/free across every enabled format.
