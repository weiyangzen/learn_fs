<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cpumask.h -->
# sources/distributed-fs/ceph-client/include/linux/cpumask.h

## Purpose

`cpumask.h` is the core bitmap API for representing sets of CPU IDs and the global possible, present, enabled, online, active, and dying CPU masks. It provides fast inline scan, set, clear, parse, print, allocate, and iteration helpers. The source was read as a complete 1,421-line file.

## Important APIs, Types, and Functions

It exposes `nr_cpu_ids`, `set_nr_cpu_ids()`, mask size constants, global masks `cpu_possible_mask`, `cpu_present_mask`, `cpu_enabled_mask`, `cpu_online_mask`, `cpu_active_mask`, and `cpu_dying_mask`, plus counters such as `__num_online_cpus` and `__num_possible_cpus`. Helpers include `cpumask_first*()`, `cpumask_next*()`, `cpumask_any*()`, `cpumask_nth*()`, `for_each_cpu*()` macros, `cpumask_set_cpu()`, `cpumask_clear_cpu()`, `cpumask_test_cpu()`, atomic test/set/clear helpers, boolean operations, equality/subset/intersection, weight, shifts, copy, parse/print helpers, off-stack allocation helpers, `get_cpu_mask()`, `num_*_cpus()`, `cpu_*()` predicates, `set_cpu_*()` mutators, and `cpumap_print_*()` sysfs helpers.

## Control Flow

Most helpers are inline wrappers over generic bitmap operations using an optimized bit count: fixed constants for small masks, `nr_cpu_ids` for runtime-sized masks, or `NR_CPUS` for larger clearing/copying. CPU hotplug and boot code update global masks, while readers iterate or query those masks to route scheduling, interrupts, memory policy, and device affinity.

## State and Persistence Behavior

Global cpumasks represent boot-lifetime CPU topology and dynamic hotplug state. `cpu_possible_mask` is fixed after boot sizing; present/online/active/enabled/dying masks vary with platform discovery and hotplug. `cpumask_var_t` may be heap-backed with `CONFIG_CPUMASK_OFFSTACK`, otherwise it is an on-stack one-element array wrapper.

## Dependencies and Integration Points

It depends on atomic, bitmap, cleanup, cpumask types, GFP types, NUMA, thread limits, generic types, and asm bug checks. It is foundational for scheduler, CPU hotplug, cpufreq, cpuidle, IRQ affinity, cpuset, NUMA, workqueues, and sysfs CPU-list exports.

## Risks and Edge Cases

Only `nr_cpu_ids` bits are valid for most masks. Direct assignment or dereference of `cpumask_var_t` can corrupt memory when off-stack allocation uses only `nr_cpumask_bits`. Iterators return `>= nr_cpu_ids` when no CPU is found. Global mask snapshots are racy without CPU hotplug locking. UP builds hardcode many predicates to CPU0, so modifying masks has no practical effect.

## Test Signals

Signals include cpumask unit tests for scan/next/wrap/nth operations, parse/print round trips, off-stack allocation failure paths, hotplug mask transitions under lockdep, UP/SMP build variants, sysfs cpulist/cpumap output size checks, and KASAN tests for allocation sizing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cpumask.h -->
