# sources/distributed-fs/ceph-client/lib/cpu_rmap.c

## Purpose

`sources/distributed-fs/ceph-client/lib/cpu_rmap.c` maintains reverse maps from CPUs to objects with CPU affinities, especially IRQs. It chooses a nearest object for each CPU based on direct affinity, sibling/core, and NUMA-node topology.

## Important APIs, Types, and Functions

Important exported APIs are `alloc_cpu_rmap`, `cpu_rmap_put`, `cpu_rmap_add`, `cpu_rmap_update`, `free_irq_cpu_rmap`, `irq_cpu_rmap_notify`, `irq_cpu_rmap_release`, and `irq_cpu_rmap_add`. Internal helpers include `cpu_rmap_release`, `cpu_rmap_get`, `cpu_rmap_copy_neigh`, `get_free_index`, and optional `debug_print_rmap`.

## Control Flow

Allocation builds a single object containing per-CPU `near[]` entries and an object pointer array, initializes a kref, and assigns each possible CPU to an initial rotating object with infinite distance. Adding an object fills the first free slot. Updating an object's affinity invalidates CPUs that pointed to that object, marks CPUs in the new affinity at distance zero, marks their NUMA nodes for update, then copies nearest mappings from SMT siblings, core siblings, and node masks at increasing distances. IRQ glue allocates notifier objects, registers affinity notifiers, and updates the rmap when IRQ affinity changes.

## State and Persistence Behavior

State lives in caller-owned `struct cpu_rmap` with kref lifetime, `near[cpu]` distance/index records, and `obj[]` pointers. IRQ integration stores `struct irq_glue` objects in `obj[]` and releases them through IRQ notifier release callbacks. There is no file persistence.

## Dependencies and Integration Points

The file depends on CPU masks, topology masks, NUMA node masks, IRQ affinity notifier APIs, krefs, and allocation helpers. It integrates with network and storage drivers that want per-CPU nearest queue/vector lookup after IRQ affinity changes.

## Risks and Edge Cases

The object count is capped at `u16` range. `alloc_cpu_rmap()` uses `cpu % size`, so callers must not pass size zero. Topology propagation only goes through siblings/core/node and does not compute arbitrary NUMA distances. IRQ notifiers must be unregistered before IRQ teardown to avoid stale callbacks.

## Test Signals

Tests should cover allocation size limits, zero-size caller guards, object add exhaustion, affinity updates for direct CPUs and neighboring CPUs, CPU hotplug assumptions around possible/online masks, IRQ notifier update/release paths, and refcount release.

## Read Coverage

Source read size: 339 lines, 8356 bytes.
