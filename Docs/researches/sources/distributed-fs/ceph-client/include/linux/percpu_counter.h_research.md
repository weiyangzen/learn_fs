<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/percpu_counter.h -->
# sources/distributed-fs/ceph-client/include/linux/percpu_counter.h

## Purpose
Defines a scalable approximate counter with per-CPU deltas and a global folded count on SMP, plus a simple exact scalar implementation on UP.

## Important APIs, Types, And Functions
- `PERCPU_COUNTER_LOCAL_BATCH` enables very large local batching for write-heavy/read-rare counters.
- SMP `struct percpu_counter` contains a raw spinlock, global `s64 count`, optional hotplug list node, and per-CPU `s32` counters.
- Initialization/destruction: `percpu_counter_init_many()`, `percpu_counter_init()`, `percpu_counter_destroy_many()`, and `percpu_counter_destroy()`.
- Mutation/read helpers: `percpu_counter_set()`, `percpu_counter_add_batch()`, `percpu_counter_add()`, `percpu_counter_add_local()`, `percpu_counter_sub_local()`, `percpu_counter_inc()`, `percpu_counter_dec()`, `percpu_counter_sub()`, and `percpu_counter_sync()`.
- Query helpers: `percpu_counter_read()`, `percpu_counter_read_positive()`, `percpu_counter_sum()`, `percpu_counter_sum_positive()`, `percpu_counter_compare()`, `__percpu_counter_compare()`, `percpu_counter_limited_add()`, and `percpu_counter_initialized()`.

## Control Flow
On SMP, updates add to a local per-CPU counter until a batch threshold requires folding into the global count under the raw spinlock. Reads can return the approximate global count or sum all per-CPU counters for accuracy. Compare and limited-add use batch-aware helpers. On UP, operations update the scalar count directly with IRQ protection where needed.

## State And Persistence
Persistent state is the global count plus per-CPU deltas. CPU hotplug state is tracked through a list when enabled. The count is approximate unless explicitly summed or synchronized.

## Dependencies And Integration Points
Depends on spinlocks, SMP/percpu allocation, lists, thread count, and CPU hotplug support. It integrates with filesystems and resource accounting paths that need cheap frequent updates and tolerate bounded read error.

## Risks And Edge Cases
Risks include treating `percpu_counter_read()` as exact, failing to destroy allocated per-CPU storage, negative approximate reads for logically nonnegative counters, batch values hiding limit crossings, hotplug folding races, and misuse in contexts that cannot take the internal lock.

## Test Signals
Stress concurrent increments/decrements, compare approximate versus summed values, limited-add at positive and negative limits, local batch behavior, CPU hotplug folding, UP and SMP builds, init-many/destroy-many arrays, and leak detection for allocated counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/percpu_counter.h -->
