# sources/distributed-fs/ceph-client/kernel/watchdog_buddy.c

## Purpose
`watchdog_buddy.c` implements a hard-lockup backend that uses hrtimer progress on one CPU to check a neighboring CPU. Instead of relying on a local perf NMI event per CPU, each active watchdog CPU periodically checks whether the next active CPU's hrtimer interrupt counter is advancing. This file plugs into the weak hardlockup hooks declared by `watchdog.c`.

## Important APIs, types, and functions
The file owns a static `cpumask_t watchdog_cpus`, the set of CPUs participating in buddy checking. The key helper is `watchdog_next_cpu()`, which uses `cpumask_next_wrap()` to find the next CPU in that mask and returns `nr_cpu_ids` when the current CPU would only find itself. Backend entry points are `watchdog_hardlockup_probe()`, `watchdog_hardlockup_enable()`, `watchdog_hardlockup_disable()`, and `watchdog_buddy_check_hardlockup()`.

## Control flow
Probe is simple: `watchdog_hardlockup_probe()` sets the shared `watchdog_hardlockup_miss_thresh` to 3 and returns success. Raising the miss threshold is important because buddy checking observes another CPU's hrtimer count and needs enough grace periods to avoid transient false positives around CPU hotplug or startup.

When a CPU is enabled, `watchdog_hardlockup_enable()` first touches that CPU's hardlockup state through `watchdog_hardlockup_touch_cpu(cpu)` so other CPUs do not report it before its hrtimer has run. It then computes the next currently participating CPU and touches that CPU too, because this CPU may soon begin checking it. A write memory barrier ensures these touch operations are visible before the CPU is added to `watchdog_cpus`, then the CPU bit is set.

When disabling, `watchdog_hardlockup_disable()` finds the next CPU before clearing the current CPU from the mask. If such a next CPU exists, it touches that CPU to avoid a false positive from the CPU before this one, which will begin checking a different buddy after the mask changes. Another write memory barrier orders the touch before the mask removal.

The periodic check is driven by the generic hrtimer code in `watchdog.c`. `watchdog_hardlockup_kick()` increments the local hrtimer interrupt counter and calls `watchdog_buddy_check_hardlockup()`. This file finds the next CPU in `watchdog_cpus`; if there is no other CPU, it returns. Otherwise it executes a read memory barrier paired with the enable/disable write barriers and calls `watchdog_hardlockup_check(next_cpu, NULL)`.

## State and persistence behavior
The only local persistent-in-memory state is `watchdog_cpus`. Hardlockup counters, touch flags, warned flags, and panic/report behavior live in `watchdog.c`. State is runtime-only and changes as CPUs are enabled or disabled for lockup detection. No userspace-visible settings are stored in this file directly.

## Dependencies and integration points
This backend depends on the generic hrtimer-counting hardlockup path in `watchdog.c`, including `watchdog_hardlockup_miss_thresh`, `watchdog_hardlockup_touch_cpu()`, and `watchdog_hardlockup_check()`. It also depends on CPU masks and SMP memory ordering. It is compiled as a backend selected by kernel configuration and supplies strong definitions that override the weak generic hardlockup hooks.

## Risks and test signals
The main risk is false hardlockup reporting during CPU hotplug, especially when a newly online CPU has been added to scheduler-visible masks before its watchdog hrtimer fires, or when removing a CPU changes which buddy another CPU checks. The explicit touch operations and memory barriers are the main safeguards. Another risk is single-CPU behavior: when only one CPU participates, there is no next CPU and no buddy check can be performed.

Useful test signals include enabling the first CPU and verifying no self-check occurs; enabling multiple CPUs and confirming each checks the next wrapped CPU; CPU online/offline churn without false positives; correct miss threshold of 3 after probe; memory-order-sensitive tests where a buddy observes mask changes only after touch state is visible; and integration with `watchdog_hardlockup_check()` reports when a buddy CPU's hrtimer counter stops.
