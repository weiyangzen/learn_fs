# sources/distributed-fs/ceph-client/tools/perf/util/affinity.c

## Purpose

`affinity.c` provides helpers to bind the current thread/process to CPUs while preserving and later restoring the original CPU mask.

## Important APIs, Types, and Functions

Public APIs are `affinity__setup`, `affinity__set`, `affinity__cleanup`, and `cpu_map__set_affinity`. `get_cpu_set_size` derives the mask size from `sysconf(_SC_NPROCESSORS_CONF)` and `CPU_ALLOC_SIZE`.

## Control Flow and State

Setup allocates `sched_getaffinity` masks for original and current affinity and records the original CPU set. `affinity__set` clears and sets one CPU, then calls `sched_setaffinity`; repeated calls avoid reapplying the same CPU. Cleanup restores the original mask once and frees allocations. `cpu_map__set_affinity` builds a stack CPU set from a perf CPU map and applies it.

## Dependencies and Integration Points

It depends on sched affinity APIs, Linux bitmap helpers, perf CPU maps, and `perf_cpu_map__max`. Perf stat/record paths use it when pinning work to target CPUs.

## Risks and Test Signals

Risks include CPU numbers beyond allocated masks, systems with large CPU counts, failed restore on cleanup, and invalid CPU maps. Tests should cover setup failure, repeated set, cleanup idempotence, sparse CPU maps, and permission errors.
