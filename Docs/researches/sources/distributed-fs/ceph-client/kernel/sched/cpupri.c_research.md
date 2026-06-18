# sources/distributed-fs/ceph-client/kernel/sched/cpupri.c

## Purpose

`sources/distributed-fs/ceph-client/kernel/sched/cpupri.c` maintains a root-domain priority-to-CPU index for real-time and deadline scheduling decisions. It lets the RT scheduler find CPUs running lower-priority work in near-constant time, while supporting affinity masks and optional fitness filters. The file was read as a complete 317-line source.

## Important APIs, Types, and Functions

`convert_prio()` maps scheduler priorities into `CPUPRI_INVALID`, `CPUPRI_NORMAL`, RT priority buckets 1-99, and `CPUPRI_HIGHER`. `__cpupri_find()` checks one priority vector's atomic count and cpumask with memory barriers. `cpupri_find()` is the basic lookup wrapper. `cpupri_find_fitness()` applies an optional per-CPU fitness function, currently used for capacity awareness. `cpupri_set()` moves a CPU between priority vectors. `cpupri_init()` allocates vector cpumasks and `cpu_to_pri`; `cpupri_cleanup()` frees them.

## Control Flow

Writers call `cpupri_set()` with the CPU rq lock held when a runqueue's highest RT-like priority changes. The function converts the incoming priority, adds the CPU to the new vector before removing it from the old vector, and uses atomic/memory-barrier ordering so racing readers see the CPU in at least one valid bucket. Readers call `cpupri_find_fitness()` with a task and optional destination mask. It iterates from lowest priority up to just below the task's priority, checks vector count/mask, intersects with task affinity and active CPUs, filters by fitness when requested, and falls back to a priority-only search if every fitted CPU failed.

## State and Persistence Behavior

State is per root domain in memory: an array of `struct cpupri_vec` buckets and a per-CPU current bucket array. It persists for root-domain lifetime and changes as rq priorities, CPU active state, and scheduler classes change.

## Dependencies and Integration Points

The file depends on cpumasks, atomic counters, memory barriers, RT priority definitions, and scheduler task affinity. It is used by RT balancing and by deadline code when deadline rq state changes map a CPU to `CPUPRI_HIGHER` or back to its RT highest priority.

## Risks and Edge Cases

The data structure is intentionally racy for readers, so correctness relies on scheduler rebalancing to repair stale choices. Barrier ordering in `cpupri_set()` is essential: adding before removing prevents missed CPUs, and decrement-before-mask-clear handles removal races. Fitness fallback favors priority correctness over CPU capacity fit. Initialization cleanup must free only successfully allocated masks on partial failure.

## Test Signals

Signals include RT migration tests with affinity-restricted tasks; priority raise/lower stress under lockdep; capacity-awareness tests with fitness rejection and fallback; CPU active/offline mask tests; randomized bucket invariant checks; and KCSAN-style coverage for reader/writer races.
