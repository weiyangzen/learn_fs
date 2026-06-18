# sources/distributed-fs/ceph-client/rust/helpers/cpumask.c

## Purpose
Provides Rust-callable cpumask mutation, query, copy, allocation, and free helpers.

## APIs, Types, and Functions
Exports set/clear/test variants, `cpumask_setall`, `cpumask_empty`, `cpumask_full`, `cpumask_weight`, `cpumask_copy`, `alloc_cpumask_var`, `zalloc_cpumask_var`, and conditionally `free_cpumask_var` when cpumasks are not offstack.

## Control Flow, State, and Persistence
The helpers mutate caller-provided masks or allocate/free cpumask storage through kernel APIs. Persistent state is the caller-owned cpumask allocation.

## Dependencies and Integration
Depends on `linux/cpumask.h` and CPU topology configuration.

## Risks and Test Signals
Risks include CPU index bounds, allocation/free mismatch under `CONFIG_CPUMASK_OFFSTACK`, and races with hotplug if masks are assumed static. Test signals are cpumask Rust tests, CPU hotplug scenarios, and config matrix builds.
