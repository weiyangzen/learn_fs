# sources/distributed-fs/ceph-client/lib/cpumask.c

## Purpose

`sources/distributed-fs/ceph-client/lib/cpumask.c` provides non-inline cpumask allocation helpers for offstack masks and CPU selection helpers that distribute work across online CPUs.

## Important APIs, Types, and Functions

Under `CONFIG_CPUMASK_OFFSTACK`, exported or init APIs are `alloc_cpumask_var_node`, `alloc_bootmem_cpumask_var`, `free_cpumask_var`, and `free_bootmem_cpumask_var`. Always-present exported helpers are `cpumask_local_spread`, `cpumask_any_and_distribute`, and `cpumask_any_distribute`. The file also defines per-CPU `distribute_cpu_mask_prev`.

## Control Flow

Offstack allocation uses `kmalloc_node(cpumask_size())`, reports allocation failures under debug config, and frees with `kfree`; boot allocation uses memblock. `cpumask_local_spread()` wraps the index by online CPU count and delegates to `sched_numa_find_nth_cpu()`. The distribute helpers read the current CPU's previous selection, find the next CPU in the requested mask or mask intersection with wraparound, and store the new previous value when a CPU is found.

## State and Persistence Behavior

Allocated cpumasks persist until caller free. The spread helper has no state. Distribution state is per-CPU and affects subsequent selections from the same CPU to avoid always choosing the first CPU.

## Dependencies and Integration Points

Dependencies include cpumask, bitops, memblock, NUMA scheduler helpers, per-CPU storage, and slab allocation. The helpers are used by drivers and core code that need masks allocated outside stack limits or need fair-ish CPU selection.

## Risks and Edge Cases

`cpumask_local_spread()` assumes at least one online CPU. The distribute helpers intentionally skip CPU 0 on first selection because previous starts at zero. Offstack allocation behavior differs at compile time; callers must handle the inline always-success version when offstack is disabled.

## Test Signals

Signals include offstack allocation/free on nodes, bootmem allocation/free during init, local-spread order by NUMA hop, distribution wraparound across masks, empty-mask return `>= nr_cpu_ids`, and debug failure reporting.

## Read Coverage

Source read size: 168 lines, 4746 bytes.
