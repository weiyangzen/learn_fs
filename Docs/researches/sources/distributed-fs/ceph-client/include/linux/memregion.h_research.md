<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/memregion.h -->
# sources/distributed-fs/ceph-client/include/linux/memregion.h

## Purpose
This header defines simple memory-region ID allocation and architecture cache-invalidation hooks for large physical memory regions.

## Important APIs, types, and functions
`struct memregion_info` records a target NUMA node and physical range. `memregion_alloc()` and `memregion_free()` are available with `CONFIG_MEMREGION`; stubs return `-ENOMEM` or no-op. `cpu_cache_invalidate_memregion()` and `cpu_cache_has_invalidate_memregion()` are available with architecture support; otherwise invalidation warns and returns `-ENXIO`. `cpu_cache_invalidate_all()` invalidates all target regions via length `-1`.

## Control flow
Memory-region providers allocate IDs for ranges and, when physical memory contents may change in a cache-incoherent way, call the cache invalidation helper. Architectures without efficient support reject such invalidation.

## State and persistence
Runtime state for allocated region IDs is held by the memregion implementation. Cache invalidation affects CPU caches but stores no durable state.

## Dependencies and integration points
It depends on types, errno, range, bug/warn helpers, and architecture support. It integrates NVDIMM/CXL/device-memory operations that need broad cache maintenance.

## Risks and test signals
Risks include assuming invalidation writes back dirty data, using all-region invalidation unintentionally, unsupported architectures only warning, and ID leaks. Test allocation/free, unsupported stubs, architecture-supported invalidation over large ranges, and secure-erase/dynamic-region workflows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/memregion.h -->
