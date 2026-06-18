<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cpu_rmap.h -->
# sources/distributed-fs/ceph-client/include/linux/cpu_rmap.h

## Purpose

`cpu_rmap.h` declares CPU affinity reverse maps, which map each CPU to the nearest object, commonly an IRQ or queue, based on affinity masks. The source was read as a complete 67-line file.

## Important APIs, Types, and Functions

`struct cpu_rmap` contains a `kref`, object count, object pointer array, and per-CPU `near[]` entries with object index and distance. `CPU_RMAP_DIST_INF` marks infinite distance. APIs include `alloc_cpu_rmap()`, `cpu_rmap_get()`, `cpu_rmap_put()`, `cpu_rmap_add()`, `cpu_rmap_update()`, `cpu_rmap_lookup_index()`, `cpu_rmap_lookup_obj()`, `alloc_irq_cpu_rmap()`, `free_irq_cpu_rmap()`, `irq_cpu_rmap_add()`, and `irq_cpu_rmap_remove()`.

## Control Flow

A driver allocates a map for a fixed number of objects, adds objects, updates each object's CPU affinity, then fast paths look up the nearest object for a CPU. IRQ-specific helpers allocate with `GFP_KERNEL` and bind IRQ affinities into the same map.

## State and Persistence Behavior

The map persists through reference counts. The per-CPU nearest-object cache must be updated when affinity changes. It is in-memory state only and has no disk persistence.

## Dependencies and Integration Points

It depends on cpumask types, GFP flags, slab allocation, and krefs. It integrates with IRQ affinity, networking queue steering, block/network multiqueue-like placement, and drivers that need CPU-local object selection.

## Risks and Edge Cases

Lookups assume a valid CPU index and initialized `near[]` entries. Affinity changes must call `cpu_rmap_update()` or stale routing can persist. Object count is fixed at allocation, and reference ownership must be balanced with `cpu_rmap_put()`.

## Test Signals

Signals include allocation/free leak tests, update tests for changing cpumasks, lookup correctness for empty/far affinity, IRQ add/remove lifecycle coverage, CPU hotplug affinity update tests, and KASAN/KCSAN runs for flexible-array bounds and races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cpu_rmap.h -->
