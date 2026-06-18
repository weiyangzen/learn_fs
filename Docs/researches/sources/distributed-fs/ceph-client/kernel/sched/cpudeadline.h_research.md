# sources/distributed-fs/ceph-client/kernel/sched/cpudeadline.h

## Purpose

`sources/distributed-fs/ceph-client/kernel/sched/cpudeadline.h` declares the CPU-deadline heap data structures and APIs used by the deadline scheduler class. The header was read as a complete 24-line source.

## Important APIs, Types, and Functions

`IDX_INVALID` marks CPUs not present in the heap. `struct cpudl_item` stores a CPU id, that CPU's current earliest deadline, and the heap index for reverse lookup. `struct cpudl` owns the raw spinlock, heap size, free-CPU cpumask, and dynamically allocated item array. The exported declarations are `cpudl_find()`, `cpudl_set()`, `cpudl_clear()`, `cpudl_init()`, and `cpudl_cleanup()`.

## Control Flow

This header has no runtime control flow. It defines the contract consumed by root-domain initialization and by `deadline.c`: initialize a `cpudl`, update it when an rq's deadline state changes, query it when a deadline task needs a later-deadline CPU, and clean it up with the root domain.

## State and Persistence Behavior

The declared state is heap and cpumask memory owned by a scheduler root domain. It persists for the root domain lifetime and is not file-backed.

## Dependencies and Integration Points

The header includes Linux scalar types and spinlock declarations and assumes scheduler definitions for `task_struct` and `cpumask` are visible to users. It is tightly paired with `cpudeadline.c` and integrated by `deadline.c`.

## Risks and Edge Cases

Because the header exposes raw structures, layout changes affect every root-domain user. `IDX_INVALID` must remain distinct from valid heap indices. Callers must hold the appropriate rq/root-domain locks around update operations as documented in the implementation.

## Test Signals

Compile coverage with `deadline.c`, root-domain init/teardown coverage, and lockdep-enabled scheduler tests that exercise `cpudl_set()`, `cpudl_clear()`, and `cpudl_find()` through deadline task migration.
