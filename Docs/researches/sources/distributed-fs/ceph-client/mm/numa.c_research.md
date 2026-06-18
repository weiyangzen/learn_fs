# sources/distributed-fs/ceph-client/mm/numa.c

## Purpose

`numa.c` provides small generic NUMA helpers for allocating per-node `pg_data_t` structures and fallback physical-address-to-node lookups. It is early-boot infrastructure used before normal allocators are available. In this source tree, it underpins the memory topology that later page allocation, reclaim, writeback throttling, and filesystem cache behavior rely on.

## Important APIs, Types, And Functions

- `struct pglist_data *node_data[MAX_NUMNODES]`: exported global array behind `NODE_DATA(nid)`.
- `alloc_node_data(int nid)`: allocates and zeros one node's `pg_data_t` from memblock, preferring memory local to `nid`.
- `alloc_offline_node_data(int nid)`: allocates `pg_data_t` for an offline node with `memblock_alloc_or_panic()`.
- `memory_add_physaddr_to_nid(u64 start)`: weak fallback for memory hotplug node selection, returning node 0 when architecture/meminfo code does not provide a real mapping.
- `phys_to_target_node(u64 start)`: weak fallback for target-node lookup, also returning node 0.

## Control Flow

During NUMA initialization, platform code calls `alloc_node_data()` for each parsed node. The function rounds `sizeof(pg_data_t)` to a cache-line boundary, tries to allocate from the target node with `memblock_phys_alloc_try_nid()`, panics on failure, reports the physical range, checks where the allocation actually landed via `early_pfn_to_nid()`, stores the virtual address in `node_data[nid]`, and zeros the structure.

`alloc_offline_node_data()` handles node structures that must exist even when a node has no online memory. It uses a generic memblock allocation and stores it in `node_data[nid]`.

The two fallback lookup functions are compiled only when no macro or architecture implementation overrides them. They log once and return node 0, preserving functionality on platforms without retained NUMA memblock metadata.

## State And Persistence Behavior

`node_data[]` is long-lived kernel memory initialized during boot and used for the lifetime of the system. Allocations come from memblock early memory and are not freed. The fallback lookup functions have no state except `pr_info_once()` rate state.

## Dependencies And Integration Points

The file depends on `memblock`, `numa.h`, and `numa_memblks.h`. Its output is consumed by the buddy allocator, page reclaim, writeback code such as `node_dirty_ok()`, memory hotplug, per-node statistics, and any subsystem that resolves `NODE_DATA()`. Ceph-client behavior is indirect: page-cache allocation, dirty throttling, and reclaim decisions depend on correct node data.

## Risks And Edge Cases

- `alloc_node_data()` panics if memblock cannot allocate per-node metadata, which is appropriate during boot but makes malformed topology fatal.
- Node-local allocation is best effort. If metadata lands on another node, the function logs it but continues.
- Fallback `memory_add_physaddr_to_nid()` and `phys_to_target_node()` always return 0; on systems needing accurate hotplug placement, relying on these stubs can misplace memory.

## Test Signals

- Boot logs should show `NODE_DATA(nid)` allocations for expected nodes and no panic.
- NUMA topology tests should confirm `NODE_DATA()` exists for memoryless/offline nodes when relevant.
- Memory hotplug tests should verify whether architecture-specific lookup functions override the stubs; if not, added memory will target node 0.
