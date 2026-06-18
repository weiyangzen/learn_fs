# sources/distributed-fs/ceph-client/include/drm/ttm/ttm_resource.h

Purpose: defines TTM resource managers, resource objects, LRU infrastructure, bulk moves, cursors, bus placements, IO/kmap iterators, allocation/free APIs, eviction, debug, and manager iteration.

Important APIs/types/functions: constants define memory-type and priority limits. Types include `ttm_lru_item`, `ttm_resource_manager_func`, `ttm_resource_manager`, `ttm_bus_placement`, `ttm_resource`, `ttm_lru_bulk_move`, `ttm_resource_cursor`, `ttm_kmap_iter_iomap`, and `ttm_kmap_iter_linear_io`. APIs initialize/finalize managers/resources, allocate/free resources, test intersections/compatibility, set BO back-pointers, bulk-move LRU ranges, evict all resources, report usage/debug, iterate LRUs, initialize IO mapping iterators, and create debugfs entries.

Control flow: BO validation asks the appropriate manager to allocate a resource for a `ttm_place`. Resources are attached to BOs, placed on priority LRUs, moved in bulk for command submission locality, evicted by resource-manager walks, and freed through the manager callback.

State and persistence: managers track usage, size, enablement, eviction fences, LRU lists, optional cgroup region, and driver funcs. Resources store placement, bus mapping, weak BO reference, cgroup charge, and LRU node.

Dependencies and integration: depends on Linux lists, mutex/spinlock/fence, iosys-map, TTM caching/kmap, DRM printer/debugfs, io_mapping, SG, and memory cgroups. It is the lower layer used by TTM BO/device/range-manager code.

Risks and test signals: LRU locking, weak BO references, eviction fence cleanup, manager usage accounting, cgroup charging, and iterator hitch correctness are high risk. Test resource allocation/free, LRU iteration during mutation, bulk moves, evict-all, debug output, IO map iterators, and manager disable with nonempty LRUs.
