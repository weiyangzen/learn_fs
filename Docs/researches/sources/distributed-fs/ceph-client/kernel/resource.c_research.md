# sources/distributed-fs/ceph-client/kernel/resource.c

## Purpose
`resource.c` is the kernel's generic I/O port and physical memory resource-tree manager. It owns the exported root resources `ioport_resource`, `iomem_resource`, and `soft_reserve_resource`, exposes `/proc/ioports` and `/proc/iomem`, arbitrates insert/request/release/adjust operations on resource trees, and supplies helper walks used by memory hotplug, `/dev/mem`, CXL/device-private memory, and driver resource reservation paths. The implementation is generic kernel infrastructure rather than Ceph-specific code.

## Important APIs, Types, And Functions
The central type is `struct resource`, with `start`, `end`, `flags`, `desc`, `parent`, `child`, and `sibling` representing ordered nested ranges. `resource_lock` is a global `rwlock_t` protecting tree topology and range metadata. Exported APIs include `request_resource()`, `request_resource_conflict()`, `release_resource()`, `allocate_resource()`, `find_resource_space()`, `insert_resource()`, `insert_resource_conflict()`, `insert_resource_expand_to_fit()`, `remove_resource()`, `adjust_resource()`, `__request_region()`, `__release_region()`, `devm_request_resource()`, `devm_release_resource()`, `__devm_request_region()`, `__devm_release_region()`, `walk_iomem_res_desc()`, `walk_system_ram_res()`, `walk_system_ram_range()`, `walk_mem_res()`, `region_intersects()`, `region_intersects_soft_reserve()`, `resource_is_exclusive()`, `iomem_is_exclusive()`, and optional `alloc_free_mem_region()` / `request_free_mem_region()` helpers under `CONFIG_GET_FREE_REGION`.

Private helpers implement the mechanics: `next_resource()` and `for_each_resource()` do preorder traversal, `__request_resource()` inserts non-overlapping children, `__release_resource()` removes a node while either dropping or lifting children, `find_next_res()` finds clipped matching ranges, `__region_intersects()` classifies a query as disjoint/intersecting/mixed, and `__find_resource_space()` scans holes under alignment and min/max constraints.

## Control Flow
Request paths acquire `resource_lock` for write, validate that the new range fits the root, walk sorted siblings, and either link the node or return the first conflict. Insert paths are more complex: `__insert_resource()` can wrap existing fully-contained conflicts under the new resource, enabling firmware or bus windows to become parents of previously discovered children. Release and remove paths unlink a resource and either release or reparent children depending on caller intent.

Range-walk APIs repeatedly call `find_next_res()` and advance to `res.end + 1`, passing clipped ranges to callbacks. Allocation scans gaps between sibling resources, clips against constraints, lets architecture code remove reservations via `arch_remove_reservations()`, applies alignment or a custom `alignf`, then installs the selected range. `/proc` display uses seq_file traversal under the read lock and hides addresses from readers lacking `CAP_SYS_ADMIN`.

Memory hotremove uses `release_mem_region_adjustable()` to remove, shrink, or split a busy memory resource. If splitting, it allocates a new high resource and reparents children above the split. Memory hotplug can mark System RAM resources mergeable and merge adjacent childless resources with identical flags, names, and descriptors.

## State And Persistence
Resource trees are in-memory global kernel state. The root resources live for the lifetime of the kernel; dynamically allocated resources are freed only if they came from slab, while early memblock-allocated descriptors may intentionally leak when released. `/proc/ioports`, `/proc/iomem`, debug messages, and `/dev/mem` mapping revocation reflect that state but do not persist it across boot. Boot parameters `reserve=` and `iomem=` mutate initial reservations or strictness policy.

## Dependencies And Integration Points
This file depends on `linux/ioport.h`, procfs, seq_file, devres, memory hotplug, Kconfig-conditioned strict devmem checks, pseudo filesystem inode support, and architecture hooks such as `arch_remove_reservations()` and `devmem_is_allowed()`. Integration points include PCI/firmware resource discovery, driver `request_region()` APIs, CXL namespace resource allocation, ZONE_DEVICE/private memory, memory hotplug/hotremove, `/dev/mem`, and System RAM walkers used by memory management.

## Risks
The main risks are off-by-one and overflow errors in inclusive ranges, stale `struct resource *` pointers after merge/free, lock ordering around callbacks and devres cleanup, and subtle child reparenting mistakes when splitting/removing nested ranges. `walk_res_desc()` and related loops must handle `res.end + 1` carefully near address-space limits. `__request_region_locked()` can sleep for muxed resources after dropping the write lock, so callers must tolerate retries. Strict devmem revocation relies on correct inode publication barriers and on resource busy/exclusive flags being set before mappings are revoked.

## Test Signals
`resource_kunit.c` directly tests resource union/intersection helpers and `region_intersects()` over nested System RAM/CXL-style windows. Additional signals should come from kernel selftests and boot tests that exercise `/proc/iomem`, `reserve=`, `iomem=strict/relaxed`, hotplug/hotremove, driver request/release paths, and CXL/device-private memory allocation. Lockdep, KASAN, KCSAN, and memory hotplug stress runs are useful for catching topology and lifetime mistakes.
