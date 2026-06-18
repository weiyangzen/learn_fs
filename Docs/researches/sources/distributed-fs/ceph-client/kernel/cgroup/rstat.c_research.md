# sources/distributed-fs/ceph-client/kernel/cgroup/rstat.c

## Purpose

`rstat.c` implements cgroup recursive statistics infrastructure. It tracks per-cpu stat updates cheaply, builds flush trees on demand, flushes subsystem and base cgroup stats, exposes CPU time totals, and registers BPF kfuncs for rstat integration.

## Important APIs, Types, and Functions

Main APIs are `css_rstat_updated()`, `css_rstat_flush()`, `css_rstat_init()`, `css_rstat_exit()`, `ss_rstat_init()`, `__cgroup_account_cputime()`, `__cgroup_account_cputime_field()`, and `cgroup_base_stat_cputime_show()`. It uses `struct css_rstat_cpu`, `struct cgroup_rstat_base_cpu`, `struct cgroup_base_stat`, per-subsystem locks and llist heads, and the global base-stat lock/list.

## Control Flow and State

Stat writers update per-cpu counters and call `css_rstat_updated()` with preemption disabled. This function atomically adds the css's per-cpu node to a lockless per-cpu backlog list, using a self-pointer/cmpxchg pattern to tolerate IRQ/NMI reentry. Flushers call `css_rstat_flush()`, which iterates possible CPUs, acquires the appropriate rstat lock, drains the lockless list into an updated tree, builds an ordered flush list with children before parents, and invokes either base-stat flushing/BPF hooks or the subsystem's `css_rstat_flush` callback.

Base CPU-time accounting stores per-cpu deltas protected by `u64_stats` seqcounts. `cgroup_base_stat_flush()` propagates deltas to cgroup and parent subtree totals. The root cgroup is handled specially by reading global kernel CPU stats directly.

## Dependencies and Integration Points

It integrates with cgroup core css lifetime, per-cpu allocation, llist, spinlocks, tracepoints, scheduler CPU time accounting, `u64_stats`, BPF/BTF kfunc registration, and optional scheduler core force-idle stats.

## Risks and Edge Cases

The memory-ordering comments are important: users needing a strict updater/flusher guarantee must provide a barrier before `css_rstat_updated()` and may need a paired barrier in flush processing. NMI updates are ignored on architectures lacking safe cmpxchg or percpu operations. Flushes can be expensive because they iterate all possible CPUs, but they drop/reacquire locks per CPU to avoid long IRQ-off sections. Exit sanity checks warn if updated lists are not clean after flush.

## Test Signals

Tests should account CPU time in nested cgroups, flush from subtree roots, validate child-before-parent propagation, exercise subsystem rstat callbacks, run concurrent updater/flusher stress, verify BPF kfunc availability for tracing programs, test css exit cleanup, and compare root cgroup CPU output to global CPU stats.
