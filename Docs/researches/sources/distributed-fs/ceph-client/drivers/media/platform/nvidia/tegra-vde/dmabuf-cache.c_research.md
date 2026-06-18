# sources/distributed-fs/ceph-client/drivers/media/platform/nvidia/tegra-vde/dmabuf-cache.c

## Purpose
`dmabuf-cache.c` caches imported DMA-buf attachments and optional IOMMU mappings for the Tegra VDE driver. It avoids repeated attach/map/unmap churn while buffers are reused across decode jobs.

## Important APIs, Types, and Functions
`struct tegra_vde_cache_entry` records direction, attachment, SG table, IOVA, delayed unmap work, reference count, and list linkage. Public helpers are `tegra_vde_dmabuf_cache_map()`, `tegra_vde_dmabuf_cache_unmap()`, `tegra_vde_dmabuf_cache_unmap_sync()`, and `tegra_vde_dmabuf_cache_unmap_all()`. Internal cleanup is `tegra_vde_release_entry()` and delayed work callback `tegra_vde_delayed_unmap()`.

## Control Flow
Map first searches `vde->map_list` under `map_lock`. If an entry for the DMA-buf exists and pending delayed unmap can be canceled, it reuses the mapping, upgrades direction to bidirectional if needed, drops the caller's DMA-buf reference, returns the cached address, and increments refcount. New maps attach the DMA-buf, map the attachment, reject sparse SG tables without IOMMU, allocate a cache entry, optionally allocate/map an IOVA, and add it to the cache. Unmap decrements refcount and either releases immediately or schedules delayed release after five seconds. Sync/all cleanup drains delayed or all cache entries.

## State and Persistence
Runtime state is the cache list in `struct tegra_vde`, each entry's reference count, delayed work, DMA-buf attachment, SG table, and IOVA. There is no persistence beyond the device lifetime.

## Dependencies and Integration Points
The code depends on DMA-buf attachment APIs, SG tables, IOVA/IOMMU helpers from `iommu.c`, workqueues, and `vde->map_lock`. It is used by the V4L2 buffer path for imported buffers.

## Risks and Edge Cases
If delayed work is already running, map skips that entry and creates a new one. Direction changes are handled by marking bidirectional, but the original DMA mapping direction may already be fixed. Non-IOMMU operation rejects non-contiguous SG tables, so imported buffers must be physically contiguous. `tegra_vde_dmabuf_cache_unmap_all()` loops until delayed work can be canceled, yielding with `schedule()`.

## Test Signals
Test repeated decode with the same DMA-buf, immediate release and delayed-release paths, sync cleanup on stream teardown, non-contiguous DMA-buf rejection without IOMMU, IOMMU map/unmap balance, and module unload with no pending cache entries.
