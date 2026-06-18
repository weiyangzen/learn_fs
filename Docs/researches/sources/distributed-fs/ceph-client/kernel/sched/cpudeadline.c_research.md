# sources/distributed-fs/ceph-client/kernel/sched/cpudeadline.c

## Purpose

`sources/distributed-fs/ceph-client/kernel/sched/cpudeadline.c` maintains the root-domain CPU deadline heap used by `SCHED_DEADLINE` load balancing. It lets the deadline class find CPUs whose current earliest deadline is later than a waking or pushable task's deadline, and separately tracks CPUs with no deadline tasks as free candidates. The file was read as a complete 278-line source.

## Important APIs, Types, and Functions

The implementation uses `struct cpudl` and `struct cpudl_item` declared in `cpudeadline.h`. The heap helpers `parent()`, `left_child()`, `right_child()`, `cpudl_heapify_down()`, `cpudl_heapify_up()`, and `cpudl_heapify()` maintain a max-heap ordered by latest earliest-deadline. `cpudl_find()` is the lookup API. `cpudl_set()` inserts or updates a CPU's deadline and removes it from `free_cpus`. `cpudl_clear()` removes a CPU from the heap and marks it free or unavailable depending on the runqueue online state. `cpudl_init()` and `cpudl_cleanup()` allocate and release heap and cpumask storage.

## Control Flow

When a deadline task becomes runnable or the earliest deadline on an rq changes, `cpudl_set()` records the CPU in the max-heap and heapifies it upward or downward. When the last deadline task leaves an rq or the CPU goes offline, `cpudl_clear()` removes its heap item by replacing it with the tail and heapifying, then updates `free_cpus`. `cpudl_find()` first prefers CPUs in `free_cpus` intersected with the task affinity mask. On asymmetric-capacity systems it filters that mask through `dl_task_fits_capacity()`, falling back to the highest-capacity CPU if none fit. If no free CPU is usable, it checks the heap root: if the root CPU is allowed and its current earliest deadline is later than the task deadline, that CPU can be preempted.

## State and Persistence Behavior

State is per root domain in memory: a raw spinlock, heap size, `free_cpus` cpumask, and one `elements` array that stores both heap positions and per-CPU reverse indices. `IDX_INVALID` means the CPU is not currently in the heap. State is rebuilt through scheduler root-domain initialization and updated under rq/root-domain scheduling events.

## Dependencies and Integration Points

The file depends on scheduler deadline time comparison (`dl_time_before()`), task affinity, CPU present/online state, capacity-awareness helpers, and raw spinlocks. It is updated from `deadline.c` through `inc_dl_deadline()`, `dec_dl_deadline()`, `rq_online_dl()`, and `rq_offline_dl()`, and queried by deadline wakeup, push, and pull balancing.

## Risks and Edge Cases

Heap reverse-index correctness is critical: every move updates `elements[cpu].idx`. `cpudl_maximum()` assumes a non-empty heap when no free CPU path succeeds, so callers rely on valid root-domain state. `cpudl_find()` may return a CPU that races with concurrent updates; deadline balancing revalidates under rq locks. Capacity fallback intentionally favors running the task over perfect fit when all allowed CPUs fail the fit test.

## Test Signals

Signals include heap invariant tests under random set/clear/update sequences; deadline migration tests where later-deadline CPUs are selected; free-CPU preference tests; CPU hotplug transitions checking `online` behavior; asymmetric-capacity deadline placement tests; and scheduler stress with concurrent wakeups and migrations under lockdep/KCSAN.
