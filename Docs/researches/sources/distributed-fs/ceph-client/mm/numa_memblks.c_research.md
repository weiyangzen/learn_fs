# sources/distributed-fs/ceph-client/mm/numa_memblks.c

## Purpose

`numa_memblks.c` manages early NUMA memory block metadata. It records parsed memory ranges, validates and merges them against memblock DRAM, registers node ownership in `memblock.memory`, handles reserved ranges, manages the NUMA distance table, supports fake NUMA emulation, and optionally retains enough metadata for memory hotplug address-to-node decisions.

This file is core topology infrastructure. Ceph-client effects are indirect but important: page-cache allocation locality, writeback dirty limits, reclaim accounting, and hotplug behavior all depend on correct physical-memory-to-node registration.

## Important APIs, Types, And Functions

- Global topology state: `nodemask_t numa_nodes_parsed`, `int numa_distance_cnt`, and static `u8 *numa_distance`.
- Static meminfo stores: `numa_meminfo` and `numa_reserved_meminfo`.
- Distance APIs: `numa_reset_distance()`, `numa_set_distance()`, and exported `__node_distance()`.
- Memblock registration APIs: `numa_add_memblk()`, `numa_add_reserved_memblk()`, `numa_cleanup_meminfo()`, `numa_memblks_init()`, and `numa_fill_memblks()`.
- Internal helpers: `numa_nodemask_from_meminfo()`, `numa_add_memblk_to()`, `numa_remove_memblk_from()`, `numa_move_tail_memblk()`, `numa_clear_kernel_node_hotplug()`, `numa_register_meminfo()`, and `cmp_memblk()`.
- Optional retained-info APIs under `CONFIG_NUMA_KEEP_MEMINFO`: exported `phys_to_target_node()` and `memory_add_physaddr_to_nid()`.

## Control Flow

Topology setup typically enters through `numa_memblks_init(init_func, memblock_force_top_down)`. It clears parsed/possible/online node masks, zeroes `numa_meminfo`, resets all `memblock.memory` and `memblock.reserved` node IDs to `NUMA_NO_NODE`, clears hotplug flags, and resets the distance table. It then calls the architecture/platform `init_func()` to populate `numa_meminfo` and distance data.

After platform parsing, it optionally restores memblock allocation direction to top-down, sanitizes parsed ranges with `numa_cleanup_meminfo()`, invokes `numa_emulation()` to mutate topology if requested, and finally registers the resulting memory info through `numa_register_meminfo()`.

`numa_cleanup_meminfo()` is the central validator. It trims all ranges to DRAM boundaries, moves non-DRAM/reserved-only ranges into `numa_reserved_meminfo`, preserves non-RAM tails above current DRAM limits as reserved ranges, removes empty ranges, rejects overlaps across different nodes, warns and merges overlaps within the same node, and merges same-node neighboring ranges if no other node owns the intervening span. Unused array entries are cleared to `NUMA_NO_NODE`.

`numa_register_meminfo()` builds `node_possible_map` from CPU-parsed nodes plus memory-bearing nodes, rejects an empty possible map, calls `memblock_set_node()` for each memory range, clears hotplug eligibility for any node containing kernel-reserved memory through `numa_clear_kernel_node_hotplug()`, and validates pfn-to-node alignment if node IDs are not stored in page flags.

Distance handling is lazy. `numa_set_distance()` allocates a square table sized to the highest currently parsed node if needed, initializes local/remote defaults, validates bounds and local-distance invariants, and writes one byte per pair. `numa_reset_distance()` frees the old memblock table and allows recreation. `__node_distance()` returns defaults for out-of-range queries.

`numa_fill_memblks()` repairs gaps across a requested physical span by collecting overlapping blocks, sorting them by start, extending first/last to cover the requested bounds, and backfilling gaps by moving later block starts to the previous end. It returns `NUMA_NO_MEMBLK` when no parsed block overlaps the range.

When `CONFIG_NUMA_KEEP_MEMINFO` is enabled, hotplug lookup helpers search retained `numa_meminfo` and `numa_reserved_meminfo`. `phys_to_target_node()` prefers online memory info unless the address is also in reserved info, while `memory_add_physaddr_to_nid()` returns the matching memory node or falls back to the first parsed block's node.

## State And Persistence Behavior

Most data is early boot `__initdata` unless `CONFIG_NUMA_KEEP_MEMINFO` preserves it. The persistent effects are node IDs written into memblock regions, node masks, hotplug flags, and the allocated NUMA distance table. Distance memory is allocated and freed through memblock, not normal slab.

Reserved meminfo records ranges outside usable memory or explicitly registered reserved ranges so later hotplug/target-node logic can avoid losing firmware/kernel placement knowledge.

## Dependencies And Integration Points

This file depends on `memblock`, `sort`, generic NUMA masks, architecture NUMA definitions, and the fake-NUMA emulation code. It is called by architecture NUMA initialization. Downstream users include page allocator initialization, node data allocation, memory hotplug, pfn-to-node mapping, reclaim, writeback, scheduler locality, and sysfs node exposure.

Ceph-client integration is through these downstream VM behaviors. Misregistered nodes can skew page-cache placement and dirty throttling for Ceph file data or metadata.

## Risks And Edge Cases

- Cross-node overlapping memory ranges are fatal to NUMA setup.
- Same-node overlaps are tolerated but can hide firmware quirks; warnings should be investigated.
- `numa_distance` uses a sentinel `(void *)1LU` on allocation failure; callers must reset before retrying.
- Distance table sizing depends on nodes known at allocation time; late higher node IDs are rejected until reset.
- Hotplug decisions are weak without `CONFIG_NUMA_KEEP_MEMINFO` or architecture overrides.
- `numa_fill_memblks()` mutates block starts/ends in place; incorrect caller ranges can broaden node ownership.
- Clearing hotplug for any node with reserved kernel memory can make entire nodes un-hotpluggable.

## Test Signals

- Boot with firmware NUMA tables and verify no overlap errors, expected merge logs, and correct `/sys/devices/system/node/` memory ranges.
- Unit or boot tests should cover distance setup, invalid distance rejection, reset/recreate behavior, and out-of-range defaults.
- Memory hotplug tests should validate `memory_add_physaddr_to_nid()` and `phys_to_target_node()` with retained meminfo.
- Fake NUMA tests should confirm `numa_memblks_init()` sanitizes emulated meminfo and registers memblock node IDs correctly.
