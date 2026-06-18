# sources/distributed-fs/ceph-client/include/linux/iova.h

Purpose: This header defines IOVA range and domain structures plus allocation APIs for managing I/O virtual address PFN ranges, typically for IOMMU DMA.

Important APIs, types, and functions: `struct iova` stores an rbtree node and inclusive PFN low/high range. `struct iova_domain` stores the rbtree lock/root, cached allocation nodes, granule, start and 32-bit PFN limits, last failed 32-bit size, anchor, rcaches, and CPU hotplug node. Helpers compute size, shift, mask, offset, alignment, DMA address, and PFN. APIs include cache get/put, reserve/find/free, fast alloc/free, domain init, rcache init, and domain teardown.

Control flow: Enabled `CONFIG_IOMMU_IOVA` builds allocate and free PFN ranges from a domain rbtree, with fast paths using per-CPU rcaches. Disabled builds provide NULL/zero/no-op stubs. Address conversion shifts PFNs by the domain granule shift.

State and persistence: IOVA allocations persist as rbtree nodes until freed. The domain tracks cached search nodes and rcache state across allocations, plus CPU hotplug cleanup linkage.

Dependencies and integration points: Depends on rbtree, DMA mapping types, spinlocks, IOMMU DMA code, and CPU hotplug for rcache maintenance.

Risks: PFN ranges are inclusive, so size/free calculations must match allocation size. Granule must be a power-of-two for `__ffs`, mask, and alignment helpers. Fast alloc/free require correct rcache flushing to avoid stale or leaked IOVAs. Disabled stubs can hide missing config support.

Test signals: Test aligned and unaligned sizes, 32-bit limit behavior, reserve conflicts, find/free, fast rcache reuse and flush, domain teardown, CPU hotplug rcache drain, and disabled-config fallbacks.
