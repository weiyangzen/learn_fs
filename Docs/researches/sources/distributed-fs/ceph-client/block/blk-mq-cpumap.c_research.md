# sources/distributed-fs/ceph-client/block/blk-mq-cpumap.c

## Purpose
`blk-mq-cpumap.c` builds CPU-to-hardware-queue mappings for multiqueue block devices. It provides generic possible/online CPU queue counts, even CPU grouping, NUMA lookup by queue, and IRQ-affinity-based mapping when a bus supplies affinity information.

## Important APIs, Types, And Functions
Exported APIs are `blk_mq_num_possible_queues()`, `blk_mq_num_online_queues()`, `blk_mq_map_queues()`, and `blk_mq_map_hw_queues()`. `blk_mq_hw_queue_to_node()` performs reverse lookup from queue index to NUMA node. The main data structure is `struct blk_mq_queue_map`, especially `nr_queues`, `queue_offset`, and per-CPU `mq_map`.

## Control Flow
Queue count helpers weight either `cpu_possible_mask` or `cpu_online_mask` and cap the result by `max_queues` when nonzero. `blk_mq_map_queues()` asks `group_cpus_evenly()` for queue-sized CPU masks; if allocation fails, all possible CPUs map to `queue_offset`. Otherwise each queue is assigned CPUs from its group and the temporary mask array is freed. `blk_mq_map_hw_queues()` first tries `dev->bus->irq_get_affinity(dev, queue + offset)` for each hardware queue; if any mask is unavailable or the bus has no callback, it falls back to even mapping.

## State And Persistence
The file only writes the caller-provided `qmap->mq_map` array. No persistent or global state is owned.

## Dependencies And Integration Points
It depends on CPU masks, NUMA `cpu_to_node()`, `group_cpus_evenly()`, bus IRQ affinity callbacks, and blk-mq queue-map initialization used by drivers.

## Risks And Test Signals
Risks include fallback mapping hiding affinity failures, possible CPUs with no online counterpart, queue offsets for multiple map types, and NUMA reverse lookup returning `NUMA_NO_NODE` when a queue is unmapped. Tests should cover max queue caps, zero max queue behavior, failed `group_cpus_evenly()`, partial IRQ affinity failure fallback, and hotplug-era possible versus online CPU counts.
